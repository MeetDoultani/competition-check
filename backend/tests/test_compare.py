import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from app.main import app
from app.models.domain import Product, Brand, Category, AttributeTemplate, DataType, ProductSpecification, PresenceState

# Tests for the core comparison logic
from app.core.comparison import generate_comparison_matrix

def test_generate_comparison_matrix_logic():
    # Mock data
    brand = Brand(id=uuid4(), name="TestBrand")
    category = Category(id=uuid4(), name="TestCategory")
    
    attr_price = AttributeTemplate(id=uuid4(), category=category, name="Price", data_type=DataType.numeric)
    attr_color = AttributeTemplate(id=uuid4(), category=category, name="Color", data_type=DataType.string)
    attr_wifi = AttributeTemplate(id=uuid4(), category=category, name="WiFi", data_type=DataType.boolean)
    
    p1 = Product(id=uuid4(), brand=brand, category=category, name="P1", url="http://p1.com")
    p2 = Product(id=uuid4(), brand=brand, category=category, name="P2", url="http://p2.com")
    
    # P1 has price=100, color="Red", WiFi=True
    p1.specifications = [
        ProductSpecification(id=uuid4(), product=p1, attribute=attr_price, attribute_id=attr_price.id, value_numeric=100.0, presence_state=PresenceState.PRESENT),
        ProductSpecification(id=uuid4(), product=p1, attribute=attr_color, attribute_id=attr_color.id, value_text="Red", presence_state=PresenceState.PRESENT),
        ProductSpecification(id=uuid4(), product=p1, attribute=attr_wifi, attribute_id=attr_wifi.id, value_boolean=True, presence_state=PresenceState.PRESENT),
    ]
    
    # P2 has price=150, color missing, WiFi=False
    p2.specifications = [
        ProductSpecification(id=uuid4(), product=p2, attribute=attr_price, attribute_id=attr_price.id, value_numeric=150.0, presence_state=PresenceState.PRESENT),
        ProductSpecification(id=uuid4(), product=p2, attribute=attr_wifi, attribute_id=attr_wifi.id, value_boolean=False, presence_state=PresenceState.VERIFIED_ABSENT),
    ]
    
    # Generate matrix with P1 as baseline
    matrix = generate_comparison_matrix([p1, p2], baseline_id=p1.id)
    
    assert matrix.baseline_product_id == p1.id
    assert len(matrix.attributes) == 3 # Price, Color, WiFi
    
    # Check Price Delta
    price_row = next(row for row in matrix.attributes if row.attribute_id == attr_price.id)
    p2_price_val = next(val for val in price_row.values if val.product_id == p2.id)
    
    assert p2_price_val.delta is not None
    assert p2_price_val.delta.raw_diff == 50.0 # 150 - 100
    assert p2_price_val.delta.percentage_change == 50.0 # (50/100)*100
    
    # Check Missing Color handling
    color_row = next(row for row in matrix.attributes if row.attribute_id == attr_color.id)
    p2_color_val = next(val for val in color_row.values if val.product_id == p2.id)
    
    assert p2_color_val.value is None
    assert p2_color_val.presence_state == PresenceState.UNKNOWN
    assert p2_color_val.delta is None # String type shouldn't have delta
    
    # Check Boolean
    wifi_row = next(row for row in matrix.attributes if row.attribute_id == attr_wifi.id)
    p2_wifi_val = next(val for val in wifi_row.values if val.product_id == p2.id)
    
    assert p2_wifi_val.value is False
    assert p2_wifi_val.delta is None # Boolean type shouldn't have delta

def test_zero_division_prevention():
    brand = Brand(id=uuid4(), name="TestBrand")
    category = Category(id=uuid4(), name="TestCategory")
    attr_price = AttributeTemplate(id=uuid4(), category=category, name="Price", data_type=DataType.numeric)
    
    p1 = Product(id=uuid4(), brand=brand, category=category, name="FreeBase", url="http://p1.com")
    p2 = Product(id=uuid4(), brand=brand, category=category, name="PaidTarget", url="http://p2.com")
    
    p1.specifications = [
        ProductSpecification(id=uuid4(), product=p1, attribute=attr_price, attribute_id=attr_price.id, value_numeric=0.0, presence_state=PresenceState.PRESENT),
    ]
    p2.specifications = [
        ProductSpecification(id=uuid4(), product=p2, attribute=attr_price, attribute_id=attr_price.id, value_numeric=50.0, presence_state=PresenceState.PRESENT),
    ]
    
    matrix = generate_comparison_matrix([p1, p2], baseline_id=p1.id)
    price_row = next(row for row in matrix.attributes if row.attribute_id == attr_price.id)
    p2_price_val = next(val for val in price_row.values if val.product_id == p2.id)
    
    assert p2_price_val.delta is not None
    assert p2_price_val.delta.raw_diff == 50.0
    assert p2_price_val.delta.percentage_change is None # Should handle division by zero gracefully

@pytest.mark.asyncio
async def test_api_compare_validation_errors():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Less than 2 products
        u1 = str(uuid4())
        response = await ac.get(f"/api/v1/compare/?product_ids={u1}&baseline_id={u1}")
        assert response.status_code == 400
        
        # Baseline not in products
        u2 = str(uuid4())
        u3 = str(uuid4())
        response = await ac.get(f"/api/v1/compare/?product_ids={u1}&product_ids={u2}&baseline_id={u3}")
        assert response.status_code == 400
