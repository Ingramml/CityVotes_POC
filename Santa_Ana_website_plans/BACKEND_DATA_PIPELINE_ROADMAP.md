# Santa Ana Data Pipeline - Backend Processing System Roadmap

## **Executive Overview**

This roadmap details the development of a robust backend data processing pipeline that extracts, processes, and delivers Santa Ana City Council voting data to the Vercel-hosted website. The pipeline transforms raw meeting documents into structured JSON APIs that seamlessly integrate with the website's data requirements.

## **Project Vision & Goals**

### **Primary Mission**
Create an automated, accurate, and scalable data processing pipeline that converts Santa Ana meeting documents into clean, structured voting data accessible via JSON API endpoints for website consumption.

### **Core Responsibilities**
- **Document Processing**: Extract votes from PDF agendas and minutes
- **Data Standardization**: Clean and validate extracted voting records
- **API Generation**: Provide JSON endpoints matching website schema
- **Quality Assurance**: Maintain 90%+ extraction accuracy
- **Automation**: Process new meetings with minimal manual intervention

### **Integration Strategy**
- **Output Format**: JSON APIs matching exact website data schema
- **Deployment**: Independent backend system with public API endpoints
- **Data Flow**: Raw documents → Processed data → JSON API → Website consumption
- **Real-time Updates**: New meetings processed and available within hours

## **Technical Architecture**

### **Core Technology Stack**
```python
# Backend Processing
Python 3.11+
FastAPI (for API endpoints)
SQLAlchemy (ORM for data management)
PostgreSQL (primary data storage)
Redis (caching and job queues)

# Document Processing
PyPDF2 / pdfplumber (PDF text extraction)
spaCy / NLTK (natural language processing)
scikit-learn (ML classification)
Pandas (data manipulation)

# Infrastructure
Docker (containerization)
Celery (background task processing)
nginx (reverse proxy)
Cloud deployment (AWS/GCP/Azure)

# API & Integration
FastAPI (REST API framework)
Pydantic (data validation)
CORS support for Vercel website
OpenAPI/Swagger documentation
```

### **System Architecture**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ Document Input  │────│ Processing       │────│ API Output          │
│                 │    │ Pipeline         │    │                     │
│ • PDF Files     │    │ • Text           │    │ • JSON Endpoints    │
│ • Agendas       │    │   Extraction     │    │ • CORS Enabled      │
│ • Minutes       │    │ • Vote Detection │    │ • Website Schema    │
│ • Auto-Ingestion│    │ • Data Cleaning  │    │ • Real-time Updates │
└─────────────────┘    │ • Quality Scoring│    └─────────────────────┘
                       │ • Analytics Gen  │              │
                       └──────────────────┘              │
                                │                        │
                       ┌────────▼────────────────────────▼─────────┐
                       │ Data Storage & Management               │
                       │ • PostgreSQL (primary data)            │
                       │ • Redis (cache & jobs)                 │
                       │ • File storage (processed documents)   │
                       └─────────────────────────────────────────┘
```

### **Application Structure**
```
santa-ana-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration settings
│   │
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/                    # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── council.py         # Council member endpoints
│   │   │   ├── votes.py           # Vote data endpoints
│   │   │   ├── meetings.py        # Meeting endpoints
│   │   │   ├── analytics.py       # Analytics endpoints
│   │   │   └── export.py          # Data export endpoints
│   │   └── dependencies.py        # Shared API dependencies
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── document_processor.py  # Main processing engine
│   │   ├── vote_extractor.py      # Vote extraction logic
│   │   ├── data_validator.py      # Data validation & cleaning
│   │   ├── analytics_generator.py # Analytics computation
│   │   └── ml_models.py           # Machine learning models
│   │
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   ├── council.py             # Council member models
│   │   ├── meetings.py            # Meeting models
│   │   ├── votes.py               # Vote models
│   │   └── analytics.py           # Analytics models
│   │
│   ├── schemas/                   # Pydantic schemas (API contracts)
│   │   ├── __init__.py
│   │   ├── council.py             # Council member schemas
│   │   ├── votes.py               # Vote schemas
│   │   ├── meetings.py            # Meeting schemas
│   │   └── analytics.py           # Analytics schemas
│   │
│   ├── services/                  # Business services
│   │   ├── __init__.py
│   │   ├── document_service.py    # Document processing service
│   │   ├── vote_service.py        # Vote data service
│   │   ├── council_service.py     # Council member service
│   │   └── export_service.py      # Data export service
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── pdf_parser.py          # PDF parsing utilities
│       ├── text_cleaner.py        # Text cleaning functions
│       ├── pattern_matcher.py     # Vote pattern matching
│       └── quality_scorer.py      # Quality assessment
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_api/                  # API tests
│   ├── test_core/                 # Business logic tests
│   └── test_services/             # Service tests
│
├── alembic/                       # Database migrations
├── scripts/                       # Utility scripts
│   ├── import_existing_data.py    # Import current 12 meetings
│   ├── training_data_processor.py # Process manual parsing data
│   └── data_quality_report.py     # Generate quality reports
│
├── docker-compose.yml             # Development environment
├── Dockerfile                     # Production deployment
├── requirements.txt               # Python dependencies
└── README.md                      # Setup instructions
```

## **Development Phases**

### **Phase 1: Foundation & Data Import (Weeks 1-2)**

#### **Week 1: Project Setup & Database Design**

**Core Infrastructure Setup**
```python
# app/main.py - FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import council, votes, meetings, analytics

