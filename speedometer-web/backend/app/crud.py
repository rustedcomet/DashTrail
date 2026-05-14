from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from . import models, schemas
from .geocoding import reverse_geocode_with_cache

APP_TIME_ZONE = "America/Panama"

def _to_utc_naive(value: datetime | None):
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)

def _local_start_as_utc_naive(value):
    local_dt = datetime.combine(value, time.min, tzinfo=ZoneInfo(APP_TIME_ZONE))
    return local_dt.astimezone(timezone.utc).replace(tzinfo=None)

def _distance_km(distance_km=None, distance_meters=None):
    if distance_km is not None:
        return distance_km
    if distance_meters is not None:
        return distance_meters / 1000
    return 0.0

def _point_to_model(point: schemas.RoutePointCreate, trip_id: int, fallback_sequence: int):
    lat = point.lat if point.lat is not None else point.latitude
    lng = point.lng if point.lng is not None else point.longitude
    if lat is None or lng is None:
        raise ValueError("Route point requires latitude/longitude")

    return models.RoutePoint(
        trip_id=trip_id,
        lat=lat,
        lng=lng,
        timestamp=_to_utc_naive(point.timestamp or point.recorded_at) or datetime.utcnow(),
        speed_kmh=point.speed_kmh,
        accuracy_m=point.accuracy_m if point.accuracy_m is not None else point.accuracy_meters,
        sequence=point.sequence if point.sequence is not None else (
            point.sequence_number if point.sequence_number is not None else fallback_sequence
        ),
    )

def get_trips(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Trip).order_by(models.Trip.started_at.desc()).offset(skip).limit(limit).all()

def get_trip(db: Session, trip_id: int):
    return db.query(models.Trip).filter(models.Trip.id == trip_id).first()

def create_trip(db: Session, trip: schemas.TripCreate):
    db_trip = models.Trip(
        started_at=_to_utc_naive(trip.started_at),
        ended_at=_to_utc_naive(trip.ended_at),
        duration_seconds=trip.duration_seconds,
        distance_km=_distance_km(trip.distance_km, trip.distance_meters),
        avg_speed_kmh=trip.avg_speed_kmh,
        max_speed_kmh=trip.max_speed_kmh,
        start_lat=trip.start_lat,
        start_lng=trip.start_lng,
        start_address=trip.start_address,
        end_lat=trip.end_lat,
        end_lng=trip.end_lng,
        end_address=trip.end_address,
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    add_trip_points(db, db_trip.id, trip.route_points)
    if db_trip.ended_at:
        db_trip.start_address = db_trip.start_address or reverse_geocode_with_cache(db, db_trip.start_lat, db_trip.start_lng)
        db_trip.end_address = db_trip.end_address or reverse_geocode_with_cache(db, db_trip.end_lat, db_trip.end_lng)
        db.commit()
    db.refresh(db_trip)
    return db_trip

def add_trip_points(db: Session, trip_id: int, points: list[schemas.RoutePointCreate]):
    trip = get_trip(db, trip_id)
    saved = 0
    for offset, pt in enumerate(points):
        db_point = _point_to_model(pt, trip_id=trip_id, fallback_sequence=offset)
        if trip and trip.start_lat is None and trip.start_lng is None:
            trip.start_lat = db_point.lat
            trip.start_lng = db_point.lng
        db.add(db_point)
        saved += 1
    db.commit()
    return saved

def stop_trip(db: Session, trip_id: int, trip_stop: schemas.TripStop):
    trip = get_trip(db, trip_id)
    if not trip:
        return None
    trip.ended_at = _to_utc_naive(trip_stop.ended_at)
    trip.duration_seconds = trip_stop.duration_seconds
    trip.distance_km = _distance_km(trip_stop.distance_km, trip_stop.distance_meters)
    trip.avg_speed_kmh = trip_stop.avg_speed_kmh
    trip.max_speed_kmh = trip_stop.max_speed_kmh
    trip.end_lat = trip_stop.end_lat
    trip.end_lng = trip_stop.end_lng
    trip.start_address = trip.start_address or reverse_geocode_with_cache(db, trip.start_lat, trip.start_lng)
    trip.end_address = trip_stop.end_address or reverse_geocode_with_cache(db, trip.end_lat, trip.end_lng)
    db.commit()
    db.refresh(trip)
    return trip

def delete_trip(db: Session, trip_id: int):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if trip:
        db.delete(trip)
        db.commit()
    return trip

def get_stats_summary(db: Session):
    now = datetime.now(ZoneInfo(APP_TIME_ZONE))
    today_start = _local_start_as_utc_naive(now.date())
    week_start = _local_start_as_utc_naive((now - timedelta(days=now.weekday())).date())
    month_start = _local_start_as_utc_naive(now.replace(day=1).date())

    def sum_km(start_date=None):
        query = db.query(func.sum(models.Trip.distance_km))
        if start_date:
            query = query.filter(models.Trip.started_at >= start_date)
        res = query.scalar()
        return res if res else 0.0

    return {
        "today_km": sum_km(today_start),
        "week_km": sum_km(week_start),
        "month_km": sum_km(month_start),
        "all_time_km": sum_km(),
        "total_km": sum_km(),
        "trip_count": db.query(models.Trip).count()
    }
