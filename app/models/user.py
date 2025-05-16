from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, StringConstraints, ConfigDict
from bson import ObjectId
import re
from pydantic_core import CoreSchema, core_schema

class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return ObjectId(str(v))

    def __repr__(self) -> str:
        return f"PyObjectId('{str(self)}')"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.json_or_python_schema(
            python_schema=core_schema.str_schema(),
            json_schema=core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(str)
        )

class UserBase(BaseModel):
    """Base user model with common fields"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, description="User's phone number")
    role: str = Field(default="user", description="User's role in the system", pattern="^(user|admin)$")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            # Basic phone number validation (can be customized based on requirements)
            if not re.match(r'^\+?1?\d{9,15}$', v):
                raise ValueError('Invalid phone number format')
        return v

    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['user', 'admin']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of {allowed_roles}')
        return v

class UserCreate(UserBase):
    """Model for user creation"""
    password: str = Field(..., min_length=8, description="User's password")
    confirm_password: str = Field(..., description="Password confirmation")

    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserInDB(UserBase):
    """Model for user data in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    failed_login_attempts: int = Field(default=0, description="Number of failed login attempts")
    is_email_verified: bool = Field(default=False, description="Whether email is verified")
    preferences: Dict = Field(default_factory=dict, description="User preferences")

    model_config = ConfigDict(
        json_encoders={
            PyObjectId: str,
            datetime: lambda dt: dt.isoformat()
        },
        populate_by_name=True
    )

class User(UserInDB):
    """Model for user API responses"""
    id: str = Field(..., alias="_id", description="User's unique identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    is_email_verified: bool = Field(..., description="Whether email is verified")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        populate_by_name = True

class UserUpdate(BaseModel):
    """Model for user updates"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)
    role: Optional[str] = Field(None, pattern="^(user|admin)$")
    is_active: Optional[bool] = None
    preferences: Optional[Dict] = None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            if not re.match(r'^\+?1?\d{9,15}$', v):
                raise ValueError('Invalid phone number format')
        return v

    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            allowed_roles = ['user', 'admin']
            if v not in allowed_roles:
                raise ValueError(f'Role must be one of {allowed_roles}')
        return v 