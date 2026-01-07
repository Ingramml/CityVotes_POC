-- =============================================================================
-- CityVotes POC - PostgreSQL Schema for Santa Ana City Council Data
-- =============================================================================
-- Normalized schema with materialized views for fast dashboard queries
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- DROP EXISTING OBJECTS (for clean recreation)
-- =============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_member_alignment CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_member_stats CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_vote_summary CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_meeting_summary CASCADE;

DROP VIEW IF EXISTS v_section_stats CASCADE;
DROP VIEW IF EXISTS v_yearly_stats CASCADE;
DROP VIEW IF EXISTS v_member_alignment CASCADE;
DROP VIEW IF EXISTS v_member_stats CASCADE;
DROP VIEW IF EXISTS v_meeting_summary CASCADE;

DROP TABLE IF EXISTS member_votes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS agenda_items CASCADE;
DROP TABLE IF EXISTS meetings CASCADE;
DROP TABLE IF EXISTS council_member_terms CASCADE;
DROP TABLE IF EXISTS council_members CASCADE;
DROP TABLE IF EXISTS session_data CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS cities CASCADE;

-- =============================================================================
-- TABLE: cities
-- =============================================================================
-- Stores city configuration and branding
-- =============================================================================
CREATE TABLE cities (
    id                  SERIAL PRIMARY KEY,
    city_key            VARCHAR(50) UNIQUE NOT NULL,
    name                VARCHAR(100) NOT NULL,
    display_name        VARCHAR(150) NOT NULL,
    state               VARCHAR(2) DEFAULT 'CA',
    total_seats         INTEGER NOT NULL DEFAULT 7,
    primary_color       VARCHAR(7) DEFAULT '#1f4e79',
    secondary_color     VARCHAR(7) DEFAULT '#f4b942',
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE cities IS 'City configuration and branding settings';
COMMENT ON COLUMN cities.city_key IS 'URL-safe identifier (e.g., santa_ana)';
COMMENT ON COLUMN cities.total_seats IS 'Number of council seats';

-- =============================================================================
-- TABLE: council_members
-- =============================================================================
-- Stores council member information for each city
-- =============================================================================
CREATE TABLE council_members (
    id                  SERIAL PRIMARY KEY,
    city_id             INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    member_key          VARCHAR(50) NOT NULL,
    full_name           VARCHAR(150) NOT NULL,
    short_name          VARCHAR(50) NOT NULL,
    title               VARCHAR(50),
    district            INTEGER,
    term_start          DATE,
    term_end            DATE,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uq_council_members_city_key UNIQUE (city_id, member_key)
);

COMMENT ON TABLE council_members IS 'Council members for each city';
COMMENT ON COLUMN council_members.member_key IS 'URL-safe identifier (e.g., amezcua)';
COMMENT ON COLUMN council_members.short_name IS 'Name as appears in vote records';

CREATE INDEX idx_council_members_city ON council_members(city_id);
CREATE INDEX idx_council_members_active ON council_members(city_id, is_active);

-- =============================================================================
-- TABLE: council_member_terms
-- =============================================================================
-- Tracks council member positions over time (handles role changes, re-elections)
-- A member can have multiple terms if they:
--   1. Get re-elected to the same position
--   2. Change positions (council member -> mayor)
--   3. Leave and return to council
-- =============================================================================
CREATE TABLE council_member_terms (
    id                  SERIAL PRIMARY KEY,
    member_id           INTEGER NOT NULL REFERENCES council_members(id) ON DELETE CASCADE,
    position            VARCHAR(50) NOT NULL DEFAULT 'Council Member',
    district            INTEGER,
    term_start          DATE NOT NULL,
    term_end            DATE,                    -- NULL means currently serving
    election_date       DATE,
    appointment_type    VARCHAR(50) DEFAULT 'elected',  -- elected, appointed, interim
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_term_dates CHECK (term_end IS NULL OR term_end > term_start),
    CONSTRAINT chk_appointment_type CHECK (appointment_type IN ('elected', 'appointed', 'interim'))
);

COMMENT ON TABLE council_member_terms IS 'Tracks council member positions over time';
COMMENT ON COLUMN council_member_terms.position IS 'Mayor, Vice Mayor, Council Member, etc.';
COMMENT ON COLUMN council_member_terms.term_end IS 'NULL indicates currently serving';
COMMENT ON COLUMN council_member_terms.appointment_type IS 'How they got the position';

CREATE INDEX idx_council_member_terms_member ON council_member_terms(member_id);
CREATE INDEX idx_council_member_terms_dates ON council_member_terms(term_start, term_end);
CREATE INDEX idx_council_member_terms_active ON council_member_terms(member_id)
    WHERE term_end IS NULL;

-- =============================================================================
-- TABLE: meetings
-- =============================================================================
-- Stores city council meeting information
-- =============================================================================
CREATE TABLE meetings (
    id                  SERIAL PRIMARY KEY,
    city_id             INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    meeting_date        DATE NOT NULL,
    meeting_type        VARCHAR(50) NOT NULL DEFAULT 'regular',
    meeting_year        INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM meeting_date)) STORED,
    meeting_month       INTEGER GENERATED ALWAYS AS (EXTRACT(MONTH FROM meeting_date)) STORED,
    start_time          TIME,
    end_time            TIME,
    location            VARCHAR(255),
    agenda_url          TEXT,
    minutes_url         TEXT,
    video_url           TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uq_meetings_city_date_type UNIQUE (city_id, meeting_date, meeting_type)
);

