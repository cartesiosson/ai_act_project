from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorCollection

async def create_item(collection: AsyncIOMotorCollection, data: dict) -> dict:
    await collection.insert_one(data)
    return data

async def list_items(collection: AsyncIOMotorCollection) -> List[dict]:
    return [doc async for doc in collection.find()]

async def get_item(collection: AsyncIOMotorCollection, key: str, value: str) -> Optional[dict]:
    return await collection.find_one({key: value})