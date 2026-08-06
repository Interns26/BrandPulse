from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.vulnerability import router as vulnerability_router
from app.api.routes_posts import router as posts_router
from app.api.routes_stats import router as stats_router
from app.api.articles import router as articles_router
from app.database.session import init_db
from app.ingestion.scheduler import start_scheduler, stop_scheduler,scheduled_competitive_ingestion_job
from app.services.vulnerability_service import run_competitive_intelligence_job

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize database tables
    init_db()

    # 2. Start background scheduler
    start_scheduler()

    yield

    # 3. Stop scheduler during application shutdown
    stop_scheduler()


app = FastAPI(
    title="BrandPulse API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router)
app.include_router(stats_router)
app.include_router(articles_router)
app.include_router(vulnerability_router)

@app.get("/")
async def root():
    return {"message": "BrandPulse API is running"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "BrandPulse",
    }


@app.post("/api/test/competitive-ingestion")
def test_competitive_ingestion():
    scheduled_competitive_ingestion_job()

    return {
        "message": "Competitive ingestion + intelligence job completed"
    }