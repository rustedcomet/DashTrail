import json
import os
import time
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from . import models

NOMINATIM_URL = os.getenv("GEOCODER_NOMINATIM_URL", "https://nominatim.openstreetmap.org/reverse")
GEOCODER_PROVIDER = os.getenv("GEOCODER_PROVIDER", "nominatim").lower()
GEOCODER_USER_AGENT = os.getenv(
    "GEOCODER_USER_AGENT",
    "DashTrail/1.0-self-hosted-configure-GEOCODER_USER_AGENT",
)
GEOCODER_LANGUAGE = os.getenv("GEOCODER_LANGUAGE", "en")
GEOCODER_TIMEOUT_SECONDS = float(os.getenv("GEOCODER_TIMEOUT_SECONDS", "5"))

_last_request_at = 0.0


def coordinate_fallback(lat: Optional[float], lng: Optional[float]) -> Optional[str]:
    if lat is None or lng is None:
        return None
    return f"{lat:.6f}, {lng:.6f}"


def reverse_geocode_with_cache(db: Session, lat: Optional[float], lng: Optional[float]) -> Optional[str]:
    if lat is None or lng is None:
        return None

    if GEOCODER_PROVIDER in {"", "off", "disabled", "none"}:
        return coordinate_fallback(lat, lng)

    key = _cache_key(lat, lng)
    cached = db.query(models.GeocodeCache).filter(models.GeocodeCache.key == key).first()
    if cached:
        return cached.address

    address = _reverse_geocode_nominatim(lat, lng)
    if not address:
        return coordinate_fallback(lat, lng)

    db.add(
        models.GeocodeCache(
            key=key,
            provider=GEOCODER_PROVIDER,
            lat=lat,
            lng=lng,
            address=address,
            created_at=datetime.utcnow(),
        )
    )
    db.flush()
    return address


def _cache_key(lat: float, lng: float) -> str:
    return f"{GEOCODER_PROVIDER}:{lat:.5f},{lng:.5f}"


def _reverse_geocode_nominatim(lat: float, lng: float) -> Optional[str]:
    if GEOCODER_PROVIDER != "nominatim":
        return coordinate_fallback(lat, lng)

    _respect_rate_limit()
    params = urlencode(
        {
            "format": "jsonv2",
            "lat": f"{lat:.7f}",
            "lon": f"{lng:.7f}",
            "zoom": "18",
            "addressdetails": "1",
            "accept-language": GEOCODER_LANGUAGE,
        }
    )
    request = Request(
        f"{NOMINATIM_URL}?{params}",
        headers={
            "User-Agent": GEOCODER_USER_AGENT,
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=GEOCODER_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    return payload.get("display_name")


def _respect_rate_limit() -> None:
    global _last_request_at
    elapsed = time.monotonic() - _last_request_at
    if elapsed < 1:
        time.sleep(1 - elapsed)
    _last_request_at = time.monotonic()
