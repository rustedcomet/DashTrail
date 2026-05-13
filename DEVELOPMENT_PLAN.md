# DEVELOPMENT_PLAN.md

# DashTrail

## 1. Project Summary

DashTrail is a lightweight, self-hosted web-based speedometer and trip logger that can run from any modern device with GPS and a web browser.

Version 1 is complete and field-tested as of 2026-05-13.

The app should focus on the essentials:

- Current speed in km/h
- Trip distance in kilometers
- Average speed
- Maximum speed
- Trip duration
- Saved trip history
- Daily, weekly, and monthly kilometer totals
- Post-trip report with route map and trip summary

The live screen should be simple and similar to a mobile speedometer app: a large speed display, three compact stat cards, and a large Start / Stop button.

The app should be deployable with Docker and usable as a Progressive Web App, or PWA, so it can be installed on a phone home screen without needing an app store.

---

## 2. Core Goals

### Primary Goals

1. Track trips using browser GPS.
2. Show live speed in km/h.
3. Calculate distance traveled during the trip.
4. Calculate average speed.
5. Track maximum speed.
6. Save trip records.
7. Show a trip report after each trip.
8. Show route on a map.
9. Show daily, weekly, and monthly kilometer totals.
10. Run as a self-hosted Docker application.

### Secondary Goals

1. Make the interface mobile-first.
2. Support desktop and tablet browsers.
3. Support PWA installation.
4. Keep the app lightweight and easy to maintain.
5. Support dark theme by default.
6. Allow exporting trip data later.

---

## 3. Non-Goals for Version 1

The first version should avoid unnecessary complexity.

Do not include these in the MVP:

- Turn-by-turn navigation
- Social sharing
- Public leaderboards
- Complex analytics
- Real-time multi-user tracking
- Native mobile app builds
- Automatic background tracking while the browser is closed
- Vehicle diagnostics
- OBD-II integration
- Paid map APIs unless absolutely necessary

---

## 4. Important Browser Limitation

Browser-based GPS tracking works, but it has one major limitation: background tracking is not as reliable as a native Android or iOS app.

The app should work well when:

- The browser is open
- The PWA is active
- The phone screen remains on
- The operating system does not aggressively suspend the browser

The app may become unreliable when:

- The phone screen is locked
- The browser is placed in the background
- Battery saver mode is enabled
- The operating system suspends JavaScript execution

This limitation should be clearly documented in the app.

Recommended in-app warning:

> For best tracking accuracy, keep this app open while recording a trip. Some phones may pause GPS tracking when the screen is locked or the browser is in the background.

---

## 5. Recommended Technology Stack

### Frontend

Recommended: **SvelteKit**

Reasoning:

- Lightweight
- Fast startup
- Good for mobile-first apps
- Simple state management
- Can be deployed as a full-stack app or static frontend
- Good PWA support

Alternative:

- React with Vite
- Vue with Vite

### Map

Recommended: **Leaflet + OpenStreetMap tiles**

Reasoning:

- Lightweight
- No required paid API key
- Easy polyline route rendering
- Works well in mobile browsers

### Backend

Recommended: **FastAPI** or **Node.js/Express**

Preferred for this plan: **FastAPI**

Reasoning:

- Simple REST API
- Good validation with Pydantic
- Easy SQLite integration
- Clean automatic API documentation
- Good Docker support

### Database

Recommended for MVP: **SQLite**

Reasoning:

- Simple self-hosted setup
- No separate database container required
- Easy backups
- Perfect for single-user or small-family usage

Future upgrade option:

- PostgreSQL for multi-user support or larger scale

### Deployment

Recommended:

- Docker Compose
- Caddy reverse proxy for HTTPS
- SQLite stored in a persistent Docker volume

---

## 6. High-Level Architecture

```text
Mobile Browser / Desktop Browser
        |
        | HTTPS
        v
Caddy Reverse Proxy
        |
        v
DashTrail App Container
        |
        v
SQLite Database Volume
```

