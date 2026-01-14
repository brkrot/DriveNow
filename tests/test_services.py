import pytest
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.business_logic import services
from app.business_logic.exceptions import (
    ErrorCode,
    CarNotFound,
    CarNotAvailable,
    ActiveRentalExists,
)
from app.data_access.orm_models import Base, CarStatus


# ---------------------------
# DB context (per test)
# ---------------------------

@contextmanager
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


# ---------------------------
# Tests
# ---------------------------

def test_create_car():
    with db_session() as db:
        car = services.create_car(db, "Toyota", 2020)
        assert car.id is not None


def test_update_car():
    with db_session() as db:
        car = services.create_car(db, "Honda", 2019)
        updated_car = services.update_car(
            db,
            car.id,
            model="Honda Civic",
            year=2021,
            status=CarStatus.RENTED.value,
        )
        assert updated_car.model == "Honda Civic"
        assert updated_car.year == 2021
        assert updated_car.status == CarStatus.RENTED.value


def test_list_cars():
    with db_session() as db:
        services.create_car(db, "Ford", 2018)
        services.create_car(db, "Chevrolet", 2021)
        cars = services.list_cars(db)
        assert len(cars) == 2


def test_register_rental():
    with db_session() as db:
        car = services.create_car(db, "Nissan", 2022)
        rental = services.register_rental(db, car.id, "John Doe")
        assert rental is not None
        assert rental.id is not None
        assert rental.car_id == car.id
        assert rental.end_date is None


def test_register_rental_car_not_found():
    with db_session() as db:
        with pytest.raises(CarNotFound) as e:
            services.register_rental(db, 999, "Jane Doe")
        assert e.value.error_code == ErrorCode.CAR_NOT_FOUND


def test_register_rental_car_not_available():
    with db_session() as db:
        car = services.create_car(db, "BMW", 2021)
        services.update_car(db, car.id, status=CarStatus.RENTED.value)

        with pytest.raises(CarNotAvailable) as e:
            services.register_rental(db, car.id, "Alice")
        assert e.value.error_code == ErrorCode.CAR_NOT_AVAILABLE

def test_register_rental_active_rental_exists():
    with db_session() as db:
        car = services.create_car(db, "Audi", 2020)
        services.register_rental(db, car.id, "Bob")

        with pytest.raises((ActiveRentalExists, CarNotAvailable)) as e:
            services.register_rental(db, car.id, "Charlie")
        assert e.value.error_code in {
            ErrorCode.ACTIVE_RENTAL_EXISTS,
            ErrorCode.CAR_NOT_AVAILABLE,
        }


def test_end_rental_sets_end_date():
    with db_session() as db:
        car = services.create_car(db, "Kia", 2019)
        rental = services.register_rental(db, car.id, "David")
        assert rental.end_date is None

        ended = services.end_rental(db, rental.id)
        assert ended.end_date is not None