COMMENT ON TABLE meetings IS 'City council meetings';
COMMENT ON COLUMN meetings.meeting_type IS 'regular, special, emergency, closed';
COMMENT ON COLUMN meetings.meeting_year IS 'Auto-generated from meeting_date';

CREATE INDEX idx_meetings_city ON meetings(city_id);
CREATE INDEX idx_meetings_date ON meetings(meeting_date DESC);
CREATE INDEX idx_meetings_year ON meetings(city_id, meeting_year);
CREATE INDEX idx_meetings_city_date ON meetings(city_id, meeting_date DESC);

-- =============================================================================
-- TABLE: agenda_items
-- =============================================================================
-- Stores individual agenda items for each meeting
-- =============================================================================
CREATE TABLE agenda_items (
    id                  SERIAL PRIMARY KEY,
    meeting_id          INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    item_number         VARCHAR(20) NOT NULL,
    title               TEXT NOT NULL,
    description         TEXT,
    section             VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    department          VARCHAR(150),
    recommended_action  TEXT,
    fiscal_impact       TEXT,
    is_public_hearing   BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uq_agenda_items_meeting_number UNIQUE (meeting_id, item_number)
);

COMMENT ON TABLE agenda_items IS 'Individual agenda items for each meeting';
COMMENT ON COLUMN agenda_items.section IS 'CONSENT, BUSINESS, PUBLIC_HEARING, CLOSED';
COMMENT ON COLUMN agenda_items.item_number IS 'Agenda item number (e.g., 8, 26, 27.A)';

CREATE INDEX idx_agenda_items_meeting ON agenda_items(meeting_id);
CREATE INDEX idx_agenda_items_section ON agenda_items(section);
CREATE INDEX idx_agenda_items_title_gin ON agenda_items USING gin(to_tsvector('english', title));

