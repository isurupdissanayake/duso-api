"""
Duso API Repositories Module
"""

from .user_repository import UserRepository
from .topic_repository import TopicRepository

__all__ = [
    'UserRepository',
    'TopicRepository',
] 