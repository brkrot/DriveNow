from typing import Optional
from datetime import datetime
import logging

from sqlalchemy.orm import Session

from app.data_access.orm_models import Car
from app.data_access import operations

logger = logging.getLogger(__name__)

def create_car(db: Session, model: str, year: int) -> Car:
    logger.info(f"create_car called with model={model} year={year}")
    car = operations.create_car(db=db, model=model, year=year)
    logger.info("create_car: created id=%s", car.id)
    return car


def update_car(
    db: Session,
    car_id: int,
    model: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
) -> Car:
    logger.info(f"update_car called for car_id={car_id} model={model} year={year} status={status}")
    car = operations.get_car_by_id(db=db, car_id=car_id)
    if car is None:
        logger.warning(f"update_car: car with id {car_id} does not exist")
        raise ValueError(f"Car with id {car_id} does not exist.")
    return operations.update_car(db=db, car=car, model=model, year=year, status=status)

def list_cars(db: Session, status: str | None = None):
    cars =  operations.list_cars(db=db, status=status)
    logger.info(f"list_cars: found {len(cars)} cars with status={status}")
    logger.debug(f'list_cars: cars={cars}')
    return cars

def register_rental(db: Session, car_id: int, customer_name: str):
    logger.info(f"register_rental called car_id={car_id} customer_name={customer_name}")
    car = operations.get_car_by_id(db=db, car_id=car_id)
    if car is None:
        logger.warning(f"register_rental: car_not_found id={car_id}")
        raise ValueError("car_not_found")

    if car.status != "available":
        logger.warning(f"register_rental: car_not_available id={car_id} status={car.status}")
        raise ValueError("car_not_available")

    ongoing = operations.get_ongoing_rental_for_car(db=db, car_id=car_id)
    if ongoing is not None:
        logger.warning(f"register_rental: active_rental_exists for car_id={car_id}")
        raise ValueError("active_rental_exists")

    rental = operations.create_rental(
        db=db,
        car_id=car_id,
        customer_name=customer_name,
        start_date=datetime.utcnow(),
    )

    operations.update_car(db=db, car=car, status="in_use")
    logger.info(f'register_rental: created rental_id={rental.id} for car_id={car_id}')

def end_rental(db: Session, rental_id: int):
    logger.info(f"end_rental called rental_id={rental_id}")
    rental = operations.get_rental_by_id(db=db, rental_id=rental_id)
    if rental is None:
        logger.warning(f"end_rental: rental_not_found id={rental_id}")
        raise ValueError("rental_not_found")

    if rental.end_date is not None:
        logger.warning(f"end_rental: rental_already_ended id={rental_id}")
        raise ValueError("rental_already_ended")

    rental = operations.end_rental(db=db, rental=rental, end_date=datetime.utcnow())

    car = operations.get_car_by_id(db=db, car_id=rental.car_id)
    if car is None:
        logger.warning(f"end_rental: car_not_found id={rental.car_id}")
        raise ValueError("car_not_found")

    operations.update_car(db=db, car=car, status="available")
    return rental
