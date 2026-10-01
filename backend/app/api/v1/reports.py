from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.domain import Product, ProductSpecification
from app.schemas.reports import ReportRequest, ReportSchema
from app.core.comparison import generate_comparison_matrix
from app.core.llm import generate_report

router = APIRouter()

@router.post("/compare/", response_model=ReportSchema)
async def generate_comparison_report(request: ReportRequest, db: AsyncSession = Depends(get_db)):
    if len(request.product_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 products are required for comparison.")
    if request.baseline_id not in request.product_ids:
        raise HTTPException(status_code=400, detail="baseline_id must be included in product_ids.")
        
    query = (
        select(Product)
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.specifications).selectinload(ProductSpecification.attribute),
            selectinload(Product.specifications).selectinload(ProductSpecification.evidence)
        )
        .where(Product.id.in_(request.product_ids))
    )
    result = await db.execute(query)
    products = result.scalars().all()
    
    if len(products) != len(request.product_ids):
        raise HTTPException(status_code=404, detail="One or more products not found.")
        
    try:
        matrix = generate_comparison_matrix(products, request.baseline_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    matrix_json = matrix.model_dump_json()
    
    try:
        report = generate_report(matrix_json)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")
