"""Data models for weather and flight information."""

from typing import List, Optional
from dataclasses import dataclass
import arrow

@dataclass
class WeatherData:
    """Container for weather data and time index."""
    data: List['WeatherObservation']
    time_index: List[int]

@dataclass
class WeatherObservation:
    """Single weather observation."""
    station: str
    time: arrow.Arrow
    raw_data: List[str]

    @classmethod
    def from_raw(cls, data: List[str]) -> 'WeatherObservation':
        """Create WeatherObservation from raw data row."""
        return cls(
            station=data[0],
            time=arrow.get(data[1], 'YYYY-MM-DD HH:mm'),
            raw_data=data
        )

@dataclass
class Diversion:
    """Flight diversion information."""
    airport: str
    arrival_time: arrow.Arrow
    departure_time: arrow.Arrow

@dataclass
class Flight:
    """Flight information including diversions."""
    origin: str
    destination: str
    departure_time: arrow.Arrow
    arrival_time: arrow.Arrow
    raw_data: List[str]
    num_diversions: int
    diversions: List[Diversion]
    useable: bool = True
