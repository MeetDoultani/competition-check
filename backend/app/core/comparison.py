from typing import List, Dict, Any, Optional
from uuid import UUID
from app.models.domain import Product, DataType, PresenceState
from app.schemas.comparison import (
    ComparisonMatrixResponse, 
    AttributeRow, 
    ProductAttributeValue, 
    DeltaInfo
)
from app.schemas.product import ProductResponse, BrandResponse, CategoryResponse, ProductSpecificationResponse

def generate_comparison_matrix(products: List[Product], baseline_id: UUID) -> ComparisonMatrixResponse:
    # 1. Map products by ID
    product_map = {p.id: p for p in products}
    if baseline_id not in product_map:
        raise ValueError(f"Baseline product {baseline_id} not found in provided products")

    # 2. Gather union of all attributes across all products
    # attribute_id -> { 'name': str, 'type': DataType, 'unit': str }
    attribute_meta: Dict[UUID, Dict[str, Any]] = {}
    
    # product_id -> attribute_id -> Specification
    product_specs: Dict[UUID, Dict[UUID, Any]] = {p.id: {} for p in products}
    
    for p in products:
        for spec in p.specifications:
            attr_id = spec.attribute_id or spec.attribute.id
            if attr_id not in attribute_meta:
                attribute_meta[attr_id] = {
                    'name': spec.attribute.name,
                    'data_type': spec.attribute.data_type,
                    'unit': spec.attribute.unit
                }
            product_specs[p.id][attr_id] = spec

    # 3. Build Attribute Rows
    attribute_rows: List[AttributeRow] = []
    
    for attr_id, meta in attribute_meta.items():
        row_values: List[ProductAttributeValue] = []
        
        # Get baseline value for this attribute
        baseline_spec = product_specs[baseline_id].get(attr_id)
        baseline_val = _extract_value(baseline_spec) if baseline_spec else None
        
        for p in products:
            spec = product_specs[p.id].get(attr_id)
            target_val = _extract_value(spec) if spec else None
            presence = spec.presence_state if spec else PresenceState.UNKNOWN
            snippet = spec.evidence.snippet if spec and spec.evidence else None
            
            # Calculate Delta if numeric
            delta = None
            if meta['data_type'] == DataType.numeric and target_val is not None and baseline_val is not None:
                # Ensure both are numeric types (int/float)
                if isinstance(target_val, (int, float)) and isinstance(baseline_val, (int, float)):
                    raw_diff = float(target_val - baseline_val)
                    pct_change = None
                    if baseline_val != 0:
                        pct_change = (raw_diff / float(baseline_val)) * 100
                    
                    delta = DeltaInfo(raw_diff=raw_diff, percentage_change=pct_change)
            
            row_values.append(ProductAttributeValue(
                product_id=p.id,
                value=target_val,
                presence_state=presence,
                evidence_snippet=snippet,
                delta=delta
            ))
            
        attribute_rows.append(AttributeRow(
            attribute_id=attr_id,
            attribute_name=meta['name'],
            data_type=meta['data_type'],
            unit=meta['unit'],
            values=row_values
        ))
    
    # 4. Serialize Product Models for Response
    product_responses = []
    for p in products:
        specs_resp = []
        for s in p.specifications:
            specs_resp.append(ProductSpecificationResponse(
                id=s.id,
                attribute_name=s.attribute.name,
                value=_extract_value(s),
                unit=s.attribute.unit,
                presence_state=s.presence_state,
                evidence_snippet=s.evidence.snippet if s.evidence else None
            ))
            
        product_responses.append(ProductResponse(
            id=p.id,
            name=p.name,
            url=p.url,
            brand=BrandResponse.model_validate(p.brand),
            category=CategoryResponse.model_validate(p.category),
            specifications=specs_resp
        ))

    return ComparisonMatrixResponse(
        baseline_product_id=baseline_id,
        products=product_responses,
        attributes=attribute_rows
    )

def _extract_value(spec: Any) -> Any:
    if spec.value_numeric is not None:
        return spec.value_numeric
    if spec.value_boolean is not None:
        return spec.value_boolean
    return spec.value_text
