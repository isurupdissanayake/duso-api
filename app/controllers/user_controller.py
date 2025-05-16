from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ..models.user import User, UserCreate, UserUpdate
from ..services.user_service import UserService
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError
from ..dependencies import get_user_service, get_app_context
from ..context.app_context import AppContext

router = APIRouter(
    tags=["Users"],
    prefix="/users"
)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    ctx: AppContext = Depends(get_app_context),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Create a new user
    
    Args:
        user_data (UserCreate): User data including email, full name, and password
        ctx (AppContext): Application context
        
    Returns:
        User: Created user information
        
    Raises:
        HTTPException: If email is already registered
    """
    try:
        return await user_service.create_user(user_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    ctx: AppContext = Depends(get_app_context),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Get user by ID
    
    Args:
        user_id (str): User's unique identifier
        ctx (AppContext): Application context
        
    Returns:
        User: User information
        
    Raises:
        HTTPException: If user is not found
    """
    try:
        return await user_service.get_user(user_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    ctx: AppContext = Depends(get_app_context),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Update user information
    
    Args:
        user_id (str): User's unique identifier
        user_data (UserUpdate): Fields to update
        ctx (AppContext): Application context
        
    Returns:
        User: Updated user information
        
    Raises:
        HTTPException: If user is not found or update data is invalid
    """
    try:
        return await user_service.update_user(user_id, user_data)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{user_id}/verify-email", response_model=User)
async def verify_email(
    user_id: str,
    ctx: AppContext = Depends(get_app_context),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Mark user's email as verified
    
    Args:
        user_id (str): User's unique identifier
        ctx (AppContext): Application context
        
    Returns:
        User: Updated user information
        
    Raises:
        HTTPException: If user is not found
    """
    try:
        return await user_service.verify_email(user_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{user_id}/preferences", response_model=User)
async def update_preferences(
    user_id: str,
    preferences: dict,
    ctx: AppContext = Depends(get_app_context),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Update user preferences
    
    Args:
        user_id (str): User's unique identifier
        preferences (Dict): New preferences
        ctx (AppContext): Application context
        
    Returns:
        User: Updated user information
        
    Raises:
        HTTPException: If user is not found
    """
    try:
        return await user_service.update_preferences(user_id, preferences)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me", response_model=User)
async def get_current_user_info(
    ctx: AppContext = Depends(get_app_context)
) -> User:
    """
    Get current user information
    
    Args:
        ctx (AppContext): Application context containing current user
        
    Returns:
        User: Current user information
        
    Raises:
        HTTPException: If user is not found
    """
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return ctx.user 