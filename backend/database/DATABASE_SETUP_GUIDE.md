# Database Setup Guide

Complete step-by-step instructions for setting up the CityVotes PostgreSQL database using the staging tables method.

---

## Prerequisites

- PostgreSQL database running
- TablePlus (or any SQL client) connected to the database
- Python 3 installed (for generating meeting URLs CSV)

---

## Step 1: Extensions and Drop

**File:** `step1_extensions_and_drop.sql`

**Purpose:** Enables the UUID extension and drops any existing tables to start fresh.

**How to run:**
1. Open TablePlus
2. Connect to your PostgreSQL database
3. Press Cmd+N to open a new SQL Query
4. Open or copy contents of `step1_extensions_and_drop.sql`
5. Press Cmd+Enter to run

**Expected output:**
```
UUID extension enabled
All existing tables dropped
Step 1 Complete
```

---

## Step 2: Core Tables

**File:** `step2_core_tables.sql`

**Purpose:** Creates the core reference tables:
- `cities` - City configuration (name, colors, seats)
- `council_members` - Council member info (name, title, active status)
- `council_member_terms` - Term history (position, district, dates)

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step2_core_tables.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Step 2 Complete: Core tables created
cities
council_member_terms
council_members
```

---

## Step 3: Meeting Tables

**File:** `step3_meeting_tables.sql`

**Purpose:** Creates the meeting and vote tables:
- `meetings` - Meeting records (date, type, URLs)
- `agenda_items` - Agenda items (number, title, section)
- `votes` - Vote records (outcome, tally counts)
- `member_votes` - Individual member vote choices

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step3_meeting_tables.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Step 3 Complete: Meeting tables created
agenda_items
meetings
member_votes
votes
```

---

## Step 4: Session Tables

**File:** `step4_session_tables.sql`

**Purpose:** Creates tables for web app session management:
- `sessions` - User sessions with expiration
- `session_data` - Uploaded data stored per session

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step4_session_tables.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Step 4 Complete: Session tables created
session_data
sessions
```

---

## Step 5: Materialized Views

**File:** `step5_materialized_views.sql`

**Purpose:** Creates materialized views for fast dashboard queries:
- `mv_meeting_summary` - Meeting stats (vote counts, pass rates)
- `mv_vote_summary` - Vote aggregations by outcome
- `mv_member_stats` - Member voting statistics
- `mv_member_alignment` - Voting alignment between members

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step5_materialized_views.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Step 5 Complete: Materialized views created
mv_meeting_summary
mv_member_alignment
mv_member_stats
mv_vote_summary
```

---

## Step 6: Functions

**File:** `step6_functions.sql`

**Purpose:** Creates helper functions:
- `refresh_all_materialized_views()` - Refreshes all views at once
- `get_active_members_for_date()` - Gets active members on a specific date
- `get_member_term_for_date()` - Gets member's term on a specific date

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step6_functions.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Step 6 Complete: Functions created
get_active_members_for_date
get_member_term_for_date
refresh_all_materialized_views
```

---

## Step 7: Seed Data

**File:** `step7_seed_data.sql`

**Purpose:** Inserts initial data for Santa Ana:
- 1 city record (Santa Ana, CA)
- 7 council members (Amezcua, Hernandez, Lopez, Penaloza, Vazquez, Phan, Bacerra)
- 7 term records

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step7_seed_data.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
City inserted: 1, santa_ana, Santa Ana, CA
Council members inserted:
  1, Amezcua, Mayor
  2, Hernandez, Council Member
  3, Lopez, Council Member
  4, Penaloza, Council Member
  5, Vazquez, Council Member
  6, Phan, Council Member
  7, Bacerra, Council Member
Council terms inserted: 7 rows
Step 7 Complete: Seed data inserted
```

---

## Step 8: Create Staging Tables

**File:** `step8_create_staging.sql`

