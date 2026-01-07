# CityVotes Database Schema Report

## Overview

This document provides a comprehensive report on each table in the CityVotes PostgreSQL database, including purpose, columns, relationships, and usage notes.

---

## Table Summary

| Table | Purpose | Records (Santa Ana 2024) |
|-------|---------|--------------------------|
| `cities` | Multi-city configuration and branding | 1 |
| `council_members` | Council member profiles | 7 |
| `council_member_terms` | Historical position tracking | 7 |
| `meetings` | City council meeting records | 22 |
| `agenda_items` | Individual items on meeting agendas | 437 |
| `votes` | Vote outcomes and tallies | 437 |
| `member_votes` | How each member voted | 3,059 |
| `sessions` | Web app user sessions | Variable |
| `session_data` | Uploaded JSON data per session | Variable |

---

## 1. cities

### Purpose
Stores configuration for each city supported by the system. Acts as the top-level entity that all other data links to. Enables multi-city support without schema changes.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `city_key` | VARCHAR(50) | URL-safe identifier (e.g., `santa_ana`) |
| `name` | VARCHAR(100) | Short name (e.g., `Santa Ana`) |
| `display_name` | VARCHAR(150) | Full display name (e.g., `Santa Ana, CA`) |
| `state` | VARCHAR(2) | State abbreviation, default `CA` |
| `total_seats` | INTEGER | Number of council seats (Santa Ana = 7) |
| `primary_color` | VARCHAR(7) | Hex color for branding (e.g., `#1f4e79`) |
| `secondary_color` | VARCHAR(7) | Secondary hex color (e.g., `#f4b942`) |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Relationships
- **Parent of:** `council_members`, `meetings`, `session_data`
- **Referenced by:** All city-specific data

### Usage
- Dashboard theming uses `primary_color` and `secondary_color`
- API routes use `city_key` in URLs: `/api/dashboard/{city_key}/votes`
- `total_seats` validates expected member count in votes

### Sample Data
```sql
INSERT INTO cities (city_key, name, display_name, total_seats, primary_color, secondary_color)
VALUES ('santa_ana', 'Santa Ana', 'Santa Ana, CA', 7, '#1f4e79', '#f4b942');
```

---

## 2. council_members

### Purpose
Stores council member profiles for each city. Contains identifying information used to match members in vote records and display on dashboards.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `city_id` | INTEGER | Foreign key to `cities` |
| `member_key` | VARCHAR(50) | URL-safe identifier (e.g., `amezcua`) |
| `full_name` | VARCHAR(150) | Full legal name |
| `short_name` | VARCHAR(50) | Name as appears in vote records (used for matching) |
| `title` | VARCHAR(50) | Current title (Mayor, Council Member, etc.) |
| `district` | INTEGER | Ward/district number if applicable |
| `term_start` | DATE | Overall term start (legacy field) |
| `term_end` | DATE | Overall term end (legacy field) |
| `is_active` | BOOLEAN | Whether currently serving |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Relationships
- **Parent:** `cities`
- **Children:** `council_member_terms`, `member_votes`
- **Referenced by:** `votes` (motion_by, seconded_by)

### Constraints
- `UNIQUE (city_id, member_key)` - No duplicate member keys per city

### Indexes
- `idx_council_members_city` - Fast lookup by city
- `idx_council_members_active` - Filter active members

### Usage
- `short_name` is critical for matching CSV import data to members
- `member_key` used in URLs: `/api/members/{member_key}`
- `is_active` filters current vs. former members

### Sample Data
```sql
INSERT INTO council_members (city_id, member_key, full_name, short_name, title, is_active)
VALUES (1, 'amezcua', 'Valerie Amezcua', 'Amezcua', 'Mayor', TRUE);
```

---

## 3. council_member_terms

### Purpose
Tracks council member positions over time. Handles scenarios where members:
1. Get re-elected to the same position
2. Change positions (council member → mayor)
3. Leave and return to council
4. Are appointed vs. elected

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `member_id` | INTEGER | Foreign key to `council_members` |
| `position` | VARCHAR(50) | Position held (Mayor, Vice Mayor, Council Member) |
| `district` | INTEGER | District/ward during this term |
| `term_start` | DATE | When term began |
| `term_end` | DATE | When term ended (NULL = currently serving) |
| `election_date` | DATE | Date of election (if applicable) |
| `appointment_type` | VARCHAR(50) | How they got position: `elected`, `appointed`, `interim` |
| `notes` | TEXT | Additional notes |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Relationships
- **Parent:** `council_members`
- **Referenced by:** `member_votes` (optional term_id)

