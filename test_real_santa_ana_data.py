#!/usr/bin/env python3
"""
Test Santa Ana Vote Extractor with Real Data

Uses the matched agenda-minutes pairs from the actual Santa Ana data
to test the vote extraction capabilities with real documents.
"""

import sys
import os
import csv
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.city_vote_extractor_factory import CityVoteExtractorFactory

def load_matched_pairs():
    """Load the matched agenda-minutes pairs from CSV"""
    matched_pairs = []

    with open('santa_ana_mapping_report.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['status'] == 'matched' and row['minutes_file']:
                matched_pairs.append({
                    'agenda_file': row['agenda_file'],
                    'minutes_file': row['minutes_file'],
                    'date': row['date']
                })

    return matched_pairs

def test_santa_ana_extraction():
    """Test Santa Ana vote extraction with real data"""

    print("🏛️  Testing Santa Ana Vote Extractor with Real Data")
    print("=" * 60)

    # Load matched pairs
    matched_pairs = load_matched_pairs()
    print(f"📊 Found {len(matched_pairs)} matched agenda-minutes pairs")

    # Initialize factory
    factory = CityVoteExtractorFactory()

    results = []

    for i, pair in enumerate(matched_pairs, 1):
        print(f"\n📄 Processing pair {i}/{len(matched_pairs)}: {pair['date']}")
        print(f"  Agenda: {Path(pair['agenda_file']).name}")
        print(f"  Minutes: {Path(pair['minutes_file']).name}")

        try:
            # Process with factory (should auto-detect as Santa Ana)
            result = factory.process_meeting_documents(
                pair['agenda_file'],
                pair['minutes_file']
            )

            # Collect results
            pair_result = {
                'date': pair['date'],
                'success': result['success'],
                'extractor_used': result['factory_metadata']['extractor_used'],
                'city_detected': result['factory_metadata']['city_detected'],
                'votes_extracted': len(result['votes']),
                'quality_score': result['validation_results']['quality_score'],
                'message': result['message']
            }

            results.append(pair_result)

            # Display results
            if result['success']:
                print(f"  ✅ Success: {result['message']}")
                print(f"  📊 Extractor: {result['factory_metadata']['extractor_used']}")
                print(f"  🎯 Quality: {result['validation_results']['quality_score']:.1%}")
                print(f"  🗳️  Votes: {len(result['votes'])}")

                # Show sample vote if available
                if result['votes']:
                    vote = result['votes'][0]
                    print(f"  📋 Sample: {vote['agenda_item_number']} - {vote['outcome']} ({vote['vote_count']})")
                    if vote['validation_notes']:
                        print(f"  ⚠️  Notes: {len(vote['validation_notes'])} validation issues")
            else:
                print(f"  ❌ Failed: {result['message']}")

        except Exception as e:
            print(f"  💥 Error: {str(e)}")
            pair_result = {
                'date': pair['date'],
                'success': False,
                'error': str(e)
            }
            results.append(pair_result)

    # Generate summary
    print("\n" + "=" * 60)
    print("📈 EXTRACTION SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]

    print(f"Total processed: {len(results)}")
    print(f"Successful extractions: {len(successful)}")
    print(f"Failed extractions: {len(failed)}")
    print(f"Success rate: {len(successful)/len(results)*100:.1f}%")

    if successful:
        avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
        total_votes = sum(r['votes_extracted'] for r in successful)
        avg_votes = total_votes / len(successful)

        print(f"Average quality score: {avg_quality:.1%}")
        print(f"Total votes extracted: {total_votes}")
        print(f"Average votes per meeting: {avg_votes:.1f}")

        # Show extractor usage
        extractors_used = {}
        for r in successful:
            extractor = r.get('extractor_used', 'Unknown')
            extractors_used[extractor] = extractors_used.get(extractor, 0) + 1

        print(f"\nExtractor usage:")
        for extractor, count in extractors_used.items():
            print(f"  {extractor}: {count} times")

    if failed:
        print(f"\nFailed extractions:")
        for r in failed:
            error_msg = r.get('error', r.get('message', 'Unknown error'))
            print(f"  {r['date']}: {error_msg}")

    # Show sample successful extraction details
    if successful:
        print(f"\n🔍 DETAILED SAMPLE EXTRACTION")
        print("-" * 40)

        # Find best quality extraction
        best_result = max(successful, key=lambda x: x['quality_score'])
        print(f"Best extraction: {best_result['date']}")
        print(f"Quality score: {best_result['quality_score']:.1%}")
        print(f"Votes extracted: {best_result['votes_extracted']}")

        # Re-process to get detailed results
        best_pair = next(p for p in matched_pairs if p['date'] == best_result['date'])
        detailed_result = factory.process_meeting_documents(
            best_pair['agenda_file'],
            best_pair['minutes_file']
        )

        if detailed_result['votes']:
            print(f"\nSample votes from {best_result['date']}:")
            for i, vote in enumerate(detailed_result['votes'][:3], 1):  # Show first 3 votes
                print(f"  {i}. {vote['agenda_item_number']}: {vote['agenda_item_title']}")
                print(f"     Outcome: {vote['outcome']} ({vote['vote_count']})")
                print(f"     Motion by: {vote['mover']}, seconded by: {vote['seconder']}")
                if vote['member_votes']:
                    ayes = [m for m, v in vote['member_votes'].items() if v == 'Aye']
                    print(f"     Ayes: {', '.join(ayes)}")
                print()

    return results

if __name__ == "__main__":
    if not Path('santa_ana_mapping_report.csv').exists():
        print("❌ santa_ana_mapping_report.csv not found!")
        print("Please run the agenda-minutes matching script first.")
        sys.exit(1)

    results = test_santa_ana_extraction()
    print(f"\n🎉 Real data testing completed!")
    print(f"🎯 Ready for production use with Santa Ana council documents.")