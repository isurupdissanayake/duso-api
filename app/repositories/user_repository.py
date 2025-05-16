from datetime import datetime
from typing import Optional, Dict
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..models.user import UserCreate, UserInDB, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize UserRepository with database connection
        
        Args:
            db (AsyncIOMotorDatabase): MongoDB database connection
        """
        self.db = db
        self.user_collection = db.users

    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email address"""
        user = await self.user_collection.find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None

    async def create(self, user: UserCreate) -> UserInDB:
        """Create a new user"""
        user_dict = user.dict(exclude={'password', 'confirm_password'})
        user_dict.update({
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "failed_login_attempts": 0,
            "is_email_verified": False,
            "preferences": {}
        })
        
        result = await self.user_collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return UserInDB(**user_dict)

    async def get_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        user = await self.user_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return UserInDB(**user)
        return None

    async def update(self, user_id: str, update_data: Dict) -> Optional[UserInDB]:
        """Update user information"""
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None

    async def update_login_info(self, user_id: str, success: bool = True) -> Optional[UserInDB]:
        """Update user's login information"""
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        if success:
            update_data.update({
                "last_login": datetime.utcnow(),
                "failed_login_attempts": 0
            })
        else:
            update_data["$inc"] = {"failed_login_attempts": 1}
        
        result = await self.user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data} if success else update_data
        )
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None

    async def verify_email(self, user_id: str) -> Optional[UserInDB]:
        """Mark user's email as verified"""
        result = await self.user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "is_email_verified": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None

    async def update_preferences(self, user_id: str, preferences: Dict) -> Optional[UserInDB]:
        """Update user preferences"""
        result = await self.user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "preferences": preferences,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None 