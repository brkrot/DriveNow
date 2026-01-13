from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

from data_access.database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default='available')  # e.g., available, rented, maintenance

    rentals = relationship("Rental", back_populates="car")

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False, index=True)
    customer_name = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = Column(String, nullable=True)

    car = relationship("Car", back_populates="rentals")


