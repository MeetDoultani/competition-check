import asyncio
import sys
import os

# Ensure the backend directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import AsyncSessionLocal
from app.models.domain import Brand, Category, AttributeTemplate, DataType, Product, ProductSpecification, PresenceState

async def seed_competitors():
    async with AsyncSessionLocal() as session:
        try:
            print("Creating brand and category...")
            brand = Brand(name="TechCorp")
            category = Category(name="Smartphones", description="Flagship Devices")
            session.add_all([brand, category])
            await session.flush()
            
            print("Creating EAV attribute templates...")
            attr_price = AttributeTemplate(category_id=category.id, name="Price", data_type=DataType.numeric, unit="USD")
            attr_storage = AttributeTemplate(category_id=category.id, name="Storage", data_type=DataType.numeric, unit="GB")
            attr_color = AttributeTemplate(category_id=category.id, name="Color", data_type=DataType.string)
            session.add_all([attr_price, attr_storage, attr_color])
            await session.flush()
            
            print("Creating 3 products (Basic, Pro, Max)...")
            p_basic = Product(brand_id=brand.id, category_id=category.id, name="TechPhone Basic", url="http://techcorp.com/basic")
            p_pro = Product(brand_id=brand.id, category_id=category.id, name="TechPhone Pro", url="http://techcorp.com/pro")
            p_max = Product(brand_id=brand.id, category_id=category.id, name="TechPhone Max", url="http://techcorp.com/max")
            session.add_all([p_basic, p_pro, p_max])
            await session.flush()
            
            print("Mapping specifications to products...")
            specs = [
                # Basic Tier
                ProductSpecification(product_id=p_basic.id, attribute_id=attr_price.id, value_numeric=599.0, presence_state=PresenceState.PRESENT),
                ProductSpecification(product_id=p_basic.id, attribute_id=attr_storage.id, value_numeric=128.0, presence_state=PresenceState.PRESENT),
                ProductSpecification(product_id=p_basic.id, attribute_id=attr_color.id, value_text="Matte Black", presence_state=PresenceState.PRESENT),
                
                # Pro Tier
                ProductSpecification(product_id=p_pro.id, attribute_id=attr_price.id, value_numeric=899.0, presence_state=PresenceState.PRESENT),
                ProductSpecification(product_id=p_pro.id, attribute_id=attr_storage.id, value_numeric=256.0, presence_state=PresenceState.PRESENT),
                ProductSpecification(product_id=p_pro.id, attribute_id=attr_color.id, value_text="Titanium Silver", presence_state=PresenceState.PRESENT),
                
                # Max Tier
                ProductSpecification(product_id=p_max.id, attribute_id=attr_price.id, value_numeric=1199.0, presence_state=PresenceState.PRESENT),
                ProductSpecification(product_id=p_max.id, attribute_id=attr_storage.id, value_numeric=512.0, presence_state=PresenceState.PRESENT),
                ProductSpecification(product_id=p_max.id, attribute_id=attr_color.id, value_text="Desert Gold", presence_state=PresenceState.PRESENT),
            ]
            session.add_all(specs)
            
            await session.commit()
            print("Successfully seeded 3 competitor products (Basic, Pro, Max) into the database.")
            print(f"Product IDs to test in Swagger:\n- Basic: {p_basic.id}\n- Pro: {p_pro.id}\n- Max: {p_max.id}")
            
        except Exception as e:
            await session.rollback()
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(seed_competitors())
