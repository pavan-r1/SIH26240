import os
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

from .database import get_db
from . import models, schemas

app = FastAPI(title="SpringVyra API", version="1.0.0", description="Mountain spring monitoring and recharge decision support")
# Keep both common local frontend hostnames allowed even if an existing .env
# only lists one. Additional deployed origins can be supplied through CORS_ORIGINS.
local_origins = {"http://localhost:3000", "http://127.0.0.1:3000"}
configured_origins = {
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
}
origins = sorted(local_origins | configured_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SpringVyra"}


@app.get("/health")
def health_compat():
    return health()


def crud_router(db: Session, model, payload: dict):
    row = model(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/api/springs", response_model=list[schemas.SpringRead])
def list_springs(db: Session = Depends(get_db)):
    return db.scalars(select(models.Spring).order_by(models.Spring.spring_code)).all()


@app.post("/api/springs", response_model=schemas.SpringRead, status_code=201)
def create_spring(item: schemas.SpringCreate, db: Session = Depends(get_db)):
    values = item.model_dump() | {"data_status": "UNVERIFIED", "geom": WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326)}
    return crud_router(db, models.Spring, values)


@app.get("/api/springs/{item_id}", response_model=schemas.SpringRead)
def get_spring(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Spring, item_id)
    if not row: raise HTTPException(404, "Spring not found")
    return row


@app.put("/api/springs/{item_id}", response_model=schemas.SpringRead)
def update_spring(item_id: int, item: schemas.SpringCreate, db: Session = Depends(get_db)):
    row = db.get(models.Spring, item_id)
    if not row: raise HTTPException(404, "Spring not found")
    for key, value in item.model_dump(exclude={"data_status"}).items(): setattr(row, key, value)
    row.geom = WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326)
    db.commit(); db.refresh(row)
    return row


@app.delete("/api/springs/{item_id}", status_code=204)
def delete_spring(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Spring, item_id)
    if not row: raise HTTPException(404, "Spring not found")
    db.delete(row); db.commit()


def zone_dict(db: Session, zone: models.RechargeZone):
    geometry = db.scalar(select(func.ST_AsGeoJSON(models.RechargeZone.geom)).where(models.RechargeZone.id == zone.id)) if zone.geom is not None else None
    import json
    return {"id": zone.id, "zone_code": zone.zone_code, "suitability_score": zone.suitability_score, "suitability_class": zone.suitability_class, "confidence": zone.confidence, "model_version": zone.model_version, "analysis_date": zone.analysis_date, "data_quality": zone.data_quality, "data_status": zone.data_status, "geometry": json.loads(geometry) if geometry else None}


@app.get("/api/recharge-zones")
def list_zones(db: Session = Depends(get_db)):
    return [zone_dict(db, row) for row in db.scalars(select(models.RechargeZone).order_by(models.RechargeZone.zone_code)).all()]


@app.get("/api/recharge/zones")
def list_zone_features(db: Session = Depends(get_db)):
    return {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": item["geometry"], "properties": {k: v for k, v in item.items() if k != "geometry"}} for item in list_zones(db) if item["geometry"]]}


@app.post("/api/recharge-zones", response_model=schemas.ZoneRead, status_code=201)
def create_zone(item: schemas.ZoneCreate, db: Session = Depends(get_db)):
    import json
    values = item.model_dump(exclude={"geometry", "data_status"}) | {"data_status": "UNVERIFIED"}
    geometry = item.geometry
    if geometry is not None:
        values["geom"] = func.ST_Multi(func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geometry)), 4326))
    row = models.RechargeZone(**values); db.add(row); db.commit(); db.refresh(row); return zone_dict(db, row)


@app.get("/api/recharge-zones/{item_id}", response_model=schemas.ZoneRead)
def get_zone(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.RechargeZone, item_id)
    if not row: raise HTTPException(404, "Recharge zone not found")
    return zone_dict(db, row)


@app.put("/api/recharge-zones/{item_id}", response_model=schemas.ZoneRead)
def update_zone(item_id: int, item: schemas.ZoneCreate, db: Session = Depends(get_db)):
    row = db.get(models.RechargeZone, item_id)
    if not row: raise HTTPException(404, "Recharge zone not found")
    import json
    for key, value in item.model_dump(exclude={"geometry", "data_status"}).items(): setattr(row, key, value)
    if item.geometry is not None:
        row.geom = func.ST_Multi(func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(item.geometry)), 4326))
    db.commit(); db.refresh(row); return zone_dict(db, row)


