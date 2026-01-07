# CityVotes 2.0 - Complete Feature Implementation Plan

## Overview

CityVotes 2.0 transforms the proof-of-concept into a production-ready civic transparency platform. This plan adds all missing features identified from the Santa Ana website plans while building on the existing database infrastructure.

---

## Current State (CityVotes 1.0)

**Completed:**
- PostgreSQL database with full schema
- 22 meetings, 437 votes, 3,059 member votes imported
- Meeting URLs (agenda, minutes, video) from PrimeGov
- Materialized views for fast queries
- Database setup automation (staging tables method)

**Architecture:**
- Database: PostgreSQL with materialized views
- Backend: Planned FastAPI
- Frontend: Planned Vanilla HTML/CSS/JS

---

## CityVotes 2.0 Feature Categories

### Category A: Core Infrastructure
### Category B: User Experience
### Category C: Analytics & Visualizations
### Category D: Data & Export
### Category E: Security & Performance
### Category F: Deployment & Operations

---

## Phase 1: Enhanced Backend API (Week 1-2)

### 1.1 FastAPI Core Setup

**Files to create:**
```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with CORS, middleware
│   ├── config.py               # Environment configuration
│   ├── database.py             # PostgreSQL connection pool
│   ├── dependencies.py         # Shared dependencies
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── cities.py           # City endpoints
│   │   ├── council.py          # Council member endpoints
│   │   ├── meetings.py         # Meeting browser endpoints
│   │   ├── votes.py            # Vote search endpoints
│   │   ├── analytics.py        # Analytics endpoints
│   │   └── export.py           # Data export endpoints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic request/response models
│   │   └── database.py         # SQLAlchemy models
│   │
│   └── services/
│       ├── __init__.py
│       ├── vote_analyzer.py    # Vote analysis logic
│       ├── member_analyzer.py  # Member analysis logic
│       ├── search.py           # Search with autocomplete
│       ├── export.py           # CSV/PDF/JSON export
│       └── cache.py            # Redis caching layer
│
├── requirements.txt
└── run.py
```

### 1.2 API Endpoints

**Cities & Council:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities` | List all cities |
| GET | `/api/cities/{key}` | City details with config |
| GET | `/api/cities/{key}/council` | All council members |
| GET | `/api/cities/{key}/council/{member}` | Member profile with stats |
| GET | `/api/cities/{key}/council/{member}/votes` | Member vote history |
| GET | `/api/cities/{key}/council/{member}/photo` | Member photo |

**Meetings:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities/{key}/meetings` | Meeting list with filters |
| GET | `/api/cities/{key}/meetings/{id}` | Meeting detail with votes |
| GET | `/api/cities/{key}/meetings/{id}/attendance` | Attendance record |

**Votes & Search:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities/{key}/votes` | Vote search with filters |
| GET | `/api/cities/{key}/votes/{id}` | Vote detail with member positions |
| GET | `/api/cities/{key}/votes/search` | Advanced search with autocomplete |
| GET | `/api/cities/{key}/votes/categories` | Votes by issue category |

**Analytics:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities/{key}/analytics/summary` | Overall statistics |
| GET | `/api/cities/{key}/analytics/alignment` | Member alignment matrix |
| GET | `/api/cities/{key}/analytics/trends` | Voting trends over time |
| GET | `/api/cities/{key}/analytics/categories` | Issue category breakdown |
| GET | `/api/cities/{key}/analytics/participation` | Attendance/participation rates |

**Export:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities/{key}/export/votes` | Export votes as CSV/JSON |
| GET | `/api/cities/{key}/export/member/{name}` | Export member report (PDF) |
| GET | `/api/cities/{key}/export/meeting/{id}` | Export meeting summary |

### 1.3 Database Enhancements

**New Tables:**
```sql
-- Issue categories for votes
CREATE TABLE issue_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    keywords TEXT[],
    color VARCHAR(7)  -- Hex color for UI
);

-- Vote to category mapping
CREATE TABLE vote_categories (
    vote_id INTEGER REFERENCES votes(id),
    category_id INTEGER REFERENCES issue_categories(id),
    confidence DECIMAL(3,2),
    PRIMARY KEY (vote_id, category_id)
);

