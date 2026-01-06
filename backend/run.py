#!/usr/bin/env python3
"""
CityVotes Backend API Server
Run with: python run.py
"""

import uvicorn
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           CityVotes POC - Backend API Server                 ║
╠══════════════════════════════════════════════════════════════╣
║  API running at: http://localhost:8000                       ║
║  API Docs at: http://localhost:8000/docs                     ║
║  Health check: http://localhost:8000/health                  ║
║                                                              ║
║  Press Ctrl+C to stop the server                             ║
╚══════════════════════════════════════════════════════════════╝
""")

    print("Make sure PostgreSQL is running!")
    print("Default connection: postgresql://cityvotes:cityvotes@localhost:5432/cityvotes")
    print()

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
