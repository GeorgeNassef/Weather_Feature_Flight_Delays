"""
Data processing functions for weather and flight data.

This module provides the core functionality for processing weather observations
and flight data. It handles data loading, timezone conversions, and matching
of weather conditions with flight events.

Key Features:
    - Timezone-aware processing of flight and weather timestamps
    - Efficient indexing of weather observations for quick lookup
    - Handling of flight diversions and schedule changes
    - Data validation and error handling

The DataProcessor class serves as the main entry point for all data processing
operations, maintaining timezone information and processing state.

Authors: George Nassef, Will Landau
Copyright © 2021
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import arrow
import pandas as pd
from .models import WeatherData, WeatherObservation, Flight, Diversion

class DataProcessor:
    """
    Main processor for weather and flight data analysis.
    
    This class handles all aspects of data processing including:
    - Loading and parsing weather observations
    - Processing flight records including diversions
    - Converting timestamps between timezones
    - Matching weather conditions with flight events
    
    The processor maintains timezone information for airports to ensure
    accurate temporal analysis across different regions.
    """
    
    def __init__(self, timezone_file: Path):
        """
        Initialize the data processor.
        
        Args:
            timezone_file (Path): Path to CSV file containing airport timezone mappings.
                                Expected format: airport_code,timezone_name
                                Example: "JFK,America/New_York"
        
        Raises:
            FileNotFoundError: If timezone_file does not exist
            ValueError: If timezone_file is malformed
        """
        self.airport_timezones = self._load_timezone_data(timezone_file)
        
    def _load_timezone_data(self, filepath: Path) -> Dict[str, str]:
        """
        Load airport timezone mappings from CSV file.
        
        Args:
            filepath (Path): Path to CSV file containing airport/timezone pairs
        
        Returns:
            Dict[str, str]: Mapping of airport codes to timezone names
                           Example: {"JFK": "America/New_York"}
        
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid
        """
        timezones = {}
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    timezones[row[0]] = row[1]
        return timezones
    
    def convert_to_utc(self, airport: str, time: arrow.Arrow) -> arrow.Arrow:
        """
        Convert local time to UTC based on airport timezone.
        
        Args:
            airport (str): Airport code to determine timezone
            time (arrow.Arrow): Local time to convert
        
        Returns:
            arrow.Arrow: Time converted to UTC
        
        Raises:
            ValueError: If airport code not found in timezone data
            arrow.ParserError: If timezone conversion fails
        """
        if airport not in self.airport_timezones:
            raise ValueError(f"No timezone data for airport: {airport}")
            
        tz = self.airport_timezones[airport]
        return time.to('UTC')
    
    def process_weather_file(self, filepath: Path) -> WeatherData:
        """
        Process ASOS weather data file into structured format.
        
        Reads and parses weather observations from ASOS format file,
        creating an indexed structure for efficient temporal lookup.
        Handles the standard ASOS file format with 6-line header.
        
        Args:
            filepath (Path): Path to ASOS format weather data file
        
        Returns:
            WeatherData: Processed weather data with time indexing
        
        Raises:
            FileNotFoundError: If weather file not found
            ValueError: If file format is invalid
        """
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
        """
        Process flight data from CSV into structured format.
        
        Reads flight records from BTS format CSV file, handling:
        - Timezone conversions for departure/arrival times
        - Flight diversions (up to 5 per flight)
        - Data validation and duplicate removal
        
        Args:
            filepath (Path): Path to BTS format flight data CSV
        
        Returns:
            List[Flight]: List of processed flight records
        
        Raises:
            FileNotFoundError: If flight data file not found
            pd.errors.EmptyDataError: If file contains no valid data
        """
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
        """
        Create Flight object from a single DataFrame row.
        
        Processes a row of flight data, handling:
        - Time parsing and timezone conversion
        - Validation of required fields
        - Processing of any diversions
        
        Args:
            row (pd.Series): Single row from flight data DataFrame
        
        Returns:
            Optional[Flight]: Processed flight record, or None if invalid
        
        Notes:
            Returns None instead of raising exceptions for invalid records
            to allow processing to continue with valid records.
        """
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
        """
        Format time integer to HHMM string.
        
        Converts integer time representation (e.g., 830 for 8:30)
        to standard 4-digit string format (e.g., "0830").
        
        Args:
            time (int): Time as integer (0-2359)
        
        Returns:
            str: Time as 4-digit string (e.g., "0830")
        
        Raises:
            ValueError: If time is negative or >= 2400
        """
        time_str = str(int(time))
        return time_str.zfill(4)
    
    def _process_diversions(self, row: pd.Series) -> List[Diversion]:
        """
        Process diversion information from flight data.
        
        Handles up to 5 diversions per flight, processing:
        - Diversion airport codes
        - Arrival/departure times at each diversion
        - Timezone conversions for all timestamps
        
        Args:
            row (pd.Series): Flight data row containing diversion fields
        
        Returns:
            List[Diversion]: Processed diversions in chronological order
        
        Notes:
            Skips invalid diversions while processing valid ones
            Ensures chronological ordering of events
        """
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
