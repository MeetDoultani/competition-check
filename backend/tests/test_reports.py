import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from app.main import app
from app.models.domain import Product, Brand, Category
from app.schemas.reports import ReportSchema, Citation

@pytest.mark.asyncio
@patch("app.api.v1.reports.AsyncSession.execute", new_callable=AsyncMock)
@patch("app.api.v1.reports.generate_report")
async def test_generate_comparison_report(mock_generate_report, mock_execute):
    pid1 = uuid4()
    pid2 = uuid4()
    
    brand = Brand(id=uuid4(), name="TestBrand")
    category = Category(id=uuid4(), name="TestCategory")
    
    p1 = Product(id=pid1, brand=brand, category=category, name="P1", url="http://p1.com")
    p2 = Product(id=pid2, brand=brand, category=category, name="P2", url="http://p2.com")
    
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [p1, p2]
    mock_execute.return_value = mock_result
    
    mock_report = ReportSchema(
        executive_summary="Summary",
        key_differences=["Diff1"],
        pricing_analysis="Pricing",
        potential_opportunities=["Opp1"],
        uncertainties_and_gaps=["Gap1"],
        evidence_citations=[Citation(evidence_id="ev1", snippet="snip")]
    )
    mock_generate_report.return_value = mock_report
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/reports/compare/",
            json={"product_ids": [str(pid1), str(pid2)], "baseline_id": str(pid1)}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert data["executive_summary"] == "Summary"
    assert len(data["key_differences"]) == 1
