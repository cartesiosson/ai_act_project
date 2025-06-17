from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.system import IntelligentSystem
from db import get_database

router = APIRouter()

@router.get("/systems", response_model=list[IntelligentSystem])
async def get_systems(db: AsyncIOMotorClient = Depends(get_database)):
    return list(await db["systems"].find().to_list(length=None))