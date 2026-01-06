"""
File upload API endpoint
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
import json
import sys
import os

# Add parent paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents import DataValidationAgent, CityConfigAgent, FileProcessingAgent
from api.models.database import get_db
from api.models.session import Session, SessionData

router = APIRouter(prefix="/upload", tags=["upload"])

# Initialize agents
data_validator = DataValidationAgent()
city_config = CityConfigAgent()
file_processor = FileProcessingAgent(data_validator, city_config)


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    city_key: str = Form(...),
    session_id: str = Form(None),
    db: DBSession = Depends(get_db)
):
    """Upload and process a vote data JSON file"""
    # Validate city
    city_cfg = city_config.get_city_config(city_key)
    if not city_cfg:
        raise HTTPException(status_code=400, detail=f"Unknown city: {city_key}")

    # Read and parse file
    try:
        content = await file.read()
        file_data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Validate data structure
    validation = data_validator.validate_json(file_data)
    if not validation['valid']:
        raise HTTPException(
            status_code=400,
            detail=f"Validation failed: {'; '.join(validation['errors'])}"
        )

    # Process the data
    processed = file_processor._process_data(file_data, city_key)

    # Get or create session
    if session_id:
        try:
            from uuid import UUID
            session = db.query(Session).filter(Session.id == UUID(session_id)).first()
        except:
            session = None
    else:
        session = None

    if not session:
        session = Session()
        db.add(session)
        db.flush()

    # Check if data already exists for this city in session
    existing = db.query(SessionData).filter(
        SessionData.session_id == session.id,
        SessionData.city_key == city_key
    ).first()

    if existing:
        # Update existing
        existing.original_filename = file.filename
        existing.raw_data = file_data
        existing.processed_data = processed
    else:
        # Create new
        session_data = SessionData(
            session_id=session.id,
            city_key=city_key,
            original_filename=file.filename,
            raw_data=file_data,
            processed_data=processed
        )
        db.add(session_data)

    db.commit()

    return {
        "success": True,
        "session_id": str(session.id),
        "city_key": city_key,
        "filename": file.filename,
        "total_votes": len(file_data.get('votes', [])),
        "message": f"Successfully uploaded {file.filename} for {city_cfg['display_name']}"
    }