### Constraints
- `CHECK (term_end IS NULL OR term_end > term_start)` - Valid date range
- `CHECK (appointment_type IN ('elected', 'appointed', 'interim'))`

### Indexes
- `idx_council_member_terms_member` - Lookup terms by member
- `idx_council_member_terms_dates` - Date range queries
- `idx_council_member_terms_active` - Partial index for current terms (WHERE term_end IS NULL)

### Usage
- Determine who was serving on a specific meeting date
- Track position changes (e.g., Amezcua was council member before becoming mayor)
- Historical accuracy for vote attribution

### Sample Data
```sql
-- Mayor Amezcua elected December 2022
INSERT INTO council_member_terms (member_id, position, district, term_start, appointment_type)
VALUES (1, 'Mayor', 3, '2022-12-13', 'elected');
```

---

## 4. meetings

### Purpose
Stores city council meeting records. Each meeting contains multiple agenda items and votes.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `city_id` | INTEGER | Foreign key to `cities` |
| `meeting_date` | DATE | Date of meeting |
| `meeting_type` | VARCHAR(50) | Type: `regular`, `special`, `emergency`, `closed` |
| `meeting_year` | INTEGER | Auto-generated from date (STORED) |
| `meeting_month` | INTEGER | Auto-generated from date (STORED) |
| `start_time` | TIME | Meeting start time |
| `end_time` | TIME | Meeting end time |
| `location` | VARCHAR(255) | Meeting location |
| `agenda_url` | TEXT | Link to original agenda PDF |
| `minutes_url` | TEXT | Link to original minutes PDF |
| `video_url` | TEXT | Link to meeting video |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Relationships
- **Parent:** `cities`
- **Children:** `agenda_items`

### Constraints
- `UNIQUE (city_id, meeting_date, meeting_type)` - One meeting per date/type combo

### Generated Columns
- `meeting_year` - Automatically extracted from `meeting_date`
- `meeting_month` - Automatically extracted from `meeting_date`

### Indexes
- `idx_meetings_city` - Filter by city
- `idx_meetings_date` - Sort by date (descending)
- `idx_meetings_year` - Filter by year
- `idx_meetings_city_date` - Combined city + date lookup

### Usage
- Group votes by meeting for dashboard display
- Link to original source documents (agenda, minutes, video)
- Filter by year/month for trend analysis

### Sample Query
```sql
-- Get all 2024 regular meetings for Santa Ana
SELECT * FROM meetings
WHERE city_id = 1 AND meeting_year = 2024 AND meeting_type = 'regular'
ORDER BY meeting_date;
```

---

## 5. agenda_items

### Purpose
Stores individual items from meeting agendas. Each agenda item can have one or more votes.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `meeting_id` | INTEGER | Foreign key to `meetings` |
| `item_number` | VARCHAR(20) | Agenda item number (e.g., `8`, `26`, `27.A`) |
| `title` | TEXT | Item title/subject |
| `description` | TEXT | Detailed description |
| `section` | VARCHAR(50) | Agenda section: `CONSENT`, `BUSINESS`, `PUBLIC_HEARING`, `CLOSED`, `GENERAL` |
| `department` | VARCHAR(150) | Responsible department |
| `recommended_action` | TEXT | Staff recommendation |
| `fiscal_impact` | TEXT | Budget/financial impact |
| `is_public_hearing` | BOOLEAN | Whether item required public hearing |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Relationships
- **Parent:** `meetings`
- **Children:** `votes`

### Constraints
- `UNIQUE (meeting_id, item_number)` - No duplicate item numbers per meeting

### Indexes
- `idx_agenda_items_meeting` - Lookup items by meeting
- `idx_agenda_items_section` - Filter by section type
- `idx_agenda_items_title_gin` - Full-text search on titles

### Usage
- Display agenda context when viewing votes
- Filter votes by section (consent vs. business items)
- Full-text search for topics across all meetings

### Sample Query
```sql
-- Search for budget-related items
SELECT ai.*, m.meeting_date
FROM agenda_items ai
JOIN meetings m ON ai.meeting_id = m.id
WHERE to_tsvector('english', ai.title) @@ to_tsquery('budget');
```

---

## 6. votes

