from pydantic import BaseModel, Field
from typing import Dict

class BaseEntityI18N(BaseModel):
    id: str = Field(..., alias="_id")
    label: Dict[str, str] = Field(default_factory=dict)
    comment: Dict[str, str] = Field(default_factory=dict)