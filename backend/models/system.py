from typing import Optional, List
from pydantic import BaseModel, Field

class IntelligentSystem(BaseModel):
    id: Optional[str] = Field(default=None, alias="@id")
    type: str = Field(alias="@type", example="ai:IntelligentSystem")
    context: Optional[str] = Field(
        default="http://localhost:8000/static/json-ld-context.json",
        alias="@context"
    )
    hasName: str = Field(..., example="Sim-01")
    hasPurpose: List[str] = Field(..., example=["ai:BiometricIdentification", "ai:Chatbot"])
    hasDeploymentContext: List[str] = Field(..., example=["ai:Education"])
    hasTrainingDataOrigin: List[str] = Field(..., example=["ai:InternalDataset", "ai:ExternalDataset"])
    hasSystemCapabilityCriteria: List[str] = Field(default_factory=list, example=["ai:CustomCriterion1", "ai:CustomCriterion2"])
    hasAlgorithmType: List[str] = Field(default_factory=list, example=["ai:NeuralNetwork", "ai:DecisionTree"])
    hasModelScale: Optional[List[str]] = Field(default_factory=list, example=["ai:FoundationModelScale"])
    hasCapability: Optional[List[str]] = Field(default_factory=list, example=["ai:GenerativeCapability"])
    hasVersion: str = Field(..., example="1.0.0")
    hasUrn: Optional[str] = Field(default=None, example="urn:uuid:...")
    hasFLOPS: Optional[float] = Field(default=None, example=1e13, description="FLOPS del sistema (opcional)")

    # ARTICLE 5: PROHIBITED PRACTICES (v0.37.4)
    hasProhibitedPractice: Optional[List[str]] = Field(
        default_factory=list,
        example=["ai:SubliminalManipulationCriterion"],
        description="Prohibited practices under Article 5 (Unacceptable Risk). Systems with these practices CANNOT be deployed in the EU."
    )
    hasLegalException: Optional[List[str]] = Field(
        default_factory=list,
        example=["ai:VictimSearchException"],
        description="Legal exceptions under Article 5.2 (only applicable to real-time biometric identification)"
    )
    hasJudicialAuthorization: Optional[bool] = Field(
        default=None,
        description="Whether the system has prior judicial authorization (required for Article 5.2 exceptions)"
    )

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "@context": "http://localhost:8000/static/json-ld-context.json",
                "@type": "ai:IntelligentSystem",
                "hasName": "Sim-01",
                "hasPurpose": ["ai:BiometricIdentification", "ai:Chatbot"],
                "hasDeploymentContext": ["ai:Education"],
                "hasTrainingDataOrigin": ["ai:InternalDataset", "ai:ExternalDataset"],
                "hasSystemCapabilityCriteria": ["ai:CustomCriterion1", "ai:CustomCriterion2"],
                "hasAlgorithmType": ["ai:NeuralNetwork", "ai:DecisionTree"],
                "hasModelScale": ["ai:FoundationModelScale"],
                "hasCapability": ["ai:GenerativeCapability"],
                "hasVersion": "1.0.0",
                "hasUrn": "urn:uuid:..."
            }
        }