### Purpose
Stores vote outcomes and tallies for each agenda item. Contains the overall result and counts, not individual member votes.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `agenda_item_id` | INTEGER | Foreign key to `agenda_items` |
| `example_id` | VARCHAR(50) | Original ID from CSV extraction (for deduplication) |
| `outcome` | VARCHAR(20) | Result: `PASS`, `FAIL`, `FLAG`, `CONTINUED`, `REMOVED`, `TIE` |
| `ayes` | INTEGER | Number of aye votes |
| `noes` | INTEGER | Number of no votes |
| `abstain` | INTEGER | Number of abstentions |
| `absent` | INTEGER | Number absent |
| `recusal` | INTEGER | Number of recusals |
| `motion_by` | INTEGER | Foreign key to `council_members` (who made motion) |
| `seconded_by` | INTEGER | Foreign key to `council_members` (who seconded) |
| `vote_number` | INTEGER | For items with multiple votes (default 1) |
| `notes` | TEXT | Additional notes |
| `created_at` | TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | Last update time |

### Relationships
- **Parent:** `agenda_items`
- **Children:** `member_votes`
- **References:** `council_members` (motion_by, seconded_by)

### Constraints
- `UNIQUE (example_id)` - Prevents duplicate imports

### Indexes
- `idx_votes_agenda_item` - Lookup votes by agenda item
- `idx_votes_outcome` - Filter by outcome
- `idx_votes_example_id` - Fast lookup for import deduplication

### Outcome Values

| Outcome | Description |
|---------|-------------|
| `PASS` | Motion passed |
| `FAIL` | Motion failed |
| `FLAG` | Flagged for review (data quality issue) |
| `CONTINUED` | Item continued to future meeting |
| `REMOVED` | Item removed from agenda |
| `TIE` | Tie vote |

### Usage
- Dashboard pie charts show outcome distribution
- Tally fields validate against member_votes count
- `example_id` enables re-running imports safely

### Sample Query
```sql
-- Get all failed votes
SELECT v.*, ai.title, m.meeting_date
FROM votes v
JOIN agenda_items ai ON v.agenda_item_id = ai.id
JOIN meetings m ON ai.meeting_id = m.id
WHERE v.outcome = 'FAIL';
```

---

## 7. member_votes

### Purpose
Stores how each council member voted on each vote. This is the most granular voting data, enabling member analysis and alignment calculations.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `vote_id` | INTEGER | Foreign key to `votes` |
| `member_id` | INTEGER | Foreign key to `council_members` |
| `term_id` | INTEGER | Foreign key to `council_member_terms` (optional) |
| `vote_choice` | VARCHAR(20) | How they voted: `AYE`, `NAY`, `ABSTAIN`, `ABSENT`, `RECUSAL` |
| `created_at` | TIMESTAMP | Record creation time |

### Relationships
- **Parents:** `votes`, `council_members`, `council_member_terms`

### Constraints
- `UNIQUE (vote_id, member_id)` - One vote per member per vote record
- `CHECK (vote_choice IN ('AYE', 'NAY', 'ABSTAIN', 'ABSENT', 'RECUSAL'))`

### Indexes
- `idx_member_votes_vote` - Lookup all votes for a vote record
- `idx_member_votes_member` - Lookup all votes by a member
- `idx_member_votes_term` - Lookup votes by term
- `idx_member_votes_choice` - Filter by vote choice
- `idx_member_votes_member_choice` - Combined member + choice lookup

### Vote Choice Values

| Choice | Description |
|--------|-------------|
| `AYE` | Voted yes/in favor |
| `NAY` | Voted no/against |
| `ABSTAIN` | Abstained from voting |
| `ABSENT` | Was not present |
| `RECUSAL` | Recused due to conflict of interest |

### Usage
- Calculate member voting statistics
- Generate alignment matrix between members
- Track attendance/participation rates
- Link to specific term for historical accuracy

### Sample Query
```sql
-- Get all NAY votes by a specific member
SELECT mv.*, ai.title, m.meeting_date
FROM member_votes mv
JOIN votes v ON mv.vote_id = v.id
JOIN agenda_items ai ON v.agenda_item_id = ai.id
JOIN meetings m ON ai.meeting_id = m.id
WHERE mv.member_id = 1 AND mv.vote_choice = 'NAY';
```

---

## 8. sessions

### Purpose
Manages web application user sessions. Each visitor gets a unique session that expires after 2 hours. Used for the upload/dashboard workflow.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated UUID) |
| `created_at` | TIMESTAMP | Session creation time |
| `expires_at` | TIMESTAMP | Expiration time (default: 2 hours from creation) |
| `ip_address` | INET | Client IP address |
| `user_agent` | TEXT | Browser user agent string |

### Relationships
- **Children:** `session_data`

### Indexes
- `idx_sessions_expires` - Find expired sessions for cleanup

### Usage
- Frontend stores `session_id` in localStorage
- Session links uploaded data to user's browser
- Automatic cleanup removes expired sessions

### Sample Query
```sql
-- Clean up expired sessions
SELECT clean_expired_sessions();

-- Get active sessions
SELECT * FROM sessions WHERE expires_at > NOW();
```

