"""
Backend configuration settings
"""
import os

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://cityvotes:cityvotes@localhost:5432/cityvotes"
)

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Session settings
SESSION_EXPIRE_HOURS = 2

# API settings
API_PREFIX = "/api"
