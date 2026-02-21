from fastapi import FastAPI

from app.api.routes import router
from app.db.session import Base, engine
from app.models import entities  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auto Question Paper Generator API")
app.include_router(router)