-- =============================================================================
-- TABLE: votes
-- =============================================================================
-- Stores vote records for each agenda item
-- =============================================================================
CREATE TABLE votes (
    id                  SERIAL PRIMARY KEY,
    agenda_item_id      INTEGER NOT NULL REFERENCES agenda_items(id) ON DELETE CASCADE,
    example_id          VARCHAR(50) UNIQUE,
    outcome             VARCHAR(20) NOT NULL,
    ayes                INTEGER DEFAULT 0,
    noes                INTEGER DEFAULT 0,
    abstain             INTEGER DEFAULT 0,
    absent              INTEGER DEFAULT 0,
    recusal             INTEGER DEFAULT 0,
    motion_by           INTEGER REFERENCES council_members(id),
    seconded_by         INTEGER REFERENCES council_members(id),
    vote_number         INTEGER DEFAULT 1,
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE votes IS 'Vote records for agenda items';
COMMENT ON COLUMN votes.outcome IS 'PASS, FAIL, FLAG, CONTINUED, REMOVED, TIE';
COMMENT ON COLUMN votes.example_id IS 'Original ID from data extraction';
COMMENT ON COLUMN votes.vote_number IS 'For items with multiple votes';

CREATE INDEX idx_votes_agenda_item ON votes(agenda_item_id);
CREATE INDEX idx_votes_outcome ON votes(outcome);
CREATE INDEX idx_votes_example_id ON votes(example_id);

-- =============================================================================
-- TABLE: member_votes
-- =============================================================================
-- Stores individual member vote choices
-- =============================================================================
CREATE TABLE member_votes (
    id                  SERIAL PRIMARY KEY,
    vote_id             INTEGER NOT NULL REFERENCES votes(id) ON DELETE CASCADE,
    member_id           INTEGER NOT NULL REFERENCES council_members(id) ON DELETE CASCADE,
    term_id             INTEGER REFERENCES council_member_terms(id) ON DELETE SET NULL,
    vote_choice         VARCHAR(20) NOT NULL,
    created_at          TIMESTAMP DEFAULT NOW(),

    CONSTRAINT uq_member_votes_vote_member UNIQUE (vote_id, member_id),
    CONSTRAINT chk_vote_choice CHECK (vote_choice IN ('AYE', 'NAY', 'ABSTAIN', 'ABSENT', 'RECUSAL'))
);

COMMENT ON TABLE member_votes IS 'Individual council member vote choices';
COMMENT ON COLUMN member_votes.vote_choice IS 'AYE, NAY, ABSTAIN, ABSENT, RECUSAL';
COMMENT ON COLUMN member_votes.term_id IS 'Links to term when vote was cast (for historical accuracy)';

CREATE INDEX idx_member_votes_vote ON member_votes(vote_id);
CREATE INDEX idx_member_votes_member ON member_votes(member_id);
CREATE INDEX idx_member_votes_term ON member_votes(term_id);
CREATE INDEX idx_member_votes_choice ON member_votes(vote_choice);
CREATE INDEX idx_member_votes_member_choice ON member_votes(member_id, vote_choice);

-- =============================================================================
-- TABLE: sessions
-- =============================================================================
-- Stores web application user sessions
-- =============================================================================
CREATE TABLE sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at          TIMESTAMP DEFAULT NOW(),
    expires_at          TIMESTAMP DEFAULT NOW() + INTERVAL '2 hours',
    ip_address          INET,
    user_agent          TEXT
);

COMMENT ON TABLE sessions IS 'Web application user sessions';
COMMENT ON COLUMN sessions.expires_at IS 'Session expires 2 hours after creation';

CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- =============================================================================
-- TABLE: session_data
-- =============================================================================
-- Stores uploaded data for each session
-- =============================================================================
CREATE TABLE session_data (
    id                  SERIAL PRIMARY KEY,
    session_id          UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    city_id             INTEGER NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    original_filename   VARCHAR(255),
    upload_timestamp    TIMESTAMP DEFAULT NOW(),
    raw_data            JSONB NOT NULL,
    processed_data      JSONB NOT NULL,
    vote_count          INTEGER DEFAULT 0,

    CONSTRAINT uq_session_data_session_city UNIQUE (session_id, city_id)
);

COMMENT ON TABLE session_data IS 'Uploaded voting data for each session';
COMMENT ON COLUMN session_data.raw_data IS 'Original uploaded JSON';
COMMENT ON COLUMN session_data.processed_data IS 'Pre-calculated summaries';

CREATE INDEX idx_session_data_session ON session_data(session_id);
CREATE INDEX idx_session_data_city ON session_data(city_id);
CREATE INDEX idx_session_data_raw ON session_data USING gin(raw_data);
CREATE INDEX idx_session_data_processed ON session_data USING gin(processed_data);