app = FastAPI(
    title="Santa Ana Votes API",
    description="Backend data pipeline for Santa Ana City Council voting analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Vercel website
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://santa-ana-votes.vercel.app",
        "https://*.vercel.app",
        "http://localhost:3000"  # Development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(council.router, prefix="/api/v1/council", tags=["council"])
app.include_router(votes.router, prefix="/api/v1/votes", tags=["votes"])
app.include_router(meetings.router, prefix="/api/v1/meetings", tags=["meetings"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
```

**Database Models (Shared Schema)**
```python
# models/votes.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True)  # e.g., "meeting-2024-01-16"
    date = Column(DateTime, nullable=False, index=True)
    meeting_type = Column(String, nullable=False)  # regular, special, joint_housing, emergency
    agenda_url = Column(String)
    minutes_url = Column(String)
    processed_date = Column(DateTime)
    total_votes = Column(Integer, default=0)
    meeting_duration = Column(Integer)  # minutes
    processing_status = Column(String, default="pending")  # pending, processing, completed, error

class Vote(Base):
    __tablename__ = "votes"

    id = Column(String, primary_key=True)  # e.g., "vote-2024-01-16-7-1"
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False, index=True)
    agenda_item_number = Column(String)
    title = Column(String, nullable=False, index=True)
    description = Column(Text)
    outcome = Column(String, nullable=False, index=True)  # Pass, Fail, Tie, Continued

    # Vote tallies
    tally_ayes = Column(Integer, default=0)
    tally_noes = Column(Integer, default=0)
    tally_abstain = Column(Integer, default=0)
    tally_absent = Column(Integer, default=0)
    tally_recused = Column(Integer, default=0)

    # Additional metadata
    motion_text = Column(Text)
    mover = Column(String)
    seconder = Column(String)

    # Quality metrics
    quality_score = Column(Float, nullable=False)  # 0.0 to 1.0
    extraction_confidence = Column(Float, nullable=False)

    # Member votes stored as JSON for flexibility
    member_votes = Column(JSON, nullable=False)  # {"member_id": {"position": "Aye", "name": "..."}}

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class CouncilMember(Base):
    __tablename__ = "council_members"

    id = Column(String, primary_key=True)  # e.g., "phil-bacerra"
    name = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # Mayor, Mayor Pro Tem, Council Member
    district = Column(Integer)
    term_start = Column(DateTime)
    term_end = Column(DateTime)
    active = Column(Boolean, default=True, index=True)
    photo_url = Column(String)
    bio_text = Column(Text)
    contact_info = Column(JSON)  # {"email": "...", "phone": "...", ...}
```

**API Schemas for Website Integration**
```python
# schemas/votes.py - Matches website TypeScript interfaces exactly
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from datetime import datetime

class MemberVote(BaseModel):
    position: Literal["Aye", "No", "Abstain", "Absent", "Recused"]
    member_id: str
    member_name: str
    recusal_reason: Optional[str] = None

class VoteResponse(BaseModel):
    """This schema EXACTLY matches the website's Vote interface"""
    id: str
    meeting_id: str = Field(alias="meetingId")
    agenda_item_number: str = Field(alias="agendaItemNumber")
    title: str
    description: str
    outcome: Literal["Pass", "Fail", "Tie", "Continued"]
    date: str  # ISO date string

    # Vote tallies
    tally_ayes: int = Field(alias="tallyAyes")
    tally_noes: int = Field(alias="tallyNoes")
    tally_abstain: int = Field(alias="tallyAbstain")
    tally_absent: int = Field(alias="tallyAbsent")
    tally_recused: Optional[int] = Field(alias="tallyRecused", default=0)

    # Member votes
    member_votes: Dict[str, MemberVote] = Field(alias="memberVotes")

    # Optional metadata
    motion_text: Optional[str] = Field(alias="motionText", default=None)
    mover: Optional[str] = None
    seconder: Optional[str] = None
    quality_score: float = Field(alias="qualityScore", ge=0, le=100)

    class Config:
        allow_population_by_field_name = True
```

**Week 1 Deliverables:**
- FastAPI application with CORS configured for Vercel website
- Complete database schema matching website requirements
- Pydantic schemas ensuring exact API contract compatibility
- Development environment with Docker Compose

#### **Week 2: Existing Data Import & API Endpoints**

**Import Existing 12 Meetings**
```python
# scripts/import_existing_data.py
import json
import os
from pathlib import Path
from app.models.votes import Meeting, Vote, CouncilMember
from app.core.data_validator import DataValidator
from datetime import datetime

class ExistingDataImporter:
    def __init__(self, db_session):
        self.db = db_session
        self.validator = DataValidator()

    def import_santa_ana_extraction_results(self):
        """Import all 12 meetings from santa_ana_extraction_results/"""
        results_dir = Path("../santa_ana_extraction_results")

        for json_file in results_dir.glob("*.json"):
            print(f"Processing {json_file.name}")

            with open(json_file) as f:
                data = json.load(f)

            # Extract meeting metadata
            meeting = self.create_meeting_record(data, json_file.stem)

            # Extract and validate votes
            votes = self.extract_votes_from_json(data, meeting.id)

            # Store in database
            self.db.add(meeting)
            for vote in votes:
                self.db.add(vote)

            self.db.commit()
            print(f"Imported {len(votes)} votes from {json_file.name}")

    def extract_votes_from_json(self, data, meeting_id):
        """Extract votes with improved quality scoring"""
        votes = []

        for vote_data in data.get("votes", []):
            # Standardize member names using known roster
            standardized_votes = self.standardize_member_votes(
                vote_data.get("member_votes", {})
            )

            vote = Vote(
                id=f"vote-{meeting_id}-{len(votes)+1}",
                meeting_id=meeting_id,
                title=vote_data.get("title", ""),
                description=vote_data.get("description", ""),
                outcome=vote_data.get("outcome", ""),
                tally_ayes=vote_data.get("tally_ayes", 0),
                tally_noes=vote_data.get("tally_noes", 0),
                member_votes=standardized_votes,
                quality_score=self.calculate_quality_score(vote_data),
                extraction_confidence=vote_data.get("confidence", 0.0)
            )

            votes.append(vote)

        return votes

    def calculate_quality_score(self, vote_data):
        """Calculate quality score based on data completeness"""
        score = 0.0

        # Title and outcome (essential - 40 points)
        if vote_data.get("title"): score += 20
        if vote_data.get("outcome") in ["Pass", "Fail", "Tie"]: score += 20

        # Vote tallies match member votes (30 points)
        member_votes = vote_data.get("member_votes", {})
        expected_total = vote_data.get("tally_ayes", 0) + vote_data.get("tally_noes", 0)
        actual_total = len([v for v in member_votes.values() if v.get("position") in ["Aye", "No"]])

        if expected_total > 0 and abs(expected_total - actual_total) <= 1:
            score += 30

        # Member identification (30 points)
        if len(member_votes) >= 5:  # Santa Ana typically has 7 members
            score += 30

        return min(score, 100.0)
```

**Core API Endpoints**
```python
# api/v1/votes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.schemas.votes import VoteResponse, VoteFilters
from app.services.vote_service import VoteService

router = APIRouter()

@router.get("/", response_model=List[VoteResponse])
async def get_votes(
    date_start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    members: Optional[List[str]] = Query(None, description="Filter by council member IDs"),
    outcome: Optional[str] = Query(None, description="Filter by vote outcome"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    vote_service: VoteService = Depends()
):
    """Get votes with filtering - EXACT same interface as website expects"""

    filters = VoteFilters(
        date_start=date_start,
        date_end=date_end,
        members=members,
        outcome=outcome,
        search=search
    )

    votes = await vote_service.get_votes(filters, limit, offset)

    # Transform to exact format expected by website
    return [VoteResponse.from_orm(vote) for vote in votes]

@router.get("/{vote_id}", response_model=VoteResponse)
async def get_vote(
    vote_id: str,
    vote_service: VoteService = Depends()
):
    """Get individual vote details"""
    vote = await vote_service.get_vote_by_id(vote_id)
    if not vote:
        raise HTTPException(status_code=404, detail="Vote not found")

    return VoteResponse.from_orm(vote)

# api/v1/council.py
@router.get("/", response_model=List[CouncilMemberResponse])
async def get_council_members(
    active_only: bool = Query(True, description="Only return active members"),
    council_service: CouncilService = Depends()
):
    """Get council members - matches website's getCouncilMembers() function"""
    members = await council_service.get_council_members(active_only)
    return [CouncilMemberResponse.from_orm(member) for member in members]

@router.get("/{member_id}", response_model=CouncilMemberDetailResponse)
async def get_council_member(
    member_id: str,
    council_service: CouncilService = Depends()
):
    """Get individual council member with voting statistics"""
    member = await council_service.get_member_with_stats(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Council member not found")

    return CouncilMemberDetailResponse.from_orm(member)
```

**Week 2 Deliverables:**
- Complete import of 12 existing meetings with quality scoring
- Functional REST API endpoints matching website schema
- Data validation and cleaning pipeline
- API documentation with OpenAPI/Swagger

### **Phase 2: Enhanced Extraction & ML Integration (Weeks 3-4)**

#### **Week 3: Pattern Recognition & Quality Improvement**

**Enhanced Vote Extraction Engine**
```python
# core/vote_extractor.py
import re
from typing import List, Dict, Optional, Tuple
from app.utils.pattern_matcher import SantaAnaPatternMatcher
from app.utils.text_cleaner import TextCleaner

class EnhancedVoteExtractor:
    def __init__(self):
        self.pattern_matcher = SantaAnaPatternMatcher()
        self.text_cleaner = TextCleaner()
        self.known_members = self.load_member_roster()

    def extract_votes_from_text(self, minutes_text: str, meeting_date: str) -> List[Dict]:
        """
        Extract votes using improved patterns specific to Santa Ana format
        Target: 85%+ accuracy (up from current 16.2%)
        """
        # Clean and prepare text
        cleaned_text = self.text_cleaner.clean_minutes_text(minutes_text)

        # Split into potential vote blocks
        vote_blocks = self.identify_vote_blocks(cleaned_text)

        votes = []
        for i, block in enumerate(vote_blocks):
            extracted_vote = self.extract_vote_from_block(block, meeting_date, i+1)
            if extracted_vote and self.validate_vote(extracted_vote):
                votes.append(extracted_vote)

        return votes

    def identify_vote_blocks(self, text: str) -> List[str]:
        """Find potential vote sections in minutes text"""
        # Santa Ana specific patterns
        vote_indicators = [
            r'MOTION.*?(?=MOTION|\n\n|\Z)',
            r'YES:\s*\d+.*?(?=YES:\s*\d+|\n\n|\Z)',
            r'Status:\s*\d+.*?(?=Status:|\n\n|\Z)',
        ]

        blocks = []
        for pattern in vote_indicators:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
            blocks.extend([match.group() for match in matches])

        return blocks

    def extract_vote_from_block(self, block: str, meeting_date: str, vote_num: int) -> Dict:
        """Extract structured vote data from a text block"""

        # Santa Ana specific vote pattern - corrected from original regex
        vote_pattern = r'YES:\s*(\d+)\s*[–-]\s*([^.]+?)\.?\s*NO:\s*(\d+).*?Status:\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(Pass|Fail)'

        match = re.search(vote_pattern, block, re.IGNORECASE | re.DOTALL)
        if not match:
            return None

        # Extract vote components
        yes_count = int(match.group(1))
        yes_names = match.group(2).strip()
        no_count = int(match.group(3))

        # Parse member names from YES votes
        member_votes = self.parse_member_names(yes_names, "Aye")

        # Extract motion/title from block context
        title = self.extract_motion_title(block)

        return {
            "id": f"vote-{meeting_date}-{vote_num}",
            "title": title,
            "outcome": "Pass" if yes_count > no_count else "Fail",
            "tally_ayes": yes_count,
            "tally_noes": no_count,
            "member_votes": member_votes,
            "raw_text": block[:500],  # Keep for debugging
            "extraction_confidence": self.calculate_confidence(match, member_votes)
        }

    def parse_member_names(self, names_text: str, position: str) -> Dict:
        """Parse member names and standardize against known roster"""
        # Split on commas and clean
        raw_names = [name.strip() for name in names_text.split(',')]

        member_votes = {}
        for raw_name in raw_names:
            # Match against known council members
            standardized_name = self.standardize_member_name(raw_name)
            if standardized_name:
                member_id = self.get_member_id(standardized_name)
                member_votes[member_id] = {
                    "position": position,
                    "member_id": member_id,
                    "member_name": standardized_name
                }

        return member_votes

    def standardize_member_name(self, raw_name: str) -> Optional[str]:
        """Match raw name against known council members"""
        # Handle common OCR errors and variations
        name_variations = {
            'bacerra': 'Phil Bacerra',
            'hernandez': 'David Hernandez',
            'penaloza': 'Jessie Lopez',  # Historical mapping
            'phan': 'Thai Viet Phan',
            # ... more mappings based on actual data
        }

        raw_lower = raw_name.lower().strip()
        for variation, standard_name in name_variations.items():
            if variation in raw_lower:
                return standard_name

        return None

    def calculate_confidence(self, regex_match, member_votes: Dict) -> float:
        """Calculate extraction confidence score"""
        confidence = 0.5  # Base confidence for pattern match

        # Boost confidence based on member identification
        if len(member_votes) >= 5:  # Expected Santa Ana council size
            confidence += 0.3

        # Boost confidence based on vote tally consistency
        yes_count = int(regex_match.group(1))
        if len([v for v in member_votes.values() if v["position"] == "Aye"]) == yes_count:
            confidence += 0.2

        return min(confidence, 1.0)
```

**Quality Scoring & Validation**
```python
# core/data_validator.py
class DataValidator:
    def __init__(self):
        self.santa_ana_members = self.load_historical_roster()

    def validate_vote(self, vote_data: Dict) -> Tuple[bool, float, List[str]]:
        """
        Comprehensive vote validation
        Returns: (is_valid, quality_score, error_messages)
        """
        errors = []
        quality_components = {
            'basic_data': 0,      # title, outcome, tallies (25 points)
            'member_votes': 0,    # member identification (35 points)
            'consistency': 0,     # internal consistency (25 points)
            'completeness': 0     # data completeness (15 points)
        }

        # Basic data validation (25 points)
        if vote_data.get('title') and len(vote_data['title'].strip()) > 10:
            quality_components['basic_data'] += 15
        else:
            errors.append("Missing or insufficient title")

        if vote_data.get('outcome') in ['Pass', 'Fail', 'Tie']:
            quality_components['basic_data'] += 10
        else:
            errors.append("Invalid or missing outcome")

        # Member votes validation (35 points)
        member_votes = vote_data.get('member_votes', {})
        if member_votes:
            valid_members = 0
            for member_id, vote_info in member_votes.items():
                if self.is_valid_member(member_id, vote_info.get('member_name')):
                    valid_members += 1

            # Score based on member identification accuracy
            member_score = min(35, (valid_members / 7) * 35)  # 7 expected members
            quality_components['member_votes'] = member_score

            if valid_members < 4:
                errors.append(f"Only {valid_members} members identified")
        else:
            errors.append("No member votes found")

        # Consistency validation (25 points)
        tally_ayes = vote_data.get('tally_ayes', 0)
        tally_noes = vote_data.get('tally_noes', 0)

        aye_votes = len([v for v in member_votes.values() if v.get('position') == 'Aye'])
        no_votes = len([v for v in member_votes.values() if v.get('position') == 'No'])

        if abs(tally_ayes - aye_votes) <= 1:  # Allow 1 vote difference
            quality_components['consistency'] += 15
        else:
            errors.append(f"Aye count mismatch: tally={tally_ayes}, members={aye_votes}")

        if abs(tally_noes - no_votes) <= 1:
            quality_components['consistency'] += 10
        else:
            errors.append(f"No count mismatch: tally={tally_noes}, members={no_votes}")

        # Completeness validation (15 points)
        if vote_data.get('motion_text'):
            quality_components['completeness'] += 8
        if vote_data.get('mover'):
            quality_components['completeness'] += 4
        if vote_data.get('agenda_item_number'):
            quality_components['completeness'] += 3

        # Calculate overall quality score
        total_quality = sum(quality_components.values())
        is_valid = total_quality >= 60  # Minimum 60% quality to be considered valid

        return is_valid, total_quality, errors
```

**Week 3 Deliverables:**
- Enhanced pattern matching with 85%+ accuracy on recent meetings
- Comprehensive data validation and quality scoring
- Member name standardization system
- Confidence scoring for extracted votes

#### **Week 4: Machine Learning & Advanced Features**

**ML-Enhanced Extraction**
```python
# core/ml_models.py
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.classification import RandomForestClassifier
from typing import List, Dict

class MLVoteExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.vote_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.outcome_classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False

    def train_models(self, training_data: List[Dict]):
        """Train ML models using manual parsing data"""
        # Prepare training data
        texts = [item['text'] for item in training_data]
        vote_labels = [1 if item['is_vote_block'] else 0 for item in training_data]
        outcome_labels = [item.get('outcome', 'Unknown') for item in training_data]

        # Feature extraction
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        text_features = self.tfidf.fit_transform(texts)

        # Train vote block classifier
        self.vote_classifier.fit(text_features, vote_labels)

        # Train outcome classifier on confirmed vote blocks
        vote_blocks = [(texts[i], outcome_labels[i]) for i, is_vote in enumerate(vote_labels) if is_vote]
        if vote_blocks:
            vote_texts, outcomes = zip(*vote_blocks)
            vote_features = self.tfidf.transform(vote_texts)
            self.outcome_classifier.fit(vote_features, outcomes)

        self.is_trained = True

    def extract_votes_ml(self, text: str) -> List[Dict]:
        """ML-powered vote extraction as fallback/enhancement"""
        if not self.is_trained:
            return []

        # Split text into potential vote blocks
        blocks = self.split_into_blocks(text)

        votes = []
        for i, block in enumerate(blocks):
            if self.is_vote_block(block):
                vote_data = self.extract_vote_details_ml(block, i)
                if vote_data:
                    votes.append(vote_data)

        return votes

    def is_vote_block(self, text: str) -> bool:
        """Classify if text block contains a vote"""
        features = self.tfidf.transform([text])
        prediction = self.vote_classifier.predict_proba(features)[0]
        return prediction[1] > 0.7  # 70% confidence threshold

    def extract_vote_details_ml(self, block: str, vote_num: int) -> Dict:
        """Extract vote details using NLP"""
        doc = self.nlp(block)

        # Extract entities (numbers, names, etc.)
        numbers = [ent.text for ent in doc.ents if ent.label_ == "CARDINAL"]
        people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

        # Predict outcome using ML
        features = self.tfidf.transform([block])
        outcome = self.outcome_classifier.predict(features)[0]
        outcome_confidence = self.outcome_classifier.predict_proba(features)[0].max()

        # Extract motion/title using pattern matching
        title = self.extract_title_ml(block)

        return {
            "id": f"ml-vote-{vote_num}",
            "title": title,
            "outcome": outcome if outcome_confidence > 0.6 else "Unknown",
            "extraction_method": "ml",
            "confidence": outcome_confidence,
            "raw_entities": {
                "numbers": numbers,
                "people": people
            }
        }
```

**Analytics Generation**
```python
# core/analytics_generator.py
from typing import Dict, List
from datetime import datetime, timedelta
from app.models.votes import Vote, CouncilMember

class AnalyticsGenerator:
    def __init__(self, db_session):
        self.db = db_session

    def generate_member_alignment_matrix(self) -> Dict:
        """Generate voting alignment matrix for analytics dashboard"""
        active_members = self.db.query(CouncilMember).filter(CouncilMember.active == True).all()

        alignment_matrix = {}
        for member1 in active_members:
            alignment_matrix[member1.id] = {}

            for member2 in active_members:
                if member1.id == member2.id:
                    alignment_matrix[member1.id][member2.id] = 100.0
                else:
                    alignment = self.calculate_member_alignment(member1.id, member2.id)
                    alignment_matrix[member1.id][member2.id] = alignment

        return {
            "matrix": alignment_matrix,
            "members": [{"id": m.id, "name": m.name} for m in active_members],
            "generated_at": datetime.now().isoformat()
        }

    def calculate_member_alignment(self, member1_id: str, member2_id: str) -> float:
        """Calculate voting agreement percentage between two members"""
        # Get all votes where both members participated
        votes = self.db.query(Vote).all()

        agreements = 0
        total_compared = 0

        for vote in votes:
            member_votes = vote.member_votes

            if member1_id in member_votes and member2_id in member_votes:
                pos1 = member_votes[member1_id].get('position')
                pos2 = member_votes[member2_id].get('position')

                # Only compare actual votes (not absent/recused)
                if pos1 in ['Aye', 'No'] and pos2 in ['Aye', 'No']:
                    total_compared += 1
                    if pos1 == pos2:
                        agreements += 1

        return (agreements / total_compared * 100) if total_compared > 0 else 0.0

    def generate_voting_trends(self) -> Dict:
        """Generate temporal voting trend data"""
        # Get all votes ordered by date
        votes = self.db.query(Vote).join(Meeting).order_by(Meeting.date).all()

        monthly_stats = {}
        for vote in votes:
            meeting_date = datetime.fromisoformat(vote.meeting.date)
            month_key = meeting_date.strftime('%Y-%m')

            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'total_votes': 0,
                    'pass_votes': 0,
                    'unanimous_votes': 0,
                    'contentious_votes': 0
                }

            stats = monthly_stats[month_key]
            stats['total_votes'] += 1

            if vote.outcome == 'Pass':
                stats['pass_votes'] += 1

            # Check if unanimous (all Aye or all No)
            member_positions = [v.get('position') for v in vote.member_votes.values()]
            unique_positions = set(pos for pos in member_positions if pos in ['Aye', 'No'])

            if len(unique_positions) == 1:
                stats['unanimous_votes'] += 1
            elif abs(vote.tally_ayes - vote.tally_noes) <= 1:
                stats['contentious_votes'] += 1

        # Calculate percentages
        trend_data = []
        for month, stats in monthly_stats.items():
            total = stats['total_votes']
            trend_data.append({
                'period': month,
                'total_votes': total,
                'pass_rate': (stats['pass_votes'] / total * 100) if total > 0 else 0,
                'unanimous_rate': (stats['unanimous_votes'] / total * 100) if total > 0 else 0,
                'contentious_rate': (stats['contentious_votes'] / total * 100) if total > 0 else 0
            })

        return {
            'trends': trend_data,
            'generated_at': datetime.now().isoformat()
        }
```

**Week 4 Deliverables:**
- Trained ML models for vote extraction enhancement
- Member alignment analytics generation
- Voting trend analysis capabilities
- Comprehensive analytics API endpoints

### **Phase 3: Production Deployment & Integration (Weeks 5-6)**

#### **Week 5: Production Infrastructure & API Finalization**

**Production Deployment Configuration**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY . .

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.production.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/santa_ana_votes
      - REDIS_URL=redis://redis:6379/0
      - API_ENV=production
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=santa_ana_votes
      - POSTGRES_USER=santa_ana_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

**Final API Endpoints Matching Website Requirements**
```python
# api/v1/__init__.py - Complete API specification
from fastapi import APIRouter
from . import council, votes, meetings, analytics, export

api_router = APIRouter()

# Council endpoints - exact match for website functions
api_router.include_router(
    council.router,
    prefix="/council",
    tags=["council"]
)

# Vote endpoints - matches website search functionality
api_router.include_router(
    votes.router,
    prefix="/votes",
    tags=["votes"]
)

# Meeting endpoints - supports meeting browser
api_router.include_router(
    meetings.router,
    prefix="/meetings",
    tags=["meetings"]
)

# Analytics endpoints - provides dashboard data
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"]
)

# Export endpoints - handles CSV/PDF generation
api_router.include_router(
    export.router,
    prefix="/export",
    tags=["export"]
)

# Health check for monitoring
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

**Week 5 Deliverables:**
- Production-ready Docker deployment configuration
- Complete API endpoints matching website schema exactly
- Database optimization with proper indexes
- Monitoring and health check endpoints

#### **Week 6: Website Integration & Go-Live**

**Integration Testing**
```python
# tests/integration/test_website_compatibility.py
import pytest
import httpx
from typing import List, Dict

class TestWebsiteIntegration:
    """Test that API responses match website expectations exactly"""

    @pytest.fixture
    def api_client(self):
        return httpx.AsyncClient(base_url="http://localhost:8000/api/v1")

    async def test_council_members_schema(self, api_client):
        """Verify council member API matches website CouncilMember interface"""
        response = await api_client.get("/council/")
        assert response.status_code == 200

        members = response.json()
        assert isinstance(members, list)

        # Verify each member matches expected schema
        for member in members:
            assert "id" in member
            assert "name" in member
            assert "role" in member
            assert member["role"] in ["Mayor", "Mayor Pro Tem", "Council Member"]
            assert "active" in member
            assert isinstance(member["active"], bool)

    async def test_votes_api_filtering(self, api_client):
        """Test vote search API matches website filtering requirements"""
        # Test date range filtering
        response = await api_client.get(
            "/votes/?date_start=2024-01-01&date_end=2024-12-31&limit=10"
        )
        assert response.status_code == 200

        votes = response.json()
        for vote in votes:
            # Verify required fields match website Vote interface
            required_fields = [
                "id", "meetingId", "title", "outcome", "date",
                "tallyAyes", "tallyNoes", "memberVotes"
            ]
            for field in required_fields:
                assert field in vote

            # Verify memberVotes structure
            member_votes = vote["memberVotes"]
            assert isinstance(member_votes, dict)
            for member_id, vote_info in member_votes.items():
                assert "position" in vote_info
                assert vote_info["position"] in ["Aye", "No", "Abstain", "Absent", "Recused"]

    async def test_analytics_data_format(self, api_client):
        """Test analytics API provides data in format expected by Chart.js"""
        response = await api_client.get("/analytics/alignment-matrix")
        assert response.status_code == 200

        data = response.json()
        assert "matrix" in data
        assert "members" in data

        # Verify format matches website's AlignmentMatrix interface
        members = data["members"]
        matrix = data["matrix"]

        assert len(members) > 0
        for member in members:
            assert "id" in member
            assert "name" in member
            assert member["id"] in matrix
```

**Website Update for Real Data**
```typescript
// Website side changes (minimal!)
// lib/api.ts - Only change API endpoints

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api'

// Change from fake data to real API calls
export async function getCouncilMembers(): Promise<CouncilMember[]> {
  // OLD (POC phase):
  // const response = await fetch('/data/council-members.json')

  // NEW (with real data):
  const response = await fetch(`${API_BASE_URL}/v1/council/`)

  if (!response.ok) {
    throw new Error('Failed to fetch council members')
  }

  return response.json()
}

export async function getVotes(filters?: VoteFilters): Promise<Vote[]> {
  // OLD (POC phase):
  // const response = await fetch('/data/votes.json')

  // NEW (with real data):
  const params = new URLSearchParams()
  if (filters?.dateRange) {
    params.append('date_start', filters.dateRange.start.toISOString().split('T')[0])
    params.append('date_end', filters.dateRange.end.toISOString().split('T')[0])
  }
  if (filters?.members) {
    filters.members.forEach(member => params.append('members', member))
  }
  if (filters?.outcome) {
    params.append('outcome', filters.outcome)
  }

  const response = await fetch(`${API_BASE_URL}/v1/votes/?${params}`)

  if (!response.ok) {
    throw new Error('Failed to fetch votes')
  }

  return response.json()
}

// All other website code stays exactly the same!
// Components, pages, styling - no changes needed
```

**Week 6 Deliverables:**
- Integration testing confirming API/website compatibility
- Production deployment with real data
- Website environment variables updated to use real API
- Documentation for ongoing maintenance

## **Success Metrics & Validation**

### **Data Quality Metrics**
- **Extraction Accuracy**: 90%+ for recent meetings (2023-2024)
- **Member Identification**: 95%+ accuracy for council member names
- **Vote Count Consistency**: 98%+ match between tallies and individual votes
- **Processing Speed**: < 5 minutes per meeting document

### **API Performance Metrics**
- **Response Time**: < 200ms for standard queries
- **Availability**: 99.5% uptime
- **Data Freshness**: New meetings processed within 24 hours
- **Schema Compatibility**: 100% compatibility with website interfaces

### **Integration Success Criteria**
- **Zero Breaking Changes**: Website works without code changes when switching to real data
- **Feature Parity**: All fake data features work with real data
- **Performance Maintained**: Real data API performs as well as fake data
- **Error Handling**: Graceful degradation when data is unavailable

## **Maintenance & Evolution Roadmap**

### **Ongoing Operations**
```python
# Automated maintenance tasks
class MaintenanceTasks:
    def daily_tasks(self):
        # Check for new meeting documents
        # Process any pending extractions
        # Validate data quality
        # Update analytics

    def weekly_tasks(self):
        # Review extraction accuracy
        # Update member rosters if needed
        # Performance optimization
        # Backup validation

    def monthly_tasks(self):
        # Comprehensive data audit
        # ML model retraining if needed
        # User feedback analysis
        # System performance review
```

### **Future Enhancements**
- **Real-time Processing**: Automated document ingestion from city website
- **Advanced ML**: Improved extraction accuracy through continuous learning
- **Multi-city Support**: Extend pipeline to other California cities
- **API v2**: Enhanced features based on user feedback

## **Risk Mitigation**

### **Data Quality Risks**
- **Continuous Monitoring**: Quality scores tracked over time
- **Validation Pipeline**: Multiple validation layers before publication
- **Manual Review Queue**: Low-confidence extractions flagged for review
- **Rollback Capability**: Ability to revert to previous data versions

### **Technical Risks**
- **API Versioning**: Backward compatibility maintained
- **Database Backups**: Daily automated backups
- **Error Handling**: Comprehensive error logging and alerting
- **Performance Monitoring**: Real-time performance tracking

## **Conclusion**

This backend data pipeline roadmap delivers a production-ready system that seamlessly integrates with the Vercel website. The pipeline transforms Santa Ana's meeting documents into clean, structured data accessible through well-designed APIs.

The key innovation is the exact schema matching between backend output and website requirements, enabling a smooth transition from fake to real data without website code changes. This approach validates the website design with realistic fake data while building the robust backend infrastructure needed for production.

The phased approach ensures steady progress from the current 16.2% extraction accuracy to a production-ready 90%+ accurate system, establishing a foundation for long-term civic transparency applications.