from abc import ABC
from typing import Generic, TypeVar
from fastapi import APIRouter
from .base_service import BaseService

T = TypeVar('T')
S = TypeVar('S', bound=BaseService)

class BaseController(ABC, Generic[T, S]):
    """Base controller class that all controllers should inherit from"""
    
    def __init__(self, service: S, router: APIRouter):
        self._service = service
        self._router = router
        self._register_routes()
    
    @property
    def service(self) -> S:
        return self._service
    
    @property
    def router(self) -> APIRouter:
        return self._router
    
    def _register_routes(self) -> None:
        """Register routes for the controller. Should be implemented by child classes."""
        pass 