**Purpose:** Creates temporary staging tables for CSV import:
- `staging_votes` - 21 TEXT columns matching vote CSV
- `staging_meetings` - 6 columns matching meetings CSV

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step8_create_staging.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Staging tables created
staging_meetings
staging_votes
```

**Verify:** In the TablePlus sidebar, you should now see `staging_votes` and `staging_meetings` tables.

---

## Step 9: Import CSVs in TablePlus

This step has three parts: generating the meetings CSV, then importing both CSVs.

### Step 9a: Generate Meeting URLs CSV

**Purpose:** Fetches meeting data from PrimeGov API and generates CSV with agenda, minutes, and video URLs.

**How to run (in Terminal):**
```bash
cd /Users/michaelingram/Documents/GitHub/CityVotes_POC
python3 tools/generate_meetings_csv.py --year 2024
```

**Expected output:**
```
Fetching meetings from API for year 2024...
  Found 23 City Council meetings from API

Generated CSV with 21 meetings: extractors/santa_ana/2024/meetings_2024.csv

URL Summary:
  Meetings: 21
  With agenda URL: 19
  With minutes URL: 15
  With video URL: 19
```

**File created:** `extractors/santa_ana/2024/meetings_2024.csv`

---

### Step 9b: Import Vote Data CSV

**Source file:** `extractors/santa_ana/2024/santa_ana_extraction_complete2024.csv`

**Contents:** 437 vote records with columns:
- example_id, meeting_date, meeting_type
- agenda_item_number, agenda_item_title, agenda_item_description
- meeting_section, outcome, tally
- Hernandez, Lopez, Penaloza, Vazquez, Phan, Bacerra, Amezcua (vote choices)
- motion_by, second_by, notes

**How to import:**
1. In the TablePlus left sidebar, find the `staging_votes` table
2. Right-click on `staging_votes`
3. Select **Import** → **From CSV...**
4. Navigate to: `extractors/santa_ana/2024/`
5. Select: `santa_ana_extraction_complete2024.csv`
6. In the import dialog:
   - Check ✅ **"First row is header"**
   - Delimiter: Comma
   - Encoding: UTF-8
7. Click **Import**

**Expected result:** 437 rows imported

**Verify:** Double-click `staging_votes` table to view data. You should see rows with meeting dates, agenda items, and vote choices (Aye, Nay, Absent, etc.).

---

### Step 9c: Import Meeting URLs CSV

**Source file:** `extractors/santa_ana/2024/meetings_2024.csv`

**Contents:** 21 meeting records with columns:
- city_id, meeting_date, meeting_type
- agenda_url, minutes_url, video_url

**How to import:**
1. In the TablePlus left sidebar, find the `staging_meetings` table
2. Right-click on `staging_meetings`
3. Select **Import** → **From CSV...**
4. Navigate to: `extractors/santa_ana/2024/`
5. Select: `meetings_2024.csv`
6. In the import dialog:
   - Check ✅ **"First row is header"**
   - Delimiter: Comma
   - Encoding: UTF-8
7. Click **Import**

**Expected result:** 21 rows imported

**Verify:** Double-click `staging_meetings` table. You should see URLs like:
- `https://santa-ana.primegov.com/Public/CompiledDocument/37917`
- `https://youtube.com/watch?v=JTdxyA1mMog`

---

## Step 10: Transform and Load Data

**File:** `step10_import_from_staging.sql`

**Purpose:** Transforms staging data and loads into final tables:
1. Creates helper functions for parsing dates, normalizing types, parsing tallies
2. Imports meetings from `staging_votes` (creates meeting records)
3. Updates meetings with URLs from `staging_meetings`
4. Imports agenda items (437 records)
5. Imports votes with tallies (437 records)
6. Imports member votes by unpivoting 7 member columns (3,059 records)
7. Refreshes all materialized views

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step10_import_from_staging.sql`
3. Press Cmd+Enter to run

**Note:** This script takes 5-10 seconds to run.

**Expected output:**
```
Step 1: Importing meetings...
Meetings imported: 22

Step 2: Updating meeting URLs...
Meetings with URLs: 19

Step 3: Importing agenda items...
Agenda items imported: 437

Step 4: Importing votes...
Votes imported: 437

Step 5: Importing member votes...
Member votes imported: 3059

Step 6: Refreshing materialized views...

Import complete! Verifying counts...

