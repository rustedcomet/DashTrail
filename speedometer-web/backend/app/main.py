from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, ensure_schema
from . import models
from .routers import trips, stats
import os

models.Base.metadata.create_all(bind=engine)
ensure_schema()

app = FastAPI(title="DashTrail API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
