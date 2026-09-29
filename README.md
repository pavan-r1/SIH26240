# SpringVyra

Geospatial decision support for mountain springs, groundwater resources, and recharge suitability zones.

## Quick start

### Backend

Requires PostgreSQL with PostGIS and Python 3.10+.

```powershell
createdb -h 127.0.0.1 springvyra
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/springvyra"
python seed.py
uvicorn backend.main:app --reload
```

Set `DATABASE_URL` and `CORS_ORIGINS` to match your environment. The API docs are at `/docs`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` if the backend is not at `http://127.0.0.1:8000`.

## API

CRUD endpoints are available at `/api/springs`, `/api/recharge-zones`, and `/api/observations`; `/api/dashboard` returns dashboard aggregates and recent inventory. Spatial data is stored in EPSG:4326 PostGIS geometry columns. Create the PostGIS extension before seeding (the seed script also requests the extension).
