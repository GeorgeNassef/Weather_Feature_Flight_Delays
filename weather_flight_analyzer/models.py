"""
Data models for weather and flight information.

This module defines the core data structures used throughout the weather-flight analyzer.
It uses dataclasses for efficient and type-safe data handling, with arrow for robust
datetime operations across timezones.

Key Classes:
    - WeatherData: Container for weather observations with time indexing
    - WeatherObservation: Individual weather measurement at a specific time and location
    - Diversion: Flight diversion information including location and timing
    - Flight: Complete flight information including route and any diversions

Authors: George Nassef, Will Landau
Copyright © 2021
"""

from typing import List, Optional
from dataclasses import dataclass
import arrow

@dataclass
class WeatherData:
    """
    Container for weather data and time index.
    
    This class organizes weather observations and provides efficient time-based lookup
    through an index mapping minutes to observation positions.
    
    Attributes:
        data (List[WeatherObservation]): Chronologically ordered weather observations
        time_index (List[int]): Maps minute offsets to positions in the data list,
                               enabling O(1) lookup of observations by time
    """
    data: List['WeatherObservation']
    time_index: List[int]

@dataclass
class WeatherObservation:
    """
    Single weather observation from a specific station at a specific time.
    
    Encapsulates all meteorological measurements from one ASOS observation,
    including the raw data for access to additional fields not explicitly
    modeled in the class attributes.
    
    Attributes:
        station (str): ASOS station identifier (usually airport code)
        time (arrow.Arrow): Timestamp of the observation with timezone information
        raw_data (List[str]): Complete raw data from the observation for additional fields
    
    Methods:
        from_raw: Factory method to create instance from raw data array
    """
    station: str
    time: arrow.Arrow
    raw_data: List[str]

    @classmethod
    def from_raw(cls, data: List[str]) -> 'WeatherObservation':
        """
        Create WeatherObservation instance from raw data array.
        
        Args:
            data (List[str]): Raw observation data from ASOS file
                             First element must be station identifier
                             Second element must be timestamp in YYYY-MM-DD HH:mm format
        
        Returns:
            WeatherObservation: New instance populated with the raw data
        
        Raises:
            ValueError: If timestamp format is invalid
            IndexError: If data array is too short
        """
        return cls(
            station=data[0],
            time=arrow.get(data[1], 'YYYY-MM-DD HH:mm'),
            raw_data=data
        )

@dataclass
class Diversion:
    """
    Flight diversion information for a single diversion event.
    
    Records when and where a flight was diverted, including both arrival
    at and departure from the diversion airport. All times are converted
    to UTC for consistency.
    
    Attributes:
        airport (str): Diversion airport identifier
        arrival_time (arrow.Arrow): When the flight arrived at diversion airport (UTC)
        departure_time (arrow.Arrow): When the flight departed diversion airport (UTC)
    """
    airport: str
    arrival_time: arrow.Arrow
    departure_time: arrow.Arrow

@dataclass
class Flight:
    """
    Complete flight information including route and any diversions.
    
    Represents a single flight with its planned route, actual times,
    and any diversions that occurred. All times are stored in UTC
    for consistent processing.
    
    Attributes:
        origin (str): Departure airport identifier
        destination (str): Planned arrival airport identifier
        departure_time (arrow.Arrow): Actual departure time (UTC)
        arrival_time (arrow.Arrow): Actual arrival time (UTC)
        raw_data (List[str]): Complete raw flight data for additional fields
        num_diversions (int): Number of diversions during this flight
        diversions (List[Diversion]): Details of each diversion in order
        useable (bool): Whether this flight record is valid for analysis
    """
    origin: str
    destination: str
    departure_time: arrow.Arrow
    arrival_time: arrow.Arrow
    raw_data: List[str]
    num_diversions: int
    diversions: List[Diversion]
    useable: bool = True