-- Council member photos
CREATE TABLE council_member_photos (
    member_id INTEGER PRIMARY KEY REFERENCES council_members(id),
    photo_url TEXT,
    photo_data BYTEA,  -- Optional: store locally
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Search analytics (for autocomplete improvement)
CREATE TABLE search_queries (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    results_count INTEGER,
    clicked_result_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User sessions for saved searches (future)
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saved_searches JSONB,
    notification_settings JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**New Materialized Views:**
```sql
-- Voting trends by month
CREATE MATERIALIZED VIEW mv_voting_trends AS
SELECT
    city_id,
    DATE_TRUNC('month', meeting_date) as month,
    COUNT(*) as total_votes,
    SUM(CASE WHEN outcome = 'PASS' THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN ayes = 7 THEN 1 ELSE 0 END) as unanimous,
    AVG(ayes + noes + abstain) as avg_participation
FROM meetings m
JOIN agenda_items ai ON ai.meeting_id = m.id
JOIN votes v ON v.agenda_item_id = ai.id
GROUP BY city_id, DATE_TRUNC('month', meeting_date);

-- Issue category summary
CREATE MATERIALIZED VIEW mv_category_summary AS
SELECT
    ic.name as category,
    COUNT(*) as vote_count,
    SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END) as passed,
    AVG(v.ayes) as avg_ayes
FROM votes v
JOIN vote_categories vc ON vc.vote_id = v.id
JOIN issue_categories ic ON ic.id = vc.category_id
GROUP BY ic.name;
```

### 1.4 Caching Layer

**Redis Configuration:**
```python
# backend/api/services/cache.py
import redis
from functools import wraps
import json

class CacheService:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.default_ttl = 300  # 5 minutes

    def cached(self, key_prefix: str, ttl: int = None):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                result = await func(*args, **kwargs)
                self.redis.setex(cache_key, ttl or self.default_ttl, json.dumps(result))
                return result
            return wrapper
        return decorator

    def invalidate(self, pattern: str):
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
```

**Cache Strategy:**
| Data Type | TTL | Invalidation |
|-----------|-----|--------------|
| City config | 1 hour | Manual on update |
| Member stats | 5 minutes | On new vote import |
| Alignment matrix | 10 minutes | On new vote import |
| Vote search results | 2 minutes | None (short TTL) |
| Meeting list | 5 minutes | On new meeting import |

---

## Phase 2: Frontend Foundation (Week 2-3)

### 2.1 Project Structure

```
frontend/
├── index.html                  # Homepage dashboard
├── council.html                # Council overview
├── council-member.html         # Member profile template
├── meetings.html               # Meeting browser
├── meeting-detail.html         # Single meeting view
├── votes.html                  # Vote search
├── vote-detail.html            # Single vote view
├── analytics.html              # Analytics dashboard
├── about.html                  # About/educational content
│
├── css/
│   ├── main.css                # Core styles
│   ├── santa-ana-theme.css     # City branding
│   ├── components.css          # Reusable components
│   ├── responsive.css          # Mobile styles
│   └── accessibility.css       # A11y enhancements
│
├── js/
│   ├── api.js                  # API client
│   ├── app.js                  # Main application
│   ├── components/
│   │   ├── search.js           # Search with autocomplete
│   │   ├── charts.js           # Chart.js wrappers
│   │   ├── tables.js           # Data tables
│   │   ├── filters.js          # Filter components
│   │   └── export.js           # Export functionality
│   ├── pages/
│   │   ├── home.js
│   │   ├── council.js
│   │   ├── meetings.js
│   │   ├── votes.js
│   │   └── analytics.js
│   └── utils/
│       ├── dates.js            # Date formatting
│       ├── numbers.js          # Number formatting
│       └── dom.js              # DOM utilities
│
├── images/
│   ├── council/                # Member photos
│   ├── icons/                  # UI icons
│   └── logos/                  # City logos
│
└── serve.py                    # Development server
```

### 2.2 Design System

**Color Palette (Santa Ana Branding):**
```css
:root {
    /* Primary */
    --sa-blue: #1f4e79;
    --sa-blue-light: #2d6da3;
    --sa-blue-dark: #163a5c;

    /* Accent */
    --sa-gold: #f4b942;
    --sa-gold-light: #f7ca6e;
    --sa-gold-dark: #d9a030;

    /* Neutrals */
    --gray-100: #f8f9fa;
    --gray-200: #e9ecef;
    --gray-300: #dee2e6;
    --gray-500: #6c757d;
    --gray-700: #495057;
    --gray-900: #212529;

    /* Semantic */
    --success: #28a745;
    --warning: #ffc107;
    --danger: #dc3545;
    --info: #17a2b8;

    /* Vote colors */
    --vote-aye: #28a745;
    --vote-nay: #dc3545;
    --vote-abstain: #6c757d;
    --vote-absent: #e9ecef;
    --vote-recusal: #17a2b8;
}
```

**Typography:**
```css
:root {
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-heading: 'Poppins', var(--font-primary);
    --font-mono: 'JetBrains Mono', monospace;

    --text-xs: 0.75rem;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.5rem;
    --text-3xl: 1.875rem;
    --text-4xl: 2.25rem;
}
```

**Component Library:**
```css
/* Vote badge component */
.vote-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: var(--text-sm);
    font-weight: 500;
}

.vote-badge--aye { background: var(--vote-aye); color: white; }
.vote-badge--nay { background: var(--vote-nay); color: white; }
.vote-badge--abstain { background: var(--vote-abstain); color: white; }
.vote-badge--absent { background: var(--vote-absent); color: var(--gray-700); }

/* Card component */
.card {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 1.5rem;
    transition: box-shadow 0.2s, transform 0.2s;
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

/* Loading states */
.skeleton {
    background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

### 2.3 Core Components

**Navigation:**
```html
<nav class="navbar" role="navigation" aria-label="Main navigation">
    <div class="navbar-brand">
        <a href="/" class="navbar-logo">
            <img src="/images/logos/cityvotes-logo.svg" alt="CityVotes">
            <span>CityVotes</span>
        </a>
    </div>

    <button class="navbar-toggle" aria-expanded="false" aria-controls="nav-menu">
        <span class="sr-only">Toggle navigation</span>
        <span class="navbar-toggle-icon"></span>
    </button>

    <div id="nav-menu" class="navbar-menu">
        <a href="/council.html" class="nav-link">Council</a>
        <a href="/meetings.html" class="nav-link">Meetings</a>
        <a href="/votes.html" class="nav-link">Votes</a>
        <a href="/analytics.html" class="nav-link">Analytics</a>
        <a href="/about.html" class="nav-link">About</a>
    </div>

    <div class="navbar-search">
        <input type="search"
               placeholder="Search votes, members, topics..."
               aria-label="Search"
               autocomplete="off">
        <div class="search-suggestions" role="listbox" hidden></div>
    </div>
</nav>

<nav aria-label="Breadcrumb" class="breadcrumb">
    <ol>
        <li><a href="/">Home</a></li>
        <li><a href="/council.html">Council</a></li>
        <li aria-current="page">Phil Bacerra</li>
    </ol>
</nav>
```

**Search with Autocomplete:**
```javascript
// frontend/js/components/search.js
class SearchAutocomplete {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.minChars = options.minChars || 2;
        this.debounceMs = options.debounceMs || 300;
        this.suggestionsEl = this.createSuggestionsElement();
        this.setupEventListeners();
    }

    async search(query) {
        if (query.length < this.minChars) {
            this.hideSuggestions();
            return;
        }

        const response = await api.get(`/votes/search?q=${encodeURIComponent(query)}&limit=5`);
        this.showSuggestions(response.suggestions);
    }

    showSuggestions(suggestions) {
        this.suggestionsEl.innerHTML = suggestions.map((s, i) => `
            <div class="suggestion"
                 role="option"
                 id="suggestion-${i}"
                 tabindex="-1">
                <span class="suggestion-type">${s.type}</span>
                <span class="suggestion-text">${this.highlight(s.text, this.input.value)}</span>
            </div>
        `).join('');
        this.suggestionsEl.hidden = false;
    }

    highlight(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
}
```

### 2.4 Page Templates

**Homepage Dashboard:**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CityVotes - Santa Ana City Council Voting Transparency</title>
    <meta name="description" content="Track Santa Ana City Council voting records, member alignment, and civic transparency data.">

    <!-- Open Graph -->
    <meta property="og:title" content="CityVotes - Santa Ana Voting Transparency">
    <meta property="og:description" content="Complete voting records and analysis for Santa Ana City Council.">
    <meta property="og:image" content="/images/og-image.png">
    <meta property="og:url" content="https://cityvotes.org">

    <!-- Schema.org -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "CityVotes",
        "description": "Santa Ana City Council voting transparency platform",
        "url": "https://cityvotes.org"
    }
    </script>

    <link rel="stylesheet" href="/css/main.css">
</head>
<body>
    <!-- Navigation -->
    <nav>...</nav>

    <!-- Hero Section -->
    <header class="hero">
        <h1>Santa Ana City Council Voting Records</h1>
        <p class="hero-subtitle">Transparency in local government decision-making</p>
        <div class="hero-search">
            <input type="search" placeholder="Search votes, topics, or council members...">
            <button type="submit">Search</button>
        </div>
    </header>

    <!-- Stats Overview -->
    <section class="stats-grid" aria-label="Voting statistics">
        <div class="stat-card">
            <span class="stat-value" id="total-votes">--</span>
            <span class="stat-label">Total Votes</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="total-meetings">--</span>
            <span class="stat-label">Meetings</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="pass-rate">--%</span>
            <span class="stat-label">Pass Rate</span>
        </div>
        <div class="stat-card">
            <span class="stat-value" id="unanimous-rate">--%</span>
            <span class="stat-label">Unanimous</span>
        </div>
    </section>

    <!-- Council Members -->
    <section class="council-section">
        <h2>City Council</h2>
        <div class="council-grid" id="council-members">
            <!-- Populated by JS -->
        </div>
    </section>

    <!-- Recent Activity -->
    <section class="activity-section">
        <h2>Recent Meetings</h2>
        <div class="meeting-list" id="recent-meetings">
            <!-- Populated by JS -->
        </div>
        <a href="/meetings.html" class="view-all-link">View all meetings →</a>
    </section>

    <!-- Featured Analysis -->
    <section class="featured-section">
        <h2>Voting Insights</h2>
        <div class="insights-grid">
            <div class="insight-card">
                <h3>Most Aligned</h3>
                <div id="most-aligned">--</div>
            </div>
            <div class="insight-card">
                <h3>Most Contentious Vote</h3>
                <div id="contentious-vote">--</div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <p>Data sourced from official Santa Ana city records.</p>
        <nav>
            <a href="/about.html">About</a>
            <a href="/api/docs">API</a>
            <a href="https://github.com/...">GitHub</a>
        </nav>
    </footer>

    <script src="/js/api.js"></script>
    <script src="/js/pages/home.js"></script>
</body>
</html>
```

---

## Phase 3: Analytics & Visualizations (Week 3-4)

### 3.1 Chart.js Integration

**Alignment Heatmap:**
```javascript
// frontend/js/components/charts.js
class AlignmentHeatmap {
    constructor(canvasId, data) {
        this.canvas = document.getElementById(canvasId);
        this.data = data;
        this.render();
    }

    render() {
        const members = this.data.members;
        const matrix = this.data.matrix;

        new Chart(this.canvas, {
            type: 'matrix',
            data: {
                datasets: [{
                    label: 'Voting Alignment',
                    data: this.formatMatrixData(members, matrix),
                    backgroundColor: (ctx) => this.getColor(ctx.raw.v),
                    borderWidth: 1,
                    width: ({chart}) => (chart.chartArea.width / members.length) - 1,
                    height: ({chart}) => (chart.chartArea.height / members.length) - 1
                }]
            },
            options: {
                plugins: {
                    tooltip: {
                        callbacks: {
                            title: () => '',
                            label: (ctx) => {
                                const {x, y, v} = ctx.raw;
                                return `${members[y]} & ${members[x]}: ${v}% agreement`;
                            }
                        }
                    }
                },
                scales: {
                    x: { labels: members, grid: { display: false } },
                    y: { labels: members, grid: { display: false } }
                }
            }
        });
    }

    getColor(value) {
        // Santa Ana blue gradient
        const alpha = value / 100;
        return `rgba(31, 78, 121, ${alpha})`;
    }
}
```

**Voting Trends Timeline:**
```javascript
class VotingTrendsChart {
    constructor(canvasId, data) {
        this.canvas = document.getElementById(canvasId);
        this.data = data;
        this.render();
    }

    render() {
        new Chart(this.canvas, {
            type: 'line',
            data: {
                labels: this.data.months,
                datasets: [
                    {
                        label: 'Total Votes',
                        data: this.data.totalVotes,
                        borderColor: '#1f4e79',
                        tension: 0.3
                    },
                    {
                        label: 'Passed',
                        data: this.data.passed,
                        borderColor: '#28a745',
                        tension: 0.3
                    },
                    {
                        label: 'Unanimous',
                        data: this.data.unanimous,
                        borderColor: '#f4b942',
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}
```

**Issue Category Breakdown:**
```javascript
class CategoryDonutChart {
    constructor(canvasId, data) {
        this.canvas = document.getElementById(canvasId);
        this.data = data;
        this.render();
    }

    render() {
        new Chart(this.canvas, {
            type: 'doughnut',
            data: {
                labels: this.data.categories.map(c => c.name),
                datasets: [{
                    data: this.data.categories.map(c => c.count),
                    backgroundColor: [
                        '#1f4e79', '#2d6da3', '#f4b942', '#28a745',
                        '#dc3545', '#17a2b8', '#6c757d', '#495057'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'right' }
                },
                onClick: (e, elements) => {
                    if (elements.length > 0) {
                        const category = this.data.categories[elements[0].index];
                        window.location.href = `/votes.html?category=${category.id}`;
                    }
                }
            }
        });
    }
}
```

### 3.2 Analytics Dashboard Page

```html
<!-- analytics.html -->
<main class="analytics-page">
    <h1>Voting Analytics</h1>

    <!-- Time Range Selector -->
    <div class="filter-bar">
        <label>
            Date Range:
            <select id="date-range">
                <option value="all">All Time</option>
                <option value="year">Past Year</option>
                <option value="6months">Past 6 Months</option>
                <option value="3months">Past 3 Months</option>
            </select>
        </label>
    </div>

    <!-- Summary Stats -->
    <section class="analytics-summary">
        <div class="stat-card">
            <h3>Pass Rate</h3>
            <div class="stat-value" id="pass-rate">--%</div>
            <div class="stat-trend" id="pass-rate-trend"></div>
        </div>
        <div class="stat-card">
            <h3>Unanimous Votes</h3>
            <div class="stat-value" id="unanimous-rate">--%</div>
        </div>
        <div class="stat-card">
            <h3>Average Participation</h3>
            <div class="stat-value" id="avg-participation">--</div>
        </div>
    </section>

    <!-- Member Alignment Matrix -->
    <section class="chart-section">
        <h2>Council Member Voting Alignment</h2>
        <p class="chart-description">
            How often do council members vote the same way?
            Darker colors indicate higher agreement.
        </p>
        <div class="chart-container chart-container--square">
            <canvas id="alignment-heatmap"></canvas>
        </div>
    </section>

    <!-- Voting Trends -->
    <section class="chart-section">
        <h2>Voting Trends Over Time</h2>
        <div class="chart-container">
            <canvas id="voting-trends"></canvas>
        </div>
    </section>

    <!-- Issue Categories -->
    <section class="chart-section">
        <h2>Votes by Issue Category</h2>
        <div class="chart-grid">
            <div class="chart-container">
                <canvas id="category-donut"></canvas>
            </div>
            <div class="category-list" id="category-details">
                <!-- Category breakdown with links -->
            </div>
        </div>
    </section>

    <!-- Participation Rates -->
    <section class="chart-section">
        <h2>Member Participation Rates</h2>
        <div class="chart-container">
            <canvas id="participation-chart"></canvas>
        </div>
    </section>
</main>
```

---

## Phase 4: Data Export & Search (Week 4-5)

### 4.1 Export Service

```python
# backend/api/services/export.py
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv
import io
import json

class ExportService:

    async def export_votes_csv(self, city_key: str, filters: dict) -> StreamingResponse:
        votes = await self.get_filtered_votes(city_key, filters)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Date', 'Meeting Type', 'Agenda Item', 'Title',
            'Outcome', 'Ayes', 'Noes', 'Abstain', 'Absent',
            'Hernandez', 'Lopez', 'Penaloza', 'Vazquez', 'Phan', 'Bacerra', 'Amezcua'
        ])

        # Data rows
        for vote in votes:
            writer.writerow([
                vote.meeting_date, vote.meeting_type, vote.item_number,
                vote.title, vote.outcome, vote.ayes, vote.noes,
                vote.abstain, vote.absent,
                *[mv.vote_choice for mv in vote.member_votes]
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=votes-{city_key}.csv"}
        )

    async def export_member_pdf(self, city_key: str, member_key: str) -> StreamingResponse:
        member = await self.get_member_profile(city_key, member_key)
        stats = await self.get_member_stats(city_key, member_key)

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        # Header
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(72, 750, f"{member.full_name}")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(72, 725, f"{member.title} - Santa Ana City Council")

        # Statistics
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(72, 680, "Voting Statistics")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(72, 655, f"Total Votes: {stats.total_votes}")
        pdf.drawString(72, 640, f"Aye Votes: {stats.aye_count} ({stats.aye_percentage:.1f}%)")
        pdf.drawString(72, 625, f"Nay Votes: {stats.nay_count} ({stats.nay_percentage:.1f}%)")

        # ... more PDF content

        pdf.save()
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={member_key}-report.pdf"}
        )

    async def export_json(self, city_key: str, filters: dict) -> dict:
        votes = await self.get_filtered_votes(city_key, filters)
        return {
            "city": city_key,
            "exported_at": datetime.utcnow().isoformat(),
            "filters": filters,
            "total_records": len(votes),
            "votes": [vote.dict() for vote in votes]
        }
```

### 4.2 Advanced Search

```python
# backend/api/services/search.py
from sqlalchemy import or_, and_, func
from typing import List, Optional

class SearchService:

    async def search_votes(
        self,
        city_key: str,
        query: Optional[str] = None,
        date_start: Optional[date] = None,
        date_end: Optional[date] = None,
        members: Optional[List[str]] = None,
        outcomes: Optional[List[str]] = None,
        categories: Optional[List[int]] = None,
        page: int = 1,
        per_page: int = 20
    ):
        filters = [City.city_key == city_key]

        if query:
            search_term = f"%{query}%"
            filters.append(or_(
                AgendaItem.title.ilike(search_term),
                AgendaItem.description.ilike(search_term),
                Vote.notes.ilike(search_term)
            ))

        if date_start:
            filters.append(Meeting.meeting_date >= date_start)
        if date_end:
            filters.append(Meeting.meeting_date <= date_end)

        if outcomes:
            filters.append(Vote.outcome.in_(outcomes))

        if members:
            # Find votes where specified members voted
            subquery = (
                select(MemberVote.vote_id)
                .join(CouncilMember)
                .where(CouncilMember.short_name.in_(members))
                .group_by(MemberVote.vote_id)
                .having(func.count() == len(members))
            )
            filters.append(Vote.id.in_(subquery))

        if categories:
            filters.append(VoteCategory.category_id.in_(categories))

        total = await self.db.scalar(
            select(func.count()).select_from(Vote).where(and_(*filters))
        )

        results = await self.db.execute(
            select(Vote)
            .where(and_(*filters))
            .order_by(Meeting.meeting_date.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "results": results.scalars().all()
        }

    async def get_autocomplete_suggestions(
        self,
        city_key: str,
        query: str,
        limit: int = 5
    ):
        suggestions = []

        # Search council members
        members = await self.db.execute(
            select(CouncilMember)
            .where(CouncilMember.full_name.ilike(f"%{query}%"))
            .limit(limit)
        )
        for member in members.scalars():
            suggestions.append({
                "type": "member",
                "text": member.full_name,
                "url": f"/council-member.html?member={member.member_key}"
            })

        # Search vote titles
        votes = await self.db.execute(
            select(AgendaItem.title, Vote.id)
            .join(Vote)
            .where(AgendaItem.title.ilike(f"%{query}%"))
            .limit(limit)
        )
        for title, vote_id in votes:
            suggestions.append({
                "type": "vote",
                "text": title[:60] + "..." if len(title) > 60 else title,
                "url": f"/vote-detail.html?id={vote_id}"
            })

        # Search categories
        categories = await self.db.execute(
            select(IssueCategory)
            .where(IssueCategory.name.ilike(f"%{query}%"))
            .limit(3)
        )
        for cat in categories.scalars():
            suggestions.append({
                "type": "category",
                "text": cat.name,
                "url": f"/votes.html?category={cat.id}"
            })

        return suggestions[:limit]
```

---

## Phase 5: Security & Performance (Week 5-6)

### 5.1 Security Implementation

**Rate Limiting:**
```python
# backend/api/middleware/rate_limit.py
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to routes
@router.get("/votes/search")
@limiter.limit("30/minute")
async def search_votes(request: Request, ...):
    ...

@router.get("/export/votes")
@limiter.limit("10/minute")
async def export_votes(request: Request, ...):
    ...
```

**Input Validation:**
```python
# backend/api/models/schemas.py
from pydantic import BaseModel, Field, validator
import re

class SearchQuery(BaseModel):
    q: str = Field(max_length=200)
    page: int = Field(default=1, ge=1, le=1000)
    per_page: int = Field(default=20, ge=1, le=100)

    @validator('q')
    def sanitize_query(cls, v):
        # Remove potential SQL injection patterns
        v = re.sub(r'[;\'"\\]', '', v)
        return v.strip()

class DateRangeFilter(BaseModel):
    start: Optional[date] = None
    end: Optional[date] = None

    @validator('end')
    def end_after_start(cls, v, values):
        if v and values.get('start') and v < values['start']:
            raise ValueError('End date must be after start date')
        return v
```

**CORS Configuration:**
```python
# backend/api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://cityvotes.org",
        "https://www.cityvotes.org"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**Security Headers:**
```python
# backend/api/middleware/security.py
from fastapi import Request

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        "font-src fonts.gstatic.com; "
        "img-src 'self' data: https:; "
    )
    return response
```

### 5.2 Performance Optimization

**Database Indexes:**
```sql
-- Add indexes for common queries
CREATE INDEX idx_votes_meeting_date ON votes USING btree (
    (SELECT meeting_date FROM meetings m
     JOIN agenda_items ai ON ai.meeting_id = m.id
     WHERE ai.id = votes.agenda_item_id)
);

CREATE INDEX idx_agenda_items_title_trgm ON agenda_items
    USING gin (title gin_trgm_ops);

CREATE INDEX idx_votes_outcome ON votes (outcome);

CREATE INDEX idx_member_votes_choice ON member_votes (vote_choice);
```

**Query Optimization:**
```python
# backend/api/services/optimized_queries.py
from sqlalchemy.orm import selectinload, joinedload

async def get_meeting_with_votes(meeting_id: int):
    return await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.agenda_items)
            .selectinload(AgendaItem.vote)
            .selectinload(Vote.member_votes)
            .joinedload(MemberVote.member)
        )
        .where(Meeting.id == meeting_id)
    )
