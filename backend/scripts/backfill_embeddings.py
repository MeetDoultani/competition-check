import asyncio
import sys
import os

# Ensure the backend directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.domain import Product, ProductEmbedding, ProductSpecification
from app.core.search import build_product_document, generate_embedding

async def backfill():
    async with AsyncSessionLocal() as session:
        print("Fetching products from database...")
        # Eagerly load all relationships required by build_product_document
        query = (
            select(Product)
            .options(
                selectinload(Product.brand),
                selectinload(Product.category),
                selectinload(Product.features),
                selectinload(Product.specifications).selectinload(ProductSpecification.attribute)
            )
        )
        result = await session.execute(query)
        products = result.scalars().all()
        
        if not products:
            print("No products found to backfill.")
            return

        print(f"Found {len(products)} products. Checking existing embeddings...")
        
        # Fetch existing product IDs that already have an embedding
        existing_query = select(ProductEmbedding.product_id)
        existing_result = await session.execute(existing_query)
        existing_ids = set(existing_result.scalars().all())

        new_embeddings = 0
        for p in products:
            if p.id in existing_ids:
                print(f"Skipping '{p.name}' - Embedding already exists.")
                continue
                
            print(f"Processing '{p.name}'...")
            
            # 1. Concatenate the rich document text
            doc_text = build_product_document(p)
            
            # 2. Generate the 384-d vector locally
            vector = generate_embedding(doc_text)
            
            # 3. Create the DB record
            embedding_record = ProductEmbedding(
                product_id=p.id,
                embedding=vector
            )
            session.add(embedding_record)
            new_embeddings += 1

        if new_embeddings > 0:
            print(f"Committing {new_embeddings} new embeddings to Supabase (pgvector)...")
            await session.commit()
            print("Backfill complete!")
        else:
            print("No new embeddings were needed.")

if __name__ == "__main__":
    asyncio.run(backfill())