@app.delete("/api/recharge-zones/{item_id}", status_code=204)
def delete_zone(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.RechargeZone, item_id)
    if not row: raise HTTPException(404, "Recharge zone not found")
    db.delete(row); db.commit()


def observation_dict(db: Session, row: models.FieldObservation):
    point = db.execute(select(func.ST_Y(models.FieldObservation.geom), func.ST_X(models.FieldObservation.geom)).where(models.FieldObservation.id == row.id)).one()
    return {"id": row.id, "spring_id": row.spring_id, "observer": row.observer, "discharge": row.discharge, "water_level": row.water_level, "vegetation_condition": row.vegetation_condition, "nearby_land_use": row.nearby_land_use, "validation_status": row.validation_status, "observed_at": row.observed_at, "latitude": point[0], "longitude": point[1], "notes": row.notes, "photo_url": row.photo_url, "data_status": row.data_status}


@app.get("/api/observations")
@app.get("/api/field-observations")
def list_observations(db: Session = Depends(get_db)):
    return [observation_dict(db, row) for row in db.scalars(select(models.FieldObservation).order_by(models.FieldObservation.id.desc())).all()]


@app.post("/api/observations", status_code=201)
@app.post("/api/field-observations", status_code=201)
def create_observation(item: schemas.ObservationCreate, db: Session = Depends(get_db)):
    if not db.get(models.Spring, item.spring_id): raise HTTPException(404, "Spring not found")
    values = item.model_dump(); lat, lon = values.pop("latitude"), values.pop("longitude")
    row = models.FieldObservation(**values, geom=WKTElement(f"POINT({lon} {lat})", srid=4326)); db.add(row); db.commit(); db.refresh(row)
    return observation_dict(db, row)


@app.get("/api/observations/{item_id}")
@app.get("/api/field-observations/{item_id}")
def get_observation(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.FieldObservation, item_id)
    if not row: raise HTTPException(404, "Observation not found")
    return observation_dict(db, row)


@app.put("/api/observations/{item_id}")
@app.put("/api/field-observations/{item_id}")
def update_observation(item_id: int, item: schemas.ObservationCreate, db: Session = Depends(get_db)):
    row = db.get(models.FieldObservation, item_id)
    if not row: raise HTTPException(404, "Observation not found")
    values = item.model_dump(); lat, lon = values.pop("latitude"), values.pop("longitude")
    for key, value in values.items(): setattr(row, key, value)
    row.geom = WKTElement(f"POINT({lon} {lat})", srid=4326); db.commit(); db.refresh(row)
    return observation_dict(db, row)


@app.delete("/api/observations/{item_id}", status_code=204)
@app.delete("/api/field-observations/{item_id}", status_code=204)
def delete_observation(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.FieldObservation, item_id)
    if not row: raise HTTPException(404, "Observation not found")
    db.delete(row); db.commit()


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    springs = db.scalars(select(models.Spring).order_by(models.Spring.id.desc())).all()
    zones = db.scalars(select(models.RechargeZone)).all()
    scores = [z.suitability_score for z in zones if z.suitability_score is not None and z.data_status in {"FIELD", "IMPORTED"}]
    confidence = [z.confidence for z in zones if z.confidence is not None and z.data_status in {"FIELD", "IMPORTED"}]
    spring_statuses = {s.data_status for s in springs}
    data_status = "DEMO" if spring_statuses == {"DEMO"} else "LATEST AVAILABLE" if spring_statuses and spring_statuses <= {"FIELD", "IMPORTED"} else "UNVERIFIED" if springs else "NO DATA"
    features = [{"type": "Feature", "geometry": item["geometry"], "properties": {k: v for k, v in item.items() if k != "geometry"}} for item in [zone_dict(db, z) for z in zones] if item["geometry"]]
    return {"total_springs": len(springs), "active_springs": sum(s.status.lower() == "active" for s in springs), "active_zones": sum(z.suitability_class.upper() in ("HIGH", "VERY HIGH") for z in zones), "average_suitability": round(sum(scores) / len(scores), 1) if scores else None, "model_confidence": round(sum(confidence) / len(confidence), 1) if confidence else None, "data_status": data_status, "springs": [schemas.SpringRead.model_validate(s).model_dump() for s in springs[:8]], "zones": features, "weather_status": "NOT CONFIGURED"}


