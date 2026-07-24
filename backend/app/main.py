import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_posts import router as posts_router
from app.api.routes_stats import router as stats_router
from app.database.session import init_db
from app.ingestion.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize database tables
    init_db()

    # 2. Start scheduler without blocking FastAPI startup
    # Option A: If start_scheduler() is non-blocking or asynchronous:
    asyncio.create_task(asyncio.to_thread(start_scheduler))

    yield  # <-- FastAPI starts accepting traffic RIGHT HERE!

    stop_scheduler()


app = FastAPI(
    title="BrandPulse API",
    version="0.1.0",
    lifespan=lifespan,
)

# ... rest of your routes and middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later replace * with your React frontend URL
    allow_credentials=False,
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