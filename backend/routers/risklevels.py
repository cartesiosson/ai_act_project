from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.risklevel import RiskLevel
from db import get_database

router = APIRouter()

@router.get("/risklevels", response_model=list[RiskLevel])
async def get_risk_levels(db: AsyncIOMotorClient = Depends(get_database)):
    return list(await db["risklevels"].find().to_list(length=None))