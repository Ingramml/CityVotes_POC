#!/usr/bin/env python3
"""
CSV to JSON Vote Extraction Converter

Converts manually extracted vote data from CSV format to JSON format
expected by the AI extractor comparison tools.

Usage:
    python csv_to_json.py <csv_file> [output_json]
    python csv_to_json.py santa_ana_2021_votes.csv
    python csv_to_json.py santa_ana_2021_votes.csv output.json
"""

import csv
import json
import sys
from pathlib import Path
from datetime import datetime

def csv_to_json(csv_file, output_file=None):
    """
    Convert extracted votes CSV to JSON format expected by AI extractor

    Supports two CSV formats:
    1. Option A: Pipe-separated member_votes column
    2. Option B: Separate column per council member
    """

    votes = []
    csv_path = Path(csv_file)

    if not csv_path.exists():
        print(f"❌ Error: File not found: {csv_file}")
        sys.exit(1)

    print(f"📥 Reading CSV: {csv_file}")

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        print(f"📋 Columns found: {', '.join(fieldnames)}")

        # Detect format
        has_member_columns = any(col in fieldnames for col in
                                ['Amezcua', 'Sarmiento', 'Bacerra', 'Hernandez',
                                 'Phan', 'Vazquez', 'Penaloza', 'Mayor', 'Councilmember'])
        has_member_votes_column = 'member_votes' in fieldnames

        if has_member_columns:
            print("✓ Format detected: Separate member columns (Option B)")
        elif has_member_votes_column:
            print("✓ Format detected: Pipe-separated member_votes (Option A)")
        else:
            print("⚠️  Warning: No member vote columns detected")

        row_num = 0
        for row in reader:
            row_num += 1

            # Skip empty rows
            if not row.get('meeting_date') or not row.get('meeting_date').strip():
                continue

            # Extract member votes
            member_votes = {}

            # Option B: Separate columns for each member
            if has_member_columns:
                # Known Santa Ana council members
                member_columns = ['Amezcua', 'Sarmiento', 'Bacerra', 'Hernandez',
                                'Phan', 'Vazquez', 'Penaloza', 'Mendoza', 'Lopez']

                for member in member_columns:
                    if member in row and row[member] and row[member].strip():
                        # Handle full name format if present
                        full_name_col = f"{member}_full"
                        if full_name_col in row and row[full_name_col]:
                            member_votes[row[full_name_col]] = row[member]
                        else:
                            member_votes[member] = row[member]

                # Also check for Mayor/Councilmember columns
                for col in fieldnames:
                    if (col.startswith('Mayor') or col.startswith('Councilmember')) and row[col]:
                        member_votes[col] = row[col]

            # Option A: Pipe-separated member_votes column
            if has_member_votes_column and row.get('member_votes'):
                for pair in row['member_votes'].split('|'):
                    if ':' in pair:
                        name, vote = pair.split(':', 1)
                        member_votes[name.strip()] = vote.strip()

            # Calculate tally
            # First try explicit columns
            if 'ayes' in row and row['ayes'] and row['ayes'].strip():
                tally = {
                    'ayes': int(row['ayes']),
                    'noes': int(row.get('noes', 0) or 0),
                    'abstain': int(row.get('abstain', 0) or 0),
                    'absent': int(row.get('absent', 0) or 0)
                }
            else:
                # Calculate from member votes
                tally = {
                    'ayes': len([v for v in member_votes.values() if v.lower() in ['aye', 'yes']]),
                    'noes': len([v for v in member_votes.values() if v.lower() in ['nay', 'no', 'nay']]),
                    'abstain': len([v for v in member_votes.values() if v.lower() == 'abstain']),
                    'absent': len([v for v in member_votes.values() if v.lower() == 'absent'])
                }

            # Create vote object in expected format
            vote = {
                'agenda_item_number': row.get('agenda_item', '').strip(),
                'agenda_item_title': row.get('item_title', '').strip(),
                'outcome': row.get('outcome', '').strip(),
                'tally': tally,
                'member_votes': member_votes,
                'meeting_date': row.get('meeting_date', '').strip()
            }

            # Add notes if present
            if 'notes' in row and row['notes']:
                vote['notes'] = row['notes'].strip()

            votes.append(vote)

        print(f"✅ Processed {row_num} rows, found {len(votes)} votes")

    if not votes:
        print("⚠️  Warning: No votes found in CSV")

    # Create output JSON
    output = {
        'votes': votes,
        'metadata': {
            'source_csv': str(csv_path),
            'total_votes': len(votes),
            'conversion_date': datetime.now().isoformat(),
            'meetings_included': sorted(set(v['meeting_date'] for v in votes if v.get('meeting_date')))
        }
    }

    # Determine output filename
    if not output_file:
        output_file = csv_path.with_suffix('.json')

    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"")
    print(f"✅ Conversion complete!")
    print(f"📄 Output: {output_file}")
    print(f"📊 Summary:")
    print(f"   - Total votes: {len(votes)}")
    print(f"   - Meetings: {len(output['metadata']['meetings_included'])}")
    if output['metadata']['meetings_included']:
        print(f"   - Date range: {output['metadata']['meetings_included'][0]} to {output['metadata']['meetings_included'][-1]}")

    return output

def main():
    if len(sys.argv) < 2:
        print("CSV to JSON Vote Extraction Converter")
        print("")
        print("Usage:")
        print("  python csv_to_json.py <csv_file> [output_json]")
        print("")
        print("Examples:")
        print("  python csv_to_json.py santa_ana_2021_votes.csv")
        print("  python csv_to_json.py data.csv output.json")
        print("")
        print("CSV Format Options:")
        print("")
        print("Option A - Pipe-separated member votes:")
        print("  meeting_date,agenda_item,item_title,outcome,ayes,noes,abstain,absent,member_votes")
        print('  2021-10-05,7.1,Budget,Pass,5,2,0,0,"Name1:Aye|Name2:Nay|..."')
        print("")
        print("Option B - Separate member columns:")
        print("  meeting_date,agenda_item,item_title,outcome,Amezcua,Sarmiento,Bacerra,...")
        print("  2021-10-05,7.1,Budget,Pass,Aye,Aye,Nay,...")
        sys.exit(1)

    csv_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    csv_to_json(csv_file, output_file)

if __name__ == '__main__':
    main()