-- =============================================================================
-- MATERIALIZED VIEW: mv_meeting_summary
-- =============================================================================
-- Pre-computed meeting statistics for dashboard
-- Refresh after new data imports
-- =============================================================================
CREATE MATERIALIZED VIEW mv_meeting_summary AS
SELECT
    m.id AS meeting_id,
    m.city_id,
    c.city_key,
    c.display_name AS city_name,
    m.meeting_date,
    m.meeting_type,
    m.meeting_year,
    m.meeting_month,
    COUNT(DISTINCT ai.id) AS total_items,
    COUNT(v.id) AS total_votes,
    SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN v.outcome = 'FAIL' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN v.outcome = 'FLAG' THEN 1 ELSE 0 END) AS flagged,
    SUM(CASE WHEN v.outcome = 'CONTINUED' THEN 1 ELSE 0 END) AS continued,
    SUM(CASE WHEN v.outcome = 'REMOVED' THEN 1 ELSE 0 END) AS removed,
    ROUND(
        SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(v.id), 0) * 100, 1
    ) AS pass_rate
FROM meetings m
JOIN cities c ON m.city_id = c.id
LEFT JOIN agenda_items ai ON ai.meeting_id = m.id
LEFT JOIN votes v ON v.agenda_item_id = ai.id
GROUP BY m.id, m.city_id, c.city_key, c.display_name, m.meeting_date,
         m.meeting_type, m.meeting_year, m.meeting_month;

CREATE UNIQUE INDEX idx_mv_meeting_summary_id ON mv_meeting_summary(meeting_id);
CREATE INDEX idx_mv_meeting_summary_city ON mv_meeting_summary(city_id);
CREATE INDEX idx_mv_meeting_summary_date ON mv_meeting_summary(meeting_date DESC);
CREATE INDEX idx_mv_meeting_summary_year ON mv_meeting_summary(city_id, meeting_year);

COMMENT ON MATERIALIZED VIEW mv_meeting_summary IS 'Pre-computed meeting statistics - refresh after imports';

-- =============================================================================
-- MATERIALIZED VIEW: mv_vote_summary
-- =============================================================================
-- Pre-computed vote totals by city and year for dashboard
-- =============================================================================
CREATE MATERIALIZED VIEW mv_vote_summary AS
SELECT
    c.id AS city_id,
    c.city_key,
    c.display_name AS city_name,
    m.meeting_year AS year,
    COUNT(DISTINCT m.id) AS total_meetings,
    COUNT(v.id) AS total_votes,
    SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN v.outcome = 'FAIL' THEN 1 ELSE 0 END) AS failed,
    SUM(CASE WHEN v.outcome = 'FLAG' THEN 1 ELSE 0 END) AS flagged,
    SUM(CASE WHEN v.outcome = 'CONTINUED' THEN 1 ELSE 0 END) AS continued,
    SUM(CASE WHEN v.outcome = 'REMOVED' THEN 1 ELSE 0 END) AS removed,
    ROUND(
        SUM(CASE WHEN v.outcome = 'PASS' THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(v.id), 0) * 100, 1
    ) AS pass_rate,
    COUNT(DISTINCT ai.section) AS sections_count
FROM cities c
LEFT JOIN meetings m ON m.city_id = c.id
LEFT JOIN agenda_items ai ON ai.meeting_id = m.id
LEFT JOIN votes v ON v.agenda_item_id = ai.id
GROUP BY c.id, c.city_key, c.display_name, m.meeting_year;

CREATE INDEX idx_mv_vote_summary_city ON mv_vote_summary(city_id);
CREATE INDEX idx_mv_vote_summary_year ON mv_vote_summary(city_id, year DESC);

COMMENT ON MATERIALIZED VIEW mv_vote_summary IS 'Pre-computed yearly vote totals - refresh after imports';

-- =============================================================================
-- MATERIALIZED VIEW: mv_member_stats
-- =============================================================================
-- Pre-computed member voting statistics for dashboard
-- =============================================================================
CREATE MATERIALIZED VIEW mv_member_stats AS
SELECT
    cm.id AS member_id,
    cm.city_id,
    c.city_key,
    cm.full_name,
    cm.short_name,
    cm.title,
    cm.is_active,
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
    ) AS aye_percentage,
    ROUND(
        SUM(CASE WHEN mv.vote_choice IN ('AYE', 'NAY') THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(mv.id), 0) * 100,
        1
    ) AS participation_rate
