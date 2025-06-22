from pydantic import BaseModel, Field
from typing import Optional

class IntelligentSystemFuseki(BaseModel):
    urn: str
    type: str = Field(default="ai:IntelligentSystem")
    hasName: Optional[str]
    hasPurpose: Optional[str]
    hasRiskLevel: Optional[str]
    hasDeploymentContext: Optional[str]
    hasTrainingDataOrigin: Optional[str]
    hasVersion: Optional[str]
