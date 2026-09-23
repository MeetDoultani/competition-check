from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from uuid import UUID
from app.models.domain import PresenceState, DataType
from app.schemas.product import ProductResponse

class DeltaInfo(BaseModel):
    raw_diff: Optional[float] = None
    percentage_change: Optional[float] = None

class ProductAttributeValue(BaseModel):
    product_id: UUID
    value: Any
    presence_state: PresenceState
    evidence_snippet: Optional[str] = None
    delta: Optional[DeltaInfo] = None
    model_config = ConfigDict(from_attributes=True)

class AttributeRow(BaseModel):
    attribute_id: UUID
    attribute_name: str
    data_type: DataType
    unit: Optional[str] = None
    values: List[ProductAttributeValue]

class ComparisonMatrixResponse(BaseModel):
    baseline_product_id: UUID
    products: List[ProductResponse]
    attributes: List[AttributeRow]