Optional future architecture:

```text
Browser / PWA
   |
   v
Frontend App
   |
   v
Backend API
   |
   v
PostgreSQL
```

---

## 7. HTTPS Requirement

Modern browsers require HTTPS for GPS access through the Geolocation API, except in limited localhost development cases.

Production deployment should use HTTPS.

Recommended options:

1. Caddy with automatic Let's Encrypt certificates.
2. Nginx Proxy Manager.
3. Cloudflare Tunnel.
4. Traefik.

Example public URL:

```text
https://dashtrail.example.com
```

Local development can use:

```text
http://localhost:5173
```

---

## 8. Main User Flows

### 8.1 Start a Trip

1. User opens the app.
2. User grants location permission.
3. User taps **Start**.
4. App creates a new active trip session.
5. App begins watching GPS position.
6. App displays live speed, distance, average speed, and max speed.

### 8.2 During a Trip

The live screen updates:

- Current speed
- Distance
- Average speed
- Max speed
- GPS status
- Optional elapsed time

The app stores GPS points locally during the active trip and periodically syncs them to the backend.

### 8.3 Stop a Trip

1. User taps **Stop**.
2. App stops GPS watch.
3. App calculates final values.
4. App saves trip summary and route points.
5. App opens the trip report page.

### 8.4 View Trip Report

Trip report shows:

- Route map
- Distance
- Duration
- Average speed
- Max speed
- Start time
- End time
- Date
- Start coordinates or resolved location
- End coordinates or resolved location

### 8.5 View Totals

Stats screen shows:

- Kilometers today
- Kilometers this week
- Kilometers this month
- All-time kilometers

---

## 9. Screens

## 9.1 Live Speedometer Screen

Purpose: show the essential live trip data.

### Required Display

- Large current speed in km/h
- Distance in km
- Average speed in km/h
- Maximum speed in km/h
- Start / Stop button
- GPS status indicator

### Optional Display

- Elapsed time
- GPS accuracy
- Pause / Resume button
- Small route preview

### Suggested Layout

```text
+--------------------------------+
|  GPS Status              18:42 |
|                                |
|             32                 |
|            km/h                |
|                                |
| +----------+ +------+ +------+ |
| | Max      | | Dist | | Avg  | |
| | 72 km/h  | |31.8km| |63km/h| |
| +----------+ +------+ +------+ |
|                                |
|          [ START / STOP ]      |
+--------------------------------+
```

### Visual Style

- Dark background
- Bright green digital-style numbers
- Large readable speed display
- Rounded stat cards
- Large thumb-friendly button
- Minimal distractions

---

## 9.2 Trip Report Screen

Purpose: show a saved trip after stopping.

### Required Display

- Map with route polyline
- Distance
- Duration
- Average speed
- Max speed
- Start time
- Stop time
- Date
- Start location
- Stop location

### Suggested Layout

```text
+--------------------------------+
| Route Map                      |
|                                |
|       green route line         |
|                                |
+--------------------------------+
| 30.54 km                 Date  |
|                                |
| Duration      01:50:16         |
| Avg Speed     17 km/h          |
| Max Speed     37 km/h          |
|                                |
| Start         18:19            |
| Location      lat/lng/address  |
|                                |
| Stop          20:09            |
| Location      lat/lng/address  |
+--------------------------------+
```

---

## 9.3 Trip History Screen

Purpose: list previous trips.

### Required Display

Each list item should show:

- Date
- Distance
- Duration
- Average speed
- Max speed

Example:

```text
May 08, 2026
30.54 km · 01:50:16 · Avg 17 km/h · Max 37 km/h
```

Clicking a trip opens the trip report.

---

## 9.4 Stats Dashboard

Purpose: show totals.

### Required Display

- Today total km
- This week total km
- This month total km
- All-time total km

Example:

```text
Today:      30.54 km
This week:  142.20 km
This month: 513.60 km
All time:   4,920.10 km
```

