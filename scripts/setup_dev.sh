#!/bin/bash

# Exit on error
set -e

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install development dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -e .

# Create data directories
echo "Creating data directories..."
mkdir -p data/raw/flights data/raw/weather data/processed

# Download sample data for testing (commented out as URLs need to be provided)
# echo "Downloading sample data..."
# wget -P data/raw/flights https://example.com/sample_flight_data.csv
# wget -P data/raw/weather https://example.com/sample_weather_data.txt

# Run basic validation
echo "Running basic validation..."
python -c "
import weather_flight_analyzer
print(f'Weather Flight Analyzer version: {weather_flight_analyzer.__version__}')
"

echo "Development environment setup complete!"
echo
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo
echo "To run the analyzer:"
echo "  weather-flight-analyzer --help"
echo
echo "Directory structure created:"
echo "  data/"
echo "  ├── raw/"
echo "  │   ├── flights/    # Put your flight CSV files here"
echo "  │   └── weather/    # Put your weather data files here"
echo "  └── processed/      # Output will be saved here"
echo
echo "Note: You need to add your actual flight and weather data files"
echo "to the respective directories before running the analyzer."
