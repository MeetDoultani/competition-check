import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.search import build_product_document, generate_embedding
from app.models.domain import Product, Brand, Category, ProductSpecification, ProductFeature, AttributeTemplate, DataType

@pytest.fixture
def mock_product():
    brand = Brand(name="TestBrand")
    category = Category(name="TestCategory")
    attr1 = AttributeTemplate(name="Color", data_type=DataType.string, unit="")
    attr2 = AttributeTemplate(name="Weight", data_type=DataType.numeric, unit="g")
    
    p = Product(name="TestProduct", brand=brand, category=category)
    p.specifications = [
        ProductSpecification(attribute=attr1, value_text="Red"),
        ProductSpecification(attribute=attr2, value_numeric=150.0)
    ]
    p.features = [
        ProductFeature(feature_text="Water resistant"),
        ProductFeature(feature_text="Bluetooth 5.0")
    ]
    return p

def test_build_product_document(mock_product):
    doc = build_product_document(mock_product)
    assert "Category: TestCategory" in doc
    assert "Brand: TestBrand" in doc
    assert "Name: TestProduct" in doc
    assert "Color: Red" in doc
    assert "Weight: 150.0g" in doc
    assert "Features: Water resistant, Bluetooth 5.0" in doc

@patch("app.core.search.get_model")
def test_generate_embedding(mock_get_model):
    class MockModel:
        def encode(self, text):
            # return a dummy numpy array of 384 dimensions
            import numpy as np
            return np.ones(384)
            
    mock_get_model.return_value = MockModel()
    
    vec = generate_embedding("test query")
    assert len(vec) == 384
    assert vec[0] == 1.0

@pytest.mark.asyncio
@patch("app.api.v1.search.generate_embedding")
async def test_search_endpoint_mocked(mock_generate_embedding):
    # Mock the embedding to avoid loading the model in API test
    mock_generate_embedding.return_value = [0.1] * 384
    
    # We just want to test that the endpoint doesn't crash and returns the right schema format
    # In a real DB test, we'd seed a product and its embedding, but this verifies the wiring.
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/search/?query=test")
    
    # It might return [] if DB is empty, which is fine, we just want 200 OK.
    assert response.status_code == 200
    assert isinstance(response.json(), list)
