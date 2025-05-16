from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..models.user import User, UserCreate
from ..repositories import UserRepository
from ..core.security import verify_password, get_password_hash, create_access_token
from ..core.exceptions import AuthenticationError, ValidationError, DatabaseError
from ..context.app_context import AppContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate, ctx: AppContext) -> User:
        """
        Register a new user
        
        Args:
            user_data (UserCreate): User registration data
            ctx (AppContext): Application context
            
        Returns:
            User: Created user
            
        Raises:
            ValidationError: If email is already registered
            DatabaseError: If database operation fails
        """
        try:
            # Check if email already exists
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ValidationError("Email already registered")

            # Create new user
            hashed_password = get_password_hash(user_data.password)
            user_dict = user_data.model_dump()
            user_dict["password"] = hashed_password
            user_dict["is_active"] = True
            user_dict["is_verified"] = False

            user = await self.user_repository.create(user_dict)
            return User(**user)

        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to register user: {str(e)}")

    async def authenticate_user(self, email: str, password: str, ctx: AppContext) -> str:
        """
        Authenticate a user and return access token
        
        Args:
            email (str): User email
            password (str): User password
            ctx (AppContext): Application context
            
        Returns:
            str: JWT access token
            
        Raises:
            AuthenticationError: If authentication fails
            DatabaseError: If database operation fails
        """
        try:
            user = await self.user_repository.get_by_email(email)
            if not user:
                raise AuthenticationError("Invalid email or password")

            if not verify_password(password, user["password"]):
                raise AuthenticationError("Invalid email or password")

            if not user.get("is_active", False):
                raise AuthenticationError("User account is inactive")

            # Create access token
            access_token_expires = timedelta(minutes=ctx.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user["_id"])},
                secret_key=ctx.settings.SECRET_KEY,
                expires_delta=access_token_expires
            )

            return access_token

        except AuthenticationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Authentication failed: {str(e)}")

    async def refresh_token(self, user_id: str, ctx: AppContext) -> str:
        """
        Refresh access token for a user
        
        Args:
            user_id (str): User ID
            ctx (AppContext): Application context
            
        Returns:
            str: New JWT access token
            
        Raises:
            AuthenticationError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")

            if not user.get("is_active", False):
                raise AuthenticationError("User account is inactive")

            # Create new access token
            access_token_expires = timedelta(minutes=ctx.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": str(user["_id"])},
                secret_key=ctx.settings.SECRET_KEY,
                expires_delta=access_token_expires
            )

            return access_token

        except AuthenticationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Token refresh failed: {str(e)}") 