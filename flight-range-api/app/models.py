from sqlalchemy import Column, Float, Integer, String

from .database import Base


class Aircraft(Base):
    """
    Performance data needed to evaluate cruise range with the Breguet
    range equation. Defaults are representative of a regional turboprop
    (ATR 72-600-class aircraft).
    """

    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # Weights, kg
    empty_weight_kg = Column(Float, nullable=False)      # W0 (OEW + payload, excl. fuel)
    max_fuel_kg = Column(Float, nullable=False)          # WF (usable fuel)

    # Cruise performance
    cruise_mach = Column(Float, nullable=False)
    speed_of_sound_ms = Column(Float, nullable=False)    # a, at cruise altitude
    lift_to_drag = Column(Float, nullable=False)         # CL/CD
    tsfc_per_s = Column(Float, nullable=False)           # CT, weight-based, 1/s


class Airport(Base):
    __tablename__ = "airports"

    id = Column(Integer, primary_key=True, index=True)
    icao = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
