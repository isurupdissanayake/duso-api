from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository class that all repositories should inherit from"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get(self, id: str) -> T:
        """Get an entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, id: str, entity: T) -> T:
        """Update an entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Delete an entity"""
        pass 