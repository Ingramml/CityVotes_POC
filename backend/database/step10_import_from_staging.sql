-- =============================================================================
-- STEP 10b: Transform and Load from Staging Tables
-- =============================================================================
-- Run this AFTER importing CSVs into staging tables
-- This script transforms staging data and inserts into final tables
-- =============================================================================

BEGIN;

-- =============================================================================
-- Helper function to parse date from various formats
-- =============================================================================
CREATE OR REPLACE FUNCTION parse_meeting_date(date_str TEXT)
RETURNS DATE AS $$
BEGIN
    -- Try M/D/YY format (1/16/24)
    BEGIN
        RETURN TO_DATE(date_str, 'MM/DD/YY');
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    -- Try M/D/YYYY format (1/16/2024)
    BEGIN
        RETURN TO_DATE(date_str, 'MM/DD/YYYY');
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    -- Try YYYY-MM-DD format (2024-01-16)
    BEGIN
        RETURN TO_DATE(date_str, 'YYYY-MM-DD');
    EXCEPTION WHEN OTHERS THEN NULL;
    END;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Helper function to normalize meeting type
-- =============================================================================
CREATE OR REPLACE FUNCTION normalize_meeting_type(mt TEXT)
RETURNS VARCHAR(50) AS $$
BEGIN
    IF mt IS NULL OR mt = '' THEN
        RETURN 'regular';
    END IF;

    mt := LOWER(TRIM(mt));

    IF mt IN ('regular', 'reguar') THEN
        RETURN 'regular';
    ELSIF mt = 'special' THEN
        RETURN 'special';
    ELSIF mt LIKE '%housing%' THEN
        RETURN 'special';
    ELSIF mt = 'emergency' THEN
        RETURN 'emergency';
    END IF;

    RETURN 'regular';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Helper function to normalize section
-- =============================================================================
CREATE OR REPLACE FUNCTION normalize_section(s TEXT)
RETURNS VARCHAR(50) AS $$
BEGIN
    IF s IS NULL OR s = '' THEN
        RETURN 'GENERAL';
    END IF;

    s := UPPER(TRIM(s));

    IF s LIKE '%CONSENT%' THEN
        RETURN 'CONSENT';
    ELSIF s LIKE '%PUBLIC%' AND s LIKE '%HEARING%' THEN
        RETURN 'PUBLIC_HEARING';
    ELSIF s LIKE '%BUSINESS%' THEN
        RETURN 'BUSINESS';
    ELSIF s LIKE '%CLOSED%' THEN
        RETURN 'CLOSED';
    END IF;

    RETURN 'GENERAL';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Helper function to normalize outcome
-- =============================================================================
CREATE OR REPLACE FUNCTION normalize_outcome(o TEXT)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF o IS NULL OR o = '' THEN
        RETURN 'PASS';
    END IF;

    o := UPPER(TRIM(o));

    IF o IN ('PASS', 'PASSED') THEN
        RETURN 'PASS';
    ELSIF o IN ('FAIL', 'FAILED') THEN
        RETURN 'FAIL';
    ELSIF o IN ('FLAG', 'FLAGGED') THEN
        RETURN 'FLAG';
    ELSIF o IN ('CONTINUED', 'CONTINUE') THEN
        RETURN 'CONTINUED';
    ELSIF o IN ('REMOVED', 'REMOVE') THEN
        RETURN 'REMOVED';
    ELSIF o = 'TIE' THEN
        RETURN 'TIE';
    END IF;

    RETURN 'PASS';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Helper function to normalize vote choice
-- =============================================================================
CREATE OR REPLACE FUNCTION normalize_vote_choice(v TEXT)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF v IS NULL OR v = '' THEN
        RETURN 'ABSENT';
    END IF;

    v := LOWER(TRIM(v));

    IF v IN ('aye', 'yes') THEN
        RETURN 'AYE';
    ELSIF v IN ('nay', 'no') THEN
        RETURN 'NAY';
    ELSIF v = 'abstain' THEN
        RETURN 'ABSTAIN';
    ELSIF v = 'absent' THEN
        RETURN 'ABSENT';
    ELSIF v IN ('recused', 'recusal') THEN
        RETURN 'RECUSAL';
    END IF;

    RETURN 'ABSENT';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- Helper function to parse tally JSON
