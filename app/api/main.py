from typing import Optional

from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette import status
from fastapi import Response
import logging


from app.metrics.metrics import metrics_response, ACTIVE_CARS, ONGOING_RENTALS
from app.api.schemas import AddCarRequest, UpdateCarRequest, CarResponse, RentalResponse, CreateRentalRequest
from app.business_logic import services
from app.data_access.database import engine
from app.data_access.orm_models import Base
from app.data_access.database import get_db
from app.data_access import operations
from app.logging.logging import setup_logging
from app.business_logic.exceptions import CarNotFound, BusinessError, CarNotAvailable, ActiveRentalExists, RentalNotFound, RentalAlreadyEnded

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

    except CarNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.error_code.value)

    except BusinessError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_code.value)


@app.get("/get_cars", response_model=list[CarResponse])
def get_cars(status: Optional[str] = None, db: Session = Depends(get_db)):
    logger.info(f'GET /get_cars with status={status}')
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

    except CarNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.error_code.value)

    except (CarNotAvailable, ActiveRentalExists) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.error_code.value)

    except BusinessError as e:
        # validation / other business-rule errors
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_code.value)





@app.post("/end_rental/{rental_id}", response_model=RentalResponse)
def end_rental(rental_id: int, db: Session = Depends(get_db)):
    logger.info(f'POST /end_rental/{rental_id}')
    try:
        rental = services.end_rental(db=db, rental_id=rental_id)
        return rental
    except RentalNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.error_code.value)

    except RentalAlreadyEnded as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.error_code.value)

    except CarNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.error_code.value)

    except BusinessError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_code.value)

@app.get("/metrics")
def metrics(db=Depends(get_db)):
    # Recalculate metrics from DB (source of truth)
    ACTIVE_CARS.set(operations.count_cars(db))
    ONGOING_RENTALS.set(operations.count_ongoing_rentals(db))

    data, content_type = metrics_response()
    return Response(content=data, media_type=content_type)