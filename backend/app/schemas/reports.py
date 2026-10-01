from pydantic import BaseModel
from typing import List
from uuid import UUID

class ReportRequest(BaseModel):
    product_ids: List[UUID]
    baseline_id: UUID

class Citation(BaseModel):
    evidence_id: str
    snippet: str

class ReportSchema(BaseModel):
    executive_summary: str
    key_differences: List[str]
    pricing_analysis: str
    potential_opportunities: List[str]
    uncertainties_and_gaps: List[str]
    evidence_citations: List[Citation]
