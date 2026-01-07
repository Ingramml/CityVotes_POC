#!/usr/bin/env python3
"""
CSV Import Script for Santa Ana Extraction Data

This script reads the extraction CSV and populates the normalized database tables:
- meetings
- agenda_items
- votes
- member_votes

Usage:
    python import_csv.py <csv_file_path> [--dry-run]

Example:
    python import_csv.py ../../extractors/santa_ana/2024/santa_ana_extraction_complete2024.csv
"""

import csv
import json
import ast
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False
    print("Warning: SQLAlchemy not installed. Running in SQL-generation mode only.")


# Santa Ana council members (must match database IDs)
MEMBER_COLUMNS = ['Hernandez', 'Lopez', 'Penaloza', 'Vazquez', 'Phan', 'Bacerra', 'Amezcua']

# Map CSV vote values to database values
VOTE_MAPPING = {
    'aye': 'AYE',
    'yes': 'AYE',
    'nay': 'NAY',
    'no': 'NAY',
    'abstain': 'ABSTAIN',
    'absent': 'ABSENT',
    'recused': 'RECUSAL',
    'recusal': 'RECUSAL',
    '': 'ABSENT',  # Empty means absent
}


def parse_date(date_str: str) -> Optional[str]:
    """Parse date from various formats to YYYY-MM-DD."""
    if not date_str:
        return None

    # Try different date formats
    formats = [
        '%m/%d/%y',    # 1/16/24
        '%m/%d/%Y',    # 1/16/2024
        '%Y-%m-%d',    # 2024-01-16
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    print(f"Warning: Could not parse date '{date_str}'")
    return None


def parse_tally(tally_str: str) -> Dict[str, int]:
    """Parse tally string to dictionary."""
    if not tally_str:
        return {'ayes': 0, 'noes': 0, 'abstain': 0, 'absent': 0, 'recused': 0}

    try:
        # Handle Python dict format: {'ayes': 7, 'noes': 0, ...}
        return ast.literal_eval(tally_str)
    except (ValueError, SyntaxError):
        pass

    try:
        # Handle JSON format
        return json.loads(tally_str)
    except json.JSONDecodeError:
        pass

    print(f"Warning: Could not parse tally '{tally_str}'")
    return {'ayes': 0, 'noes': 0, 'abstain': 0, 'absent': 0, 'recused': 0}


def normalize_vote(vote_str: str) -> str:
    """Normalize vote value to database format."""
    if not vote_str:
        return 'ABSENT'
    return VOTE_MAPPING.get(vote_str.lower().strip(), 'ABSENT')


def normalize_meeting_type(meeting_type: str) -> str:
    """Normalize meeting type."""
    if not meeting_type:
        return 'regular'

    mt = meeting_type.lower().strip()
    if mt in ['regular', 'reguar']:  # Handle typo in data
        return 'regular'
    elif mt == 'special':
        return 'special'
    elif 'housing' in mt:
        return 'joint_housing'
    elif mt == 'emergency':
        return 'emergency'
    return 'regular'


def normalize_section(section: str) -> str:
    """Normalize meeting section."""
    if not section:
        return 'GENERAL'

    s = section.upper().strip()
    if 'CONSENT' in s:
        return 'CONSENT'
    elif 'PUBLIC' in s and 'HEARING' in s:
        return 'PUBLIC_HEARING'
    elif 'BUSINESS' in s:
        return 'BUSINESS'
    elif 'CLOSED' in s:
        return 'CLOSED'
    return 'GENERAL'


def normalize_outcome(outcome: str) -> str:
    """Normalize vote outcome."""
    if not outcome:
        return 'PASS'

    o = outcome.upper().strip()
    if o in ['PASS', 'PASSED']:
        return 'PASS'
    elif o in ['FAIL', 'FAILED']:
        return 'FAIL'
    elif o in ['FLAG', 'FLAGGED']:
        return 'FLAG'
    elif o in ['CONTINUED', 'CONTINUE']:
        return 'CONTINUED'
    elif o in ['REMOVED', 'REMOVE']:
        return 'REMOVED'
    elif o == 'TIE':
        return 'TIE'
    return 'PASS'


def read_csv(file_path: str) -> List[Dict]:
    """Read CSV file and return list of row dictionaries."""
    rows = []
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
            print(f"Successfully read CSV with encoding: {encoding}")
            return rows
        except (UnicodeDecodeError, UnicodeError):
            continue

    raise ValueError(f"Could not read CSV with any supported encoding")


def group_by_meeting(rows: List[Dict]) -> Dict[str, List[Dict]]:
    """Group rows by meeting date and type."""
    meetings = {}
    for row in rows:
        date = parse_date(row.get('meeting_date', ''))
        if not date:
            continue
        meeting_type = normalize_meeting_type(row.get('meeting_type', ''))
        key = f"{date}_{meeting_type}"
        if key not in meetings:
            meetings[key] = []
        meetings[key].append(row)
    return meetings


def generate_sql_statements(rows: List[Dict], city_id: int = 1) -> Tuple[str, Dict]:
    """Generate SQL INSERT statements from CSV rows."""

    meetings = group_by_meeting(rows)

    sql_statements = []
    stats = {
        'meetings': 0,
        'agenda_items': 0,
        'votes': 0,
        'member_votes': 0,
        'skipped': 0,
    }

    sql_statements.append("-- Generated SQL for Santa Ana vote data import")
    sql_statements.append(f"-- Source rows: {len(rows)}")
    sql_statements.append(f"-- Generated: {datetime.now().isoformat()}")
    sql_statements.append("")
    sql_statements.append("BEGIN;")
    sql_statements.append("")

    meeting_id = 1  # We'll use placeholder IDs; actual IDs come from database
    item_id = 1
    vote_id = 1

    for meeting_key, meeting_rows in sorted(meetings.items()):
        date_str, meeting_type = meeting_key.rsplit('_', 1)

        # Insert meeting
        sql_statements.append(f"-- Meeting: {date_str} ({meeting_type})")
        sql_statements.append(f"""
INSERT INTO meetings (city_id, meeting_date, meeting_type)
VALUES ({city_id}, '{date_str}', '{meeting_type}')
ON CONFLICT (city_id, meeting_date, meeting_type) DO UPDATE SET updated_at = NOW()
RETURNING id;
-- Use returned meeting_id for subsequent inserts
""")
        stats['meetings'] += 1

        for row in meeting_rows:
            example_id = row.get('example_id', '')
            item_number = row.get('agenda_item_number', '')
            title = row.get('agenda_item_title', '').replace("'", "''")[:500]  # Escape quotes, limit length
            description = row.get('agenda_item_description', '').replace("'", "''")[:2000]
            section = normalize_section(row.get('meeting_section', ''))
            outcome = normalize_outcome(row.get('outcome', ''))
            tally = parse_tally(row.get('tally', ''))

            if not item_number:
                stats['skipped'] += 1
                continue

            # Insert agenda item
            sql_statements.append(f"""
-- Agenda Item: {item_number}
INSERT INTO agenda_items (meeting_id, item_number, title, description, section)
SELECT m.id, '{item_number}', '{title[:200]}', '{description[:500]}', '{section}'
FROM meetings m
WHERE m.city_id = {city_id} AND m.meeting_date = '{date_str}' AND m.meeting_type = '{meeting_type}'
ON CONFLICT (meeting_id, item_number) DO UPDATE SET title = EXCLUDED.title, updated_at = NOW()
RETURNING id;
""")
            stats['agenda_items'] += 1

            # Insert vote record
            sql_statements.append(f"""
INSERT INTO votes (agenda_item_id, example_id, outcome, ayes, noes, abstain, absent, recusal)
SELECT ai.id, '{example_id}', '{outcome}', {tally.get('ayes', 0)}, {tally.get('noes', 0)},
       {tally.get('abstain', 0)}, {tally.get('absent', 0)}, {tally.get('recused', 0)}
FROM agenda_items ai
JOIN meetings m ON ai.meeting_id = m.id
WHERE m.city_id = {city_id} AND m.meeting_date = '{date_str}' AND m.meeting_type = '{meeting_type}'
  AND ai.item_number = '{item_number}'
ON CONFLICT (example_id) DO UPDATE SET outcome = EXCLUDED.outcome, updated_at = NOW()
RETURNING id;
""")
            stats['votes'] += 1

            # Insert member votes
            for member in MEMBER_COLUMNS:
                vote_choice = normalize_vote(row.get(member, ''))
                sql_statements.append(f"""
INSERT INTO member_votes (vote_id, member_id, vote_choice)
SELECT v.id, cm.id, '{vote_choice}'
FROM votes v
JOIN agenda_items ai ON v.agenda_item_id = ai.id
JOIN meetings m ON ai.meeting_id = m.id
JOIN council_members cm ON cm.city_id = {city_id} AND cm.short_name = '{member}'
WHERE v.example_id = '{example_id}'
ON CONFLICT (vote_id, member_id) DO UPDATE SET vote_choice = EXCLUDED.vote_choice;
""")
                stats['member_votes'] += 1

    sql_statements.append("")
    sql_statements.append("-- Refresh materialized views after import")
    sql_statements.append("SELECT refresh_all_materialized_views();")
    sql_statements.append("")
    sql_statements.append("COMMIT;")

    return '\n'.join(sql_statements), stats


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    if not os.path.exists(csv_path):
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    print(f"Reading CSV: {csv_path}")
    rows = read_csv(csv_path)
    print(f"Found {len(rows)} rows")

    print("\nGenerating SQL statements...")
    sql, stats = generate_sql_statements(rows)

    # Write SQL to file
    output_path = os.path.join(os.path.dirname(csv_path), 'import_votes.sql')
    with open(output_path, 'w') as f:
        f.write(sql)

    print(f"\nSQL written to: {output_path}")
    print(f"\nStatistics:")
    print(f"  Meetings:     {stats['meetings']}")
    print(f"  Agenda Items: {stats['agenda_items']}")
    print(f"  Votes:        {stats['votes']}")
    print(f"  Member Votes: {stats['member_votes']}")
    print(f"  Skipped:      {stats['skipped']}")

    if dry_run:
        print("\n[DRY RUN] SQL file generated but not executed.")
        print(f"To import, run: psql -d cityvotes -f {output_path}")
    else:
        print(f"\nTo import into database, run:")
        print(f"  psql -d cityvotes -f {output_path}")


if __name__ == '__main__':
    main()
