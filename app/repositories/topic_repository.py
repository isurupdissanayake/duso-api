from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.topic import TopicCreate, TopicInDB, TopicUpdate

class TopicRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.topic_collection = db.topics

    async def create(self, topic: TopicCreate, user_id: str) -> TopicInDB:
        topic_dict = topic.model_dump()
        topic_dict["user_id"] = ObjectId(user_id)
        topic_dict["created_at"] = datetime.utcnow()
        topic_dict["updated_at"] = datetime.utcnow()
        
        result = await self.topic_collection.insert_one(topic_dict)
        created_topic = await self.topic_collection.find_one({"_id": result.inserted_id})
        return TopicInDB(**created_topic)

    async def get_by_id(self, topic_id: str) -> Optional[TopicInDB]:
        topic = await self.topic_collection.find_one({"_id": ObjectId(topic_id)})
        return TopicInDB(**topic) if topic else None

    async def get_all_for_user(self, user_id: str) -> List[TopicInDB]:
        cursor = self.topic_collection.find({"user_id": ObjectId(user_id)})
        topics = await cursor.to_list(length=None)
        return [TopicInDB(**topic) for topic in topics]

    async def update(self, topic_id: str, topic_update: TopicUpdate) -> Optional[TopicInDB]:
        update_data = topic_update.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()
            await self.topic_collection.update_one(
                {"_id": ObjectId(topic_id)},
                {"$set": update_data}
            )
        return await self.get_by_id(topic_id)

    async def delete(self, topic_id: str) -> bool:
        result = await self.topic_collection.delete_one({"_id": ObjectId(topic_id)})
        return result.deleted_count > 0 