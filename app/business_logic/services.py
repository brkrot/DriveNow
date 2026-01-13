from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.data_access.orm_models import Car
from app.data_access import operations

def create_car(db: Session, model: str, year: int) -> Car:
    return operations.create_car(db=db, model=model, year=year)

def update_car(
    db: Session,
    car_id: int,
    model: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
) -> Car:
    car = operations.get_car_by_id(db=db, car_id=car_id)
    if car is None:
        raise ValueError(f"Car with id {car_id} does not exist.")
    return operations.update_car(db=db, car=car, model=model, year=year, status=status)

def register_rental(db: Session, car_id: int, customer_name: str):
    car = operations.get_car_by_id(db=db, car_id=car_id)
    if car is None:
        raise ValueError("car_not_found")

    if car.status != "available":
        raise ValueError("car_not_available")

    ongoing = operations.get_ongoing_rental_for_car(db=db, car_id=car_id)
    if ongoing is not None:
        raise ValueError("active_rental_exists")

    rental = operations.create_rental(
        db=db,
        car_id=car_id,
        customer_name=customer_name,
        start_date=datetime.utcnow(),
    )

    operations.update_car(db=db, car=car, status="in_use")
    return rental


def end_rental(db: Session, rental_id: int):
    rental = operations.get_rental_by_id(db=db, rental_id=rental_id)
    if rental is None:
        raise ValueError("rental_not_found")

    if rental.end_date is not None:
        raise ValueError("rental_already_ended")

    rental = operations.end_rental(db=db, rental=rental, end_date=datetime.utcnow())

    car = operations.get_car_by_id(db=db, car_id=rental.car_id)
    if car is None:
        raise ValueError("car_not_found")

    operations.update_car(db=db, car=car, status="available")
    return rental