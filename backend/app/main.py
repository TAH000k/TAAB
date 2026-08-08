"""
Main application entry point for the TAAB API.
Configures the FastAPI application, mounts static file directories,
initializes database tables, and registers API routers.
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Database configuration and models
from app.database import Base, engine
import app.models

# API routers
from app.routers import auth, users
from app.routers import items
from app.routers import borrows
from app.routers import groups

# Initialize FastAPI instance
app = FastAPI(
    title="TAAB API",
    version="0.1.0"
)

# Ensure local upload directory exists and mount it for static serving
os.makedirs("uploads", exist_ok=True)

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/static", StaticFiles(directory="defaults"), name="static")

# Create all database tables defined in SQLAlchemy models
Base.metadata.create_all(bind=engine)

# Register application routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(items.router)
app.include_router(borrows.router)
app.include_router(groups.router)


@app.get("/")
def root():
    """
    Root endpoint serving basic API metadata and status.
    """
    return {
        "name": "TAAB API",
        "version": "0.1.0",
        "status": "online"
    }
