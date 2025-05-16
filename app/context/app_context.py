from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from ..models.user import UserInDB
from ..config import Settings

class AppContext(BaseModel):
    """
    Application context that holds request-level data.
    This includes the current authenticated user and application settings.
    """
    user: Optional[UserInDB] = None
    settings: Settings

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )

    @property
    def is_authenticated(self) -> bool:
        """Check if the current request has an authenticated user"""
        return self.user is not None

    @property
    def is_admin(self) -> bool:
        """Check if the current user is an admin"""
        return self.is_authenticated and self.user.role == "admin" 