-- =============================================================================
-- CityVotes POC - PostgreSQL Schema for Santa Ana City Council Data
-- =============================================================================
-- This schema is designed to store all voting data for Santa Ana city council
-- with full normalization for efficient querying and reporting.
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- CORE TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Cities: Store city configuration
-- -----------------------------------------------------------------------------
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    city_key VARCHAR(50) UNIQUE NOT NULL,      -- e.g., 'santa_ana'
    name VARCHAR(100) NOT NULL,                 -- e.g., 'Santa Ana'
    display_name VARCHAR(150) NOT NULL,         -- e.g., 'Santa Ana, CA'
    state VARCHAR(2) DEFAULT 'CA',
    total_seats INTEGER NOT NULL DEFAULT 7,
    primary_color VARCHAR(7) DEFAULT '#1f4e79',
    secondary_color VARCHAR(7) DEFAULT '#f4b942',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Insert Santa Ana
INSERT INTO cities (city_key, name, display_name, total_seats, primary_color, secondary_color)
VALUES ('santa_ana', 'Santa Ana', 'Santa Ana, CA', 7, '#1f4e79', '#f4b942');

-- -----------------------------------------------------------------------------
-- Council Members: Store council member information
-- -----------------------------------------------------------------------------
CREATE TABLE council_members (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    member_key VARCHAR(50) NOT NULL,            -- e.g., 'amezcua'
    full_name VARCHAR(150) NOT NULL,            -- e.g., 'Mayor Valerie Amezcua'
    short_name VARCHAR(50) NOT NULL,            -- e.g., 'Amezcua'
    title VARCHAR(50),                          -- e.g., 'Mayor', 'Council Member'
    district INTEGER,                           -- Ward/District number if applicable
    term_start DATE,
    term_end DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(city_id, member_key)
);

-- Insert Santa Ana Council Members (2024)
INSERT INTO council_members (city_id, member_key, full_name, short_name, title, is_active)
VALUES
    (1, 'amezcua', 'Mayor Valerie Amezcua', 'Amezcua', 'Mayor', TRUE),
    (1, 'hernandez', 'Johnathan Ryan Hernandez', 'Hernandez', 'Council Member', TRUE),
    (1, 'lopez', 'Jessie Lopez', 'Lopez', 'Council Member', TRUE),
    (1, 'penaloza', 'David Penaloza', 'Penaloza', 'Council Member', TRUE),
    (1, 'vazquez', 'Benjamin Vazquez', 'Vazquez', 'Council Member', TRUE),
    (1, 'phan', 'Thai Viet Phan', 'Phan', 'Council Member', TRUE),
    (1, 'bacerra', 'Phil Bacerra', 'Bacerra', 'Council Member', TRUE);

-- -----------------------------------------------------------------------------
-- Meetings: Store meeting information
-- -----------------------------------------------------------------------------
CREATE TABLE meetings (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    meeting_date DATE NOT NULL,
    meeting_type VARCHAR(50) NOT NULL,          -- 'regular', 'special', 'emergency'
    meeting_year INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM meeting_date)) STORED,
    meeting_month INTEGER GENERATED ALWAYS AS (EXTRACT(MONTH FROM meeting_date)) STORED,
    start_time TIME,
    end_time TIME,
    location VARCHAR(255),
    agenda_url TEXT,
    minutes_url TEXT,
    video_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(city_id, meeting_date, meeting_type)
);

-- Index for fast date-based queries
CREATE INDEX idx_meetings_date ON meetings(meeting_date DESC);
CREATE INDEX idx_meetings_year ON meetings(city_id, meeting_year);

-- -----------------------------------------------------------------------------
-- Agenda Items: Store individual agenda items
-- -----------------------------------------------------------------------------
CREATE TABLE agenda_items (
    id SERIAL PRIMARY KEY,
    meeting_id INTEGER REFERENCES meetings(id) ON DELETE CASCADE,
    item_number VARCHAR(20) NOT NULL,           -- e.g., '8', '26', '27.A'
    title TEXT NOT NULL,
    description TEXT,
    section VARCHAR(50) NOT NULL,               -- 'CONSENT', 'BUSINESS', 'PUBLIC_HEARING'
    department VARCHAR(150),                    -- e.g., 'City Clerk's Office'
    recommended_action TEXT,
    fiscal_impact TEXT,
    is_public_hearing BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(meeting_id, item_number)
);

-- Index for fast item lookups
CREATE INDEX idx_agenda_items_meeting ON agenda_items(meeting_id);
CREATE INDEX idx_agenda_items_section ON agenda_items(section);

