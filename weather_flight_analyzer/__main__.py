"""Main entry point for the weather flight analyzer."""

import sys
import argparse
from pathlib import Path
from typing import List
import pandas as pd

from .data_processor import DataProcessor
from .models import Flight, WeatherData

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Process weather and flight data for delay prediction.'
    )
    parser.add_argument(
        '--timezone-file',
        type=Path,
        required=True,
        help='Path to airport timezone mapping CSV file'
    )
    parser.add_argument(
        '--flight-data-dir',
        type=Path,
        required=True,
        help='Directory containing flight data CSV files'
    )
    parser.add_argument(
        '--weather-data-dir',
        type=Path,
        required=True,
        help='Directory containing weather data files'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        required=True,
        help='Directory to save processed data'
    )
    return parser.parse_args()

def process_monthly_data(
    processor: DataProcessor,
    flight_file: Path,
    weather_dir: Path,
    output_dir: Path
) -> None:
    """Process one month of flight and weather data."""
    print(f"Processing {flight_file.name}...")
    
    # Process flights
    flights = processor.process_flight_data(flight_file)
    
    # Create output for this month
    month_data = []
    for flight in flights:
        # Get weather data for relevant dates
        weather_file = weather_dir / f"{flight.departure_time.format('YYYYMMDD')}.txt"
        try:
            weather = processor.process_weather_file(weather_file)
            # TODO: Match weather observations with flight events
            # This would involve finding the closest weather observation
            # for each significant point in the flight (departure, arrival, diversions)
            month_data.append({
                'flight_number': flight.raw_data[10],  # Flight_Number_Marketing_Airline
                'origin': flight.origin,
                'destination': flight.destination,
                'departure_time': flight.departure_time.isoformat(),
                'arrival_time': flight.arrival_time.isoformat(),
                'num_diversions': flight.num_diversions,
                # Add weather data here
            })
        except FileNotFoundError:
            print(f"Weather data not found for {weather_file}")
            continue
    
    # Save processed data
    if month_data:
        output_file = output_dir / f"processed_{flight_file.stem}.csv"
        pd.DataFrame(month_data).to_csv(output_file, index=False)
        print(f"Saved processed data to {output_file}")

def main() -> None:
    """Main execution function."""
    args = parse_args()
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = DataProcessor(args.timezone_file)
    
    # Process each month's data
    flight_files = sorted(args.flight_data_dir.glob('*.csv'))
    for flight_file in flight_files:
        try:
            process_monthly_data(
                processor,
                flight_file,
                args.weather_data_dir,
                args.output_dir
            )
        except Exception as e:
            print(f"Error processing {flight_file}: {e}")
            continue

if __name__ == '__main__':
    main()
