# CityVotes POC - Monorepo Architecture

## Overview

This project uses a **monorepo** structure with two separate applications:
1. **Backend API** (FastAPI + PostgreSQL) - runs on port 8000
2. **Frontend** (Vanilla HTML/CSS/JS) - runs on port 3000

Both applications live in the same repository but are completely independent and can be deployed separately.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | Vanilla HTML/CSS/JS | Static web pages, no framework dependencies |
| **Backend** | FastAPI (Python) | REST API with auto-generated docs |
| **Database** | PostgreSQL | Persistent data storage with JSONB support |
| **ORM** | SQLAlchemy | Database models and queries |
| **Validation** | Pydantic | Request/response schema validation |

---

## Project Structure

```
CityVotes_POC/
│
├── backend/                          # FastAPI Backend (Port 8000)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── cities.py             # GET /api/cities endpoints
│   │   │   ├── upload.py             # POST /api/upload endpoint
│   │   │   ├── sessions.py           # Session management endpoints
│   │   │   └── dashboard.py          # Dashboard data endpoints
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── database.py           # SQLAlchemy database setup
│   │   │   ├── session.py            # Session & SessionData models
│   │   │   └── schemas.py            # Pydantic request/response schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── vote_analyzer.py      # Vote summary calculations
│   │       └── member_analyzer.py    # Member alignment calculations
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── api_security_agent.py     # API security analysis
│   │   ├── city_config_agent.py      # City configuration management
│   │   ├── data_validation_agent.py  # JSON data validation
│   │   └── file_processing_agent.py  # File processing logic
│   ├── config.py                     # Database URL, CORS settings
│   ├── requirements.txt              # Python dependencies
│   └── run.py                        # Server entry point
│
├── frontend/                         # Static Frontend (Port 3000)
│   ├── index.html                    # Home page
│   ├── upload.html                   # File upload page
│   ├── dashboards/
│   │   ├── vote-summary.html         # Vote outcomes dashboard
│   │   ├── member-analysis.html      # Member alignment dashboard
│   │   ├── member-profile.html       # Individual member page
│   │   ├── agenda-items.html         # Agenda items list
│   │   └── agenda-item-detail.html   # Individual agenda item
│   ├── css/
│   │   └── main.css                  # All styles
│   ├── js/
│   │   ├── api.js                    # API client for backend
│   │   └── main.js                   # UI utilities, charts
│   └── serve.py                      # Simple HTTP server
│
├── extractors/                       # Data extraction tools
│   └── santa_ana/
│       └── 2024/
│           └── santa_ana_votes_2024.json
│
├── app/                              # Legacy Flask app (deprecated)
│   └── ...
│
├── agents/                           # Legacy agents location
│   └── ...
│
├── tools/                            # Utility scripts
│   └── ...
│
└── docs/                             # Documentation
    ├── MONOREPO_ARCHITECTURE.md      # This file
    └── ...
```

---

## Backend API Endpoints

### Cities
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities` | List all configured cities |
| GET | `/api/cities/{city_key}` | Get specific city configuration |

### Upload & Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload JSON vote file, returns session_id |
| GET | `/api/sessions/{session_id}` | Get session info |
| GET | `/api/sessions/{session_id}/cities` | List cities in session |

### Dashboard Data
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/{session_id}/{city}/summary` | Vote summary with metrics |
| GET | `/api/dashboard/{session_id}/{city}/members` | Member analysis with alignment |
| GET | `/api/dashboard/{session_id}/{city}/members/{name}` | Individual member profile |
| GET | `/api/dashboard/{session_id}/{city}/agenda-items` | Agenda items grouped by meeting |
| GET | `/api/dashboard/{session_id}/{city}/agenda-items/{id}` | Individual agenda item detail |

---

## Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '2 hours'
);

-- Uploaded data table
CREATE TABLE session_data (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    city_key VARCHAR(50) NOT NULL,
    original_filename VARCHAR(255),
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    raw_data JSONB NOT NULL,        -- The uploaded JSON
    processed_data JSONB NOT NULL,  -- Calculated summaries
    UNIQUE(session_id, city_key)
);

-- Indexes
CREATE INDEX idx_session_data_session ON session_data(session_id);
CREATE INDEX idx_session_data_city ON session_data(city_key);
```

---

## Frontend Pages

| Page | File | Description |
|------|------|-------------|
| Home | `index.html` | City selection, quick links |
| Upload | `upload.html` | Drag-and-drop JSON upload |
| Vote Summary | `dashboards/vote-summary.html` | Pie chart, metrics, member table |
| Member Analysis | `dashboards/member-analysis.html` | Alignment matrix, member cards |
| Member Profile | `dashboards/member-profile.html` | Individual voting history |
| Agenda Items | `dashboards/agenda-items.html` | Meetings grouped by date |
| Agenda Detail | `dashboards/agenda-item-detail.html` | Individual vote breakdown |

---

## Running the Application

### Prerequisites
- Python 3.9+
- PostgreSQL 15+ (or Docker)

### Option 1: Using Docker for PostgreSQL

```bash
# Start PostgreSQL container
docker run -d --name cityvotes-db \
  -e POSTGRES_DB=cityvotes \
  -e POSTGRES_USER=cityvotes \
  -e POSTGRES_PASSWORD=cityvotes \
  -p 5432:5432 \
  postgres:15
```

### Option 2: Local PostgreSQL

```bash
# Create database and user
createdb cityvotes
psql -c "CREATE USER cityvotes WITH PASSWORD 'cityvotes';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE cityvotes TO cityvotes;"
```

### Start Backend (Terminal 1)

```bash
cd backend
pip install -r requirements.txt
python run.py

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Start Frontend (Terminal 2)

```bash
cd frontend
python serve.py

# Server runs at http://localhost:3000
```

### Access the Application

1. Open http://localhost:3000 in your browser
2. Select a city and upload a JSON voting data file
3. View dashboards with voting analysis

---

## Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│   Backend API   │────▶│   PostgreSQL    │
│  (Port 3000)    │     │   (Port 8000)   │     │   (Port 5432)   │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
     Browser              FastAPI + Uvicorn        JSONB Storage

1. User uploads JSON file via frontend
2. Frontend sends POST to /api/upload
3. Backend validates and stores in PostgreSQL
4. Backend returns session_id
5. Frontend stores session_id in localStorage
6. Frontend fetches dashboard data via API
7. Frontend renders charts and tables
```

---

## Environment Variables

### Backend (`backend/config.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://cityvotes:cityvotes@localhost:5432/cityvotes` | PostgreSQL connection string |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed frontend origins |

---

## Key Design Decisions

1. **Monorepo over Multi-repo**: Easier to maintain, shared documentation, atomic commits

2. **Vanilla JS over Framework**: Reuses existing Flask templates, no build step, simpler deployment

3. **PostgreSQL over SQLite**: Production-ready, JSONB for flexible vote data, better concurrency

4. **FastAPI over Flask**: Modern Python, automatic OpenAPI docs, Pydantic validation

5. **Session-based over Auth**: POC simplicity, 2-hour expiry, no user accounts needed

6. **JSONB Storage**: Flexible schema for vote data, efficient querying, no migrations needed

---

## Future Improvements

- [ ] Add user authentication (OAuth2/JWT)
- [ ] Implement data caching (Redis)
- [ ] Add export functionality (CSV, PDF reports)
- [ ] Create admin dashboard
- [ ] Add real-time updates (WebSockets)
- [ ] Containerize with Docker Compose
- [ ] Add CI/CD pipeline
