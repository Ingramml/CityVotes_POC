-- =============================================================================
-- STEP 7: Insert Seed Data (Santa Ana city and council members)
-- =============================================================================

-- Insert Santa Ana city
INSERT INTO cities (city_key, name, display_name, total_seats, primary_color, secondary_color)
VALUES ('santa_ana', 'Santa Ana', 'Santa Ana, CA', 7, '#1f4e79', '#f4b942');

-- Verify city inserted
SELECT 'City inserted:' as status, id, city_key, display_name FROM cities;

-- Insert Santa Ana Council Members (2024)
INSERT INTO council_members (city_id, member_key, full_name, short_name, title, is_active)
VALUES
    (1, 'amezcua', 'Valerie Amezcua', 'Amezcua', 'Mayor', TRUE),
    (1, 'hernandez', 'Johnathan Ryan Hernandez', 'Hernandez', 'Council Member', TRUE),
    (1, 'lopez', 'Jessie Lopez', 'Lopez', 'Council Member', TRUE),
    (1, 'penaloza', 'David Penaloza', 'Penaloza', 'Council Member', TRUE),
    (1, 'vazquez', 'Benjamin Vazquez', 'Vazquez', 'Council Member', TRUE),
    (1, 'phan', 'Thai Viet Phan', 'Phan', 'Council Member', TRUE),
    (1, 'bacerra', 'Phil Bacerra', 'Bacerra', 'Council Member', TRUE);

-- Verify members inserted
SELECT 'Council members inserted:' as status;
SELECT id, short_name, title FROM council_members ORDER BY id;

-- Insert term records for Santa Ana Council
INSERT INTO council_member_terms (member_id, position, district, term_start, term_end, appointment_type)
VALUES
    (1, 'Mayor', 3, '2022-12-13', NULL, 'elected'),
    (2, 'Council Member', 1, '2020-12-08', NULL, 'elected'),
    (3, 'Council Member', 2, '2020-12-08', NULL, 'elected'),
    (4, 'Council Member', 5, '2020-12-08', NULL, 'elected'),
    (5, 'Council Member', 4, '2022-12-13', NULL, 'elected'),
    (6, 'Council Member', 1, '2020-12-08', NULL, 'elected'),
    (7, 'Council Member', 4, '2018-12-11', NULL, 'elected');

-- Verify terms inserted
SELECT 'Council terms inserted:' as status;
SELECT cm.short_name, cmt.position, cmt.district, cmt.term_start
FROM council_member_terms cmt
JOIN council_members cm ON cmt.member_id = cm.id
ORDER BY cmt.id;

SELECT 'Step 7 Complete: Seed data inserted' as status;
