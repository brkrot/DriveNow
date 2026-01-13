from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.business_logic import services
from app.data_access.orm_models import Base, CarStatus

def get_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return TestingSession()

def test_create_car():
    db = get_db()
    car = services.create_car(db, "Toyota", 2020)
    assert car.id is not None

def test_update_car():
    db = get_db()
    car = services.create_car(db, "Honda", 2019)
    updated_car = services.update_car(db, car.id, model="Honda Civic", year=2021, status=CarStatus.RENTED.value)
    assert updated_car.model == "Honda Civic"
    assert updated_car.year == 2021
    assert updated_car.status == CarStatus.RENTED.value

def test_list_cars():
    db = get_db()
    services.create_car(db, "Ford", 2018)
    services.create_car(db, "Chevrolet", 2021)
    cars = services.list_cars(db)
    assert len(cars) == 2

def test_register_rental():
    db = get_db()
    car = services.create_car(db, "Nissan", 2022)
    rental = services.register_rental(db, car.id, "John Doe")
    assert rental is not None

# todo - add those cases where things go wrong
# def test_register_rental_car_not_found():
#     db = get_db()
#     try:
#         services.register_rental(db, 999, "Jane Doe")
#     except ValueError as e:
#         assert str(e) == "car_not_found"
#
# def test_register_rental_car_not_available():
#     db = get_db()
#     car = services.create_car(db, "BMW", 2021)
#     services.update_car(db, car.id, status=CarStatus.RENTED.value)
#     try:
#         services.register_rental(db, car.id, "Alice")
#     except ValueError as e:
#         assert str(e) == "car_not_available"
#
# def test_register_rental_active_rental_exists():
#     db = get_db()
#     car = services.create_car(db, "Audi", 2020)
#     services.register_rental(db, car.id, "Bob")
#     try:
#         services.register_rental(db, car.id, "Charlie")
#     except ValueError as e:
#         assert str(e) == "active_rental_exists"

def test_end_rental():
    db = get_db()
    car = services.create_car(db, "Kia", 2019)
    rental = services.register_rental(db, car.id, "David")
    assert rental.end_date is None







