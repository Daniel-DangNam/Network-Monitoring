from app.api.v1.api_router import api_router as router
from app.api.v1.endpoints.auth import *
from app.api.v1.endpoints.traffic import *
from app.api.v1.endpoints.agent import *
from app.api.v1.endpoints.websocket import *

__all__ = ["router"]
