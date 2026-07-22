from pydantic import BaseModel, ConfigDict, Field


class AircraftBase(BaseModel):
    name: str
    empty_weight_kg: float = Field(gt=0)
    max_fuel_kg: float = Field(gt=0)
    cruise_mach: float = Field(gt=0, lt=1.2)
    speed_of_sound_ms: float = Field(gt=0)
    lift_to_drag: float = Field(gt=0)
    tsfc_per_s: float = Field(gt=0)


class AircraftCreate(AircraftBase):
    pass


class AircraftOut(AircraftBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AirportBase(BaseModel):
    icao: str
    name: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AirportCreate(AirportBase):
    pass


class AirportOut(AirportBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FeasibilityOut(BaseModel):
    origin: str
    destination: str
    aircraft: str
    great_circle_distance_km: float
    max_range_km: float
    feasible: bool
    margin_km: float
