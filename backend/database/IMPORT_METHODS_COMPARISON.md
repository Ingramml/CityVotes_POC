# CSV Import Methods Comparison

## Overview

Two CSVs need to be imported:
1. `meetings_2024.csv` - Meeting URLs (agenda, minutes, video)
2. `santa_ana_extraction_complete2024.csv` - Vote data (feeds multiple tables)

---

## Method 1: Current Approach (Python + Generated SQL)

### How it works:
1. Python script reads CSV
2. Generates SQL INSERT statements
3. Copy/paste SQL into TablePlus
4. Run manually

### Pros:
- Validates data in Python before SQL generation
- Can handle complex transformations
- No PostgreSQL extensions needed

### Cons:
- Two-step process (generate SQL, then run it)
- Large SQL files (import_votes.sql is ~4000 lines)
- Harder to re-run or update
- Can't easily run from TablePlus alone

---

## Method 2: PostgreSQL Staging Tables (Recommended)

### How it works:
1. Upload CSV directly to staging table in TablePlus
2. Run SQL to transform and move data to final tables
3. All logic lives in PostgreSQL

### Pros:
- **Single workflow in TablePlus** - no Python needed
- Re-runnable (can refresh data anytime)
- Easier to debug (can inspect staging data)
- Uses PostgreSQL's COPY command (very fast)
- All transformations in SQL (portable, documented)

### Cons:
- Requires staging tables
- SQL transformations can be complex

---

## Recommended: Method 2 Implementation

### Step 1: Create Staging Tables

```sql
-- Staging table for vote extraction CSV
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

-- Staging table for meetings CSV
CREATE TABLE staging_meetings (
    city_id INTEGER,
    meeting_date TEXT,
    meeting_type TEXT,
    agenda_url TEXT,
    minutes_url TEXT,
    video_url TEXT
);
```

### Step 2: Import CSVs in TablePlus

1. Right-click `staging_votes` → Import → From CSV
2. Select `santa_ana_extraction_complete2024.csv`
3. Check "First row is header"
4. Import

Repeat for `staging_meetings` with `meetings_2024.csv`

### Step 3: Transform and Load

Run SQL to move data from staging to final tables:

```sql
-- See: step10_import_from_staging.sql
```

---

## Files

| File | Purpose |
|------|---------|
| `step10a_create_staging.sql` | Creates staging tables |
| `step10b_import_from_staging.sql` | Transforms staging → final tables |
| `step10c_cleanup_staging.sql` | Drops staging tables (optional) |
