# app/routers/__init__.py
from .agents import router as agents_router
from .mock_community import router as mock_community_router

__all__ = ["agents_router", "mock_community_router"]

