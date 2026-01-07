-- =============================================================================
-- STEP 5: Create Materialized Views (for fast dashboard queries)
-- =============================================================================

-- Meeting summary view
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

COMMENT ON MATERIALIZED VIEW mv_meeting_summary IS 'Pre-computed meeting statistics';

-- Vote summary view
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

COMMENT ON MATERIALIZED VIEW mv_vote_summary IS 'Pre-computed yearly vote totals';

-- Member stats view
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

COMMENT ON MATERIALIZED VIEW mv_member_stats IS 'Pre-computed member voting stats';

-- Member alignment view
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

COMMENT ON MATERIALIZED VIEW mv_member_alignment IS 'Pre-computed member alignment';

-- Verify views created
SELECT 'Step 5 Complete: Materialized views created' as status;
SELECT matviewname FROM pg_matviews WHERE schemaname = 'public';
