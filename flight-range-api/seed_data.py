"""
Populates the database with a couple of example aircraft and airports so
the API has something to query out of the box.

Run with: python seed_data.py
"""
from app import crud, schemas
from app.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

AIRCRAFT = [
    schemas.AircraftCreate(
        name="ATR 72-600",
        empty_weight_kg=13450.0,
        max_fuel_kg=4626.0,
        cruise_mach=0.443,
        speed_of_sound_ms=309.6,
        lift_to_drag=16.5,
        tsfc_per_s=1.25e-4,
    ),
    schemas.AircraftCreate(
        name="Airbus A320neo",
        empty_weight_kg=44300.0,
        max_fuel_kg=18000.0,
        cruise_mach=0.78,
        speed_of_sound_ms=295.0,
        lift_to_drag=18.0,
        tsfc_per_s=1.0e-4,
    ),
]

AIRPORTS = [
    schemas.AirportCreate(icao="LPPT", name="Lisbon Humberto Delgado", latitude=38.7813, longitude=-9.1359),
    schemas.AirportCreate(icao="LPPD", name="Ponta Delgada Jo\u00e3o Paulo II", latitude=37.7412, longitude=-25.6979),
    schemas.AirportCreate(icao="EGLL", name="London Heathrow", latitude=51.4700, longitude=-0.4543),
    schemas.AirportCreate(icao="LEMD", name="Madrid Barajas", latitude=40.4936, longitude=-3.5668),
]


def main():
    db = SessionLocal()
    try:
        for a in AIRCRAFT:
            if not crud.get_aircraft_by_name(db, a.name):
                crud.create_aircraft(db, a)
        for ap in AIRPORTS:
            if not crud.get_airport_by_icao(db, ap.icao):
                crud.create_airport(db, ap)
        print(f"Seeded {len(AIRCRAFT)} aircraft and {len(AIRPORTS)} airports.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
