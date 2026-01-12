from pydantic import BaseModel, Field
from typing import Optional, List

class AddCarRequest(BaseModel):
    model: str = Field(min_length=1)
    year: int = Field(ge=1886)  # The first  car was invented in 1886

class UpdateCarRequest(BaseModel):
    model: Optional[str] = Field(default=None, min_length=1)
    year: Optional[int] = Field(default=None, ge=1886)
    status: Optional[str] = Field(default=None, min_length=1)

class CreateRentalRequest(BaseModel):
    car_id: int
    customer_name: str = Field(min_length=1)