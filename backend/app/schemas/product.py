from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from app.models.domain import PresenceState

class BrandResponse(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)

class ProductSpecificationResponse(BaseModel):
    id: UUID
    attribute_name: str
    value: Any
    unit: Optional[str] = None
    presence_state: PresenceState
    evidence_snippet: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ProductResponse(BaseModel):
    id: UUID
    name: str
    url: HttpUrl
    brand: BrandResponse
    category: CategoryResponse
    specifications: List[ProductSpecificationResponse] = []
    model_config = ConfigDict(from_attributes=True)