---

## 10. GPS Tracking Logic

The browser should use:

```javascript
navigator.geolocation.watchPosition(success, error, options)
```

Recommended options:

```javascript
const options = {
  enableHighAccuracy: true,
  maximumAge: 1000,
  timeout: 10000
};
```

Each position update may include:

- latitude
- longitude
- accuracy
- altitude
- altitudeAccuracy
- heading
- speed
- timestamp

Browser-provided speed may not always be available. If unavailable, calculate speed manually using distance over time.

---

## 11. Distance Calculation

Distance should be calculated between consecutive GPS points using the Haversine formula.

Basic logic:

```text
for each new GPS point:
    if previous point exists:
        segment_distance = distance(previous_point, current_point)
        total_distance += segment_distance
```

Distance should be stored internally in meters, then displayed in kilometers.

Example:

```text
4235 meters = 4.235 km
```

---

## 12. Speed Calculation

### Current Speed

Prefer browser-provided speed when available:

```text
coords.speed
```

Browser speed is usually returned in meters per second.

Convert to km/h:

```text
km/h = meters_per_second * 3.6
```

If browser speed is unavailable:

```text
current_speed = segment_distance / elapsed_seconds
```

Then convert to km/h.

### Average Speed

Recommended formula:

```text
average_speed_kmh = distance_km / duration_hours
```

### Max Speed

Max speed is the highest valid current speed recorded during the trip.

---

## 13. GPS Noise Filtering

GPS can jump, especially in cities, tunnels, indoors, or near tall buildings.

Apply basic filtering.

### Ignore points when:

- Accuracy is missing and the point is suspicious.
- Accuracy is worse than 50 meters.
- Segment speed is impossibly high for the selected mode.
- Timestamp is older than the previous point.
- Distance jump is too large for the elapsed time.

### Default Filters

```text
max_accuracy_meters = 50
max_reasonable_speed_kmh = 220
minimum_movement_meters = 3
```

For walking/cycling mode later, `max_reasonable_speed_kmh` can be lower.

---

## 14. Trip State Machine

The app should manage trip state clearly.

```text
IDLE
  -> STARTING
  -> TRACKING
  -> STOPPING
  -> SAVED
  -> IDLE
```

Optional later:

```text
TRACKING
  -> PAUSED
  -> TRACKING
```

---

## 15. Local Resilience

A trip should not be lost if the page refreshes or the network briefly fails.

Recommended approach:

- Store active trip state in IndexedDB or localStorage.
- Store unsynced GPS points locally.
- Sync to backend periodically.
- On app reload, detect unfinished trip and offer recovery.

MVP can start with localStorage, but IndexedDB is better for route points.

---

## 16. Database Schema

## 16.1 trips

```sql
CREATE TABLE trips (
    id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_seconds INTEGER DEFAULT 0,
    distance_meters REAL DEFAULT 0,
    avg_speed_kmh REAL DEFAULT 0,
    max_speed_kmh REAL DEFAULT 0,
    start_lat REAL,
    start_lng REAL,
    end_lat REAL,
    end_lng REAL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## 16.2 trip_points

```sql
CREATE TABLE trip_points (
    id TEXT PRIMARY KEY,
    trip_id TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    accuracy_meters REAL,
    speed_kmh REAL,
    heading REAL,
    altitude REAL,
    recorded_at TEXT NOT NULL,
    sequence_number INTEGER NOT NULL,
    FOREIGN KEY (trip_id) REFERENCES trips(id) ON DELETE CASCADE
);
```

## 16.3 app_settings

```sql
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## 16.4 Optional users table for future multi-user support

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

For MVP, user accounts can be skipped if the app is only used privately behind a secure network or single-user authentication layer.

---

## 17. API Design

Base URL:

```text
/api
```

## 17.1 Create Trip

```http
POST /api/trips
```

Request:

```json
{
  "started_at": "2026-05-08T18:19:00Z"
}
```

