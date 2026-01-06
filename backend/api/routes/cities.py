"""
City configuration API endpoints
"""
from fastapi import APIRouter
import sys
import os

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents import CityConfigAgent

router = APIRouter(prefix="/cities", tags=["cities"])

# Initialize city config agent
city_config = CityConfigAgent()


@router.get("")
async def list_cities():
    """List all configured cities"""
    cities = city_config.get_all_cities()
    return {
        "success": True,
        "cities": cities,
        "total": len(cities)
    }


@router.get("/{city_key}")
async def get_city(city_key: str):
    """Get configuration for a specific city"""
    config = city_config.get_city_config(city_key)
    if not config:
        return {
            "success": False,
            "error": f"City '{city_key}' not found"
        }
    return {
        "success": True,
        "city": config
    }