-- =============================================================================
CREATE OR REPLACE FUNCTION parse_tally(tally_str TEXT)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    IF tally_str IS NULL OR tally_str = '' THEN
        RETURN '{"ayes": 0, "noes": 0, "abstain": 0, "absent": 0, "recused": 0}'::JSONB;
    END IF;

    -- Convert Python dict format to JSON
    -- {'ayes': 7, 'noes': 0} → {"ayes": 7, "noes": 0}
    tally_str := REPLACE(tally_str, '''', '"');

    BEGIN
        result := tally_str::JSONB;
        RETURN result;
    EXCEPTION WHEN OTHERS THEN
        RETURN '{"ayes": 0, "noes": 0, "abstain": 0, "absent": 0, "recused": 0}'::JSONB;
    END;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- STEP 1: Import Meetings from staging_votes (creates meeting records)
-- =============================================================================
SELECT 'Step 1: Importing meetings...' as status;

INSERT INTO meetings (city_id, meeting_date, meeting_type)
SELECT DISTINCT
    1 as city_id,
    parse_meeting_date(meeting_date) as meeting_date,
    normalize_meeting_type(meeting_type) as meeting_type
FROM staging_votes
WHERE parse_meeting_date(meeting_date) IS NOT NULL
ON CONFLICT (city_id, meeting_date, meeting_type)
DO UPDATE SET updated_at = NOW();

SELECT 'Meetings imported: ' || COUNT(*) as status FROM meetings WHERE city_id = 1;

-- =============================================================================
-- STEP 2: Update Meetings with URLs from staging_meetings
-- =============================================================================
SELECT 'Step 2: Updating meeting URLs...' as status;

UPDATE meetings m
SET
    agenda_url = NULLIF(sm.agenda_url, ''),
    minutes_url = NULLIF(sm.minutes_url, ''),
    video_url = NULLIF(sm.video_url, ''),
    updated_at = NOW()
FROM staging_meetings sm
WHERE m.city_id = sm.city_id
  AND m.meeting_date = TO_DATE(sm.meeting_date, 'YYYY-MM-DD')
  AND m.meeting_type = normalize_meeting_type(sm.meeting_type);

SELECT 'Meetings with URLs: ' || COUNT(*) as status
FROM meetings
WHERE city_id = 1 AND (agenda_url IS NOT NULL OR video_url IS NOT NULL);

-- =============================================================================
-- STEP 3: Import Agenda Items
-- =============================================================================
SELECT 'Step 3: Importing agenda items...' as status;

INSERT INTO agenda_items (meeting_id, item_number, title, description, section)
SELECT DISTINCT
    m.id as meeting_id,
    sv.agenda_item_number as item_number,
    LEFT(sv.agenda_item_title, 500) as title,
    LEFT(sv.agenda_item_description, 2000) as description,
    normalize_section(sv.meeting_section) as section
FROM staging_votes sv
JOIN meetings m ON m.city_id = 1
    AND m.meeting_date = parse_meeting_date(sv.meeting_date)
    AND m.meeting_type = normalize_meeting_type(sv.meeting_type)
WHERE sv.agenda_item_number IS NOT NULL AND sv.agenda_item_number != ''
ON CONFLICT (meeting_id, item_number)
DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    section = EXCLUDED.section,
    updated_at = NOW();

SELECT 'Agenda items imported: ' || COUNT(*) as status FROM agenda_items;

-- =============================================================================
-- STEP 4: Import Votes
-- =============================================================================
SELECT 'Step 4: Importing votes...' as status;

INSERT INTO votes (agenda_item_id, example_id, outcome, ayes, noes, abstain, absent, recusal)
SELECT
    ai.id as agenda_item_id,
    sv.example_id,
    normalize_outcome(sv.outcome) as outcome,
    COALESCE((parse_tally(sv.tally)->>'ayes')::INTEGER, 0) as ayes,
    COALESCE((parse_tally(sv.tally)->>'noes')::INTEGER, 0) as noes,
    COALESCE((parse_tally(sv.tally)->>'abstain')::INTEGER, 0) as abstain,
    COALESCE((parse_tally(sv.tally)->>'absent')::INTEGER, 0) as absent,
    COALESCE((parse_tally(sv.tally)->>'recused')::INTEGER, 0) as recusal
FROM staging_votes sv
JOIN meetings m ON m.city_id = 1
    AND m.meeting_date = parse_meeting_date(sv.meeting_date)
    AND m.meeting_type = normalize_meeting_type(sv.meeting_type)
JOIN agenda_items ai ON ai.meeting_id = m.id
    AND ai.item_number = sv.agenda_item_number
WHERE sv.example_id IS NOT NULL AND sv.example_id != ''
ON CONFLICT (example_id)
DO UPDATE SET
    outcome = EXCLUDED.outcome,
    ayes = EXCLUDED.ayes,
    noes = EXCLUDED.noes,
    abstain = EXCLUDED.abstain,
    absent = EXCLUDED.absent,
    recusal = EXCLUDED.recusal,
    updated_at = NOW();

SELECT 'Votes imported: ' || COUNT(*) as status FROM votes;

-- =============================================================================
-- STEP 5: Import Member Votes
-- =============================================================================
SELECT 'Step 5: Importing member votes...' as status;

-- Create temp table with unpivoted member votes
CREATE TEMP TABLE temp_member_votes AS
SELECT
    sv.example_id,
    cm.id as member_id,
    normalize_vote_choice(
        CASE cm.short_name
            WHEN 'Hernandez' THEN sv.hernandez
            WHEN 'Lopez' THEN sv.lopez
            WHEN 'Penaloza' THEN sv.penaloza
            WHEN 'Vazquez' THEN sv.vazquez
            WHEN 'Phan' THEN sv.phan
            WHEN 'Bacerra' THEN sv.bacerra
            WHEN 'Amezcua' THEN sv.amezcua
        END
    ) as vote_choice
FROM staging_votes sv
CROSS JOIN council_members cm
WHERE cm.city_id = 1
  AND sv.example_id IS NOT NULL AND sv.example_id != '';

-- Insert member votes
INSERT INTO member_votes (vote_id, member_id, vote_choice)
SELECT
    v.id as vote_id,
    tmv.member_id,
    tmv.vote_choice
FROM temp_member_votes tmv
JOIN votes v ON v.example_id = tmv.example_id
ON CONFLICT (vote_id, member_id)
DO UPDATE SET vote_choice = EXCLUDED.vote_choice;

DROP TABLE temp_member_votes;

SELECT 'Member votes imported: ' || COUNT(*) as status FROM member_votes;

-- =============================================================================
-- STEP 6: Refresh Materialized Views
-- =============================================================================
SELECT 'Step 6: Refreshing materialized views...' as status;

SELECT refresh_all_materialized_views();

-- =============================================================================
-- STEP 7: Verify Import
-- =============================================================================
SELECT 'Import complete! Verifying counts...' as status;

SELECT 'cities' as table_name, COUNT(*) as count FROM cities
UNION ALL SELECT 'council_members', COUNT(*) FROM council_members
UNION ALL SELECT 'meetings', COUNT(*) FROM meetings
UNION ALL SELECT 'agenda_items', COUNT(*) FROM agenda_items
UNION ALL SELECT 'votes', COUNT(*) FROM votes
UNION ALL SELECT 'member_votes', COUNT(*) FROM member_votes;

-- Show meetings with URLs
SELECT 'Meetings with URLs:' as status;
SELECT meeting_date, meeting_type,
    CASE WHEN agenda_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_agenda,
    CASE WHEN minutes_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_minutes,
    CASE WHEN video_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_video
FROM meetings
WHERE city_id = 1
ORDER BY meeting_date DESC
LIMIT 10;

COMMIT;

SELECT 'Step 10b Complete: Data imported from staging tables' as status;
