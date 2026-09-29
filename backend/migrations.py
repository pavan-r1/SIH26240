"""Small forward-only schema additions for databases created by early prototypes."""
from sqlalchemy import text
from sqlalchemy.engine import Engine


def upgrade_legacy_schema(engine: Engine) -> None:
    statements = (
        "ALTER TABLE springs ADD COLUMN IF NOT EXISTS catchment VARCHAR(120)",
        "ALTER TABLE springs ADD COLUMN IF NOT EXISTS description TEXT",
        "ALTER TABLE springs ADD COLUMN IF NOT EXISTS data_status VARCHAR(20) DEFAULT 'UNVERIFIED'",
        "ALTER TABLE springs ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE springs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP",
        "ALTER TABLE recharge_zones ADD COLUMN IF NOT EXISTS analysis_date TIMESTAMPTZ",
        "ALTER TABLE recharge_zones ADD COLUMN IF NOT EXISTS data_quality VARCHAR(32)",
        "ALTER TABLE recharge_zones ADD COLUMN IF NOT EXISTS data_status VARCHAR(20) DEFAULT 'UNVERIFIED'",
        "ALTER TABLE recharge_zones ADD COLUMN IF NOT EXISTS geom geometry(MultiPolygon, 4326)",
        "ALTER TABLE recharge_zones ALTER COLUMN confidence DROP NOT NULL",
        "ALTER TABLE field_observations ADD COLUMN IF NOT EXISTS notes TEXT",
        "ALTER TABLE field_observations ADD COLUMN IF NOT EXISTS photo_url VARCHAR(500)",
        "ALTER TABLE field_observations ADD COLUMN IF NOT EXISTS data_status VARCHAR(20) DEFAULT 'FIELD'",
        "UPDATE springs SET data_status='DEMO', description='Synthetic development record; not a verified real spring.' WHERE spring_code LIKE 'NG-00%' AND data_status='UNVERIFIED'",
        "UPDATE field_observations SET data_status='DEMO', validation_status='NEEDS_REVIEW', notes='Synthetic development record; not a field observation.' WHERE observer='Van Panchayat team' AND validation_status='verified'",
        "UPDATE recharge_zones SET data_status='DEMO', confidence=NULL, data_quality='SYNTHETIC' WHERE zone_code LIKE 'RZ-0%' AND model_version='sv-2.4'",
    )
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
