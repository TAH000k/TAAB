from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import os

from app.database import Base, engine
import app.models

from app.routers import auth, users
from app.routers import items
from app.routers import borrows
from app.routers import groups

app = FastAPI(
    title="TAAB API",
    version="0.1.0"
)

os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="uploads"), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(borrows.router)
app.include_router(groups.router)

@app.get("/")
def root():
    return {
        "name": "TAAB API",
        "version": "0.1.0",
        "status": "online"
    }
