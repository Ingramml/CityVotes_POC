# Database Setup - Step by Step Guide

## Overview

This folder contains SQL scripts to set up the CityVotes PostgreSQL database in TablePlus (or any SQL client).

## Two Import Methods

### Method A: Staging Tables (Recommended)
Upload CSVs directly to PostgreSQL, then run SQL to transform data.

### Method B: Python + Generated SQL (Legacy)
Generate SQL from Python, then run in TablePlus.

See [IMPORT_METHODS_COMPARISON.md](IMPORT_METHODS_COMPARISON.md) for details.

---

## Method A: Staging Tables (Recommended)

### Step-by-Step Process

| Step | File | What it does |
|------|------|--------------|
| 1 | `step1_extensions_and_drop.sql` | Enables UUID extension, drops existing tables |
| 2 | `step2_core_tables.sql` | Creates cities, council_members, council_member_terms |
| 3 | `step3_meeting_tables.sql` | Creates meetings, agenda_items, votes, member_votes |
| 4 | `step4_session_tables.sql` | Creates sessions, session_data (for web app) |
| 5 | `step5_materialized_views.sql` | Creates mv_meeting_summary, mv_vote_summary, mv_member_stats, mv_member_alignment |
| 6 | `step6_functions.sql` | Creates helper functions |
| 7 | `step7_seed_data.sql` | Inserts Santa Ana city and council members |
| 8 | `step8_create_staging.sql` | Creates staging tables for CSV import |
| 9 | **Import CSVs in TablePlus** | See instructions below |
| 10 | `step10_import_from_staging.sql` | Transforms staging → final tables |
| 11 | `step11_cleanup_staging.sql` | (Optional) Drops staging tables |

### Importing CSVs in TablePlus (Step 9)

After running `step8_create_staging.sql`:

**Import Vote Data:**
1. Right-click `staging_votes` table → Import → From CSV
2. Select: `extractors/santa_ana/2024/santa_ana_extraction_complete2024.csv`
3. Check "First row is header"
4. Click Import

**Import Meeting URLs:**
1. First generate the CSV: `python3 tools/generate_meetings_csv.py --year 2024`
2. Right-click `staging_meetings` table → Import → From CSV
3. Select: `extractors/santa_ana/2024/meetings_2024.csv`
4. Check "First row is header"
5. Click Import

Then run `step10_import_from_staging.sql` to load data into final tables.

---

## Method B: Python + Generated SQL (Legacy)

| Step | File | What it does |
|------|------|--------------|
| 1-7 | Same as Method A | Schema and seed data |
| 8 | `method_b_step8_import_votes.sql` | Instructions for importing votes |
| 9 | `method_b_step9_verify_and_refresh.sql` | Refreshes views and verifies data |
| 10 | `update_meeting_urls.sql` (in extractors folder) | Adds agenda, minutes, video URLs |

### Generating the Import Files

Before Step 8, generate the vote import SQL from the CSV:

```bash
cd /Users/michaelingram/Documents/GitHub/CityVotes_POC
python3 backend/database/import_csv.py extractors/santa_ana/2024/santa_ana_extraction_complete2024.csv
```

This creates: `extractors/santa_ana/2024/import_votes.sql`

Before Step 10, generate the meeting URLs from PrimeGov:

```bash
cd /Users/michaelingram/Documents/GitHub/CityVotes_POC
python3 tools/generate_meetings_csv.py --year 2024
```

This creates: `extractors/santa_ana/2024/meetings_2024.csv`

## Expected Record Counts After Import

| Table | Expected Count |
|-------|----------------|
| cities | 1 |
| council_members | 7 |
| council_member_terms | 7 |
| meetings | 22 |
| agenda_items | 437 |
| votes | 437 |
| member_votes | 3,059 |

## Files

```
backend/database/
├── README.md                            # This file
├── IMPORT_METHODS_COMPARISON.md         # Comparison of import methods
├── schema.sql                           # Complete schema (all-in-one)
├── import_csv.py                        # Python script to generate import SQL
│
│ # Method A: Staging Tables (Steps 1-11)
├── step1_extensions_and_drop.sql        # Step 1: Clean database
├── step2_core_tables.sql                # Step 2: Core tables
├── step3_meeting_tables.sql             # Step 3: Meeting tables
├── step4_session_tables.sql             # Step 4: Session tables
├── step5_materialized_views.sql         # Step 5: Materialized views
├── step6_functions.sql                  # Step 6: Functions
├── step7_seed_data.sql                  # Step 7: Santa Ana seed data
├── step8_create_staging.sql             # Step 8: Create staging tables
├── step10_import_from_staging.sql       # Step 10: Transform and load
├── step11_cleanup_staging.sql           # Step 11: Cleanup (optional)
│
│ # Method B: Legacy Python + SQL
├── method_b_step8_import_votes.sql      # Instructions for Method B
└── method_b_step9_verify_and_refresh.sql # Verify for Method B
```

## Troubleshooting

### "relation already exists" error
Run Step 1 again to drop all existing objects.

### "violates foreign key constraint" error
Make sure you run steps in order. Each step depends on previous ones.

### "function does not exist" error
Run Step 6 (functions) before Step 9.

### Views show 0 records
Run `SELECT refresh_all_materialized_views();` after importing data.