Response:

```json
{
  "id": "trip_123",
  "started_at": "2026-05-08T18:19:00Z"
}
```

## 17.2 Add Trip Points

```http
POST /api/trips/{trip_id}/points
```

Request:

```json
{
  "points": [
    {
      "latitude": 8.982,
      "longitude": -79.519,
      "accuracy_meters": 8,
      "speed_kmh": 32.4,
      "heading": 140,
      "altitude": 12,
      "recorded_at": "2026-05-08T18:19:05Z",
      "sequence_number": 1
    }
  ]
}
```

Response:

```json
{
  "saved": 1
}
```

## 17.3 Stop Trip

```http
POST /api/trips/{trip_id}/stop
```

Request:

```json
{
  "ended_at": "2026-05-08T20:09:00Z",
  "duration_seconds": 6616,
  "distance_meters": 30540,
  "avg_speed_kmh": 17,
  "max_speed_kmh": 37,
  "end_lat": 9.012,
  "end_lng": -79.502
}
```

Response:

```json
{
  "id": "trip_123",
  "distance_km": 30.54,
  "duration_seconds": 6616,
  "avg_speed_kmh": 17,
  "max_speed_kmh": 37
}
```

## 17.4 List Trips

```http
GET /api/trips
```

Optional query params:

```text
?page=1&limit=25
```

## 17.5 Get Trip Detail

```http
GET /api/trips/{trip_id}
```

Should return trip summary plus route points.

## 17.6 Get Stats

```http
GET /api/stats
```

Response:

```json
{
  "today_km": 30.54,
  "week_km": 142.2,
  "month_km": 513.6,
  "all_time_km": 4920.1
}
```

---

## 18. Frontend Routes

Recommended routes:

```text
/                 Live speedometer
/trips            Trip history
/trips/:id        Trip report
/stats            Totals dashboard
/settings         App settings
```

---

## 19. Frontend State

Live tracking state:

```typescript
type TrackingState = {
  status: 'idle' | 'starting' | 'tracking' | 'stopping' | 'saved' | 'error';
  tripId: string | null;
  startedAt: string | null;
  currentSpeedKmh: number;
  distanceMeters: number;
  avgSpeedKmh: number;
  maxSpeedKmh: number;
  durationSeconds: number;
  lastPoint: TripPoint | null;
  points: TripPoint[];
  gpsAccuracyMeters: number | null;
  errorMessage: string | null;
};
```

Trip point type:

```typescript
type TripPoint = {
  latitude: number;
  longitude: number;
  accuracyMeters?: number;
  speedKmh?: number;
  heading?: number;
  altitude?: number;
  recordedAt: string;
  sequenceNumber: number;
};
```

---

## 20. PWA Requirements

The app should support PWA installation.

Required files:

```text
manifest.webmanifest
service-worker.js
icons/icon-192.png
icons/icon-512.png
```

Manifest example:

```json
{
  "name": "Speedometer",
  "short_name": "Speedometer",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#050505",
  "theme_color": "#00ff33",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

Service worker should cache:

- App shell
- CSS
- JS
- Icons

Do not aggressively cache API responses unless explicitly handled.

---

## 21. Docker Deployment

## 21.1 Suggested Directory Structure

```text
speedometer-web/
  frontend/
  backend/
  data/
  docker-compose.yml
  Caddyfile
  README.md
  DEVELOPMENT_PLAN.md
```

## 21.2 Example Docker Compose

```yaml
services:
  app:
    build: .
    container_name: speedometer-app
    restart: unless-stopped
    environment:
      - DATABASE_URL=sqlite:////data/speedometer.db
    volumes:
      - ./data:/data
    expose:
      - "8000"

  caddy:
    image: caddy:2
    container_name: speedometer-caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - app

volumes:
  caddy_data:
  caddy_config:
