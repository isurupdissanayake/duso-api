from typing import Optional, Dict
from datetime import datetime
import logging
from ..models.user import User, UserCreate, UserInDB, UserUpdate
from ..repositories import UserRepository
from passlib.context import CryptContext
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user with proper validation and password hashing
        
        Args:
            user_data (UserCreate): User creation data
            
        Returns:
            User: Created user information
            
        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Validate password strength
            user_data.validate_password_strength()
            
            # Check if email already exists
            existing_user = await self.repository.get_by_email(user_data.email)
            if existing_user:
                raise ValidationError("Email already registered")
            
            # Create user in database
            user_in_db = await self.repository.create(user_data)
            
            # Convert to response model
            return self._convert_to_user_model(user_in_db)
        except ValidationError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to create user: {str(e)}")

    async def get_user(self, user_id: str) -> User:
        """
        Get user by ID with proper error handling
        
        Args:
            user_id (str): User's unique identifier
            
        Returns:
            User: User information if found
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            user_in_db = await self.repository.get_by_id(user_id)
            if not user_in_db:
                raise NotFoundError("User", user_id)

            return self._convert_to_user_model(user_in_db)
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get user: {str(e)}")

    async def update_user(self, user_id: str, update_data: UserUpdate) -> User:
        """
        Update user information with validation
        
        Args:
            user_id (str): User's unique identifier
            update_data (UserUpdate): Fields to update
            
        Returns:
            User: Updated user information
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Check if user exists
            existing_user = await self.repository.get_by_id(user_id)
            if not existing_user:
                raise NotFoundError("User", user_id)

            # If email is being updated, check if it's already taken
            if update_data.email and update_data.email != existing_user.email:
                existing_user_by_email = await self.repository.get_by_email(update_data.email)
                if existing_user_by_email:
                    raise ValidationError("Email already registered")

            # Update user
            updated_user = await self.repository.update(user_id, update_data.dict(exclude_unset=True))
            if not updated_user:
                raise ValidationError("Failed to update user")

            return self._convert_to_user_model(updated_user)
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update user: {str(e)}")

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password (str): Plain text password
            hashed_password (str): Hashed password
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email (str): User's email address
            
        Returns:
            Optional[User]: User information if found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            user_in_db = await self.repository.get_by_email(email)
            if not user_in_db:
                return None

            return self._convert_to_user_model(user_in_db)
        except Exception as e:
            raise DatabaseError(f"Failed to get user by email: {str(e)}")

    async def update_login_info(self, user_id: str, success: bool = True) -> User:
        """
        Update user's login information
        
        Args:
            user_id (str): User's unique identifier
            success (bool): Whether the login was successful
            
        Returns:
            User: Updated user information
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            user_in_db = await self.repository.get_by_id(user_id)
            if not user_in_db:
                raise NotFoundError("User", user_id)
            
            return await self.repository.update_login_info(user_id, success)
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update login info: {str(e)}")

    async def verify_email(self, user_id: str) -> User:
        """
        Mark user's email as verified
        
        Args:
            user_id (str): User's unique identifier
            
        Returns:
            User: Updated user information
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            user_in_db = await self.repository.get_by_id(user_id)
            if not user_in_db:
                raise NotFoundError("User", user_id)
            
            return await self.repository.verify_email(user_id)
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to verify email: {str(e)}")

    async def update_preferences(self, user_id: str, preferences: Dict) -> User:
        """
        Update user preferences
        
        Args:
            user_id (str): User's unique identifier
            preferences (Dict): New preferences
            
        Returns:
            User: Updated user information
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            user_in_db = await self.repository.get_by_id(user_id)
            if not user_in_db:
                raise NotFoundError("User", user_id)
            
            return await self.repository.update_preferences(user_id, preferences)
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update preferences: {str(e)}")

    def _convert_to_user_model(self, user_in_db: UserInDB) -> User:
        """
        Convert UserInDB to User model
        
        Args:
            user_in_db (UserInDB): Database user model
            
        Returns:
            User: API response user model
        """
        return User(
            id=str(user_in_db.id),
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            is_active=user_in_db.is_active,
            phone_number=user_in_db.phone_number,
            role=user_in_db.role,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at,
            last_login=user_in_db.last_login,
            is_email_verified=user_in_db.is_email_verified
        ) 