FROM council_members cm
JOIN cities c ON cm.city_id = c.id
LEFT JOIN member_votes mv ON mv.member_id = cm.id
GROUP BY cm.id, cm.city_id, c.city_key, cm.full_name, cm.short_name, cm.title, cm.is_active;

CREATE UNIQUE INDEX idx_mv_member_stats_id ON mv_member_stats(member_id);
CREATE INDEX idx_mv_member_stats_city ON mv_member_stats(city_id);
CREATE INDEX idx_mv_member_stats_aye ON mv_member_stats(city_id, aye_percentage DESC);

COMMENT ON MATERIALIZED VIEW mv_member_stats IS 'Pre-computed member voting stats - refresh after imports';

-- =============================================================================
-- MATERIALIZED VIEW: mv_member_alignment
-- =============================================================================
-- Pre-computed alignment percentages between member pairs
-- =============================================================================
CREATE MATERIALIZED VIEW mv_member_alignment AS
SELECT
    m1.city_id,
    c.city_key,
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
JOIN cities c ON m1.city_id = c.id
WHERE mv1.vote_choice IN ('AYE', 'NAY')
  AND mv2.vote_choice IN ('AYE', 'NAY')
GROUP BY m1.city_id, c.city_key, m1.id, m1.short_name, m2.id, m2.short_name;

CREATE INDEX idx_mv_member_alignment_city ON mv_member_alignment(city_id);
CREATE INDEX idx_mv_member_alignment_m1 ON mv_member_alignment(member1_id);
CREATE INDEX idx_mv_member_alignment_m2 ON mv_member_alignment(member2_id);
CREATE INDEX idx_mv_member_alignment_pct ON mv_member_alignment(city_id, alignment_percentage DESC);

COMMENT ON MATERIALIZED VIEW mv_member_alignment IS 'Pre-computed member alignment - refresh after imports';

-- =============================================================================
-- FUNCTION: refresh_all_materialized_views
-- =============================================================================
-- Call after importing new data to update all materialized views
-- =============================================================================
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_meeting_summary;
    REFRESH MATERIALIZED VIEW mv_vote_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_member_stats;
    REFRESH MATERIALIZED VIEW mv_member_alignment;
    RAISE NOTICE 'All materialized views refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_all_materialized_views IS 'Refresh all materialized views after data import';

-- =============================================================================
-- FUNCTION: clean_expired_sessions
-- =============================================================================
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