```

**Response Compression:**
```python
# backend/api/main.py
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 5.3 Accessibility (WCAG 2.1 AA)

```html
<!-- Accessibility enhancements -->

<!-- Skip link -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Proper heading hierarchy -->
<main id="main-content">
    <h1>Vote Search Results</h1>
    <section aria-labelledby="filters-heading">
        <h2 id="filters-heading">Search Filters</h2>
        ...
    </section>
    <section aria-labelledby="results-heading">
        <h2 id="results-heading">Results</h2>
        ...
    </section>
</main>

<!-- Form labels -->
<label for="date-start">Start Date</label>
<input type="date" id="date-start" name="date_start">

<!-- ARIA for dynamic content -->
<div id="search-results"
     role="region"
     aria-live="polite"
     aria-label="Search results">
</div>

<!-- Focus management -->
<button onclick="openModal()" aria-haspopup="dialog">
    Export Data
</button>
<div role="dialog"
     aria-modal="true"
     aria-labelledby="modal-title"
     tabindex="-1">
    <h2 id="modal-title">Export Options</h2>
    ...
</div>
```

```css
/* frontend/css/accessibility.css */

/* Focus indicators */
:focus {
    outline: 2px solid var(--sa-gold);
    outline-offset: 2px;
}

:focus:not(:focus-visible) {
    outline: none;
}

:focus-visible {
    outline: 2px solid var(--sa-gold);
    outline-offset: 2px;
}

/* Skip link */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--sa-blue);
    color: white;
    padding: 8px 16px;
    z-index: 100;
}

.skip-link:focus {
    top: 0;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}

/* High contrast support */
@media (prefers-contrast: high) {
    .vote-badge {
        border: 2px solid currentColor;
    }

    .card {
        border: 1px solid var(--gray-700);
    }
}

/* Screen reader only */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    border: 0;
}
```

