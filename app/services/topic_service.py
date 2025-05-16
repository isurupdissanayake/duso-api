from typing import List, Optional
from ..models.topic import TopicCreate, TopicInDB, TopicUpdate, Topic
from ..repositories import TopicRepository
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError

class TopicService:
    def __init__(self, repository: TopicRepository):
        self.repository = repository

    async def create_topic(self, topic: TopicCreate, user_id: str) -> Topic:
        """
        Create a new topic for a user
        
        Args:
            topic (TopicCreate): Topic creation data
            user_id (str): User's unique identifier
            
        Returns:
            Topic: Created topic information
            
        Raises:
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            topic_in_db = await self.repository.create(topic, user_id)
            return self._convert_to_topic_model(topic_in_db)
        except Exception as e:
            raise DatabaseError(f"Failed to create topic: {str(e)}")

    async def get_topic(self, topic_id: str) -> Topic:
        """
        Get a topic by ID
        
        Args:
            topic_id (str): Topic's unique identifier
            
        Returns:
            Topic: Topic information
            
        Raises:
            NotFoundError: If topic not found
            DatabaseError: If database operation fails
        """
        try:
            topic = await self.repository.get_by_id(topic_id)
            if not topic:
                raise NotFoundError("Topic", topic_id)
            return self._convert_to_topic_model(topic)
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get topic: {str(e)}")

    async def get_user_topics(self, user_id: str) -> List[Topic]:
        """
        Get all topics for a user
        
        Args:
            user_id (str): User's unique identifier
            
        Returns:
            List[Topic]: List of user's topics
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            topics = await self.repository.get_all_for_user(user_id)
            return [self._convert_to_topic_model(topic) for topic in topics]
        except Exception as e:
            raise DatabaseError(f"Failed to get user topics: {str(e)}")

    async def update_topic(self, topic_id: str, topic_update: TopicUpdate) -> Topic:
        """
        Update a topic
        
        Args:
            topic_id (str): Topic's unique identifier
            topic_update (TopicUpdate): Fields to update
            
        Returns:
            Topic: Updated topic information
            
        Raises:
            NotFoundError: If topic not found
            ValidationError: If validation fails
            DatabaseError: If database operation fails
        """
        try:
            # Check if topic exists
            existing_topic = await self.repository.get_by_id(topic_id)
            if not existing_topic:
                raise NotFoundError("Topic", topic_id)

            # Update topic
            updated_topic = await self.repository.update(topic_id, topic_update)
            if not updated_topic:
                raise ValidationError("Failed to update topic")

            return self._convert_to_topic_model(updated_topic)
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update topic: {str(e)}")

    async def delete_topic(self, topic_id: str) -> None:
        """
        Delete a topic
        
        Args:
            topic_id (str): Topic's unique identifier
            
        Raises:
            NotFoundError: If topic not found
            DatabaseError: If database operation fails
        """
        try:
            # Check if topic exists
            existing_topic = await self.repository.get_by_id(topic_id)
            if not existing_topic:
                raise NotFoundError("Topic", topic_id)

            # Delete topic
            if not await self.repository.delete(topic_id):
                raise DatabaseError("Failed to delete topic")
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to delete topic: {str(e)}")

    def _convert_to_topic_model(self, topic_in_db: TopicInDB) -> Topic:
        """
        Convert TopicInDB to Topic model
        
        Args:
            topic_in_db (TopicInDB): Database topic model
            
        Returns:
            Topic: API response topic model
        """
        return Topic(
            id=str(topic_in_db.id),
            title=topic_in_db.title,
            description=topic_in_db.description,
            user_id=str(topic_in_db.user_id),
            created_at=topic_in_db.created_at,
            updated_at=topic_in_db.updated_at
        ) 