from typing import Dict, Type, TypeVar, Any, Optional, Callable
from fastapi import FastAPI
from .base_repository import BaseRepository
from .base_service import BaseService
from .base_controller import BaseController

T = TypeVar('T')

class Container:
    """Dependency injection container"""
    
    def __init__(self):
        self._repositories: Dict[Type[BaseRepository], BaseRepository] = {}
        self._services: Dict[Type[BaseService], BaseService] = {}
        self._controllers: Dict[Type[BaseController], BaseController] = {}
        self._singletons: Dict[Type[Any], Any] = {}
        self._dependencies: Dict[Callable, Callable] = {}
    
    def register_singleton(self, cls: Type[T], instance: T) -> None:
        """Register a singleton instance"""
        self._singletons[cls] = instance
    
    def get_singleton(self, cls: Type[T]) -> Optional[T]:
        """Get a singleton instance"""
        return self._singletons.get(cls)
    
    def register_repository(self, cls: Type[BaseRepository], instance: BaseRepository) -> None:
        """Register a repository instance"""
        self._repositories[cls] = instance
    
    def get_repository(self, cls: Type[BaseRepository]) -> Optional[BaseRepository]:
        """Get a repository instance"""
        return self._repositories.get(cls)
    
    def register_service(self, cls: Type[BaseService], instance: BaseService) -> None:
        """Register a service instance"""
        self._services[cls] = instance
    
    def get_service(self, cls: Type[BaseService]) -> Optional[BaseService]:
        """Get a service instance"""
        return self._services.get(cls)
    
    def register_controller(self, cls: Type[BaseController], instance: BaseController) -> None:
        """Register a controller instance"""
        self._controllers[cls] = instance
    
    def get_controller(self, cls: Type[BaseController]) -> Optional[BaseController]:
        """Get a controller instance"""
        return self._controllers.get(cls)
    
    def register_dependency(self, dependency_func: Callable, implementation: Callable) -> None:
        """Register a FastAPI dependency override"""
        self._dependencies[dependency_func] = implementation
    
    def wire_dependencies(self, app: FastAPI) -> None:
        """Wire up all dependencies and register routes with FastAPI app"""
        # Register dependency overrides
        for dependency_func, implementation in self._dependencies.items():
            app.dependency_overrides[dependency_func] = implementation
        for controller in self._controllers.values():
            app.include_router(controller.router) 