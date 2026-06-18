import os
import logging
import time
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.database.session import SessionLocal
from app.api.routes import auth, customers, churn, retention, dashboard, metrics

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("app_main")

# --- Redis Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client: redis.Redis = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown.
    Fix: Using synchronous 'with' for SQLAlchemy SessionLocal.
    """
    global redis_client
    logger.info("Starting application lifecycle...")
    
    # 1. Initialize Redis (Async client remains async)
    try:
        redis_client = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Successfully connected to Redis.")
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
    
    # 2. Verify Database Connection (Sync session uses 'with', no 'await')
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        logger.info("Successfully verified Database connection via synchronous session.")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")

    yield
    
    # Shutdown
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed.")
    logger.info("Application lifecycle terminated.")

# --- App Initialization ---
app = FastAPI(
    title="AI Churn Intelligence Platform",
    description="Enterprise-grade Customer Analytics and Prescriptive Retention System.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- Exception Handling ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Contact system administrator."},
    )

# --- Routes ---
API_V1_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_V1_PREFIX)
app.include_router(customers.router, prefix=API_V1_PREFIX)
app.include_router(churn.router, prefix=API_V1_PREFIX)
app.include_router(retention.router, prefix=API_V1_PREFIX)
app.include_router(dashboard.router, prefix=API_V1_PREFIX)
app.include_router(metrics.router, prefix=API_V1_PREFIX)
@app.get("/")
def root():
    return {"message": "RetentionIQ API is running 🚀"}
# --- Health Check ---
@app.get("/health", tags=["System"])
async def health_check():
    health_status = {"status": "healthy", "components": {}}
    
    try:
        # Sync DB check
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        health_status["components"]["database"] = "up"
    except Exception:
        health_status["components"]["database"] = "down"
        health_status["status"] = "degraded"
        
    try:
        # Async Redis check
        await redis_client.ping()
        health_status["components"]["redis"] = "up"
    except Exception:
        health_status["components"]["redis"] = "down"
        health_status["status"] = "degraded"

    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)