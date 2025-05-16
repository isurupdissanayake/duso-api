from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..models.user import User, UserCreate
from ..services.auth_service import AuthService
from ..core.exceptions import AuthenticationError, ValidationError, DatabaseError
from ..dependencies import get_auth_service, get_app_context, get_app_config_context
from ..context.app_context import AppContext
from ..context.app_context import AppContext

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    ctx: AppContext = Depends(get_app_config_context)
) -> User:
    """
    Register a new user
    
    Args:
        user_data (UserCreate): User registration data
        auth_service (AuthService): Authentication service
        ctx (AppContext): Application context
        
    Returns:
        User: Created user information
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        return await auth_service.register_user(user_data, ctx)
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

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    ctx: AppContext = Depends(get_app_config_context),
    response: Response = None
) -> dict:
    """
    Authenticate user and return access token
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login form data
        auth_service (AuthService): Authentication service
        ctx (AppContext): Application context
        response (Response): FastAPI response object
        
    Returns:
        dict: Access token information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        access_token = await auth_service.authenticate_user(
            form_data.username,
            form_data.password,
            ctx
        )
        
        # Set access token cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=ctx.settings["COOKIE_SECURE"],
            samesite=ctx.settings["COOKIE_SAMESITE"],
            max_age=ctx.settings["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/logout")
async def logout(
    response: Response,
    ctx: AppContext = Depends(get_app_context)
) -> dict:
    """
    Logout user by clearing access token cookie
    
    Args:
        response (Response): FastAPI response object
        ctx (AppContext): Application context
        
    Returns:
        dict: Success message
    """
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=ctx.settings["COOKIE_SECURE"],
        samesite=ctx.settings["COOKIE_SAMESITE"]
    )
    return {"message": "Successfully logged out"}

@router.post("/refresh")
async def refresh_token(
    auth_service: AuthService = Depends(get_auth_service),
    ctx: AppContext = Depends(get_app_context),
    response: Response = None
) -> dict:
    """
    Refresh access token
    
    Args:
        auth_service (AuthService): Authentication service
        ctx (AppContext): Application context
        response (Response): FastAPI response object
        
    Returns:
        dict: New access token information
        
    Raises:
        HTTPException: If token refresh fails
    """
    try:
        # Get user ID from current token
        user_id = ctx.user["id"]
        
        # Generate new token
        access_token = await auth_service.refresh_token(user_id, ctx)
        
        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=ctx.settings["COOKIE_SECURE"],
            samesite=ctx.settings["COOKIE_SAMESITE"],
            max_age=ctx.settings["ACCESS_TOKEN_EXPIRE_MINUTES"] * 60
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 