from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.models.domain import Product, ProductEmbedding, ProductSpecification
from app.core.search import generate_embedding
from app.schemas.product import ProductResponse, BrandResponse, CategoryResponse, ProductSpecificationResponse

class SearchResultResponse(BaseModel):
    product: ProductResponse
    similarity_score: float

router = APIRouter()

@router.get("/", response_model=List[SearchResultResponse])
async def semantic_search(
    query: str = Query(..., description="Semantic search query"),
    limit: int = Query(5, ge=1, le=50, description="Max results to return"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    threshold: float = Query(0.7, description="Maximum cosine distance threshold"),
    db: AsyncSession = Depends(get_db)
):
    query_embedding = generate_embedding(query)
    
    stmt = (
        select(Product, ProductEmbedding.embedding.cosine_distance(query_embedding).label("distance"))
        .join(ProductEmbedding, Product.id == ProductEmbedding.product_id)
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.specifications).selectinload(ProductSpecification.attribute),
            selectinload(Product.specifications).selectinload(ProductSpecification.evidence)
        )
        .where(ProductEmbedding.embedding.cosine_distance(query_embedding) < threshold)
    )
    
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
        
    stmt = stmt.order_by("distance").limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    response = []
    for product, distance in rows:
        specs_resp = []
        for s in product.specifications:
            val = s.value_numeric if s.value_numeric is not None else (s.value_boolean if s.value_boolean is not None else s.value_text)
            specs_resp.append(ProductSpecificationResponse(
                id=s.id,
                attribute_name=s.attribute.name if s.attribute else "Unknown",
                value=val,
                unit=s.attribute.unit if s.attribute else None,
                presence_state=s.presence_state,
                evidence_snippet=s.evidence.snippet if s.evidence else None
            ))
            
        product_resp = ProductResponse(
            id=product.id,
            name=product.name,
            url=product.url,
            brand=BrandResponse.model_validate(product.brand),
            category=CategoryResponse.model_validate(product.category),
            specifications=specs_resp
        )
        
        similarity_score = 1.0 - float(distance)
        
        response.append(SearchResultResponse(
            product=product_resp,
            similarity_score=similarity_score
        ))
        
    return response
