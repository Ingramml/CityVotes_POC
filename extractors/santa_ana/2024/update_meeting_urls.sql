-- =============================================================================
-- Update meetings table with PrimeGov URLs
-- Generated from meetings_2024.csv
-- Run this AFTER importing votes (step 8)
-- =============================================================================

BEGIN;

-- 2024-01-02 (no URLs available)
UPDATE meetings SET agenda_url = NULL, minutes_url = NULL, video_url = NULL, updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-01-02';

-- 2024-01-16
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/37917',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40113',
    video_url = 'https://youtube.com/watch?v=JTdxyA1mMog',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-01-16';

-- 2024-02-20
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/38520',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40114',
    video_url = 'https://youtube.com/watch?v=nbGR-j-q-hk',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-02-20';

-- 2024-03-05
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/38919',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40341',
    video_url = 'https://youtube.com/watch?v=N4r4ZhOa280',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-03-05';

-- 2024-03-19
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/39256',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/39793',
    video_url = 'https://youtube.com/watch?v=7Re91G1PXaY',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-03-19';

-- 2024-04-16
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/39833',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40945',
    video_url = 'https://youtube.com/watch?v=kCYrJx-9-AY',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-04-16';

-- 2024-04-20
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40020',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40946',
    video_url = 'https://youtube.com/watch?v=wo7LEwgNctY',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-04-20';

-- 2024-05-16
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40798',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/42439',
    video_url = 'https://youtube.com/watch?v=vBDs08fiBgw',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-05-16';

-- 2024-05-21
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/40875',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/42438',
    video_url = 'https://youtube.com/watch?v=iyE_fXgFZ0Y',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-05-21';

-- 2024-06-18
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/41218',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/42435',
    video_url = 'https://youtube.com/watch?v=OBdZrrAO1RQ',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-06-18';

-- 2024-06-27
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/41371',
    minutes_url = NULL,
    video_url = 'https://youtube.com/watch?v=Hk4UQj32DNU',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-06-27';

-- 2024-07-02 (no URLs available)
UPDATE meetings SET agenda_url = NULL, minutes_url = NULL, video_url = NULL, updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-07-02';

-- 2024-07-16
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/41656',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/42434',
    video_url = 'https://youtube.com/watch?v=IfxylKPuP8M',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-07-16';

-- 2024-08-20
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/42278',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/43101',
    video_url = 'https://youtube.com/watch?v=miKLUW6O8Cc',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-08-20';

-- 2024-10-01
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/43136',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/44050',
    video_url = 'https://youtube.com/watch?v=gvXruPlME9M',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-10-01';

-- 2024-10-15
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/43287',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/44049',
    video_url = 'https://youtube.com/watch?v=gRL1Vim4aRA',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-10-15';

-- 2024-10-28
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/43501',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/44048',
    video_url = 'https://youtube.com/watch?v=9Nu4E3JGu28',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-10-28';

-- 2024-11-19
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/43806',
    minutes_url = NULL,
    video_url = 'https://youtube.com/watch?v=XWx87-dPbXU',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-11-19';

-- 2024-12-03
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/44041',
    minutes_url = NULL,
    video_url = 'https://youtube.com/watch?v=-_SU_IlCZsI',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-12-03';

-- 2024-12-10
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/44150',
    minutes_url = NULL,
    video_url = 'https://youtube.com/watch?v=NtAyrvp58I8',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-12-10';

-- 2024-12-17
UPDATE meetings SET
    agenda_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/44240',
    minutes_url = 'https://santa-ana.primegov.com/Public/CompiledDocument/48209',
    video_url = 'https://youtube.com/watch?v=0plzhwLg00U',
    updated_at = NOW()
WHERE city_id = 1 AND meeting_date = '2024-12-17';

-- Verify updates
SELECT meeting_date, meeting_type,
       CASE WHEN agenda_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_agenda,
       CASE WHEN minutes_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_minutes,
       CASE WHEN video_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_video
FROM meetings
WHERE city_id = 1 AND EXTRACT(YEAR FROM meeting_date) = 2024
ORDER BY meeting_date;

COMMIT;

SELECT 'Meeting URLs updated successfully' as status;
