#!/usr/bin/env python3
"""
Vote Extraction Shortcut
Quick script to run vote extraction and capture results in session archiver
"""

import os
import sys
import json
import csv
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daily_claude_logs'))

def run_vote_extraction(mapping_file="santa_ana_mapping_report.csv", limit=None):
    """
    Run vote extraction on Santa Ana meetings with session archiving

    Args:
        mapping_file: CSV file with agenda/minutes pairs
        limit: Optional limit on number of meetings to process
    """

    print("🗳️  Vote Extraction Shortcut")
    print("=" * 50)

    try:
        # Initialize session archiver
        from claude_session_archiver import ClaudeSessionArchiver
        archiver = ClaudeSessionArchiver()
        session_id = archiver.start_session()
        print(f"📝 Started session: {session_id}")

        # Initialize vote extractor
        from agents.city_vote_extractor_factory import CityVoteExtractorFactory
        factory = CityVoteExtractorFactory()

        # Load mapping file
        if not os.path.exists(mapping_file):
            print(f"❌ Mapping file not found: {mapping_file}")
            return

        with open(mapping_file, 'r') as f:
            reader = csv.DictReader(f)
            matched_pairs = [row for row in reader if row['status'] == 'matched']

        if limit:
            matched_pairs = matched_pairs[:limit]

        print(f"🔍 Processing {len(matched_pairs)} matched meetings")

        # Process meetings
        results = []
        votes_found = 0

        for i, pair in enumerate(matched_pairs, 1):
            agenda_path = pair['agenda_file']
            minutes_path = pair['minutes_file']
            date = pair['date']

            print(f"\n📅 {i}/{len(matched_pairs)}: {date}")

            try:
                result = factory.process_meeting_documents(agenda_path, minutes_path)

                success = result['success']
                vote_count = len(result.get('votes', []))
                quality = result.get('validation_results', {}).get('quality_score', 0)

                if vote_count > 0:
                    print(f"   ✅ {vote_count} votes found (Quality: {quality:.1%})")
                    votes_found += vote_count

                    # Save individual meeting results
                    output_file = f"votes_{date.replace('-', '_')}.json"
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                    print(f"   💾 Saved: {output_file}")

                else:
                    print(f"   ⚪ No votes extracted")

                results.append({
                    'date': date,
                    'success': success,
                    'votes_count': vote_count,
                    'quality_score': quality,
                    'output_file': output_file if vote_count > 0 else None
                })

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                results.append({
                    'date': date,
                    'success': False,
                    'votes_count': 0,
                    'error': str(e)
                })

        # Generate summary
        successful = sum(1 for r in results if r['success'])
        meetings_with_votes = sum(1 for r in results if r.get('votes_count', 0) > 0)

        summary = {
            'extraction_date': datetime.now().isoformat(),
            'total_meetings': len(results),
            'successful_extractions': successful,
            'meetings_with_votes': meetings_with_votes,
            'total_votes_found': votes_found,
            'results': results
        }

        # Save summary
        summary_file = f"vote_extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n📊 SUMMARY:")
        print(f"   Total meetings: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   With votes: {meetings_with_votes}")
        print(f"   Total votes: {votes_found}")
        print(f"   Summary saved: {summary_file}")

        # Capture in session archiver
        archiver.capture_interaction(
            prompt=f"Run vote extraction shortcut on {len(matched_pairs)} Santa Ana meetings",
            response=f"Processed {len(results)} meetings, found {votes_found} votes in {meetings_with_votes} meetings. Success rate: {successful/len(results)*100:.1f}%",
            tool_calls=[
                {'tool_name': 'CityVoteExtractorFactory', 'parameters': {'meetings': len(matched_pairs)}},
                {'tool_name': 'Write', 'parameters': {'file_path': summary_file}}
            ],
            files_accessed=[mapping_file] + [r.get('output_file') for r in results if r.get('output_file')],
            context={'task_type': 'batch_vote_extraction', 'meetings_processed': len(results), 'votes_found': votes_found}
        )

        # End session
        stats = archiver.end_session()
        print(f"📝 Session completed: {stats['interactions']} interactions")

        return summary

    except Exception as e:
        print(f"❌ Error in vote extraction: {e}")
        import traceback
        traceback.print_exc()
        return None

def quick_manual_analysis(meeting_date, minutes_file):
    """
    Quick manual analysis helper for specific meetings

    Args:
        meeting_date: Date string (YYYY-MM-DD)
        minutes_file: Path to minutes file
    """

    print(f"🔍 Manual Analysis: {meeting_date}")
    print("=" * 40)

    try:
        # Initialize session archiver
        from claude_session_archiver import ClaudeSessionArchiver
        archiver = ClaudeSessionArchiver()
        session_id = archiver.start_session()

        print(f"📝 Session: {session_id}")
        print(f"📄 Minutes: {minutes_file}")
        print("\n💡 Tip: Use Claude to analyze this file for vote information")
        print("   Look for: motion, vote, aye, nay, pass, carried, approved")

        # Capture the setup
        archiver.capture_interaction(
            prompt=f"Set up manual analysis for {meeting_date}",
            response=f"Initialized manual vote analysis session for {meeting_date}. Ready to analyze {minutes_file}",
            files_accessed=[minutes_file],
            context={'task_type': 'manual_analysis_setup', 'meeting_date': meeting_date}
        )

        return archiver

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Vote Extraction Shortcut")
    parser.add_argument("--auto", action="store_true", help="Run automated extraction")
    parser.add_argument("--manual", metavar="DATE", help="Set up manual analysis for specific date")
    parser.add_argument("--mapping", default="santa_ana_mapping_report.csv", help="Mapping CSV file")
    parser.add_argument("--limit", type=int, help="Limit number of meetings to process")
    parser.add_argument("--minutes", help="Minutes file for manual analysis")

    args = parser.parse_args()

    if args.auto:
        run_vote_extraction(args.mapping, args.limit)
    elif args.manual:
        if not args.minutes:
            print("❌ --minutes required for manual analysis")
            sys.exit(1)
        quick_manual_analysis(args.manual, args.minutes)
    else:
        print("Vote Extraction Shortcut")
        print("Usage:")
        print("  --auto                    Run automated extraction")
        print("  --manual DATE --minutes   Set up manual analysis")
        print("  --mapping FILE           Specify mapping CSV")
        print("  --limit N                Limit to N meetings")
        print("\nExamples:")
        print("  python vote_extraction_shortcut.py --auto")
        print("  python vote_extraction_shortcut.py --auto --limit 5")
        print("  python vote_extraction_shortcut.py --manual 2024-01-16 --minutes /path/to/minutes.txt")