@app.get("/api/weather")
def weather_status():
    return {"status": "NOT CONFIGURED", "message": "Weather data source is not configured."}


@app.get("/api/recharge/readiness")
def recharge_readiness(db: Session = Depends(get_db)):
    required = ["DEM", "slope/aspect", "rainfall", "geology", "soil", "land cover", "drainage network"]
    sources = db.scalars(select(models.DataSource).order_by(models.DataSource.dataset_name)).all()
    catalog_names = {source.dataset_name.casefold() for source in sources}
    available = [{"parameter": source.dataset_name, "source": source.source_name, "acquisition_date": source.acquisition_date, "resolution_m": source.spatial_resolution_m, "license": source.license_name, "data_status": source.data_status} for source in sources]
    missing = [name for name in required if not any(name.casefold() in entry or entry in name.casefold() for entry in catalog_names)]
    return {"can_analyze": False, "available_parameters": available, "missing_parameters": missing, "data_quality": "Metadata cataloged; spatial files and quality checks are not connected to a processing pipeline." if sources else "Not assessed", "data_source": "See data-source catalog" if sources else "Not configured", "analysis_date": None, "message": "Recharge analysis is disabled until sourced spatial files and a validated analysis pipeline are configured."}


@app.post("/api/recharge/analyze", status_code=409)
def analyze_recharge():
    raise HTTPException(status_code=409, detail={"message": "Recharge analysis cannot be completed because required spatial data is unavailable.", "missing_parameters": ["DEM", "rainfall", "geology", "soil", "land cover", "drainage network"], "prediction_created": False})


@app.get("/api/monitoring")
def list_monitoring(db: Session = Depends(get_db)):
    rows = db.scalars(select(models.SpringMeasurement).order_by(models.SpringMeasurement.measured_at.desc()).limit(250)).all()
    return [{"id": r.id, "spring_id": r.spring_id, "discharge": r.discharge, "water_level": r.water_level, "water_quality_ph": r.water_quality_ph, "measured_at": r.measured_at, "observer": r.observer, "notes": r.notes, "data_status": r.data_status} for r in rows]


@app.post("/api/monitoring", status_code=201)
def create_measurement(item: schemas.MeasurementCreate, db: Session = Depends(get_db)):
    if not db.get(models.Spring, item.spring_id): raise HTTPException(404, "Spring not found")
    row = models.SpringMeasurement(**item.model_dump(exclude_none=True)); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "spring_id": row.spring_id, "discharge": row.discharge, "water_level": row.water_level, "water_quality_ph": row.water_quality_ph, "measured_at": row.measured_at, "observer": row.observer, "notes": row.notes, "data_status": row.data_status}


@app.get("/api/interventions")
def list_interventions(db: Session = Depends(get_db)):
    rows = db.scalars(select(models.InterventionSite).order_by(models.InterventionSite.id.desc())).all()
    return [{"id": r.id, "site_code": r.site_code, "intervention_type": r.intervention_type, "status": r.status, "rationale": r.rationale, "risk_notes": r.risk_notes, "data_status": r.data_status} for r in rows]


@app.post("/api/interventions", status_code=201)
def create_intervention(item: schemas.InterventionCreate, db: Session = Depends(get_db)):
    row = models.InterventionSite(site_code=item.site_code, intervention_type=item.intervention_type, rationale=item.rationale, risk_notes=item.risk_notes, data_status="UNVERIFIED", geom=WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326))
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "site_code": row.site_code, "intervention_type": row.intervention_type, "status": row.status, "rationale": row.rationale, "risk_notes": row.risk_notes, "data_status": row.data_status, "latitude": item.latitude, "longitude": item.longitude}


@app.get("/api/risk-analysis")
def risk_analysis_status():
    return {"status": "NOT AVAILABLE", "risks": [], "missing_parameters": ["terrain stability", "flood hazard", "geology", "accessibility", "protected-area boundaries"], "message": "Risk analysis is unavailable until authoritative spatial layers are configured."}