```

## 21.3 Example Caddyfile

```text
dashtrail.example.com {
    reverse_proxy app:8000
}
```

For local testing:

```text
localhost {
    reverse_proxy app:8000
}
```

---

## 22. Authentication

For MVP, there are three possible approaches.

### Option A: No Login

Best for local-only use on a trusted private network.

Pros:

- Simple
- Fast to build

Cons:

- Not safe for public internet exposure

### Option B: Reverse Proxy Authentication

Use Authelia, Cloudflare Access, Caddy basic auth, or Nginx auth.

Pros:

- Keeps app simple
- Good for self-hosting

Cons:

- Less integrated user experience

### Option C: Built-In Login

Add username and password inside the app.

Pros:

- App can be safely exposed with HTTPS
- Better for multiple users

Cons:

- More code
- More security responsibility

Recommended MVP:

Use **reverse proxy authentication** or **single-user app login** if exposed publicly.

---

## 23. Settings

Initial settings:

- Distance unit: kilometers only for MVP
- Speed unit: km/h only for MVP
- GPS accuracy threshold
- Max reasonable speed threshold
- Keep screen awake toggle, if supported
- Dark theme enabled by default

Optional later:

- MPH support
- Trip categories
- Vehicle profiles
- Map tile provider
- Export options

---

## 24. Keep Screen Awake

Use the Screen Wake Lock API where available.

```javascript
let wakeLock = null;

