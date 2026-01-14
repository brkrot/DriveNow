from pydantic import BaseModel, Field
from typing import Optional

class AddCarRequest(BaseModel):
    model: str = Field(min_length=1)
    year: int = Field(ge=1886)  # The first  car was invented in 1886

class UpdateCarRequest(BaseModel):
    model: Optional[str] = Field(default=None, min_length=1)
    year: Optional[int] = Field(default=None, ge=1886)
    # todo: define allowed status values using Enum (CarStatus)
    status: Optional[str] = Field(default=None, min_length=1)

class CreateRentalRequest(BaseModel):
    car_id: int
    customer_name: str = Field(min_length=1)

#--------------
from datetime import datetime
from typing import Optional


class CarResponse(BaseModel):
    id: int
    model: str
    year: int
    status: str

    class Config:
        from_attributes = True


class RentalResponse(BaseModel):
    id: int
    car_id: int
    customer_name: str
    start_date: datetime
    end_date: Optional[datetime]

    class Config:
        from_attributes = True
