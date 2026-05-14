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

## Project Layout

- `speedometer-web/`: DashTrail application source.
- `speedometer-web/frontend/`: SvelteKit frontend.
- `speedometer-web/backend/`: FastAPI backend with SQLite.
- `DEPLOYMENT.md`: Production deployment guide.
- `DEVELOPMENT_PLAN.md`: Version 1 development plan and implementation notes.

## Quick Start

```bash
cd speedometer-web
cp .env.example .env
docker compose up -d --build
```

DashTrail is served on `APP_PORT`, defaulting to `3080`.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker, reverse proxy, SSL, domain, and data backup notes.

GPS access requires HTTPS in production browser contexts, so deploy behind a domain with SSL/TLS.

## Development

Backend:

```bash
cd speedometer-web/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd speedometer-web/frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`.

## Notes

Browser/PWA GPS tracking can keep the screen awake on supported browsers while a trip is active, but reliable background tracking while the screen is locked is a mobile OS limitation.

Trip times are displayed in Panama time, `America/Panama` (GMT-5), while timestamps are stored as UTC internally.
