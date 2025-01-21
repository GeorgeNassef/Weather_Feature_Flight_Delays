"""Data processing functions for weather and flight data."""

import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import arrow
import pandas as pd
from .models import WeatherData, WeatherObservation, Flight, Diversion

class DataProcessor:
    """Handles processing of weather and flight data."""
    
    def __init__(self, timezone_file: Path):
        """Initialize with airport timezone data."""
        self.airport_timezones = self._load_timezone_data(timezone_file)
        
    def _load_timezone_data(self, filepath: Path) -> Dict[str, str]:
        """Load airport timezone mappings."""
        timezones = {}
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    timezones[row[0]] = row[1]
        return timezones
    
    def convert_to_utc(self, airport: str, time: arrow.Arrow) -> arrow.Arrow:
        """Convert local time to UTC based on airport timezone."""
        if airport not in self.airport_timezones:
            raise ValueError(f"No timezone data for airport: {airport}")
            
        tz = self.airport_timezones[airport]
        return time.to('UTC')
    
    def process_weather_file(self, filepath: Path) -> WeatherData:
        """Process weather data file into structured format."""
        try:
            with open(filepath, 'r') as file:
                reader = csv.reader(file)
                # Skip header rows
                for _ in range(6):
                    next(reader)
                    
                observations = []
                time_index = [0]
                current_time = None
                
                for i, row in enumerate(reader):
                    obs = WeatherObservation.from_raw(row)
                    
                    if current_time != obs.time:
                        current_time = obs.time
                        time_index.append(i)
                        
                    observations.append(obs)
                    
                return WeatherData(observations, time_index)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Weather data file not found: {filepath}")
            
    def process_flight_data(self, filepath: Path) -> List[Flight]:
        """Process flight data from CSV into structured format."""
        df = pd.read_csv(filepath, low_memory=False)
        df = df[df.Duplicate != "Y"]  # Remove duplicates
        
        flights = []
        for _, row in df.iterrows():
            try:
                flight = self._create_flight_from_row(row)
                if flight:
                    flights.append(flight)
            except (ValueError, KeyError) as e:
                print(f"Error processing flight row: {e}")
                continue
                
        return flights
    
    def _create_flight_from_row(self, row: pd.Series) -> Optional[Flight]:
        """Create Flight object from DataFrame row."""
        try:
            # Process departure time
            dep_time = self._format_time(row['CRSDepTime'])
            dep_date = row['FlightDate']
            dep = arrow.get(f"{dep_date}{dep_time}", 'YYYY-MM-DDHHmm')
            dep = self.convert_to_utc(row['Origin'], dep)
            
            # Process arrival time
            arr_time = self._format_time(row['CRSArrTime'])
            arr = arrow.get(f"{dep_date}{arr_time}", 'YYYY-MM-DDHHmm')
            arr = self.convert_to_utc(row['Dest'], arr)
            
            # Handle arrival time crossing midnight
            if arr < dep:
                arr = arr.shift(days=1)
            
            # Process diversions
            diversions = self._process_diversions(row)
            
            return Flight(
                origin=row['Origin'],
                destination=row['Dest'],
                departure_time=dep,
                arrival_time=arr,
                raw_data=row.to_list(),
                num_diversions=int(row['DivAirportLandings']),
                diversions=diversions
            )
            
        except (ValueError, KeyError) as e:
            print(f"Error creating flight: {e}")
            return None
    
    def _format_time(self, time: int) -> str:
        """Format time integer to HHMM string."""
        time_str = str(int(time))
        return time_str.zfill(4)
    
    def _process_diversions(self, row: pd.Series) -> List[Diversion]:
        """Process diversion information from flight data."""
        diversions = []
        num_divs = int(row['DivAirportLandings'])
        
        for i in range(1, min(num_divs + 1, 6)):  # Max 5 diversions
            try:
                airport = row[f'Div{i}Airport']
                if pd.isna(airport):
                    continue
                    
                wheels_on = row[f'Div{i}WheelsOn']
                wheels_off = row[f'Div{i}WheelsOff']
                
                if pd.isna(wheels_on) or pd.isna(wheels_off):
                    continue
                
                # Process times
                arr_time = self._format_time(int(wheels_on))
                dep_time = self._format_time(int(wheels_off))
                
                arr = arrow.get(f"{row['FlightDate']}{arr_time}", 'YYYY-MM-DDHHmm')
                dep = arrow.get(f"{row['FlightDate']}{dep_time}", 'YYYY-MM-DDHHmm')
                
                arr = self.convert_to_utc(airport, arr)
                dep = self.convert_to_utc(airport, dep)
                
                if arr < dep:
                    arr = arr.shift(days=1)
                
                diversions.append(Diversion(airport, arr, dep))
                
            except (ValueError, KeyError) as e:
                print(f"Error processing diversion {i}: {e}")
                continue
                
        return diversions
