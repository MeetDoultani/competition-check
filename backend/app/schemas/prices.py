from pydantic import BaseModel, ConfigDict
from typing import List
from uuid import UUID
from datetime import datetime

class PricePoint(BaseModel):
    price: float
    currency: str
    observed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PriceHistoryResponse(BaseModel):
    product_id: UUID
    history: List[PricePoint]
