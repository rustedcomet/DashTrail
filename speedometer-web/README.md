# DashTrail

DashTrail is a lightweight, self-hosted GPS speedometer and trip logger for phones, tablets, and desktop browsers.

## Features

- Live GPS speed in km/h
- Trip distance, duration, average speed, and max speed
- Saved trip history
- Trip report with route map and start/stop locations
- Reverse-geocoded street addresses with coordinate fallback
- Daily, weekly, monthly, and all-time distance totals
- PWA install support
- Docker Compose deployment

## Project Structure

- `frontend/`: SvelteKit frontend application.
- `backend/`: FastAPI backend with SQLite.
- `docker-compose.yml`: Production container setup.
- `Caddyfile`: Internal reverse proxy for frontend and API routing.
- `../DEPLOYMENT.md`: Deployment guide.

## Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Configuration

Copy `.env.example` to `.env` for deployment settings:

```bash
cp .env.example .env
```

Important values:

- `APP_PORT`: Host port exposed by Caddy, default `3080`.
- `GEOCODER_PROVIDER`: `nominatim` or `off`.
- `GEOCODER_USER_AGENT`: Custom User-Agent for Nominatim.
- `GEOCODER_LANGUAGE`: Preferred address language.

## Reverse Geocoding

DashTrail reverse-geocodes trip start and stop coordinates when a trip is saved. Results are cached in SQLite so repeated nearby lookups do not keep hitting the provider.

The default provider is Nominatim/OpenStreetMap. Use it lightly, keep caching enabled, and set a custom `GEOCODER_USER_AGENT`. If the lookup fails or geocoding is disabled, trip reports show coordinates.

## Important Limitations

- GPS requires HTTPS in production browser contexts.
- A domain and SSL/TLS certificate are required for phone GPS access outside localhost.
- Trip times are displayed in Panama time, `America/Panama` (GMT-5), while timestamps are stored as UTC internally.
- Browser/PWA tracking is not as reliable in the background as a native mobile app.
- For best tracking accuracy, keep DashTrail open while recording a trip.
- Some phones may pause GPS when the screen is locked, the PWA is backgrounded, or battery saver is enabled.