table_name       | count
-----------------|------
cities           | 1
council_members  | 7
meetings         | 22
agenda_items     | 437
votes            | 437
member_votes     | 3059

Meetings with URLs:
meeting_date | meeting_type | has_agenda | has_minutes | has_video
-------------|--------------|------------|-------------|----------
2024-12-17   | special      | Yes        | Yes         | Yes
2024-12-10   | special      | Yes        | No          | Yes
2024-12-03   | regular      | Yes        | No          | Yes
...

Step 10b Complete: Data imported from staging tables
```

---

## Step 11: Cleanup Staging Tables (Optional)

**File:** `step11_cleanup_staging.sql`

**Purpose:** Drops the staging tables after successful import.

**When to run:** Only after verifying the import was successful in Step 10.

**How to run:**
1. Press Cmd+N for new SQL Query
2. Open or copy contents of `step11_cleanup_staging.sql`
3. Press Cmd+Enter to run

**Expected output:**
```
Staging tables dropped
(empty result - no staging tables remain)
```

---

## Verification

After completing all steps, run this query to verify record counts:

```sql
SELECT 'cities' as table_name, COUNT(*) as count FROM cities
UNION ALL SELECT 'council_members', COUNT(*) FROM council_members
UNION ALL SELECT 'council_member_terms', COUNT(*) FROM council_member_terms
UNION ALL SELECT 'meetings', COUNT(*) FROM meetings
UNION ALL SELECT 'agenda_items', COUNT(*) FROM agenda_items
UNION ALL SELECT 'votes', COUNT(*) FROM votes
UNION ALL SELECT 'member_votes', COUNT(*) FROM member_votes;
```

**Expected counts:**

| Table | Count |
|-------|-------|
| cities | 1 |
| council_members | 7 |
| council_member_terms | 7 |
| meetings | 22 |
| agenda_items | 437 |
| votes | 437 |
| member_votes | 3,059 |

**Verify URLs are working:**

```sql
SELECT meeting_date,
       CASE WHEN agenda_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_agenda,
       CASE WHEN minutes_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_minutes,
       CASE WHEN video_url IS NOT NULL THEN 'Yes' ELSE 'No' END as has_video
FROM meetings
WHERE city_id = 1
ORDER BY meeting_date DESC
LIMIT 10;
```

**Verify member stats:**

```sql
SELECT short_name, total_votes, aye_count, nay_count, aye_percentage
FROM mv_member_stats
WHERE city_key = 'santa_ana'
ORDER BY total_votes DESC;
```

---

## Troubleshooting

### "relation already exists" error
Run Step 1 again to drop all existing objects.

### "violates foreign key constraint" error
Make sure you run steps in order. Each step depends on previous ones.

### "function does not exist" error
Run Step 6 (functions) before Step 10.

### Views show 0 records
Run `SELECT refresh_all_materialized_views();` after importing data.

### CSV import fails with encoding error
Make sure the CSV file is saved with UTF-8 encoding. If issues persist, try Latin-1 encoding in the import dialog.

### Staging tables not visible in sidebar
Click the refresh button in TablePlus sidebar, or disconnect and reconnect.

---

## Summary

| Step | File | Action |
|------|------|--------|
| 1 | `step1_extensions_and_drop.sql` | Run SQL |
| 2 | `step2_core_tables.sql` | Run SQL |
| 3 | `step3_meeting_tables.sql` | Run SQL |
| 4 | `step4_session_tables.sql` | Run SQL |
| 5 | `step5_materialized_views.sql` | Run SQL |
| 6 | `step6_functions.sql` | Run SQL |
| 7 | `step7_seed_data.sql` | Run SQL |
| 8 | `step8_create_staging.sql` | Run SQL |
| 9a | Terminal command | Run `python3 tools/generate_meetings_csv.py --year 2024` |
| 9b | TablePlus import | Import `santa_ana_extraction_complete2024.csv` → `staging_votes` |
| 9c | TablePlus import | Import `meetings_2024.csv` → `staging_meetings` |
| 10 | `step10_import_from_staging.sql` | Run SQL |
| 11 | `step11_cleanup_staging.sql` | Run SQL (optional) |
