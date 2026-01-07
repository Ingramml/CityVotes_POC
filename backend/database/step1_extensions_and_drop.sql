-- =============================================================================
-- STEP 1: Enable Extensions and Drop Existing Objects
-- =============================================================================
-- Run this first to clean slate the database
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop materialized views
DROP MATERIALIZED VIEW IF EXISTS mv_member_alignment CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_member_stats CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_vote_summary CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_meeting_summary CASCADE;

-- Drop regular views
DROP VIEW IF EXISTS v_section_stats CASCADE;
DROP VIEW IF EXISTS v_yearly_stats CASCADE;
DROP VIEW IF EXISTS v_member_alignment CASCADE;
DROP VIEW IF EXISTS v_member_stats CASCADE;
DROP VIEW IF EXISTS v_meeting_summary CASCADE;

-- Drop tables (order matters due to foreign keys)
DROP TABLE IF EXISTS member_votes CASCADE;
DROP TABLE IF EXISTS votes CASCADE;
DROP TABLE IF EXISTS agenda_items CASCADE;
DROP TABLE IF EXISTS meetings CASCADE;
DROP TABLE IF EXISTS council_member_terms CASCADE;
DROP TABLE IF EXISTS council_members CASCADE;
DROP TABLE IF EXISTS session_data CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS cities CASCADE;

-- Verify clean state
SELECT 'Step 1 Complete: Database cleaned' as status;
