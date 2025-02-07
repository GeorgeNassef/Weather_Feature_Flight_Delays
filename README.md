# Weather-Flight Data Analyzer

A Python package for processing and analyzing weather observations and flight data to create datasets for flight delay prediction models. This tool matches weather conditions with flight events, handling timezone conversions and flight diversions.

## Authors
- George Nassef
- Will Landau

Copyright © 2021

## Data Sources

This project uses the following data sources:

- **Flight Data**: [Bureau of Transportation Statistics (BTS)](https://www.transtats.bts.gov/)
  - Specifically uses the "Airline On-Time Performance Data" which provides detailed flight operation data
  - Data includes scheduled/actual times, delays, diversions, and cancellations
  - License: Public Domain (U.S. Government Work)

- **Weather Data**: [ASOS (Automated Surface Observing System)](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/automated-surface-observing-system-asos)
  - Provides minute-by-minute weather observations from airports
  - Includes temperature, wind speed, precipitation, and other meteorological data
  - License: Public Domain (NOAA)

## Requirements

- Python 3.11+
- Docker (for containerized operation)
- Sufficient storage for flight and weather data files

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/george-nassef/weather-flight-analyzer.git
cd weather-flight-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Docker Installation

Build the Docker image:
```bash
docker build -t weather-flight-analyzer .
```

## Usage

### Data Directory Structure

Organize your data files as follows:
```
data/
├── raw/
│   ├── flights/          # Monthly flight data CSV files
│   │   ├── 2021_1.csv
│   │   ├── 2021_2.csv
│   │   └── ...
│   └── weather/         # Daily weather observation files
│       ├── 20210101.txt
│       ├── 20210102.txt
│       └── ...
└── processed/           # Output directory for processed data
```

### Running with Python

```bash
python -m weather_flight_analyzer \
    --timezone-file /path/to/AirportTZ.csv \
    --flight-data-dir /path/to/data/raw/flights \
    --weather-data-dir /path/to/data/raw/weather \
    --output-dir /path/to/data/processed
```

### Running with Docker

```bash
docker run -v /path/to/data:/app/data \
    weather-flight-analyzer \
    --timezone-file /app/data/AirportTZ.csv \
    --flight-data-dir /app/data/raw/flights \
    --weather-data-dir /app/data/raw/weather \
    --output-dir /app/data/processed
```

## AWS Fargate Deployment

The deployment script requires the following environment variables:

```bash
export AWS_ACCOUNT_ID="your-aws-account-id"
export AWS_REGION="your-aws-region"
export EFS_ID="your-efs-id"
export SUBNET_ID="your-subnet-id"
export SECURITY_GROUP_ID="your-security-group-id"
```

1. Push the Docker image to Amazon ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com
docker tag weather-flight-analyzer:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/weather-flight-analyzer:latest
docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/weather-flight-analyzer:latest
```

2. Create an ECS task definition that:
   - Uses the ECR image
   - Mounts an EFS volume for data storage
   - Sets appropriate memory and CPU allocations
   - Configures environment variables if needed

3. Create a Fargate cluster and service using the task definition

4. Monitor the service through CloudWatch logs

## Output Data Format

The processed data files contain matched flight and weather information:
- Flight details (number, origin, destination, times)
- Weather conditions at departure and arrival
- Any diversions and associated weather conditions
- Delay information and potential weather correlations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bureau of Transportation Statistics for flight data
- NOAA/National Weather Service for ASOS weather data
- Contributors to the Arrow and Pandas libraries
