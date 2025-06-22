from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache

@lru_cache()
def get_client():
    return AsyncIOMotorClient("mongodb://mongo:27017")

async def get_database():
    client = get_client()
    return client["ai_act_db"]

async def ensure_indexes():
    db = await get_database()
    collection = db["intelligent_systems"]
    await collection.create_index("hasUrn", unique=True)