from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from models.compliance import ComplianceRequirement
from db import get_database

router = APIRouter()

@router.get("/compliance", response_model=list[ComplianceRequirement])
async def get_compliance_requirements(db: AsyncIOMotorClient = Depends(get_database)):
    return list(await db["compliance"].find().to_list(length=None))