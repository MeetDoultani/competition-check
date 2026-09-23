import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class DataType(str, Enum):
    numeric = "numeric"
    boolean = "boolean"
    string = "string"

class PresenceState(str, Enum):
    PRESENT = "PRESENT"
    VERIFIED_ABSENT = "VERIFIED_ABSENT"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"

class Brand(Base):
    __tablename__ = "brands"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    products = relationship("Product", back_populates="brand")

class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    attribute_templates = relationship("AttributeTemplate", back_populates="category")
    products = relationship("Product", back_populates="category")

class AttributeTemplate(Base):
    __tablename__ = "attribute_templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    data_type = Column(SQLEnum(DataType), nullable=False)
    unit = Column(String, nullable=True)
    category = relationship("Category", back_populates="attribute_templates")

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products")
    specifications = relationship("ProductSpecification", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
    prices = relationship("PriceObservation", back_populates="product", cascade="all, delete-orphan")
    embedding = relationship("ProductEmbedding", uselist=False, back_populates="product", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, nullable=False)
    snippet = Column(Text, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow)

class ProductSpecification(Base):
    __tablename__ = "product_specifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    attribute_id = Column(UUID(as_uuid=True), ForeignKey("attribute_templates.id"), nullable=False)
    value_text = Column(String, nullable=True)
    value_numeric = Column(Float, nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    presence_state = Column(SQLEnum(PresenceState), default=PresenceState.UNKNOWN, nullable=False)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=True)
    
    product = relationship("Product", back_populates="specifications")
    attribute = relationship("AttributeTemplate")
    evidence = relationship("Evidence")

class ProductFeature(Base):
    __tablename__ = "product_features"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    feature_text = Column(Text, nullable=False)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=True)
    
    product = relationship("Product", back_populates="features")
    evidence = relationship("Evidence")

class PriceObservation(Base):
    __tablename__ = "price_observations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    source_url = Column(String, nullable=False)
    observed_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="prices")

class ProductEmbedding(Base):
    __tablename__ = "product_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, unique=True)
    embedding = Column(Vector(384))
    
    product = relationship("Product", back_populates="embedding")
