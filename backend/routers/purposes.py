from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.purpose import Purpose
from db import get_database

router = APIRouter()

@router.get("/", response_model=list[Purpose])
async def get_purposes(db: AsyncIOMotorClient = Depends(get_database)):
    return list(await db["purposes"].find().to_list(length=None))