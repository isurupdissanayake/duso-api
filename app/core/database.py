from motor.motor_asyncio import AsyncIOMotorClient
from ..config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def get_database() -> AsyncIOMotorClient:
    return db.db

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]

async def close_mongo_connection():
    if db.client:
        db.client.close() 