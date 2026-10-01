import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.main import app
from app.models.domain import PriceObservation

@pytest.mark.asyncio
@patch("app.api.v1.prices.AsyncSession.execute", new_callable=AsyncMock)
async def test_get_price_history(mock_execute):
    pid = uuid4()
    
    mock_product_result = MagicMock()
    mock_product_result.scalar_one_or_none.return_value = pid
    
    base_time = datetime.utcnow()
    obs1 = PriceObservation(product_id=pid, price=100.0, currency="USD", observed_at=base_time - timedelta(days=2))
    obs2 = PriceObservation(product_id=pid, price=90.0, currency="USD", observed_at=base_time - timedelta(days=1))
    obs3 = PriceObservation(product_id=pid, price=95.0, currency="USD", observed_at=base_time)
    
    mock_obs_result = MagicMock()
    mock_obs_result.scalars().all.return_value = [obs1, obs2, obs3]
    
    mock_execute.side_effect = [mock_product_result, mock_obs_result]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/prices/{pid}/price-history")
        
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == str(pid)
    assert len(data["history"]) == 3
    assert data["history"][0]["price"] == 100.0
    assert data["history"][1]["price"] == 90.0
    assert data["history"][2]["price"] == 95.0
