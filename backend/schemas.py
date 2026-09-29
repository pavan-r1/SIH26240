from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

DataStatus = Literal["DEMO", "FIELD", "IMPORTED", "UNVERIFIED"]


class SpringBase(BaseModel):
    spring_code: str
    name: str
    spring_type: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    elevation: float
    discharge_rate: float = Field(default=0, ge=0)
    water_quality_ph: float = Field(default=7, ge=0, le=14)
    status: str = "active"
    catchment: str | None = None
    description: str | None = None
    data_status: DataStatus = "UNVERIFIED"


class SpringCreate(SpringBase): pass
class SpringRead(SpringBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ZoneBase(BaseModel):
    zone_code: str
    suitability_score: float | None = Field(default=None, ge=0, le=100)
    suitability_class: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    model_version: str | None = None
    analysis_date: datetime | None = None
    data_quality: str | None = None
    data_status: DataStatus = "UNVERIFIED"
    geometry: dict | None = None

    @field_validator("geometry")
    @classmethod
    def polygon_geometry_only(cls, value):
        if value is not None and value.get("type") not in {"Polygon", "MultiPolygon"}:
            raise ValueError("Recharge zone geometry must be a GeoJSON Polygon or MultiPolygon")
        return value


class ZoneCreate(ZoneBase): pass
class ZoneRead(ZoneBase):
    id: int
    geometry: dict | None = None
    model_config = ConfigDict(from_attributes=True)


class ObservationBase(BaseModel):
    spring_id: int
    observer: str
    discharge: float = Field(ge=0)
    water_level: float
    vegetation_condition: str
    nearby_land_use: str
    validation_status: Literal["PENDING"] = "PENDING"
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    notes: str | None = None
    photo_url: str | None = None
    data_status: DataStatus = "FIELD"


class ObservationCreate(ObservationBase):
    data_status: Literal["FIELD", "UNVERIFIED"] = "FIELD"
class ObservationRead(ObservationBase):
    id: int
    observed_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AssistantQuery(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    spring_id: int | None = None


class MeasurementCreate(BaseModel):
    spring_id: int
    discharge: float | None = Field(default=None, ge=0)
    water_level: float | None = None
    water_quality_ph: float | None = Field(default=None, ge=0, le=14)
    measured_at: datetime | None = None
    observer: str | None = None
    notes: str | None = None
    data_status: Literal["FIELD"] = "FIELD"

    @model_validator(mode="after")
    def require_measurement(self):
        if all(getattr(self, name) is None for name in ("discharge", "water_level", "water_quality_ph")):
            raise ValueError("At least one measurement value is required")
        return self


class InterventionCreate(BaseModel):
    site_code: str
    intervention_type: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    rationale: str | None = None
    risk_notes: str | None = None
    data_status: Literal["UNVERIFIED"] = "UNVERIFIED"


class DataSourceCreate(BaseModel):
    dataset_name: str = Field(min_length=1, max_length=120)
    source_name: str = Field(min_length=1, max_length=180)
    source_url: str | None = None
    acquisition_date: datetime | None = None
    spatial_resolution_m: float | None = Field(default=None, gt=0)
    license_name: str | None = None
    processing_method: str | None = None
    data_status: Literal["UNVERIFIED"] = "UNVERIFIED"
