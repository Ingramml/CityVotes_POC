-- =============================================================================
-- STEP 9: Verify Import and Refresh Views
-- =============================================================================

-- Refresh all materialized views
SELECT refresh_all_materialized_views();

-- Verify record counts
SELECT 'Record counts:' as status;
SELECT 'cities' as table_name, COUNT(*) as count FROM cities
UNION ALL SELECT 'council_members', COUNT(*) FROM council_members
UNION ALL SELECT 'council_member_terms', COUNT(*) FROM council_member_terms
UNION ALL SELECT 'meetings', COUNT(*) FROM meetings
UNION ALL SELECT 'agenda_items', COUNT(*) FROM agenda_items
UNION ALL SELECT 'votes', COUNT(*) FROM votes
UNION ALL SELECT 'member_votes', COUNT(*) FROM member_votes;

-- Check meetings by date
SELECT 'Meetings by date:' as status;
SELECT meeting_date, meeting_type,
       (SELECT COUNT(*) FROM agenda_items ai
        JOIN votes v ON v.agenda_item_id = ai.id
        WHERE ai.meeting_id = m.id) as vote_count
FROM meetings m
ORDER BY meeting_date;

-- Check member stats from materialized view
SELECT 'Member statistics:' as status;
SELECT short_name, total_votes, aye_count, nay_count, aye_percentage
FROM mv_member_stats
WHERE city_key = 'santa_ana'
ORDER BY total_votes DESC;

-- Check vote outcomes
SELECT 'Vote outcomes:' as status;
SELECT outcome, COUNT(*) as count
FROM votes
GROUP BY outcome
ORDER BY count DESC;

SELECT 'Step 9 Complete: Database verified and views refreshed' as status;
