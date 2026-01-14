from typing import Optional, List
from sqlalchemy.orm import Session

from app.data_access.orm_models import Car, CarStatus


def create_car(db: Session, model: str, year: int, status: str = CarStatus.AVAILABLE.value) -> Car:
    car = Car(model=model, year=year, status=status)
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


def get_car_by_id(db: Session, car_id: int) -> Optional[Car]:
    return db.query(Car).filter(Car.id == car_id).first()


def list_cars(db: Session, status: Optional[str] = None) -> List[Car]:
    query = db.query(Car)
    if status is not None:
        query = query.filter(Car.status == status)
    return query.all()


def update_car(
    db: Session,
    car: Car,
    model: Optional[str] = None,
    year: Optional[int] = None,
    status: Optional[str] = None,
) -> Car:
    if model is not None:
        car.model = model
    if year is not None:
        car.year = year
    if status is not None:
        car.status = status

    db.add(car)
    db.commit()
    db.refresh(car)
    return car

# todo - split to different files
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.data_access.orm_models import Rental


def create_rental(
    db: Session,
    car_id: int,
    customer_name: str,
    start_date: datetime,
) -> Rental:
    rental = Rental(
        car_id=car_id,
        customer_name=customer_name,
        start_date=start_date,
        end_date=None,
    )
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


def get_rental_by_id(db: Session, rental_id: int) -> Optional[Rental]:
    return db.query(Rental).filter(Rental.id == rental_id).first()


def get_ongoing_rental_for_car(db: Session, car_id: int) -> Optional[Rental]:
    return (
        db.query(Rental)
        .filter(Rental.car_id == car_id, Rental.end_date.is_(None))
        .first()
    )


def end_rental(db: Session, rental: Rental, end_date: datetime) -> Rental:
    rental.end_date = end_date
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


# todo - split to different files
from app.data_access.orm_models import Car, Rental
def count_cars(db: Session) -> int:
    """
    Total number of cars in the system
    """
    return db.query(Car).count()


def count_ongoing_rentals(db: Session) -> int:
    """
    Rentals with no end date
    """
    return (
        db.query(Rental)
        .filter(Rental.end_date.is_(None))
        .count()
    )