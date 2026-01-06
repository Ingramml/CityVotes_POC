"""
Dashboard data API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from uuid import UUID
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from api.models.database import get_db
from api.models.session import Session, SessionData
from api.services.vote_analyzer import VoteAnalyzer
from api.services.member_analyzer import MemberAnalyzer
from agents import CityConfigAgent

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
city_config = CityConfigAgent()


def get_session_data(session_id: str, city_key: str, db: DBSession):
    """Helper to get session data or raise 404"""
    try:
        session_data = db.query(SessionData).filter(
            SessionData.session_id == UUID(session_id),
            SessionData.city_key == city_key
        ).first()
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session_data:
        raise HTTPException(status_code=404, detail=f"No data found for city '{city_key}' in this session")

    return session_data


@router.get("/{session_id}/{city_key}/summary")
async def get_vote_summary(session_id: str, city_key: str, db: DBSession = Depends(get_db)):
    """Get vote summary dashboard data"""
    session_data = get_session_data(session_id, city_key, db)
    processed = session_data.processed_data

    result = VoteAnalyzer.calculate_vote_summary(processed)

    return {
        "success": True,
        "city_info": processed.get('city_info', {}),
        "vote_summary": result['vote_summary'],
        "member_participation": result['member_participation'],
        "total_members": result['total_members'],
        "active_members": result['active_members'],
        "upload_info": {
            "filename": session_data.original_filename,
            "uploaded_at": session_data.upload_timestamp.isoformat()
        }
    }


@router.get("/{session_id}/{city_key}/members")
async def get_member_analysis(session_id: str, city_key: str, db: DBSession = Depends(get_db)):
    """Get member analysis dashboard data"""
    session_data = get_session_data(session_id, city_key, db)
    processed = session_data.processed_data
    raw = session_data.raw_data

    member_analysis = processed.get('member_analysis', {})
    raw_votes = raw.get('votes', [])

    alignment_data = MemberAnalyzer.calculate_alignment_matrix(member_analysis, raw_votes)
    most_aligned, least_aligned = MemberAnalyzer.get_aligned_pairs(alignment_data)

    return {
        "success": True,
        "city_info": processed.get('city_info', {}),
        "member_analysis": member_analysis,
        "alignment_data": alignment_data,
        "most_aligned": most_aligned,
        "least_aligned": least_aligned
    }


@router.get("/{session_id}/{city_key}/members/{member_name}")
async def get_member_profile(session_id: str, city_key: str, member_name: str, db: DBSession = Depends(get_db)):
    """Get individual member profile data"""
    session_data = get_session_data(session_id, city_key, db)
    processed = session_data.processed_data
    raw = session_data.raw_data

    member_analysis = processed.get('member_analysis', {})
    raw_votes = raw.get('votes', [])

    profile = MemberAnalyzer.get_member_profile(member_name, member_analysis, raw_votes)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Member '{member_name}' not found")

    return {
        "success": True,
        "member_name": member_name,
        "city_info": processed.get('city_info', {}),
        "member_stats": profile['member_stats'],
        "vote_history": profile['vote_history'],
        "agreements": profile['agreements']
    }


@router.get("/{session_id}/{city_key}/agenda-items")
async def get_agenda_items(session_id: str, city_key: str, db: DBSession = Depends(get_db)):
    """Get agenda items grouped by meeting"""
    session_data = get_session_data(session_id, city_key, db)
    processed = session_data.processed_data
    raw = session_data.raw_data

    meetings = VoteAnalyzer.get_agenda_items_grouped(raw)

    return {
        "success": True,
        "city_info": processed.get('city_info', {}),
        "meetings": meetings,
        "total_items": len(raw.get('votes', []))
    }


@router.get("/{session_id}/{city_key}/agenda-items/{item_id}")
async def get_agenda_item_detail(session_id: str, city_key: str, item_id: str, db: DBSession = Depends(get_db)):
    """Get details for a specific agenda item"""
    session_data = get_session_data(session_id, city_key, db)
    processed = session_data.processed_data
    raw = session_data.raw_data

    detail = VoteAnalyzer.get_agenda_item_detail(raw, item_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Agenda item '{item_id}' not found")

    return {
        "success": True,
        "city_info": processed.get('city_info', {}),
        "item": detail['item'],
        "member_votes": detail['member_votes']
    }


@router.get("/{session_id}/comparison")
async def get_city_comparison(session_id: str, db: DBSession = Depends(get_db)):
    """Get comparison data for all cities in session"""
    try:
        session = db.query(Session).filter(Session.id == UUID(session_id)).first()
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if len(session.data) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 cities for comparison")

    comparison_data = {}
    comparison_metrics = {}

    for sd in session.data:
        city_key = sd.city_key
        processed = sd.processed_data
        city_cfg = city_config.get_city_config(city_key)

        if city_cfg:
            vote_summary = processed.get('vote_summary', {})
            member_analysis = processed.get('member_analysis', {})

            comparison_data[city_key] = {
                'display_name': city_cfg['display_name'],
                'colors': city_cfg['colors'],
                'council_size': city_cfg['total_seats'],
                'vote_summary': vote_summary,
                'member_count': len(member_analysis),
                'upload_filename': sd.original_filename,
                'upload_time': sd.upload_timestamp.isoformat()
            }

            total_votes = vote_summary.get('total_votes', 0)
            outcomes = vote_summary.get('outcomes', {})
            pass_count = outcomes.get('PASS', {}).get('count', 0)

            comparison_metrics[city_key] = {
                'pass_rate': round((pass_count / total_votes * 100) if total_votes > 0 else 0, 1),
                'votes_per_member': round(total_votes / len(member_analysis) if member_analysis else 0, 1),
                'council_efficiency': round(len(member_analysis) / city_cfg['total_seats'] * 100, 1)
            }

    return {
        "success": True,
        "comparison_data": comparison_data,
        "comparison_metrics": comparison_metrics,
        "cities_count": len(comparison_data)
    }
