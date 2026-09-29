# Database

The local database is PostgreSQL with PostGIS, named `spring_recharge` by default. SQLAlchemy uses the `pg8000` driver and an IPv4 loopback URL in `.env`. Spring and observation locations are EPSG:4326 points; recharge boundaries are optional EPSG:4326 multipolygons. Foreign keys connect observations to springs, and measurement records reference springs.

Run `python seed.py` to enable PostGIS, create the current schema, and apply small additive upgrades for the earlier prototype. Seeded records use `data_status=DEMO`; the old prototype's known sample rows are relabeled DEMO. Do not use a production database for this development seeder.

The current prototype does not yet include user, rainfall, weather, intervention-site, model-prediction, or sensor-reading tables. Add migrations for these before expanding those workflows. Back up any non-demo database before applying schema changes.
