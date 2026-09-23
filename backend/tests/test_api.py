import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_ingest_url_valid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/products/ingest-url", json={"url": "https://www.apple.com/airpods"})
    assert response.status_code == 202
    assert response.json()["url"] == "https://www.apple.com/airpods"

@pytest.mark.asyncio
async def test_ingest_url_invalid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/products/ingest-url", json={"url": "just some text"})
    assert response.status_code == 422 # Pydantic validation error
