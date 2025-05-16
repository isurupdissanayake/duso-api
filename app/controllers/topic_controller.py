from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..models.topic import Topic, TopicCreate, TopicUpdate
from ..services.topic_service import TopicService
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError
from ..dependencies import get_topic_service, get_app_context
from ..context.app_context import AppContext

router = APIRouter(
    prefix="/topics",
    tags=["topics"]
)

@router.post("", response_model=Topic, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic: TopicCreate,
    ctx: AppContext = Depends(get_app_context),
    topic_service: TopicService = Depends(get_topic_service)
) -> Topic:
    """
    Create a new topic for the current user
    
    Args:
        topic (TopicCreate): Topic creation data
        ctx (AppContext): Application context
        
    Returns:
        Topic: Created topic information
        
    Raises:
        HTTPException: If topic creation fails
    """
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        return await topic_service.create_topic(topic, str(ctx.user.id))
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

@router.get("/{topic_id}", response_model=Topic)
async def get_topic(
    topic_id: str,
    ctx: AppContext = Depends(get_app_context),
    topic_service: TopicService = Depends(get_topic_service)
) -> Topic:
    """
    Get a specific topic by ID
    
    Args:
        topic_id (str): Topic's unique identifier
        ctx (AppContext): Application context
        
    Returns:
        Topic: Topic information
        
    Raises:
        HTTPException: If topic is not found
    """
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        return await topic_service.get_topic(topic_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("", response_model=List[Topic])
async def get_user_topics(
    ctx: AppContext = Depends(get_app_context),
    topic_service: TopicService = Depends(get_topic_service)
) -> List[Topic]:
    """
    Get all topics for the current user
    
    Args:
        ctx (AppContext): Application context
        
    Returns:
        List[Topic]: List of user's topics
        
    Raises:
        HTTPException: If retrieval fails
    """
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        return await topic_service.get_user_topics(str(ctx.user.id))
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/{topic_id}", response_model=Topic)
async def update_topic(
    topic_id: str,
    topic_update: TopicUpdate,
    ctx: AppContext = Depends(get_app_context),
    topic_service: TopicService = Depends(get_topic_service)
) -> Topic:
    """
    Update a topic's title or description
    
    Args:
        topic_id (str): Topic's unique identifier
        topic_update (TopicUpdate): Fields to update
        ctx (AppContext): Application context
        
    Returns:
        Topic: Updated topic information
        
    Raises:
        HTTPException: If topic is not found or update fails
    """
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        return await topic_service.update_topic(topic_id, topic_update)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
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

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: str,
    ctx: AppContext = Depends(get_app_context),
    topic_service: TopicService = Depends(get_topic_service)
) -> None:
    """
    Delete a topic
    
    Args:
        topic_id (str): Topic's unique identifier
        ctx (AppContext): Application context
        
    Raises:
        HTTPException: If topic is not found or deletion fails
    """
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    try:
        await topic_service.delete_topic(topic_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 