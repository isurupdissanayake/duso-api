from typing import Annotated, AsyncGenerator
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from .core.database import get_database
from .config import Settings, get_settings
from .core.security import get_current_user
from .repositories import UserRepository, TopicRepository
from .services import UserService, AuthService, TopicService
from .context.app_context import AppContext

# Database dependency
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Get database connection
    
    Returns:
        AsyncGenerator[AsyncIOMotorDatabase, None]: Database connection
    """
    db = await get_database()
    try:
        yield db
    finally:
        # Connection is managed by the database module
        pass

# Repository dependencies
async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    """
    Get UserRepository instance
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
        
    Returns:
        UserRepository: UserRepository instance
    """
    return UserRepository(db)

async def get_topic_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> TopicRepository:
    """
    Get TopicRepository instance
    
    Args:
        db (AsyncIOMotorDatabase): Database connection
        
    Returns:
        TopicRepository: TopicRepository instance
    """
    return TopicRepository(db)

# Service dependencies
async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    """
    Get UserService instance
    
    Args:
        user_repository (UserRepository): UserRepository instance
        
    Returns:
        UserService: UserService instance
    """
    return UserService(user_repository)

async def get_topic_service(
    topic_repository: TopicRepository = Depends(get_topic_repository)
) -> TopicService:
    """
    Get TopicService instance
    
    Args:
        topic_repository (TopicRepository): TopicRepository instance
        
    Returns:
        TopicService: TopicService instance
    """
    return TopicService(topic_repository)

async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository)
) -> AuthService:
    """
    Get AuthService instance
    
    Args:
        user_repository (UserRepository): UserRepository instance
        
    Returns:
        AuthService: AuthService instance
    """
    return AuthService(user_repository)

async def get_app_context(
    user: dict = Depends(get_current_user),
    settings: Settings = Depends(get_settings)
) -> AsyncGenerator[AppContext, None]:
    """
    Get application context for the current request.
    This includes the current user and application settings.
    
    Args:
        user (dict): Current authenticated user from get_current_user
        settings (Settings): Application settings from get_settings
        
    Returns:
        AppContext: Application context instance
    """
    context = AppContext(
        user=user,
        settings=settings
    )
    yield context 