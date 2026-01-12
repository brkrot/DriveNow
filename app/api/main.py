from fastapi import FastAPI


from app.data_access.database import engine
from app.data_access.orm_models import Base

app = FastAPI(title="DriveNow Car Rental Service API")

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
