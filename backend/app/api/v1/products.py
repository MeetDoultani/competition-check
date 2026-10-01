from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.domain import Product, AttributeTemplate, Evidence, ProductSpecification
from app.schemas.product import ProductResponse, ProductSpecificationResponse, BrandResponse, CategoryResponse
from app.schemas.ingestion import URLIngestRequest

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def list_products(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    query = (
        select(Product)
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.specifications).selectinload(ProductSpecification.attribute),
            selectinload(Product.specifications).selectinload(ProductSpecification.evidence)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    products = result.scalars().all()
    
    response = []
    for p in products:
        specs = []
        for s in p.specifications:
            val = s.value_numeric if s.value_numeric is not None else (s.value_boolean if s.value_boolean is not None else s.value_text)
            specs.append(ProductSpecificationResponse(
                id=s.id,
                attribute_name=s.attribute.name if s.attribute else "Unknown",
                value=val,
                unit=s.attribute.unit if s.attribute else None,
                presence_state=s.presence_state,
                evidence_snippet=s.evidence.snippet if s.evidence else None
            ))
            
        response.append(ProductResponse(
            id=p.id,
            name=p.name,
            url=p.url,
            brand=BrandResponse.model_validate(p.brand),
            category=CategoryResponse.model_validate(p.category),
            specifications=specs
        ))
    return response

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    query = (
        select(Product)
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.specifications).selectinload(ProductSpecification.attribute),
            selectinload(Product.specifications).selectinload(ProductSpecification.evidence)
        )
        .where(Product.id == product_id)
    )
    result = await db.execute(query)
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
        
    specs = []
    for s in p.specifications:
        val = s.value_numeric if s.value_numeric is not None else (s.value_boolean if s.value_boolean is not None else s.value_text)
        specs.append(ProductSpecificationResponse(
            id=s.id,
            attribute_name=s.attribute.name if s.attribute else "Unknown",
            value=val,
            unit=s.attribute.unit if s.attribute else None,
            presence_state=s.presence_state,
            evidence_snippet=s.evidence.snippet if s.evidence else None
        ))
        
    return ProductResponse(
        id=p.id,
        name=p.name,
        url=p.url,
        brand=BrandResponse.model_validate(p.brand),
        category=CategoryResponse.model_validate(p.category),
        specifications=specs
    )

@router.post("/ingest-url", status_code=status.HTTP_202_ACCEPTED)
async def ingest_url(request: URLIngestRequest, db: AsyncSession = Depends(get_db)):
    return {"message": "URL accepted for ingestion", "url": str(request.url)}
