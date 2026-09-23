import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.domain import Brand, Category, AttributeTemplate, DataType, Product, ProductSpecification, PresenceState, Evidence, PriceObservation

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        # Brands
        apple = Brand(name="Apple")
        samsung = Brand(name="Samsung")
        sony = Brand(name="Sony")
        bose = Brand(name="Bose")
        jabra = Brand(name="Jabra")
        session.add_all([apple, samsung, sony, bose, jabra])
        
        # Categories & Templates
        tws = Category(name="TWS Earbuds", description="True Wireless Stereo Earbuds")
        session.add(tws)
        await session.flush()
        
        battery_attr = AttributeTemplate(category_id=tws.id, name="Battery Life", data_type=DataType.numeric, unit="hours")
        anc_attr = AttributeTemplate(category_id=tws.id, name="Active Noise Cancellation", data_type=DataType.boolean)
        driver_attr = AttributeTemplate(category_id=tws.id, name="Driver Size", data_type=DataType.numeric, unit="mm")
        session.add_all([battery_attr, anc_attr, driver_attr])
        await session.flush()
        
        # Evidence
        ev1 = Evidence(url="https://apple.com/airpods-pro", snippet="Up to 6 hours of listening time with a single charge.")
        session.add(ev1)
        
        # Products
        ap_pro = Product(brand_id=apple.id, category_id=tws.id, name="AirPods Pro 2", url="https://apple.com/airpods-pro")
        session.add(ap_pro)
        await session.flush()
        
        # Specs
        spec1 = ProductSpecification(
            product_id=ap_pro.id, attribute_id=battery_attr.id, 
            value_numeric=6.0, presence_state=PresenceState.PRESENT, evidence_id=ev1.id
        )
        spec2 = ProductSpecification(
            product_id=ap_pro.id, attribute_id=anc_attr.id, 
            value_boolean=True, presence_state=PresenceState.PRESENT
        )
        session.add_all([spec1, spec2])
        
        # Prices
        price1 = PriceObservation(product_id=ap_pro.id, price=249.0, source_url="https://apple.com/airpods-pro")
        session.add(price1)
        
        await session.commit()
        print("Seed data inserted successfully.")

if __name__ == "__main__":
    asyncio.run(seed())
