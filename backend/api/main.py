"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import CORS_ORIGINS, API_PREFIX
from api.models.database import init_db
from api.routes import cities_router, upload_router, sessions_router, dashboard_router

# Create FastAPI app
app = FastAPI(
    title="CityVotes API",
    description="API for municipal voting data analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cities_router, prefix=API_PREFIX)
app.include_router(upload_router, prefix=API_PREFIX)
app.include_router(sessions_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix=API_PREFIX)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "CityVotes API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "cities": f"{API_PREFIX}/cities",
            "upload": f"{API_PREFIX}/upload",
            "sessions": f"{API_PREFIX}/sessions",
            "dashboard": f"{API_PREFIX}/dashboard"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
