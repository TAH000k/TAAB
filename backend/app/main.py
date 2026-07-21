from fastapi import FastAPI

from app.database import Base, engine
import app.models

app = FastAPI(
    title="TAAB API",
    version="0.1.0"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {
        "name": "TAAB API",
        "version": "0.1.0",
        "status": "online"
    }
