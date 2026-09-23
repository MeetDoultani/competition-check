from fastapi import FastAPI
from app.api.v1 import products, compare
from app.core.database import engine, Base

app = FastAPI(title="Competitive Intelligence Platform API")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["compare"])
