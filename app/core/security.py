from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..context.app_context import AppContext

from ..config import settings
from ..services.user_service import UserService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, secret_key: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new access token
    
    Args:
        data (dict): Token payload data
        secret_key (str): Secret key for token signing
        expires_delta (Optional[timedelta]): Token expiration time
        
    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Dependency for getting the current authenticated user.
    
    Args:
        token (str): JWT token from OAuth2PasswordBearer
        
    Returns:
        Dict: User information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            "your-secret-key",
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user_service = UserService()
    user = await user_service.get_user(user_id)
    if user is None:
        raise credentials_exception
    
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role
    } 