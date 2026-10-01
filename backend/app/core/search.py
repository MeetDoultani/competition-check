from sentence_transformers import SentenceTransformer
from app.models.domain import Product
from typing import List

# Global model instance for reuse
_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def build_product_document(product: Product) -> str:
    """Concatenates product attributes into a rich text document for embedding."""
    parts = []
    parts.append(f"Category: {product.category.name if product.category else 'Unknown'}")
    parts.append(f"Brand: {product.brand.name if product.brand else 'Unknown'}")
    parts.append(f"Name: {product.name}")
    
    specs_parts = []
    for spec in product.specifications:
        val = spec.value_text if spec.value_text is not None else (
            spec.value_numeric if spec.value_numeric is not None else spec.value_boolean
        )
        if val is not None:
            attr_name = spec.attribute.name if spec.attribute else 'Unknown'
            unit = spec.attribute.unit if spec.attribute and spec.attribute.unit else ''
            specs_parts.append(f"{attr_name}: {val}{unit}")
    
    if specs_parts:
        parts.append(f"Specs: {', '.join(specs_parts)}")
        
    features_parts = []
    for feature in product.features:
        features_parts.append(feature.feature_text)
        
    if features_parts:
        parts.append(f"Features: {', '.join(features_parts)}")
        
    return " | ".join(parts)

def generate_embedding(text: str) -> List[float]:
    """Generates a 384-dimensional dense vector using all-MiniLM-L6-v2."""
    model = get_model()
    # model.encode returns a numpy array, we convert to list of floats for pgvector
    return model.encode(text).tolist()
