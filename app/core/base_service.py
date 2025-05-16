from abc import ABC
from typing import Generic, TypeVar
from .base_repository import BaseRepository

T = TypeVar('T')
R = TypeVar('R', bound=BaseRepository)

class BaseService(ABC, Generic[T, R]):
    """Base service class that all services should inherit from"""
    
    def __init__(self, repository: R):
        self._repository = repository
    
    @property
    def repository(self) -> R:
        return self._repository 