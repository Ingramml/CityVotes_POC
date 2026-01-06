"""
Session management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from uuid import UUID
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from api.models.database import get_db
from api.models.session import Session, SessionData

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{session_id}")
async def get_session(session_id: str, db: DBSession = Depends(get_db)):
    """Get session info"""
    try:
        session = db.query(Session).filter(Session.id == UUID(session_id)).first()
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    cities = [sd.city_key for sd in session.data]

    return {
        "success": True,
        "session_id": str(session.id),
        "created_at": session.created_at.isoformat(),
        "cities": cities
    }


@router.get("/{session_id}/cities")
async def get_session_cities(session_id: str, db: DBSession = Depends(get_db)):
    """List cities with data in this session"""
    try:
        session = db.query(Session).filter(Session.id == UUID(session_id)).first()
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    cities = []
    for sd in session.data:
        cities.append({
            "city_key": sd.city_key,
            "filename": sd.original_filename,
            "uploaded_at": sd.upload_timestamp.isoformat(),
            "total_votes": sd.processed_data.get('vote_summary', {}).get('total_votes', 0)
        })

    return {
        "success": True,
        "session_id": str(session.id),
        "cities": cities
    }
