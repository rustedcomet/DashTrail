# DashTrail Deployment

This guide deploys DashTrail on a typical Linux server with Docker and Docker Compose already installed.

## Requirements

- Docker Engine
- Docker Compose plugin
- A domain name pointed at the server
- SSL/TLS through nginx, Caddy, Traefik, Cloudflare Tunnel, or another reverse proxy
- A modern browser on the phone

GPS access requires HTTPS in production. Plain HTTP only works reliably for localhost development.

DashTrail displays trip times in Panama time, `America/Panama` (GMT-5), regardless of the VM or container timezone. Trip timestamps are stored as UTC internally.

## Files

Deploy from the `speedometer-web/` directory:

```bash
cd speedometer-web
cp .env.example .env
```

Edit `.env`:

```bash
APP_PORT=3080
GEOCODER_PROVIDER=nominatim
GEOCODER_USER_AGENT=DashTrail/1.0-self-hosted-your-domain
GEOCODER_LANGUAGE=en
```

`APP_PORT` is the local port exposed on the Docker host. Your public reverse proxy should forward HTTPS traffic to this port.

## Start

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
docker compose logs --tail=100
curl http://127.0.0.1:3080/api/health
```

Expected health response:

```json
{"status":"ok"}
```

## Reverse Proxy

Point your HTTPS reverse proxy to the Docker host and `APP_PORT`.

Example nginx server block:

```nginx
server {
    listen 443 ssl http2;
    server_name dashtrail.example.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:3080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

Also redirect HTTP to HTTPS:

```nginx
server {
    listen 80;
    server_name dashtrail.example.com;
    return 301 https://$host$request_uri;
}
```

## Data Storage

Trip data is stored in the Docker volume:

```text
speedometer-web_speedo_data
```

Back up this volume to preserve trip history.

## Reverse Geocoding

DashTrail uses Nominatim/OpenStreetMap by default for start and stop street addresses. Results are cached in SQLite.

For public Nominatim:

- Use a custom `GEOCODER_USER_AGENT`.
- Keep request volume low.
- Do not bulk geocode.

Disable external geocoding with:

```bash
GEOCODER_PROVIDER=off
```

When geocoding is disabled or unavailable, DashTrail falls back to coordinates.

## Update

```bash
git pull
cd speedometer-web
docker compose up -d --build
```

## Stop

```bash
docker compose down
```

This stops containers but keeps Docker volumes unless you explicitly remove them.
