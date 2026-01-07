-- =============================================================================
-- STEP 10c: Cleanup Staging Tables (Optional)
-- =============================================================================
-- Run this AFTER verifying the import was successful
-- This removes the staging tables to clean up the database
-- =============================================================================

-- Drop staging tables
DROP TABLE IF EXISTS staging_votes CASCADE;
DROP TABLE IF EXISTS staging_meetings CASCADE;

-- Drop helper functions (optional - keep if you want to re-import later)
-- DROP FUNCTION IF EXISTS parse_meeting_date(TEXT);
-- DROP FUNCTION IF EXISTS normalize_meeting_type(TEXT);
-- DROP FUNCTION IF EXISTS normalize_section(TEXT);
-- DROP FUNCTION IF EXISTS normalize_outcome(TEXT);
-- DROP FUNCTION IF EXISTS normalize_vote_choice(TEXT);
-- DROP FUNCTION IF EXISTS parse_tally(TEXT);

SELECT 'Staging tables dropped' as status;

-- Verify tables are gone
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE 'staging_%'
ORDER BY table_name;
