from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SpringBase(BaseModel):
    spring_code: str
    name: str
    spring_type: str
    latitude: float
    longitude: float
    elevation: float
    discharge_rate: float = 0
    water_quality_ph: float = 7
    status: str = "active"


class SpringCreate(SpringBase): pass
class SpringRead(SpringBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ZoneBase(BaseModel):
    zone_code: str
    suitability_score: float
    suitability_class: str
    confidence: float
    model_version: str


class ZoneCreate(ZoneBase): pass
class ZoneRead(ZoneBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ObservationBase(BaseModel):
    spring_id: int
    observer: str
    discharge: float
    water_level: float
    vegetation_condition: str
    nearby_land_use: str
    validation_status: str = "pending"
    latitude: float
    longitude: float


class ObservationCreate(ObservationBase): pass
class ObservationRead(ObservationBase):
    id: int
    observed_at: datetime
    model_config = ConfigDict(from_attributes=True)
