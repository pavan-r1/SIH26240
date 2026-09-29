from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
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
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True))
    observations: Mapped[list["FieldObservation"]] = relationship(back_populates="spring", cascade="all, delete-orphan")


class RechargeZone(Base):
    __tablename__ = "recharge_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    suitability_score: Mapped[float] = mapped_column(Float)
    suitability_class: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(64))


class FieldObservation(Base):
    __tablename__ = "field_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    spring_id: Mapped[int] = mapped_column(ForeignKey("springs.id", ondelete="CASCADE"), index=True)
    observer: Mapped[str] = mapped_column(String(120))
    discharge: Mapped[float] = mapped_column(Float)
    water_level: Mapped[float] = mapped_column(Float)
    vegetation_condition: Mapped[str] = mapped_column(String(80))
    nearby_land_use: Mapped[str] = mapped_column(String(100))
    validation_status: Mapped[str] = mapped_column(String(32), default="pending")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=True))
    spring: Mapped[Spring] = relationship(back_populates="observations")
