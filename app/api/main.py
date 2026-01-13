from typing import Optional

from fastapi import FastAPI
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from fastapi import Response
import logging


from app.metrics.metrics import metrics_response, ACTIVE_CARS
from app.data_access.database import get_db
from app.api.schemas import AddCarRequest, UpdateCarRequest, CarResponse, RentalResponse, CreateRentalRequest
from app.business_logic import services
from app.data_access.database import engine
from app.data_access.orm_models import Base
from app.logging.logging import setup_logging

logger = logging.getLogger(__name__)

app = FastAPI(title="DriveNow Car Rental Service API")

@app.on_event("startup")
def on_startup():
    # Create database tables

    Base.metadata.create_all(bind=engine)
    setup_logging()
    logger.info("Starting up")

# route for adding new car
@app.post("/add_car", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def add_car(payload: AddCarRequest, db: Session = Depends(get_db)):
    logger.info('POST /add_car')
    car  = services.create_car(db=db, model=payload.model, year=payload.year)
    return car

@app.patch("/update_car/{car_id}", response_model=CarResponse)
def update_car(car_id: int, payload: UpdateCarRequest, db: Session = Depends(get_db)):
    logger.info(f'PATCH /update_car/{car_id}')
    try:
        car = services.update_car(
            db=db,
            car_id=car_id,
            model=payload.model,
            year=payload.year,
            status=payload.status,
        )
        return car
    except ValueError as e:
        if str(e) == "car_not_found":
            raise HTTPException(status_code=404, detail="Car not found")
        raise HTTPException(status_code=400, detail="Bad request")


@app.get("/get_cars", response_model=list[CarResponse])
def get_cars(status: Optional[str] = None, db: Session = Depends(get_db)):
    logger.info(f'GET /get_cars')
    cars = services.list_cars(db=db, status=status)
    return cars

@app.post("/register_rental", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def register_rental(payload: CreateRentalRequest, db: Session = Depends(get_db)):
    logger.info(f"POST /register_rental")
    try:
        rental = services.register_rental(
            db=db,
            car_id=payload.car_id,
            customer_name=payload.customer_name,
        )
        return rental
    except ValueError as e:
        error_map = {
            "car_not_found": (404, "Car not found"),
            "car_not_available": (400, "Car is not available for rental"),
            "active_rental_exists": (400, "An active rental already exists for this car"),
        }
        if str(e) in error_map:
            status_code, detail = error_map[str(e)]
            raise HTTPException(status_code=status_code, detail=detail)
        raise HTTPException(status_code=400, detail="Bad request")


@app.post("/end_rental/{rental_id}", response_model=RentalResponse)
def end_rental(rental_id: int, db: Session = Depends(get_db)):
    logger.info(f'POST /end_rental/{rental_id}')
    try:
        rental = services.end_rental(db=db, rental_id=rental_id)
        return rental
    except ValueError as e:
        error_map = {
            "rental_not_found": (404, "Rental not found"),
            "rental_already_ended": (400, "Rental has already been ended"),
            "car_not_found": (404, "Associated car not found"),
        }
        if str(e) in error_map:
            status_code, detail = error_map[str(e)]
            raise HTTPException(status_code=status_code, detail=detail)
        raise HTTPException(status_code=400, detail="Bad request")


