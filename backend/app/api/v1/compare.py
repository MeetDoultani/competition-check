from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.domain import Product
from app.schemas.comparison import ComparisonMatrixResponse
from app.core.comparison import generate_comparison_matrix

router = APIRouter()

@router.get("/", response_model=ComparisonMatrixResponse)
async def compare_products(
    product_ids: List[UUID] = Query(..., description="List of product UUIDs to compare"),
    baseline_id: UUID = Query(..., description="UUID of the baseline product for delta calculations"),
    db: AsyncSession = Depends(get_db)
):
    if len(product_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 products are required for comparison.")
    if baseline_id not in product_ids:
        raise HTTPException(status_code=400, detail="baseline_id must be included in product_ids.")
        
    query = (
        select(Product)
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.specifications).selectinload(Product.attribute),
            selectinload(Product.specifications).selectinload(Product.evidence)
        )
        .where(Product.id.in_(product_ids))
    )
    result = await db.execute(query)
    products = result.scalars().all()
    
    if len(products) != len(product_ids):
        found_ids = {p.id for p in products}
        missing_ids = set(product_ids) - found_ids
        raise HTTPException(status_code=404, detail=f"Products not found: {missing_ids}")
        
    try:
        matrix = generate_comparison_matrix(products, baseline_id)
        return matrix
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