---

## Phase 6: Deployment & Operations (Week 6)

### 6.1 Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM nginx:alpine

COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: cityvotes
      POSTGRES_USER: cityvotes
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cityvotes"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://cityvotes:${DB_PASSWORD}@db:5432/cityvotes
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl:ro

volumes:
  postgres_data:
  redis_data:
```

### 6.2 Monitoring & Logging

```python
# backend/api/middleware/monitoring.py
import time
import logging
from fastapi import Request

logger = logging.getLogger("cityvotes")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.3f}s"
    )

    # Alert on slow requests
    if duration > 2.0:
        logger.warning(f"Slow request: {request.url.path} took {duration:.2f}s")

    return response
```

```python
# backend/api/health.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }

@router.get("/health/detailed")
async def detailed_health():
    # Check database
    try:
        await db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e}"

    # Check Redis
    try:
        redis.ping()
        redis_status = "healthy"
    except Exception as e:
        redis_status = f"unhealthy: {e}"

    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "cache": redis_status
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 6.3 Backup & Recovery

```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
docker exec cityvotes-db pg_dump -U cityvotes cityvotes | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Retain last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
# aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" s3://cityvotes-backups/
```

---

## Implementation Timeline

| Week | Phase | Deliverables |
|------|-------|--------------|
| 1 | Backend API Core | FastAPI setup, database models, basic endpoints |
| 2 | Backend API Complete | All endpoints, caching, search service |
| 3 | Frontend Foundation | HTML templates, CSS design system, core JS |
| 4 | Analytics & Visualizations | Chart.js integration, analytics dashboard |
| 5 | Export & Search | CSV/PDF export, advanced search, autocomplete |
| 6 | Security & Deployment | Security hardening, Docker, monitoring |