-- -----------------------------------------------------------------------------
-- Votes: Store vote records for each agenda item
-- -----------------------------------------------------------------------------
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    agenda_item_id INTEGER REFERENCES agenda_items(id) ON DELETE CASCADE,
    example_id VARCHAR(50) UNIQUE,              -- Original ID from extraction (e.g., 'EX00820240220')
    outcome VARCHAR(20) NOT NULL,               -- 'PASS', 'FAIL', 'FLAG', 'CONTINUED', 'REMOVED', 'TIE'
    ayes INTEGER DEFAULT 0,
    noes INTEGER DEFAULT 0,
    abstain INTEGER DEFAULT 0,
    absent INTEGER DEFAULT 0,
    recusal INTEGER DEFAULT 0,
    motion_by INTEGER REFERENCES council_members(id),
    seconded_by INTEGER REFERENCES council_members(id),
    vote_number INTEGER DEFAULT 1,              -- For items with multiple votes
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast vote lookups
CREATE INDEX idx_votes_agenda_item ON votes(agenda_item_id);
CREATE INDEX idx_votes_outcome ON votes(outcome);
CREATE INDEX idx_votes_example_id ON votes(example_id);

-- -----------------------------------------------------------------------------
-- Member Votes: Store individual member vote choices
-- -----------------------------------------------------------------------------
CREATE TABLE member_votes (
    id SERIAL PRIMARY KEY,
    vote_id INTEGER REFERENCES votes(id) ON DELETE CASCADE,
    member_id INTEGER REFERENCES council_members(id) ON DELETE CASCADE,
    vote_choice VARCHAR(20) NOT NULL,           -- 'AYE', 'NAY', 'ABSTAIN', 'ABSENT', 'RECUSAL'
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(vote_id, member_id)
);

-- Index for fast member vote lookups
CREATE INDEX idx_member_votes_vote ON member_votes(vote_id);
CREATE INDEX idx_member_votes_member ON member_votes(member_id);
CREATE INDEX idx_member_votes_choice ON member_votes(vote_choice);

-- =============================================================================
-- SESSION MANAGEMENT TABLES (for web application)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- User Sessions: Track upload sessions
-- -----------------------------------------------------------------------------
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '2 hours',
    ip_address INET,
    user_agent TEXT
);

-- Index for session expiry cleanup
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- -----------------------------------------------------------------------------
-- Session Data: Store uploaded data temporarily
-- -----------------------------------------------------------------------------
CREATE TABLE session_data (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    original_filename VARCHAR(255),
    upload_timestamp TIMESTAMP DEFAULT NOW(),
    raw_data JSONB NOT NULL,                    -- Original uploaded JSON
    processed_data JSONB NOT NULL,              -- Calculated summaries
    vote_count INTEGER DEFAULT 0,
    UNIQUE(session_id, city_id)
);

-- Index for session data lookups
CREATE INDEX idx_session_data_session ON session_data(session_id);
CREATE INDEX idx_session_data_city ON session_data(city_id);

-- =============================================================================
-- ANALYTICS & REPORTING VIEWS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- View: Vote Summary by Meeting
-- -----------------------------------------------------------------------------
CREATE VIEW v_meeting_summary AS
SELECT
    m.id AS meeting_id,
    c.display_name AS city_name,
    m.meeting_date,
    m.meeting_type,
    COUNT(DISTINCT ai.id) AS total_items,
    COUNT(v.id) AS total_votes,
    SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN v.outcome = 'FAIL' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN v.outcome = 'FLAG' THEN 1 ELSE 0 END) AS flagged
FROM meetings m
JOIN cities c ON m.city_id = c.id
LEFT JOIN agenda_items ai ON ai.meeting_id = m.id
LEFT JOIN votes v ON v.agenda_item_id = ai.id
GROUP BY m.id, c.display_name, m.meeting_date, m.meeting_type
ORDER BY m.meeting_date DESC;

