-- =============================================================================
-- STEP 6: Create Database Functions
-- =============================================================================

-- Function to refresh all materialized views
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

-- Function to clean expired sessions
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

-- Function to get active members for a specific date
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

-- Function to get member term for a specific date
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

-- Function to get member voting history
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

-- Verify functions created
SELECT 'Step 6 Complete: Functions created' as status;
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';
