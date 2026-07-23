from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_posts import router as posts_router
from app.api.routes_stats import router as stats_router

app = FastAPI(
    title="BrandPulse API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Later replace * with your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(posts_router)
app.include_router(stats_router)


@app.get("/")
async def root():
    return {"message": "BrandPulse API is running"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "BrandPulse",
    }