---

## Success Metrics

### Technical
- Page load time: < 2 seconds
- Search response: < 1 second
- API response: < 500ms
- Uptime: 99.5%
- Lighthouse score: > 90

### User Engagement
- Monthly visitors: 500+
- Session duration: > 3 minutes
- Return rate: > 30%
- Export usage: > 20%

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigable
- Screen reader compatible

---

## Dependencies

### Backend
```
fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
redis>=4.5.0
pydantic>=2.0.0
python-multipart>=0.0.6
reportlab>=4.0.0
slowapi>=0.1.8
```

### Frontend
```
Chart.js 4.x
```

### Infrastructure
```
PostgreSQL 15
Redis 7
Nginx
Docker & Docker Compose
```

---

## File Checklist

### Backend (New)
- [ ] `backend/api/main.py`
- [ ] `backend/api/config.py`
- [ ] `backend/api/database.py`
- [ ] `backend/api/routes/cities.py`
- [ ] `backend/api/routes/council.py`
- [ ] `backend/api/routes/meetings.py`
- [ ] `backend/api/routes/votes.py`
- [ ] `backend/api/routes/analytics.py`
- [ ] `backend/api/routes/export.py`
- [ ] `backend/api/services/search.py`
- [ ] `backend/api/services/export.py`
- [ ] `backend/api/services/cache.py`
- [ ] `backend/api/middleware/rate_limit.py`
- [ ] `backend/api/middleware/security.py`
- [ ] `backend/api/middleware/monitoring.py`
- [ ] `backend/requirements.txt`
- [ ] `backend/Dockerfile`

