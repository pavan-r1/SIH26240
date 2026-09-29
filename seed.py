"""Initialize the PostGIS schema and add explicitly labeled DEMO records."""
from sqlalchemy import text

from backend.database import Base, SessionLocal, engine
from backend.migrations import upgrade_legacy_schema
from backend.models import FieldObservation, RechargeZone, Spring
from geoalchemy2 import WKTElement


DEMO_SPRINGS = [
    ("NG-001", "Jal Dhara", "D hillslope", 30.1264, 78.3120, 1840, 0.42, 7.1, "active"),
    ("NG-002", "Banshi Gad", "Fracture", 30.1432, 78.3395, 2115, 0.28, 6.8, "active"),
    ("NG-003", "Kaphal Pani", "Depression", 30.1088, 78.3654, 1670, 0.63, 7.3, "active"),
    ("NG-004", "Aama Naula", "Contact", 30.1630, 78.2891, 2260, 0.19, 7.0, "seasonal"),
    ("NG-005", "Buransh Source", "Hillslope", 30.0902, 78.3258, 1535, 0.51, 7.2, "active"),
    ("NG-006", "Kwarik Khal", "Fracture", 30.1774, 78.3580, 2380, 0.11, 6.9, "monitoring"),
    ("NG-007", "Simal Srot", "Depression", 30.1351, 78.2750, 1980, 0.34, 7.4, "active"),
    ("NG-008", "Gwar Gaad", "Contact", 30.0761, 78.3792, 1450, 0.23, 6.7, "active"),
]
DEMO_ZONES = [
    ("RZ-DEMO-01", 91, "HIGH"), ("RZ-DEMO-02", 86, "HIGH"),
    ("RZ-DEMO-03", 67, "MODERATE"), ("RZ-DEMO-04", 42, "LOW"),
]


def main():
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=engine)
    upgrade_legacy_schema(engine)
    with SessionLocal() as db:
        for code, name, kind, lat, lon, elev, flow, ph, status in DEMO_SPRINGS:
            if not db.query(Spring).filter_by(spring_code=code).first():
                spring = Spring(spring_code=code, name=name, spring_type=kind, latitude=lat, longitude=lon, elevation=elev, discharge_rate=flow, water_quality_ph=ph, status=status, data_status="DEMO", catchment="DEMO catchment", description="Synthetic development record; not a verified real spring.", geom=WKTElement(f"POINT({lon} {lat})", srid=4326))
                db.add(spring); db.flush()
                db.add(FieldObservation(spring_id=spring.id, observer="DEMO SAMPLE", discharge=flow, water_level=1.2 + flow, vegetation_condition="Sample only", nearby_land_use="Sample only", validation_status="NEEDS_REVIEW", data_status="DEMO", notes="Synthetic development record; not a field observation.", geom=WKTElement(f"POINT({lon} {lat})", srid=4326)))
        for code, score, klass in DEMO_ZONES:
            if not db.query(RechargeZone).filter_by(zone_code=code).first():
                db.add(RechargeZone(zone_code=code, suitability_score=score, suitability_class=klass, confidence=None, model_version=None, data_quality="SYNTHETIC", data_status="DEMO"))
        db.commit()
    print("SpringVyra schema initialized. All inserted spring, observation, and suitability records are synthetic DEMO DATA; no real measurements or model confidence are asserted.")


if __name__ == "__main__":
    main()