async function requestWakeLock() {
  if ('wakeLock' in navigator) {
    wakeLock = await navigator.wakeLock.request('screen');
  }
}
```

This can help prevent the phone from locking during tracking.

The app should handle unsupported browsers gracefully.

---

## 25. Route Map

Use Leaflet to render the route.

Trip report map requirements:

- Show route polyline
- Show start marker
- Show stop marker
- Auto-fit map bounds to route

Example frontend logic:

```javascript
const route = points.map(point => [point.latitude, point.longitude]);
L.polyline(route).addTo(map);
map.fitBounds(route);
```

---

## 26. Reverse Geocoding

For MVP, start and stop can show coordinates.

Example:

```text
Start: 8.982000, -79.519000
Stop: 9.012000, -79.502000
```

Future option:

- Use Nominatim reverse geocoding from OpenStreetMap
- Or allow self-hosted geocoding later

Important: public Nominatim has usage policies and should not be abused.

Recommended MVP:

Use coordinates only, then add reverse geocoding later.

Implemented update:

- Reverse geocoding is enabled for saved trip start and stop coordinates.
- Default provider is Nominatim/OpenStreetMap.
- Results are cached in SQLite to avoid repeated lookups for the same coordinate area.
- The backend uses a custom User-Agent through `GEOCODER_USER_AGENT`.
- If the lookup fails or reverse geocoding is disabled, the trip report falls back to coordinates.

---

## 27. Data Export

Future export formats:

- CSV
- JSON
- GPX

Recommended route export:

```text
/trips/:id/export/gpx
/trips/:id/export/csv
```

---

## 28. Testing Plan

## 28.1 Unit Tests

Test:

- Haversine distance function
- Speed calculation
- Average speed calculation
- Max speed calculation
- GPS filtering logic
- Date range stats

## 28.2 API Tests

Test:

- Create trip
- Add points
- Stop trip
- List trips
- Get trip report
- Get stats

## 28.3 Manual Field Tests

Test with actual phone GPS:

1. Short walking route.
2. Short driving route.
3. Poor GPS area.
4. App refresh during trip.
5. Screen stays on for full trip.
6. Screen lock behavior.
7. Docker deployment over HTTPS.

---

## 29. MVP Build Milestones

## Milestone 1: Project Setup

- Create repository
- Add frontend app
- Add backend API
- Add SQLite database
- Add Dockerfile
- Add docker-compose.yml
- Add basic health check

Deliverable:

- App runs locally and in Docker

## Milestone 2: Live GPS Tracking

- Request GPS permission
- Watch position
- Show current speed
- Show GPS status
- Show Start / Stop button

Deliverable:

- Live speed works in browser

## Milestone 3: Trip Calculations

- Calculate distance
- Calculate duration
- Calculate average speed
- Calculate max speed
- Filter bad GPS points

Deliverable:

- Live screen shows speed, distance, avg speed, and max speed

## Milestone 4: Save Trips

- Create trip API
- Save route points
- Stop trip API
- Persist trip summary

Deliverable:

- Completed trips are saved to SQLite

## Milestone 5: Trip Report

- Add trip report page
- Add route map
- Add summary cards
- Add start/stop times and coordinates

Deliverable:

- User can open a saved trip report

## Milestone 6: History and Stats

- Add trip history screen
- Add daily total
- Add weekly total
- Add monthly total
- Add all-time total

Deliverable:

- App shows previous trips and totals

## Milestone 7: PWA and Production Deployment

- Add manifest
- Add service worker
- Add icons
- Add Caddy reverse proxy
- Add HTTPS deployment documentation

Deliverable:

- App can be installed as PWA and self-hosted with HTTPS

---

## 30. Suggested MVP Acceptance Criteria

The MVP is complete when:

1. User can open the app on a GPS-enabled phone.
2. User can start a trip.
3. App displays live current speed in km/h.
4. App displays trip distance in km.
5. App displays average speed in km/h.
6. App displays max speed in km/h.
7. User can stop a trip.
8. Trip is saved to the database.
9. Trip report shows route map and summary.
10. Trip history lists previous trips.
11. Stats screen shows today, week, month, and all-time kilometers.
12. App runs from Docker Compose.
13. App works over HTTPS.
14. App can be installed as a PWA.

---

## 31. Suggested Initial Repository Tasks

```text
[ ] Create repo speedometer-web
[ ] Create frontend project
[ ] Create backend project
[ ] Add SQLite connection
[ ] Add trips table
[ ] Add trip_points table
[ ] Add REST API
[ ] Add live speedometer screen
[ ] Add geolocation tracking
[ ] Add distance calculation
[ ] Add trip save logic
[ ] Add trip report page
[ ] Add Leaflet map
[ ] Add trip history page
[ ] Add stats page
[ ] Add PWA manifest
[ ] Add Docker setup
[ ] Add Caddy setup
[ ] Add README deployment instructions
```

---

## 32. Recommended First Implementation Choice

Use this stack for the first build:

```text
Frontend: SvelteKit
Backend: FastAPI
Database: SQLite
Map: Leaflet + OpenStreetMap
Deployment: Docker Compose + Caddy
```

This stack is lightweight, practical, and well-suited for a personal self-hosted app.

---

## 33. Future Enhancements

Potential future features:

- Pause / Resume trip
- Export GPX
- Export CSV
- Import GPX
- Reverse geocoded addresses
- User login
- Multi-user support
- Vehicle profiles
- Walking / cycling / driving modes
- Charts
- Monthly reports
- Backup / restore
- Trip notes
- Trip tags
- Offline queue using IndexedDB
- Automatic bad route correction
- Map tile caching

---

## 34. Build Prompt for an AI Coding Assistant

Use this prompt to start implementation with an AI coding tool:

```text
Build DashTrail, a self-hosted GPS speedometer and trip logger, based on DEVELOPMENT_PLAN.md.

Use SvelteKit for the frontend, FastAPI for the backend, SQLite for storage, Leaflet for maps, and Docker Compose for deployment.

The MVP must include:

1. A mobile-first live speedometer screen.
2. Browser GPS tracking using navigator.geolocation.watchPosition.
3. Live current speed in km/h.
4. Live trip distance in kilometers.
5. Live average speed.
6. Live max speed.
7. Start and Stop trip controls.
8. GPS noise filtering.
9. SQLite tables for trips and trip_points.
10. REST API endpoints for creating trips, saving points, stopping trips, listing trips, viewing trip detail, and stats.
11. Trip report page with Leaflet route map.
12. Trip history page.
13. Stats page showing today, week, month, and all-time kilometers.
14. PWA manifest and install support.
15. Docker Compose deployment with persistent SQLite volume.
16. Caddy reverse proxy example for HTTPS.