-- -----------------------------------------------------------------------------
-- View: Member Voting Statistics
-- -----------------------------------------------------------------------------
CREATE VIEW v_member_stats AS
SELECT
    cm.id AS member_id,
    cm.full_name,
    cm.short_name,
    c.display_name AS city_name,
    COUNT(mv.id) AS total_votes,
    SUM(CASE WHEN mv.vote_choice = 'AYE' THEN 1 ELSE 0 END) AS aye_count,
    SUM(CASE WHEN mv.vote_choice = 'NAY' THEN 1 ELSE 0 END) AS nay_count,
    SUM(CASE WHEN mv.vote_choice = 'ABSTAIN' THEN 1 ELSE 0 END) AS abstain_count,
    SUM(CASE WHEN mv.vote_choice = 'ABSENT' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN mv.vote_choice = 'RECUSAL' THEN 1 ELSE 0 END) AS recusal_count,
    ROUND(
        SUM(CASE WHEN mv.vote_choice = 'AYE' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(SUM(CASE WHEN mv.vote_choice IN ('AYE', 'NAY') THEN 1 ELSE 0 END), 0) * 100,
        1
    ) AS aye_percentage
FROM council_members cm
JOIN cities c ON cm.city_id = c.id
LEFT JOIN member_votes mv ON mv.member_id = cm.id
GROUP BY cm.id, cm.full_name, cm.short_name, c.display_name
ORDER BY cm.full_name;

-- -----------------------------------------------------------------------------
-- View: Member Alignment (agreement percentage between pairs)
-- -----------------------------------------------------------------------------
CREATE VIEW v_member_alignment AS
SELECT
    m1.id AS member1_id,
    m1.short_name AS member1_name,
    m2.id AS member2_id,
    m2.short_name AS member2_name,
    COUNT(*) AS total_comparisons,
    SUM(CASE WHEN mv1.vote_choice = mv2.vote_choice THEN 1 ELSE 0 END) AS agreements,
    ROUND(
        SUM(CASE WHEN mv1.vote_choice = mv2.vote_choice THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(*), 0) * 100,
        1
    ) AS alignment_percentage
FROM member_votes mv1
JOIN member_votes mv2 ON mv1.vote_id = mv2.vote_id AND mv1.member_id < mv2.member_id
JOIN council_members m1 ON mv1.member_id = m1.id
JOIN council_members m2 ON mv2.member_id = m2.id
WHERE mv1.vote_choice IN ('AYE', 'NAY') AND mv2.vote_choice IN ('AYE', 'NAY')
GROUP BY m1.id, m1.short_name, m2.id, m2.short_name
ORDER BY alignment_percentage DESC;

-- -----------------------------------------------------------------------------
-- View: Yearly Vote Statistics
-- -----------------------------------------------------------------------------
CREATE VIEW v_yearly_stats AS
SELECT
    c.display_name AS city_name,
    m.meeting_year AS year,
    COUNT(DISTINCT m.id) AS total_meetings,
    COUNT(v.id) AS total_votes,
    SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN v.outcome = 'FAIL' THEN 1 ELSE 0 END) AS failed,
    ROUND(
        SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(v.id), 0) * 100,
        1
    ) AS pass_rate
FROM meetings m
JOIN cities c ON m.city_id = c.id
LEFT JOIN agenda_items ai ON ai.meeting_id = m.id
LEFT JOIN votes v ON v.agenda_item_id = ai.id
GROUP BY c.display_name, m.meeting_year
ORDER BY m.meeting_year DESC;

-- -----------------------------------------------------------------------------
-- View: Section Statistics
-- -----------------------------------------------------------------------------
CREATE VIEW v_section_stats AS
SELECT
    c.display_name AS city_name,
    ai.section,
    COUNT(v.id) AS total_votes,
    SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END) AS passed,
    ROUND(
        SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(v.id), 0) * 100,
        1
    ) AS pass_rate,
    ROUND(AVG(v.ayes + v.noes), 1) AS avg_participating_members
FROM agenda_items ai
JOIN meetings m ON ai.meeting_id = m.id
JOIN cities c ON m.city_id = c.id
LEFT JOIN votes v ON v.agenda_item_id = ai.id
GROUP BY c.display_name, ai.section
ORDER BY ai.section;

