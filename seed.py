"""Create SpringVyra's PostGIS schema and seed representative field data."""
from sqlalchemy import text

from backend.database import Base, SessionLocal, engine
from backend.models import FieldObservation, RechargeZone, Spring
from geoalchemy2 import WKTElement


SPRINGS = [
    ("NG-001", "Jal Dhara", "D hillslope", 30.1264, 78.3120, 1840, 0.42, 7.1, "active"),
    ("NG-002", "Banshi Gad", "Fracture", 30.1432, 78.3395, 2115, 0.28, 6.8, "active"),
    ("NG-003", "Kaphal Pani", "Depression", 30.1088, 78.3654, 1670, 0.63, 7.3, "active"),
    ("NG-004", "Aama Naula", "Contact", 30.1630, 78.2891, 2260, 0.19, 7.0, "seasonal"),
    ("NG-005", "Buransh Source", "Hillslope", 30.0902, 78.3258, 1535, 0.51, 7.2, "active"),
    ("NG-006", "Kwarik Khal", "Fracture", 30.1774, 78.3580, 2380, 0.11, 6.9, "monitoring"),
    ("NG-007", "Simal Srot", "Depression", 30.1351, 78.2750, 1980, 0.34, 7.4, "active"),
    ("NG-008", "Gwar Gaad", "Contact", 30.0761, 78.3792, 1450, 0.23, 6.7, "active"),
]
ZONES = [
    ("RZ-01", 91, "Very high", 94, "sv-2.4"), ("RZ-02", 86, "Very high", 91, "sv-2.4"),
    ("RZ-03", 78, "High", 88, "sv-2.4"), ("RZ-04", 73, "High", 85, "sv-2.4"),
    ("RZ-05", 67, "Moderate", 82, "sv-2.4"), ("RZ-06", 61, "Moderate", 79, "sv-2.4"),
    ("RZ-07", 54, "Moderate", 76, "sv-2.4"), ("RZ-08", 42, "Low", 71, "sv-2.4"),
]


def main():
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for code, name, kind, lat, lon, elev, flow, ph, status in SPRINGS:
            if not db.query(Spring).filter_by(spring_code=code).first():
                spring = Spring(spring_code=code, name=name, spring_type=kind, latitude=lat, longitude=lon, elevation=elev, discharge_rate=flow, water_quality_ph=ph, status=status, geom=WKTElement(f"POINT({lon} {lat})", srid=4326))
                db.add(spring); db.flush()
                db.add(FieldObservation(spring_id=spring.id, observer="Van Panchayat team", discharge=flow, water_level=1.2 + flow, vegetation_condition="Healthy", nearby_land_use="Mixed oak forest", validation_status="verified", geom=WKTElement(f"POINT({lon} {lat})", srid=4326)))
        for code, score, klass, confidence, version in ZONES:
            if not db.query(RechargeZone).filter_by(zone_code=code).first():
                db.add(RechargeZone(zone_code=code, suitability_score=score, suitability_class=klass, confidence=confidence, model_version=version))
        db.commit()
    print("SpringVyra database initialized with representative field records.")


if __name__ == "__main__":
    main()
