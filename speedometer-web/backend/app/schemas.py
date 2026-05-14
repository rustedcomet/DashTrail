from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import List, Optional
from datetime import datetime, timezone

def serialize_utc_datetime(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

class RoutePointCreate(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    timestamp: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    recorded_at: Optional[datetime] = None
    speed_kmh: Optional[float] = None
    accuracy_m: Optional[float] = None
    accuracy_meters: Optional[float] = None
    heading: Optional[float] = None
    altitude: Optional[float] = None
    sequence: Optional[int] = None
    sequence_number: Optional[int] = None

class RoutePoint(BaseModel):
    id: int
    trip_id: int
    lat: float
    lng: float
    timestamp: datetime
    speed_kmh: Optional[float] = None
    accuracy_m: Optional[float] = None
    sequence: int
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("timestamp", when_used="json")
    def serialize_timestamp(self, value: datetime) -> str:
        return serialize_utc_datetime(value) or ""

class TripPointsCreate(BaseModel):
    points: List[RoutePointCreate] = Field(default_factory=list)

class TripCreate(BaseModel):
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    distance_km: Optional[float] = None
    distance_meters: Optional[float] = None
    avg_speed_kmh: float = 0.0
    max_speed_kmh: float = 0.0
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    start_address: Optional[str] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    end_address: Optional[str] = None
    route_points: List[RoutePointCreate] = Field(default_factory=list)

class TripStop(BaseModel):
    ended_at: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: int
    distance_km: Optional[float] = None
    distance_meters: Optional[float] = None
    avg_speed_kmh: float
    max_speed_kmh: float
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    end_address: Optional[str] = None

class Trip(BaseModel):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: int
    distance_km: float
    avg_speed_kmh: float
    max_speed_kmh: float
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    start_address: Optional[str] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    end_address: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("started_at", "ended_at", "created_at", when_used="json")
    def serialize_datetimes(self, value: Optional[datetime]) -> Optional[str]:
        return serialize_utc_datetime(value)

class TripWithPoints(Trip):
    route_points: List[RoutePoint] = []
