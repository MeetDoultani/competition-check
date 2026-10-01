from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.domain import PriceObservation, Product
from app.schemas.prices import PriceHistoryResponse, PricePoint

router = APIRouter()

@router.get("/{product_id}/price-history", response_model=PriceHistoryResponse)
async def get_price_history(product_id: UUID, db: AsyncSession = Depends(get_db)):
    product_query = select(Product.id).where(Product.id == product_id)
    product_result = await db.execute(product_query)
    if not product_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Product not found")

    query = (
        select(PriceObservation)
        .where(PriceObservation.product_id == product_id)
        .order_by(PriceObservation.observed_at.asc())
    )
    result = await db.execute(query)
    observations = result.scalars().all()
    
    points = [
        PricePoint(
            price=obs.price,
            currency=obs.currency,
            observed_at=obs.observed_at
        ) for obs in observations
    ]
    
    return PriceHistoryResponse(
        product_id=product_id,
        history=points
    )
