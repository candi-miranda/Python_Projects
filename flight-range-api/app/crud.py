from sqlalchemy.orm import Session

from . import models, schemas


def create_aircraft(db: Session, aircraft: schemas.AircraftCreate) -> models.Aircraft:
    db_obj = models.Aircraft(**aircraft.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def list_aircraft(db: Session) -> list[models.Aircraft]:
    return db.query(models.Aircraft).all()


def get_aircraft(db: Session, aircraft_id: int) -> models.Aircraft | None:
    return db.query(models.Aircraft).filter(models.Aircraft.id == aircraft_id).first()


def get_aircraft_by_name(db: Session, name: str) -> models.Aircraft | None:
    return db.query(models.Aircraft).filter(models.Aircraft.name == name).first()


def create_airport(db: Session, airport: schemas.AirportCreate) -> models.Airport:
    data = airport.model_dump()
    data["icao"] = data["icao"].upper()
    db_obj = models.Airport(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def list_airports(db: Session) -> list[models.Airport]:
    return db.query(models.Airport).all()


def get_airport_by_icao(db: Session, icao: str) -> models.Airport | None:
    return db.query(models.Airport).filter(models.Airport.icao == icao.upper()).first()
