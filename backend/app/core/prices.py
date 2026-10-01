from uuid import UUID
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.domain import PriceObservation

async def record_price_observation(
    db: AsyncSession,
    product_id: UUID,
    price: float,
    source_url: str,
    currency: str = "USD",
    observed_at: Optional[datetime] = None
) -> PriceObservation:
    obs = PriceObservation(
        product_id=product_id,
        price=price,
        source_url=source_url,
        currency=currency,
        observed_at=observed_at or datetime.utcnow()
    )
    db.add(obs)
    await db.commit()
    await db.refresh(obs)
    return obs