Prioritize clean, readable code and a simple dark mobile UI with bright green speedometer-style numbers.
```

---

## 35. Final Notes

The first version should stay focused. The live screen only needs to show what matters during a trip:

- Current speed
- Distance
- Average speed
- Max speed

Everything else belongs in the saved trip report.

The app should be designed as a reliable, simple, self-hosted trip recorder rather than a complex navigation app.

---

## 36. Code Review Bugfixes

Review completed against this plan on 2026-05-12.

Fixed implementation issues:

- Restored the missing `%sveltekit.body%` token in `frontend/src/app.html`; SvelteKit could not compile without it.
- Added the planned trip lifecycle API endpoints: `POST /api/trips/{trip_id}/points` and `POST /api/trips/{trip_id}/stop`.
- Made `POST /api/trips` support both active trip creation and the existing completed-trip save flow.
- Added plan-compatible point and distance payload support, including `latitude`, `longitude`, `recorded_at`, `sequence_number`, `accuracy_meters`, and `distance_meters`.
- Updated live tracking to create a backend trip at start, sync GPS points during the trip, and stop the trip through the stop endpoint.
- Tightened GPS filtering for poor accuracy, stale timestamps, tiny movement under 3 meters, and speeds above 220 km/h.
- Added Screen Wake Lock support when available, with graceful fallback on unsupported browsers.
- Added `/trips` as the trip history route while preserving `/history`.
- Added max speed to trip history entries and full `h:m:s` duration plus start/stop coordinates to trip reports.
- Updated stats to expose and display the documented `all_time_km` value.
- Added PWA service worker support and generated required `icon-192.png` and `icon-512.png` assets.
- Fixed production Docker routing so one exposed Caddy port serves both the frontend and `/api` backend routes for use behind nginx or Cloudflare.

---

## 37. Version 1 Deployment Status

Version 1 deployment completed on 2026-05-12 and was field-tested successfully on 2026-05-13.

- Recommended application directory: `/home/<user>/apps/dashtrail/speedometer-web`
- Default exposed application port: `3080`
- Example reverse proxy target: `http://127.0.0.1:3080`
- Health endpoint: `/api/health`
- Docker Compose services: `frontend`, `backend`, and `caddy`
- Persistent SQLite storage: Docker volume `speedometer-web_speedo_data`

Verified deployment checks:

- `GET /api/health` returns `{"status":"ok"}`.
- `GET /` returned HTTP 200 through Caddy.
- Port `3080` is the default local application port.

Operational note:

- GPS requires HTTPS except for localhost, so production phone testing should go through nginx/Cloudflare with HTTPS enabled.
- Browser/PWA GPS tracking can keep the screen awake on supported browsers while a trip is active, but reliable background tracking while the screen is locked is a mobile OS limitation and requires a native app for full support.

---

## 38. Reverse Geocoding Implementation

Implemented on 2026-05-13.

Backend changes:

- Added `start_address` and `end_address` fields to saved trips.
- Added a `geocode_cache` SQLite table for cached reverse-geocoding results.
- Added startup schema migration for existing SQLite databases so deployed data is preserved.
- Added server-side reverse geocoding when a trip is stopped.
- Added support for one-shot completed trip saves to resolve addresses too.
- Added `GEOCODER_PROVIDER`, `GEOCODER_USER_AGENT`, and `GEOCODER_LANGUAGE` environment settings.

Frontend changes:

- Trip reports now show full street addresses when available.
- Coordinates remain the fallback display when the geocoder is unavailable or disabled.

Operational notes:

- Default provider is Nominatim.
- The public Nominatim service should be used lightly, with caching and a custom User-Agent.
- For heavier use or stricter address quality, switch to a paid provider or a self-hosted geocoder later.