-- =============================================================================
-- FUNCTIONS & PROCEDURES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: Clean expired sessions
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION clean_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- Function: Get member voting history
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_member_voting_history(
    p_member_id INTEGER,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    meeting_date DATE,
    item_number VARCHAR(20),
    title TEXT,
    section VARCHAR(50),
    vote_choice VARCHAR(20),
    outcome VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.meeting_date,
        ai.item_number,
        ai.title,
        ai.section,
        mv.vote_choice,
        v.outcome
    FROM member_votes mv
    JOIN votes v ON mv.vote_id = v.id
    JOIN agenda_items ai ON v.agenda_item_id = ai.id
    JOIN meetings m ON ai.meeting_id = m.id
    WHERE mv.member_id = p_member_id
    ORDER BY m.meeting_date DESC, ai.item_number
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- Function: Import votes from JSON
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION import_votes_from_json(
    p_city_id INTEGER,
    p_json_data JSONB
)
RETURNS TABLE (
    meetings_created INTEGER,
    items_created INTEGER,
    votes_created INTEGER
) AS $$
DECLARE
    v_vote JSONB;
    v_meeting_id INTEGER;
    v_item_id INTEGER;
    v_vote_id INTEGER;
    v_member_id INTEGER;
    v_member_key TEXT;
    v_vote_choice TEXT;
    v_meeting_date DATE;
    v_meetings_created INTEGER := 0;
    v_items_created INTEGER := 0;
    v_votes_created INTEGER := 0;
BEGIN
    -- Loop through each vote in the JSON array
    FOR v_vote IN SELECT * FROM jsonb_array_elements(p_json_data->'votes')
    LOOP
        -- Parse meeting date
        v_meeting_date := TO_DATE(v_vote->>'meeting_date', 'MM/DD/YY');

        -- Insert or get meeting
        INSERT INTO meetings (city_id, meeting_date, meeting_type)
        VALUES (
            p_city_id,
            v_meeting_date,
            COALESCE(v_vote->>'meeting_type', 'regular')
        )
        ON CONFLICT (city_id, meeting_date, meeting_type) DO UPDATE
        SET updated_at = NOW()
        RETURNING id INTO v_meeting_id;

        IF NOT FOUND THEN
            SELECT id INTO v_meeting_id FROM meetings
            WHERE city_id = p_city_id AND meeting_date = v_meeting_date;
        ELSE
            v_meetings_created := v_meetings_created + 1;
        END IF;

        -- Insert agenda item
        INSERT INTO agenda_items (
            meeting_id,
            item_number,
            title,
            description,
            section
        )
        VALUES (
            v_meeting_id,
            v_vote->>'agenda_item_number',
            v_vote->>'agenda_item_title',
            v_vote->>'agenda_item_description',
            COALESCE(v_vote->>'meeting_section', 'GENERAL')
        )
        ON CONFLICT (meeting_id, item_number) DO UPDATE
        SET updated_at = NOW()
        RETURNING id INTO v_item_id;

        v_items_created := v_items_created + 1;

        -- Insert vote record
        INSERT INTO votes (
            agenda_item_id,
            example_id,
            outcome,
            ayes,
            noes,
            abstain,
            absent
        )
        VALUES (
            v_item_id,
            v_vote->>'example_id',
            COALESCE(v_vote->>'outcome', 'PASS'),
            COALESCE((v_vote->'tally'->>'ayes')::INTEGER, 0),
            COALESCE((v_vote->'tally'->>'noes')::INTEGER, 0),
            COALESCE((v_vote->'tally'->>'abstain')::INTEGER, 0),
            COALESCE((v_vote->'tally'->>'absent')::INTEGER, 0)
        )
        ON CONFLICT (example_id) DO UPDATE
        SET updated_at = NOW()
        RETURNING id INTO v_vote_id;

        v_votes_created := v_votes_created + 1;

        -- Insert member votes
        FOR v_member_key, v_vote_choice IN
            SELECT key, value FROM jsonb_each_text(v_vote->'member_votes')
        LOOP
            -- Find member by short name
            SELECT id INTO v_member_id FROM council_members
            WHERE city_id = p_city_id AND LOWER(short_name) = LOWER(v_member_key);

            IF v_member_id IS NOT NULL THEN
                INSERT INTO member_votes (vote_id, member_id, vote_choice)
                VALUES (v_vote_id, v_member_id, UPPER(v_vote_choice))
                ON CONFLICT (vote_id, member_id) DO UPDATE
                SET vote_choice = EXCLUDED.vote_choice;
            END IF;
        END LOOP;
    END LOOP;

    RETURN QUERY SELECT v_meetings_created, v_items_created, v_votes_created;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Full-text search on agenda item titles
CREATE INDEX idx_agenda_items_title_gin ON agenda_items USING gin(to_tsvector('english', title));

-- JSONB indexes for session data
CREATE INDEX idx_session_data_raw ON session_data USING gin(raw_data);
CREATE INDEX idx_session_data_processed ON session_data USING gin(processed_data);

-- =============================================================================
-- SAMPLE QUERIES
-- =============================================================================

-- Get all votes for a specific meeting
-- SELECT * FROM votes v
-- JOIN agenda_items ai ON v.agenda_item_id = ai.id
-- JOIN meetings m ON ai.meeting_id = m.id
-- WHERE m.meeting_date = '2024-01-16';

-- Get member voting record
-- SELECT * FROM get_member_voting_history(1, 50);

-- Get alignment between two members
-- SELECT * FROM v_member_alignment
-- WHERE member1_name = 'Amezcua' OR member2_name = 'Amezcua';

-- Search agenda items
-- SELECT * FROM agenda_items
-- WHERE to_tsvector('english', title) @@ to_tsquery('budget & amendment');

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
