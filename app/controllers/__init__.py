"""
Duso API Controllers Module
"""

from .auth_controller import router as auth_router
from .user_controller import router as user_router
from .topic_controller import router as topic_router

__all__ = [
    'auth_router',
    'user_router',
    'topic_router',
] 