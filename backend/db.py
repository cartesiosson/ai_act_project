from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache

@lru_cache()
def get_client():
    return AsyncIOMotorClient("mongodb://mongo:27017")

async def get_database():
    client = get_client()
    return client["ai_act_db"]