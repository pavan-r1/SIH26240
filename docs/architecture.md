# Architecture and implementation status

SpringVyra currently has a Next.js App Router dashboard, a FastAPI API, SQLAlchemy models, and a PostGIS persistence layer. The frontend reads `/api/dashboard`; the map uses spring point coordinates and draws recharge zones only when polygon geometry is supplied. The assistant calls an allow-listed backend lookup and cannot write data or issue arbitrary SQL.

The API reports weather and recharge-analysis readiness explicitly. No GIS analysis or model prediction is generated until required source datasets are configured. Never treat a displayed class as groundwater truth; field validation and expert review are required.

## Implemented prototype scope

- Spring CRUD with EPSG:4326 point geometry.
- Recharge-zone CRUD with optional GeoJSON Polygon/MultiPolygon geometry.
- Field-observation CRUD with point geometry and validation status.
- Field-worker observation form with browser GPS and `PENDING` validation status.
- Explicit DEMO provenance for seeded synthetic records.
- Dataset provenance records for source, date, resolution, license, and processing method.
- Monitoring and candidate intervention record endpoints; no automated construction recommendation.
- Weather not-configured response and recharge-analysis missing-input response.
- OSM and Esri imagery basemaps; sourced zones only.
- Docker Compose for the local PostGIS, API, and frontend stack.

## Not implemented yet

Authentication and role authorization, uploads with storage validation, actual GIS/DEM processing, trained and validated ML, source integrations, time-series monitoring charts, intervention and risk workflows, LLM provider integration, speech, translations, PDF reports, and deployment hardening. See the phase docs for the required inputs and safeguards.
