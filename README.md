# SPRINGVYRA

AI-assisted geospatial spring-recharge decision-support prototype. The current implementation provides a Next.js dashboard, FastAPI service, PostgreSQL/PostGIS models, spring/zone/observation APIs, sourced geometry rendering, a read-only controlled data assistant, and a Docker Compose development stack.

**Scientific safeguard:** SpringVyra does not determine groundwater truth. Seeded values are synthetic `DEMO DATA`; recharge analysis is blocked until real, sourced GIS inputs are configured. Any future prediction requires field validation and expert assessment before intervention.

## What is implemented

- Spring, recharge-zone, and field-observation CRUD endpoints.
- EPSG:4326 point storage for springs/observations and optional MultiPolygon boundaries for recharge zones.
- Field monitoring record creation and intervention candidate record entry.
- Field-worker form with device GPS capture and pending review status.
- Dataset provenance catalog fields for source, acquisition date, resolution, license, and processing method.
- Demo-data provenance labels and no demo model confidence.
- Dashboard, inventory, OSM/satellite map layers, spring popups, and recharge polygons only when supplied.
- Weather source status, GIS readiness response, blocked analysis endpoint, and bounded read-only assistant lookup.
- Additive schema upgrades for the earlier prototype.

Authentication/RBAC, actual GIS processing, trained/validated ML, live weather, media upload/storage, risk scoring, multilingual UI, voice, PDF reports, and production hardening are not implemented yet. See [docs/architecture.md](docs/architecture.md) for status.

## Requirements

- Python 3.10+.
- Node.js 18+ with npm (the checked-in frontend currently uses Next.js 14 and React 18).
- PostgreSQL with PostGIS, or Docker Desktop for the container workflow.
- Network access to install dependencies and load external basemap tiles.

## Run on Windows

### 1. Configure PostgreSQL

Create a database named `spring_recharge` using pgAdmin or:

```powershell
createdb -h 127.0.0.1 -U postgres spring_recharge
```

From the repository root, configure the backend environment:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Set `DATABASE_URL` to your PostgreSQL credentials. The host must be IPv4 loopback:

```text
postgresql+pg8000://postgres:YOUR_PASSWORD@127.0.0.1:5432/spring_recharge
```

The database role must be able to enable PostGIS on the first run. Do not commit `.env` or use a production database for demo seeding.

### 2. Install, seed, and run the API

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python seed.py
python -m uvicorn backend.main:app --reload
```

`seed.py` enables PostGIS, creates current tables, applies additive upgrades, and inserts clearly labeled synthetic examples. It does not generate real observations or confidence values.

Check [API health](http://127.0.0.1:8000/health), [interactive API docs](http://127.0.0.1:8000/docs), and the [dashboard feed](http://127.0.0.1:8000/api/dashboard). Keep this terminal open.

### 3. Install and run the dashboard

In a second PowerShell window:

```powershell
cd frontend
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm.cmd install
node .\node_modules\next\dist\bin\next dev
```

Open [http://localhost:3000](http://localhost:3000). If the API is offline, the UI falls back to a synthetic preview and labels it `DEMO DATA`. An API connection does not make demo records real.

## Run with Docker Compose

Install Docker Desktop, copy `.env.example` to `.env`, set a local `POSTGRES_PASSWORD`, then from the repository root run:

```powershell
docker compose up --build
```

The services are frontend `localhost:3000`, API `localhost:8000`, and PostGIS. The database health check gates backend startup. This configuration is for local development only.

## Important configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection (`pg8000`, IPv4 localhost by default; psycopg2 URLs are also supported) |
| `CORS_ORIGINS` | Allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | Browser-visible API base URL; set in `frontend/.env.local` for local npm runs |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Docker Compose database settings |
| `WEATHER_API_KEY`, `LLM_API_KEY`, `JWT_SECRET` | Reserved for future integrations; no provider/auth flow is active yet |

## Key API routes

- `GET /api/springs`, `/api/springs/{id}` and POST/PUT/DELETE spring routes.
- `GET /api/recharge/zones` serves only zones with supplied polygon geometry; `/api/recharge-zones` manages zone records.
- `/api/observations` and `/api/field-observations` provide field-observation CRUD.
- `GET/POST /api/monitoring` reads and creates spring measurements.
- `GET/POST /api/interventions` stores candidate records; it does not recommend construction.
- `GET/POST /api/data-sources` stores provenance metadata supplied by the user.
- `GET /api/weather` reports `NOT CONFIGURED` without a provider.
- `GET /api/recharge/readiness` lists missing GIS inputs; `POST /api/recharge/analyze` returns a clear unavailable response and creates no prediction.
- `POST /api/assistant/query` performs allow-listed read-only lookups; no arbitrary SQL or data changes.

## API contract checks

With the backend virtual environment active, install the development dependencies and run the API contract tests:

```powershell
python -m pip install -r backend/requirements-dev.txt
python -m pytest
```

For a frontend production build in PowerShell, run `node .\node_modules\next\dist\bin\next build` from the `frontend` folder. This calls the local Next.js executable directly and avoids PowerShell blocking npm's generated `.ps1` shim.

## Data and scientific limitations

The seed coordinates and values are synthetic examples only. Demo zone scores are not model results, have no confidence value, and have no mapped boundary. No rainfall, geology, DEM, soil, land-cover, drainage, or verified field dataset is bundled. Supply licensed, dated source layers and quality metadata before implementing recharge suitability, risk analysis, or intervention prioritization. Never act on a demo record or unvalidated result.

## Documentation

- [Architecture and implementation status](docs/architecture.md)
- [Database](docs/database.md)
- [GIS pipeline and required inputs](docs/gis-pipeline.md)
- [ML validation requirements](docs/ml-pipeline.md)
- [API notes](docs/api.md)
- [Local container deployment](docs/deployment.md)
- [Prototype user guide](docs/user-guide.md)
