-- =============================================================================
-- STEP 10a: Create Staging Tables for CSV Import
-- =============================================================================
-- Run this BEFORE importing CSVs in TablePlus
-- These staging tables match the CSV column structure exactly
-- =============================================================================

-- Drop existing staging tables if they exist
DROP TABLE IF EXISTS staging_votes CASCADE;
DROP TABLE IF EXISTS staging_meetings CASCADE;

-- =============================================================================
-- Staging table for vote extraction CSV
-- Source: extractors/santa_ana/2024/santa_ana_extraction_complete2024.csv
-- =============================================================================
CREATE TABLE staging_votes (
    example_id TEXT,
    meeting_date TEXT,
    minutes_location TEXT,
    agenda_location TEXT,
    meeting_type TEXT,
    agenda_item_number TEXT,
    agenda_item_title TEXT,
    agenda_item_description TEXT,
    meeting_section TEXT,
    outcome TEXT,
    tally TEXT,
    hernandez TEXT,
    lopez TEXT,
    penaloza TEXT,
    vazquez TEXT,
    phan TEXT,
    bacerra TEXT,
    amezcua TEXT,
    motion_by TEXT,
    second_by TEXT,
    notes TEXT
);

COMMENT ON TABLE staging_votes IS 'Staging table for vote extraction CSV import';

-- =============================================================================
-- Staging table for meetings CSV (with URLs)
-- Source: extractors/santa_ana/2024/meetings_2024.csv
-- =============================================================================
CREATE TABLE staging_meetings (
    city_id INTEGER,
    meeting_date TEXT,
    meeting_type TEXT,
    agenda_url TEXT,
    minutes_url TEXT,
    video_url TEXT
);

COMMENT ON TABLE staging_meetings IS 'Staging table for meetings CSV import';

-- Verify tables created
SELECT 'Staging tables created' as status;
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE 'staging_%'
ORDER BY table_name;

-- =============================================================================
-- NEXT STEPS:
-- 1. In TablePlus: Right-click staging_votes → Import → From CSV
--    Select: extractors/santa_ana/2024/santa_ana_extraction_complete2024.csv
--    Check: "First row is header"
--
-- 2. In TablePlus: Right-click staging_meetings → Import → From CSV
--    Select: extractors/santa_ana/2024/meetings_2024.csv
--    Check: "First row is header"
--
-- 3. Run step10b_import_from_staging.sql to transform and load data
-- =============================================================================
