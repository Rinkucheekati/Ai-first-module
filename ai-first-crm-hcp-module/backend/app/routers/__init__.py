from app.routers.hcp import router as hcp_router
from app.routers.interaction import router as interaction_router
from app.routers.auth import router as auth_router

__all__ = ["hcp_router", "interaction_router", "auth_router"]
