from typing import Optional, List
from pydantic import BaseModel, Field

class IntelligentSystem(BaseModel):
    id: Optional[str] = Field(default=None, alias="@id")
    type: str = Field(alias="@type", example="ai:IntelligentSystem")
    context: Optional[str] = Field(
        default="http://ontologias/json-ld-context.json",
        alias="@context"
    )
    hasName: str = Field(..., example="Sim-01")
    hasPurpose: List[str] = Field(..., example=["ai:BiometricIdentification", "ai:Chatbot"])
    hasDeploymentContext: List[str] = Field(..., example=["ai:Education"])
    hasTrainingDataOrigin: List[str] = Field(..., example=["ai:InternalDataset", "ai:ExternalDataset"])
    hasSystemCapabilityCriteria: List[str] = Field(default_factory=list, example=["ai:CustomCriterion1", "ai:CustomCriterion2"])
    hasVersion: str = Field(..., example="1.0.0")
    hasUrn: Optional[str] = Field(default=None, example="urn:uuid:...")
    # Puedes agregar más campos según los módulos, por ejemplo, requisitos, actores, etc.

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "@context": "http://ontologias/json-ld-context.json",
                "@type": "ai:IntelligentSystem",
                "hasName": "Sim-01",
                "hasPurpose": ["ai:BiometricIdentification", "ai:Chatbot"],
                "hasDeploymentContext": ["ai:Education"],
                "hasTrainingDataOrigin": ["ai:InternalDataset", "ai:ExternalDataset"],
                "hasSystemCapabilityCriteria": ["ai:CustomCriterion1", "ai:CustomCriterion2"],
                "hasVersion": "1.0.0",
                "hasUrn": "urn:uuid:..."
            }
        }
