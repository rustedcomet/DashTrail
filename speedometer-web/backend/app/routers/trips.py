from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, models, schemas
from ..database import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Trip])
def read_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_trips(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Trip)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    return crud.create_trip(db=db, trip=trip)

@router.post("/{trip_id}/points")
def add_trip_points(trip_id: int, payload: schemas.TripPointsCreate, db: Session = Depends(get_db)):
    db_trip = crud.get_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    try:
        saved = crud.add_trip_points(db, trip_id=trip_id, points=payload.points)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"saved": saved}

@router.post("/{trip_id}/stop", response_model=schemas.Trip)
def stop_trip(trip_id: int, payload: schemas.TripStop, db: Session = Depends(get_db)):
    db_trip = crud.stop_trip(db, trip_id=trip_id, trip_stop=payload)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@router.get("/{trip_id}", response_model=schemas.TripWithPoints)
def read_trip(trip_id: int, db: Session = Depends(get_db)):
    db_trip = crud.get_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_trip

@router.delete("/{trip_id}", response_model=schemas.Trip)
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    db_trip = crud.get_trip(db, trip_id=trip_id)
    if db_trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    crud.delete_trip(db, trip_id=trip_id)
    return db_trip
