import os
from typing import Type

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement

from .database import Base, engine, get_db
from . import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SpringVyra API", version="1.0.0", description="Mountain spring monitoring and recharge decision support")
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in origins], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SpringVyra"}


def crud_router(db: Session, model: Type, payload: dict, geom: bool = False):
    if geom:
        payload["geom"] = WKTElement(f"POINT({payload.pop('longitude')} {payload.pop('latitude')})", srid=4326)
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
    return crud_router(db, models.Spring, item.model_dump() | {"geom": WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326)})


@app.get("/api/springs/{item_id}", response_model=schemas.SpringRead)
def get_spring(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Spring, item_id)
    if not row: raise HTTPException(404, "Spring not found")
    return row


@app.put("/api/springs/{item_id}", response_model=schemas.SpringRead)
def update_spring(item_id: int, item: schemas.SpringCreate, db: Session = Depends(get_db)):
    row = db.get(models.Spring, item_id)
    if not row: raise HTTPException(404, "Spring not found")
    for key, value in item.model_dump().items(): setattr(row, key, value)
    row.geom = WKTElement(f"POINT({item.longitude} {item.latitude})", srid=4326)
    db.commit(); db.refresh(row)
    return row


@app.delete("/api/springs/{item_id}", status_code=204)
def delete_spring(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.Spring, item_id)
    if not row: raise HTTPException(404, "Spring not found")
    db.delete(row); db.commit()


@app.get("/api/recharge-zones", response_model=list[schemas.ZoneRead])
def list_zones(db: Session = Depends(get_db)):
    return db.scalars(select(models.RechargeZone).order_by(models.RechargeZone.zone_code)).all()


@app.post("/api/recharge-zones", response_model=schemas.ZoneRead, status_code=201)
def create_zone(item: schemas.ZoneCreate, db: Session = Depends(get_db)):
    row = models.RechargeZone(**item.model_dump()); db.add(row); db.commit(); db.refresh(row); return row


@app.get("/api/recharge-zones/{item_id}", response_model=schemas.ZoneRead)
def get_zone(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.RechargeZone, item_id)
    if not row: raise HTTPException(404, "Recharge zone not found")
    return row


@app.put("/api/recharge-zones/{item_id}", response_model=schemas.ZoneRead)
def update_zone(item_id: int, item: schemas.ZoneCreate, db: Session = Depends(get_db)):
    row = db.get(models.RechargeZone, item_id)
    if not row: raise HTTPException(404, "Recharge zone not found")
    for key, value in item.model_dump().items(): setattr(row, key, value)
    db.commit(); db.refresh(row); return row


@app.delete("/api/recharge-zones/{item_id}", status_code=204)
def delete_zone(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.RechargeZone, item_id)
    if not row: raise HTTPException(404, "Recharge zone not found")
    db.delete(row); db.commit()


def observation_dict(db: Session, row: models.FieldObservation):
    point = db.execute(select(func.ST_Y(row.geom), func.ST_X(row.geom))).one()
    return {"id": row.id, "spring_id": row.spring_id, "observer": row.observer, "discharge": row.discharge, "water_level": row.water_level, "vegetation_condition": row.vegetation_condition, "nearby_land_use": row.nearby_land_use, "validation_status": row.validation_status, "observed_at": row.observed_at, "latitude": point[0], "longitude": point[1]}


@app.get("/api/observations")
def list_observations(db: Session = Depends(get_db)):
    return [observation_dict(db, row) for row in db.scalars(select(models.FieldObservation).order_by(models.FieldObservation.id.desc())).all()]


@app.post("/api/observations", status_code=201)
def create_observation(item: schemas.ObservationCreate, db: Session = Depends(get_db)):
    if not db.get(models.Spring, item.spring_id): raise HTTPException(404, "Spring not found")
    values = item.model_dump(); lat, lon = values.pop("latitude"), values.pop("longitude")
    row = models.FieldObservation(**values, geom=WKTElement(f"POINT({lon} {lat})", srid=4326)); db.add(row); db.commit(); db.refresh(row)
    return observation_dict(db, row)


@app.get("/api/observations/{item_id}")
def get_observation(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.FieldObservation, item_id)
    if not row: raise HTTPException(404, "Observation not found")
    return observation_dict(db, row)


@app.put("/api/observations/{item_id}")
def update_observation(item_id: int, item: schemas.ObservationCreate, db: Session = Depends(get_db)):
    row = db.get(models.FieldObservation, item_id)
    if not row: raise HTTPException(404, "Observation not found")
    values = item.model_dump(); lat, lon = values.pop("latitude"), values.pop("longitude")
    for key, value in values.items(): setattr(row, key, value)
    row.geom = WKTElement(f"POINT({lon} {lat})", srid=4326); db.commit(); db.refresh(row)
    return observation_dict(db, row)


@app.delete("/api/observations/{item_id}", status_code=204)
def delete_observation(item_id: int, db: Session = Depends(get_db)):
    row = db.get(models.FieldObservation, item_id)
    if not row: raise HTTPException(404, "Observation not found")
    db.delete(row); db.commit()


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    springs = db.scalars(select(models.Spring).order_by(models.Spring.id.desc())).all()
    zones = db.scalars(select(models.RechargeZone)).all()
    return {"total_springs": len(springs), "active_springs": sum(s.status.lower() == "active" for s in springs), "active_zones": sum(z.suitability_class.lower() in ("high", "very high") for z in zones), "average_suitability": round(sum(z.suitability_score for z in zones) / len(zones), 1) if zones else 0, "model_confidence": round(sum(z.confidence for z in zones) / len(zones), 1) if zones else 0, "springs": [schemas.SpringRead.model_validate(s).model_dump() for s in springs[:8]], "zones": [schemas.ZoneRead.model_validate(z).model_dump() for z in zones]}
