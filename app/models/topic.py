from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .user import PyObjectId

class TopicBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class TopicCreate(TopicBase):
    pass

class TopicInDB(TopicBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            PyObjectId: str,
            datetime: lambda dt: dt.isoformat()
        }
        populate_by_name = True

class Topic(TopicInDB):
    pass

class TopicUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500) 