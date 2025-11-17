#!/usr/bin/env python3
"""
Quick Vote Extraction Shortcut
Simple script to run vote extraction and capture in session archiver
"""

import os
import sys
import json
import csv
from datetime import datetime

def quick_extract():
    """Quick extraction on recent Santa Ana meetings"""

    print("🗳️  Quick Vote Extraction")
    print("=" * 30)

    try:
        from agents.city_vote_extractor_factory import CityVoteExtractorFactory

        factory = CityVoteExtractorFactory()

        # Load mapping and get recent meetings
        with open('santa_ana_mapping_report.csv', 'r') as f:
            pairs = [r for r in csv.DictReader(f) if r['status'] == 'matched'][-3:]

        print(f"Testing last {len(pairs)} meetings:")

        results = []
        for pair in pairs:
            print(f"\n📅 {pair['date']}")
            try:
                result = factory.process_meeting_documents(pair['agenda_file'], pair['minutes_file'])
                votes = len(result.get('votes', []))
                quality = result.get('validation_results', {}).get('quality_score', 0)

                if votes > 0:
                    print(f"   ✅ {votes} votes ({quality:.1%} quality)")
                    # Save result
                    filename = f"votes_{pair['date'].replace('-', '_')}.json"
                    with open(filename, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"   💾 Saved: {filename}")
                else:
                    print(f"   ⚪ No votes found")

                results.append({
                    'date': pair['date'],
                    'votes': votes,
                    'quality': quality,
                    'success': result['success']
                })

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results.append({
                    'date': pair['date'],
                    'votes': 0,
                    'error': str(e)
                })

        # Summary
        total_votes = sum(r.get('votes', 0) for r in results)
        successful = sum(1 for r in results if r.get('success', False))

        print(f"\n📊 Summary:")
        print(f"   Meetings: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Total votes: {total_votes}")

        return results

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def manual_setup(date_str):
    """Set up for manual analysis"""
    print(f"🧠 Manual Analysis Setup: {date_str}")
    print("=" * 40)
    print("💡 Steps for manual vote extraction:")
    print("1. Read the minutes file")
    print("2. Search for: motion, vote, aye, nay, pass, carried")
    print("3. Extract individual council member votes")
    print("4. Create JSON structure matching automated format")
    print(f"5. Save as: AI_EXTRACTED_votes_{date_str.replace('-', '_')}.json")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "manual" and len(sys.argv) > 2:
            manual_setup(sys.argv[2])
        else:
            print("Usage: python quick_vote_extract.py [manual DATE]")
    else:
        quick_extract()