-- =============================================================================
-- FUNCTION: get_active_members_for_date
-- =============================================================================
-- Returns council members who were actively serving on a specific date
-- Useful for determining who should have voted in a meeting
-- =============================================================================
CREATE OR REPLACE FUNCTION get_active_members_for_date(
    p_city_id INTEGER,
    p_date DATE
)
RETURNS TABLE (
    member_id INTEGER,
    full_name VARCHAR(150),
    short_name VARCHAR(50),
    position VARCHAR(50),
    district INTEGER,
    term_id INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cm.id AS member_id,
        cm.full_name,
        cm.short_name,
        cmt.position,
        cmt.district,
        cmt.id AS term_id
    FROM council_members cm
    JOIN council_member_terms cmt ON cm.id = cmt.member_id
    WHERE cm.city_id = p_city_id
      AND cmt.term_start <= p_date
      AND (cmt.term_end IS NULL OR cmt.term_end >= p_date)
    ORDER BY
        CASE cmt.position
            WHEN 'Mayor' THEN 1
            WHEN 'Vice Mayor' THEN 2
            WHEN 'Mayor Pro Tem' THEN 3
            ELSE 4
        END,
        cm.short_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_active_members_for_date IS 'Get council members serving on a specific date';

-- =============================================================================
-- FUNCTION: get_member_term_for_date
-- =============================================================================
-- Returns the specific term a member was serving during a date
-- =============================================================================
CREATE OR REPLACE FUNCTION get_member_term_for_date(
    p_member_id INTEGER,
    p_date DATE
)
RETURNS INTEGER AS $$
DECLARE
    v_term_id INTEGER;
BEGIN
    SELECT id INTO v_term_id
    FROM council_member_terms
    WHERE member_id = p_member_id
      AND term_start <= p_date
      AND (term_end IS NULL OR term_end >= p_date)
    ORDER BY term_start DESC
    LIMIT 1;

    RETURN v_term_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_member_term_for_date IS 'Get the term ID for a member on a specific date';

-- =============================================================================
-- FUNCTION: get_member_voting_history
-- =============================================================================
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

-- =============================================================================
-- FUNCTION: import_votes_from_json
-- =============================================================================
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
    FOR v_vote IN SELECT * FROM jsonb_array_elements(p_json_data->'votes')
    LOOP
        -- Parse meeting date (handles M/D/YY format)
        v_meeting_date := TO_DATE(v_vote->>'meeting_date', 'MM/DD/YY');

        -- Insert or get meeting
        INSERT INTO meetings (city_id, meeting_date, meeting_type)
        VALUES (
            p_city_id,
            v_meeting_date,
            COALESCE(LOWER(v_vote->>'meeting_type'), 'regular')
        )
        ON CONFLICT (city_id, meeting_date, meeting_type) DO UPDATE
        SET updated_at = NOW()
        RETURNING id INTO v_meeting_id;

        IF FOUND THEN
            v_meetings_created := v_meetings_created + 1;
        END IF;

        -- Insert agenda item
        INSERT INTO agenda_items (
            meeting_id, item_number, title, description, section
        )
        VALUES (
            v_meeting_id,
            v_vote->>'agenda_item_number',
            v_vote->>'agenda_item_title',
            v_vote->>'agenda_item_description',
            COALESCE(UPPER(v_vote->>'meeting_section'), 'GENERAL')
        )
        ON CONFLICT (meeting_id, item_number) DO UPDATE
        SET title = EXCLUDED.title, updated_at = NOW()
        RETURNING id INTO v_item_id;

        v_items_created := v_items_created + 1;

        -- Insert vote record
        INSERT INTO votes (
            agenda_item_id, example_id, outcome, ayes, noes, abstain, absent
        )
        VALUES (
            v_item_id,
            v_vote->>'example_id',
            COALESCE(UPPER(v_vote->>'outcome'), 'PASS'),
            COALESCE((v_vote->'tally'->>'ayes')::INTEGER, 0),
            COALESCE((v_vote->'tally'->>'noes')::INTEGER, 0),
            COALESCE((v_vote->'tally'->>'abstain')::INTEGER, 0),
            COALESCE((v_vote->'tally'->>'absent')::INTEGER, 0)
        )
        ON CONFLICT (example_id) DO UPDATE
        SET outcome = EXCLUDED.outcome, updated_at = NOW()
        RETURNING id INTO v_vote_id;

        v_votes_created := v_votes_created + 1;

        -- Insert member votes
        FOR v_member_key, v_vote_choice IN
            SELECT key, value FROM jsonb_each_text(v_vote->'member_votes')
        LOOP
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

    -- Refresh materialized views after import
    PERFORM refresh_all_materialized_views();

    RETURN QUERY SELECT v_meetings_created, v_items_created, v_votes_created;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- INSERT SANTA ANA DATA
-- =============================================================================

-- Insert Santa Ana city
INSERT INTO cities (city_key, name, display_name, total_seats, primary_color, secondary_color)
VALUES ('santa_ana', 'Santa Ana', 'Santa Ana, CA', 7, '#1f4e79', '#f4b942');

-- Insert Santa Ana Council Members (2024)
-- Note: member_key and short_name are used for matching votes from extraction
INSERT INTO council_members (city_id, member_key, full_name, short_name, title, is_active)
VALUES
    (1, 'amezcua', 'Valerie Amezcua', 'Amezcua', 'Mayor', TRUE),
    (1, 'hernandez', 'Johnathan Ryan Hernandez', 'Hernandez', 'Council Member', TRUE),
    (1, 'lopez', 'Jessie Lopez', 'Lopez', 'Council Member', TRUE),
    (1, 'penaloza', 'David Penaloza', 'Penaloza', 'Council Member', TRUE),
    (1, 'vazquez', 'Benjamin Vazquez', 'Vazquez', 'Council Member', TRUE),
    (1, 'phan', 'Thai Viet Phan', 'Phan', 'Council Member', TRUE),
    (1, 'bacerra', 'Phil Bacerra', 'Bacerra', 'Council Member', TRUE);

-- Insert term records for Santa Ana Council (2024 term)
-- These track when each member started serving in their current role
INSERT INTO council_member_terms (member_id, position, district, term_start, term_end, appointment_type)
VALUES
    -- Mayor Amezcua - Ward 3, elected Mayor Dec 2022
    (1, 'Mayor', 3, '2022-12-13', NULL, 'elected'),
    -- Hernandez - Ward 1
    (2, 'Council Member', 1, '2020-12-08', NULL, 'elected'),
    -- Lopez - Ward 2
    (3, 'Council Member', 2, '2020-12-08', NULL, 'elected'),
    -- Penaloza - Ward 5
    (4, 'Council Member', 5, '2020-12-08', NULL, 'elected'),
    -- Vazquez - Ward 4
    (5, 'Council Member', 4, '2022-12-13', NULL, 'elected'),
    -- Phan - Ward 1 (appointed, then elected)
    (6, 'Council Member', 1, '2020-12-08', NULL, 'elected'),
    -- Bacerra - Ward 4
    (7, 'Council Member', 4, '2018-12-11', NULL, 'elected');

-- =============================================================================
-- SAMPLE QUERIES
-- =============================================================================

-- Fast dashboard query using materialized view:
-- SELECT * FROM mv_member_stats WHERE city_key = 'santa_ana' ORDER BY aye_percentage DESC;

-- Fast alignment query:
-- SELECT * FROM mv_member_alignment WHERE city_key = 'santa_ana' ORDER BY alignment_percentage DESC LIMIT 10;

-- Fast meeting summary:
-- SELECT * FROM mv_meeting_summary WHERE city_key = 'santa_ana' AND meeting_year = 2024;

-- Import data from JSON:
-- SELECT * FROM import_votes_from_json(1, '{"votes": [...]}');

-- Refresh views after import:
-- SELECT refresh_all_materialized_views();

-- =============================================================================
-- COUNCIL MEMBER TERM QUERIES
-- =============================================================================

-- Get all members who were serving on a specific date:
-- SELECT * FROM get_active_members_for_date(1, '2024-06-15');

-- Get a member's term during a specific meeting:
-- SELECT get_member_term_for_date(1, '2024-06-15');

-- View all terms for a member (history of positions):
-- SELECT cm.full_name, cmt.position, cmt.district, cmt.term_start, cmt.term_end
-- FROM council_members cm
-- JOIN council_member_terms cmt ON cm.id = cmt.member_id
-- WHERE cm.id = 1
-- ORDER BY cmt.term_start DESC;

-- Example: When a council member becomes mayor, add new term:
-- INSERT INTO council_member_terms (member_id, position, district, term_start, term_end, appointment_type)
-- VALUES (2, 'Mayor', 1, '2026-12-10', NULL, 'elected');
-- UPDATE council_member_terms SET term_end = '2026-12-09' WHERE member_id = 2 AND position = 'Council Member' AND term_end IS NULL;

-- Example: When a council member is replaced mid-term:
-- 1. End the outgoing member's term:
-- UPDATE council_member_terms SET term_end = '2025-06-30' WHERE member_id = 3 AND term_end IS NULL;
-- UPDATE council_members SET is_active = FALSE WHERE id = 3;
-- 2. Add new member and their term:
-- INSERT INTO council_members (city_id, member_key, full_name, short_name, title, is_active)
-- VALUES (1, 'new_member', 'New Member Name', 'NewMember', 'Council Member', TRUE);
-- INSERT INTO council_member_terms (member_id, position, district, term_start, appointment_type)
-- VALUES (8, 'Council Member', 2, '2025-07-01', 'appointed');

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