### Frontend (New)
- [ ] `frontend/index.html`
- [ ] `frontend/council.html`
- [ ] `frontend/council-member.html`
- [ ] `frontend/meetings.html`
- [ ] `frontend/meeting-detail.html`
- [ ] `frontend/votes.html`
- [ ] `frontend/vote-detail.html`
- [ ] `frontend/analytics.html`
- [ ] `frontend/about.html`
- [ ] `frontend/css/main.css`
- [ ] `frontend/css/santa-ana-theme.css`
- [ ] `frontend/css/components.css`
- [ ] `frontend/css/responsive.css`
- [ ] `frontend/css/accessibility.css`
- [ ] `frontend/js/api.js`
- [ ] `frontend/js/app.js`
- [ ] `frontend/js/components/search.js`
- [ ] `frontend/js/components/charts.js`
- [ ] `frontend/js/components/tables.js`
- [ ] `frontend/js/components/filters.js`
- [ ] `frontend/js/components/export.js`
- [ ] `frontend/Dockerfile`
- [ ] `frontend/nginx.conf`

### Database (Updates)
- [ ] `step12_issue_categories.sql`
- [ ] `step13_additional_views.sql`
- [ ] `step14_search_indexes.sql`

### Infrastructure
- [ ] `docker-compose.yml`
- [ ] `docker-compose.prod.yml`
- [ ] `scripts/backup.sh`
- [ ] `scripts/deploy.sh`
- [ ] `.env.example`

---

## Notes

- All features from Santa_Ana_website_plans are included
- Builds on existing PostgreSQL schema
- Mobile-first responsive design
- Accessibility is a first-class concern
- Caching layer for performance
- Comprehensive export functionality
- Production-ready deployment configuration
