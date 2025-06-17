from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.criterion import RiskCriterion
from db import get_database

router = APIRouter()

@router.get("/", response_model=list[RiskCriterion])
async def get_criteria(db: AsyncIOMotorClient = Depends(get_database)):
    return list(await db["criteria"].find().to_list(length=None))