"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from app import config
from app.cache import TMDBCache
from app.routes import upload, status, download

# Global cache instance
_cache: TMDBCache = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global _cache
    _cache = TMDBCache()
    yield
    # Save cache on shutdown
    _cache.save()


# Create app
app = FastAPI(
    title="Letterboxd Stats API",
    version="1.0.0",
    lifespan=lifespan
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


def get_shared_cache() -> dict:
    """Get shared cache data for dependency injection."""
    return _cache.get_data()


def notify_cache_dirty(new_count: int = 1):
    """Notify cache manager of changes."""
    _cache.mark_dirty(new_count)

def force_save_cache():
    """Force save cache to disk."""
    if _cache:
        _cache.force_save()


def get_cache_size() -> int:
    """Get cache size for health check."""
    return _cache.size() if _cache else 0


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "cache_size": get_cache_size()}
