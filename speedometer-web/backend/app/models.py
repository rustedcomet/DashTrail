from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    distance_km = Column(Float, default=0.0)
    avg_speed_kmh = Column(Float, default=0.0)
    max_speed_kmh = Column(Float, default=0.0)
    start_lat = Column(Float, nullable=True)
    start_lng = Column(Float, nullable=True)
    start_address = Column(String, nullable=True)
    end_lat = Column(Float, nullable=True)
    end_lng = Column(Float, nullable=True)
    end_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    route_points = relationship("RoutePoint", back_populates="trip", cascade="all, delete-orphan")

class RoutePoint(Base):
    __tablename__ = "route_points"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    speed_kmh = Column(Float, nullable=True)
    accuracy_m = Column(Float, nullable=True)
    sequence = Column(Integer, nullable=False)

    trip = relationship("Trip", back_populates="route_points")

class GeocodeCache(Base):
    __tablename__ = "geocode_cache"

    key = Column(String, primary_key=True)
    provider = Column(String, default="nominatim")
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
