# API notes

Run `uvicorn backend.main:app --reload` from the repository root. Open `/docs` for the generated OpenAPI page.

- `GET /health`, `GET /api/health`
- CRUD `/api/springs`
- CRUD `/api/recharge-zones`; GeoJSON boundary feed `/api/recharge/zones`
- CRUD `/api/observations` and compatibility alias `/api/field-observations`
- `GET /api/dashboard`
- `GET /api/weather` returns `NOT CONFIGURED` until a source is set up
- `GET /api/recharge/readiness`; `POST /api/recharge/analyze` reports missing inputs and creates no prediction
- `POST /api/assistant/query` performs a bounded read-only lookup of spring/zone rows or weather configuration

The current prototype has no authentication or role authorization. Do not expose it to an untrusted network.
