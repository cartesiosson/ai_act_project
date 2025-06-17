from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.assessment import RiskAssessment
from db import get_database

router = APIRouter()

@router.get("/assessments", response_model=list[RiskAssessment])
async def get_assessments(db: AsyncIOMotorClient = Depends(get_database)):
    return list(await db["assessments"].find().to_list(length=None))