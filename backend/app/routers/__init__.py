"""
API routers package initialization.
Imports and exposes modular route handlers for integration into the FastAPI application.
"""

from . import users
from .users import router as users_router
from . import auth
