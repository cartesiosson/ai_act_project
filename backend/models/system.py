from pydantic import BaseModel, AnyUrl, Field

class IntelligentSystem(BaseModel):
    name: str = Field(..., alias="hasName")
    purpose: AnyUrl = Field(..., alias="hasPurpose")
    risk_level: AnyUrl = Field(..., alias="hasRiskLevel")
    deployment_context: AnyUrl = Field(..., alias="hasDeploymentContext")
    training_data_origin: AnyUrl = Field(..., alias="hasTrainingDataOrigin")
    version: str = Field(..., alias="hasVersion")

    class Config:
        # Permite usar los aliases (hasName, hasPurpose, etc.) al instanciar con .dict(by_alias=True)
        allow_population_by_field_name = True