@app.get("/api/reports/status")
def report_status():
    return {"status": "NOT CONFIGURED", "message": "PDF report generation is not configured. No report was created."}


@app.get("/api/data-sources")
def list_data_sources(db: Session = Depends(get_db)):
    rows = db.scalars(select(models.DataSource).order_by(models.DataSource.dataset_name)).all()
    return [{"id": r.id, "dataset_name": r.dataset_name, "source_name": r.source_name, "source_url": r.source_url, "acquisition_date": r.acquisition_date, "spatial_resolution_m": r.spatial_resolution_m, "license_name": r.license_name, "processing_method": r.processing_method, "data_status": r.data_status} for r in rows]


@app.post("/api/data-sources", status_code=201)
def create_data_source(item: schemas.DataSourceCreate, db: Session = Depends(get_db)):
    row = models.DataSource(**item.model_dump(exclude={"data_status"}) | {"data_status": "UNVERIFIED"}); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, **item.model_dump()}


@app.post("/api/assistant/query")
def assistant_query(request: schemas.AssistantQuery, db: Session = Depends(get_db)):
    """Small allow-listed data lookup; no model, arbitrary SQL, or write actions."""
    q = request.question.casefold()
    if any(term in q for term in ("weather", "rain", "rainfall")):
        return {"answer": "Weather data source is not configured.", "data_status": "NOT CONFIGURED", "actions": []}
    if "discharge" in q:
        statement = select(models.SpringMeasurement).order_by(models.SpringMeasurement.measured_at.desc()).limit(1)
        if request.spring_id is not None:
            statement = statement.where(models.SpringMeasurement.spring_id == request.spring_id)
        row = db.scalar(statement)
        if not row:
            return {"answer": "No spring measurement records are available.", "data_status": "NO DATA", "actions": []}
        return {"answer": f"Most recent stored measurement: {row.discharge if row.discharge is not None else 'not recorded'} L/s at {row.measured_at.isoformat()}. Source status: {row.data_status}.", "data_status": row.data_status, "results": [{"spring_id": row.spring_id, "discharge": row.discharge, "measured_at": row.measured_at, "data_status": row.data_status}], "actions": []}
    if any(term in q for term in ("zone", "recharge", "suitability")):
        statement = select(models.RechargeZone).order_by(models.RechargeZone.zone_code)
        if "high" in q:
            statement = statement.where(models.RechargeZone.suitability_class.ilike("%high%"))
        rows = db.scalars(statement).all()
        if not rows:
            return {"answer": "No recharge-zone records are available. No suitability analysis has been run.", "data_status": "NO DATA", "actions": []}
        items = [{"zone_code": row.zone_code, "suitability_class": row.suitability_class, "data_status": row.data_status, "score": row.suitability_score if row.data_status != "DEMO" else None, "geometry_available": row.geom is not None} for row in rows]
        summary = ", ".join(f"{x['zone_code']} ({x['suitability_class']}, {x['data_status']})" for x in items)
        return {"answer": f"Stored zone records: {summary}. These are decision-support records and require source review and field validation.", "data_status": "DEMO" if all(x["data_status"] == "DEMO" for x in items) else "UNVERIFIED", "results": items, "actions": []}
    if "spring" in q or request.spring_id is not None:
        query = select(models.Spring).order_by(models.Spring.spring_code).limit(12)
        if request.spring_id is not None:
            query = select(models.Spring).where(models.Spring.id == request.spring_id)
        rows = db.scalars(query).all()
        if not rows:
            return {"answer": "No matching spring records were found.", "data_status": "NO DATA", "actions": []}
        names = ", ".join(f"{row.name} ({row.spring_code}, {row.data_status})" for row in rows)
        return {"answer": f"Available spring records: {names}. Confirm data provenance before using measurements for decisions.", "data_status": "DEMO" if all(row.data_status == "DEMO" for row in rows) else "UNVERIFIED", "results": [{"id": row.id, "name": row.name, "spring_code": row.spring_code, "data_status": row.data_status} for row in rows], "actions": []}
    return {"answer": "I can look up stored spring records, recharge-zone records, or weather-source configuration. I cannot run analysis or change data through chat.", "data_status": "LIMITED ASSISTANT", "actions": []}
