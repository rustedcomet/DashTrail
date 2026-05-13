from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud
from ..database import get_db

router = APIRouter()

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return crud.get_stats_summary(db)
