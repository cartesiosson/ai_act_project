from typing import Optional, List
from pydantic import BaseModel, Field

class IntelligentSystem(BaseModel):
    id: Optional[str] = Field(default=None, alias="@id")
    type: str = Field(alias="@type", example="ai:IntelligentSystem")
    context: Optional[str] = Field(
        default="http://localhost/docs/ontologias.jsonld",
        alias="@context"
    )

    hasName: str = Field(..., example="Sim-01")
    hasPurpose: List[str] = Field(..., example=["ai:ForEducation", "ai:Chatbot"])
    hasRiskLevel: str = Field(..., example="ai:HighRisk")
    hasDeploymentContext: List[str] = Field(..., example=["ai:Education"])
    hasTrainingDataOrigin: List[str] = Field(..., example=["ai:InternalDataset", "ai:ExternalDataset"])
    hasVersion: str = Field(..., example="1.0.0")

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "@context": "http://ontologias/docs/ontology.jsonld",
                "@type": "ai:IntelligentSystem",
                "hasName": "Sim-01",
                "hasPurpose": ["ai:ForEducation", "ai:Chatbot"],
                "hasRiskLevel": "ai:HighRisk",
                "hasDeploymentContext": ["ai:Education"],
                "hasTrainingDataOrigin": ["ai:InternalDataset", "ai:ExternalDataset"],
                "hasVersion": "1.0.0"
            }
        }
