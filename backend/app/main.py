from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import products, compare, search, prices, reports
from app.core.database import engine, Base

app = FastAPI(title="Competitive Intelligence Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(compare.router, prefix="/api/v1/compare", tags=["compare"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
app.include_router(prices.router, prefix="/api/v1/prices", tags=["prices"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
