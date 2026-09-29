from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Spring(Base):
    __tablename__ = "springs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    spring_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    spring_type: Mapped[str] = mapped_column(String(64))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation: Mapped[float] = mapped_column(Float)
    discharge_rate: Mapped[float] = mapped_column(Float, default=0)
    water_quality_ph: Mapped[float] = mapped_column(Float, default=7)
    status: Mapped[str] = mapped_column(String(32), default="active")
    catchment: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED", server_default="UNVERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True))
    observations: Mapped[list["FieldObservation"]] = relationship(back_populates="spring", cascade="all, delete-orphan")


class RechargeZone(Base):
    __tablename__ = "recharge_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    suitability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    suitability_class: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    analysis_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_quality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED", server_default="UNVERIFIED")
    geom = mapped_column(Geometry("MULTIPOLYGON", srid=4326, spatial_index=True), nullable=True)


class FieldObservation(Base):
    __tablename__ = "field_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    spring_id: Mapped[int] = mapped_column(ForeignKey("springs.id", ondelete="CASCADE"), index=True)
    observer: Mapped[str] = mapped_column(String(120))
    discharge: Mapped[float] = mapped_column(Float)
    water_level: Mapped[float] = mapped_column(Float)
    vegetation_condition: Mapped[str] = mapped_column(String(80))
    nearby_land_use: Mapped[str] = mapped_column(String(100))
    validation_status: Mapped[str] = mapped_column(String(32), default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="FIELD", server_default="FIELD")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True))
    spring: Mapped[Spring] = relationship(back_populates="observations")


class SpringMeasurement(Base):
    __tablename__ = "spring_measurements"
    __table_args__ = (CheckConstraint("discharge >= 0", name="ck_measurement_discharge_nonnegative"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    spring_id: Mapped[int] = mapped_column(ForeignKey("springs.id", ondelete="CASCADE"), index=True)
    discharge: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_level: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_quality_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    observer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="FIELD", server_default="FIELD")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('ADMIN','OFFICER','GIS_ANALYST','FIELD_WORKER','RESEARCHER','VIEWER')", name="ck_users_role"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(24), default="VIEWER")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("recharge_zones.id", ondelete="SET NULL"), nullable=True)
    prediction_class: Mapped[str] = mapped_column(String(32))
    suitability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    geom = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)


class InterventionSite(Base):
    __tablename__ = "intervention_sites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    intervention_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="CANDIDATE_FOR_FIELD_VALIDATION")
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True))


class RainfallRecord(Base):
    __tablename__ = "rainfall"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    rainfall_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(180), nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=True)


class WeatherRecord(Base):
    __tablename__ = "weather"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(180), nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=True)


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spring_id: Mapped[int] = mapped_column(ForeignKey("springs.id", ondelete="CASCADE"), index=True)
    sensor_code: Mapped[str] = mapped_column(String(64), index=True)
    metric: Mapped[str] = mapped_column(String(64))
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(24))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_name: Mapped[str] = mapped_column(String(120), index=True)
    source_name: Mapped[str] = mapped_column(String(180))
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    acquisition_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    spatial_resolution_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    license_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    processing_method: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_status: Mapped[str] = mapped_column(String(20), default="UNVERIFIED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
