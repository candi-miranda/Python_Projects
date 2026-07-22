from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import Base, engine, get_db
from .geo import breguet_range_km, great_circle_distance_km

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Flight Range API",
    description=(
        "Given an aircraft's performance data and two airports, tells you "
        "whether the aircraft can fly that route non-stop, using the "
        "Breguet range equation and great-circle distance."
    ),
    version="1.0.0",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# --- Aircraft ---------------------------------------------------------


@app.post("/aircraft", response_model=schemas.AircraftOut, status_code=201)
def create_aircraft(aircraft: schemas.AircraftCreate, db: Session = Depends(get_db)):
    if crud.get_aircraft_by_name(db, aircraft.name):
        raise HTTPException(status_code=409, detail="Aircraft with this name already exists")
    return crud.create_aircraft(db, aircraft)


@app.get("/aircraft", response_model=list[schemas.AircraftOut])
def read_all_aircraft(db: Session = Depends(get_db)):
    return crud.list_aircraft(db)


@app.get("/aircraft/{aircraft_id}", response_model=schemas.AircraftOut)
def read_aircraft(aircraft_id: int, db: Session = Depends(get_db)):
    db_obj = crud.get_aircraft(db, aircraft_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Aircraft not found")
    return db_obj


# --- Airports -----------------------------------------------------------


@app.post("/airports", response_model=schemas.AirportOut, status_code=201)
def create_airport(airport: schemas.AirportCreate, db: Session = Depends(get_db)):
    if crud.get_airport_by_icao(db, airport.icao):
        raise HTTPException(status_code=409, detail="Airport with this ICAO code already exists")
    return crud.create_airport(db, airport)


@app.get("/airports", response_model=list[schemas.AirportOut])
def read_all_airports(db: Session = Depends(get_db)):
    return crud.list_airports(db)


# --- Route feasibility ---------------------------------------------------


@app.get("/route/{origin_icao}/{destination_icao}/feasibility", response_model=schemas.FeasibilityOut)
def route_feasibility(
    origin_icao: str,
    destination_icao: str,
    aircraft_name: str,
    db: Session = Depends(get_db),
):
    origin = crud.get_airport_by_icao(db, origin_icao)
    destination = crud.get_airport_by_icao(db, destination_icao)
    aircraft = crud.get_aircraft_by_name(db, aircraft_name)

    if origin is None:
        raise HTTPException(status_code=404, detail=f"Unknown origin airport: {origin_icao}")
    if destination is None:
        raise HTTPException(status_code=404, detail=f"Unknown destination airport: {destination_icao}")
    if aircraft is None:
        raise HTTPException(status_code=404, detail=f"Unknown aircraft: {aircraft_name}")

    distance_km = great_circle_distance_km(
        origin.latitude, origin.longitude, destination.latitude, destination.longitude
    )
    max_range_km = breguet_range_km(
        cruise_mach=aircraft.cruise_mach,
        speed_of_sound_ms=aircraft.speed_of_sound_ms,
        lift_to_drag=aircraft.lift_to_drag,
        tsfc_per_s=aircraft.tsfc_per_s,
        empty_weight_kg=aircraft.empty_weight_kg,
        fuel_weight_kg=aircraft.max_fuel_kg,
    )

    return schemas.FeasibilityOut(
        origin=origin.icao,
        destination=destination.icao,
        aircraft=aircraft.name,
        great_circle_distance_km=round(distance_km, 1),
        max_range_km=round(max_range_km, 1),
        feasible=distance_km <= max_range_km,
        margin_km=round(max_range_km - distance_km, 1),
    )
