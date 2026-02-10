"""FastAPI application entry point."""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app import config
from app.routes import upload, status, download
from app.workers import cleanup_old_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(cleanup_old_jobs())
    yield
    task.cancel()


# Create app
app = FastAPI(
    title="Letterboxd Stats API",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(download.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