---

## 9. session_data

### Purpose
Stores uploaded voting data for each session. When a user uploads a JSON file, the raw data and pre-calculated summaries are stored here for quick dashboard rendering.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL | Primary key |
| `session_id` | UUID | Foreign key to `sessions` |
| `city_id` | INTEGER | Foreign key to `cities` |
| `original_filename` | VARCHAR(255) | Name of uploaded file |
| `upload_timestamp` | TIMESTAMP | When file was uploaded |
| `raw_data` | JSONB | Original uploaded JSON |
| `processed_data` | JSONB | Pre-calculated summaries for dashboard |
| `vote_count` | INTEGER | Number of votes in upload |

### Relationships
- **Parents:** `sessions`, `cities`

### Constraints
- `UNIQUE (session_id, city_id)` - One upload per city per session

### Indexes
- `idx_session_data_session` - Lookup by session
- `idx_session_data_city` - Lookup by city
- `idx_session_data_raw` - GIN index for JSONB queries on raw data
- `idx_session_data_processed` - GIN index for JSONB queries on processed data

### JSONB Fields

**raw_data** - Original upload format:
```json
{
  "votes": [
    {
      "example_id": "EX20240116_26",
      "meeting_date": "1/16/24",
      "outcome": "Pass",
      "member_votes": {"Amezcua": "Aye", ...}
    }
  ]
}
```

**processed_data** - Pre-calculated summaries:
```json
{
  "total_votes": 437,
  "pass_rate": 95.2,
  "member_stats": {...},
  "alignment_matrix": {...}
}
```

### Usage
- Quick dashboard rendering without recalculating
- Preserves original upload for debugging
- JSONB indexes enable fast queries within JSON

---

## Materialized Views

### Purpose
Pre-computed aggregations for fast dashboard queries. Refreshed after data imports.

| View | Purpose | Key Columns |
|------|---------|-------------|
| `mv_meeting_summary` | Meeting statistics | total_items, total_votes, pass_rate |
| `mv_vote_summary` | Yearly vote totals | total_meetings, passed, failed, pass_rate |
| `mv_member_stats` | Member voting statistics | aye_count, nay_count, aye_percentage, participation_rate |
| `mv_member_alignment` | Pairwise member agreement | agreements, alignment_percentage |

### Refresh Command
```sql
SELECT refresh_all_materialized_views();
```

---

## Database Functions

| Function | Purpose | Parameters |
|----------|---------|------------|
| `refresh_all_materialized_views()` | Refresh all views after import | None |
| `clean_expired_sessions()` | Delete expired sessions | None |
| `get_active_members_for_date(city_id, date)` | Get who was serving on a date | city_id, date |
| `get_member_term_for_date(member_id, date)` | Get term for member on date | member_id, date |
| `get_member_voting_history(member_id, limit)` | Get member's vote history | member_id, limit |

---

## Entity Relationship Diagram

```
┌─────────────┐
│   cities    │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────────────┐     ┌──────────────────────┐
│  council_members    │────▶│ council_member_terms │
└──────────┬──────────┘     └──────────────────────┘
           │                           │
           │ 1:N                       │ (optional)
           ▼                           ▼
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  meetings   │────▶│ agenda_items│────▶│    votes     │
└─────────────┘ 1:N └─────────────┘ 1:N └──────┬───────┘
                                              │ 1:N
                                              ▼
                                       ┌──────────────┐
                                       │ member_votes │
                                       └──────────────┘

┌─────────────┐     ┌──────────────┐
│  sessions   │────▶│ session_data │
└─────────────┘ 1:N └──────────────┘
```

---

## Data Volume Estimates

Based on Santa Ana 2024 data:

| Metric | Value |
|--------|-------|
| Meetings per year | ~22 |
| Votes per meeting | ~20 |
| Total votes per year | ~437 |
| Member votes per year | ~3,059 (7 members × 437 votes) |

### Growth Projections (5 years)

| Table | 1 City | 5 Cities |
|-------|--------|----------|
| meetings | 110 | 550 |
| agenda_items | 2,185 | 10,925 |
| votes | 2,185 | 10,925 |
| member_votes | 15,295 | 76,475 |

The schema handles this scale easily with proper indexing.

---

## Maintenance Tasks

### Daily
```sql
-- Clean expired sessions
SELECT clean_expired_sessions();
```

### After Data Import
```sql
-- Refresh all materialized views
SELECT refresh_all_materialized_views();
```

### Weekly (Optional)
```sql
-- Analyze tables for query optimization
ANALYZE;
```

---

*Report generated for CityVotes POC - January 2026*
