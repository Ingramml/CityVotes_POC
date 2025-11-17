#!/usr/bin/env python3
"""
Test script for improved Santa Ana vote extractor
"""

import sys
import os
from pathlib import Path

# Add the current directory and agents directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'agents'))

from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor

def test_single_file():
    """Test the improved extractor on a single problematic file"""

    # Initialize the improved extractor
    extractor = AIPoweredSantaAnaExtractor()

    # Test on a file that previously failed
    agenda_path = "/Volumes/SSD/CityVotes/Santa_Ana_CA/Agenda/txt_files/20210216_Meetings3528Agenda.txt"
    minutes_path = "/Volumes/SSD/CityVotes/Santa_Ana_CA/Minutes/txt_files/20210216_minutes_regular_city_council_meeting.txt"

    print(f"Testing extraction on: {minutes_path}")
    print("="*60)

    try:
        # Run extraction
        result = extractor.process_santa_ana_meeting(
            agenda_path=agenda_path,
            minutes_path=minutes_path
        )

        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        print(f"Votes extracted: {len(result.get('votes', []))}")

        if result.get('votes'):
            print("\nExtracted votes:")
            for i, vote in enumerate(result['votes'][:3], 1):  # Show first 3 votes
                print(f"\nVote {i}:")
                print(f"  Agenda Item: {vote.get('agenda_item_number', 'Unknown')}")
                print(f"  Outcome: {vote.get('outcome', 'Unknown')}")
                print(f"  Vote Count: {vote.get('vote_count', 'Unknown')}")
                print(f"  Member Votes: {vote.get('member_votes', {})}")

        # Show extraction metadata
        metadata = result.get('extraction_metadata', {})
        print(f"\nExtraction Method: {metadata.get('method_used', 'Unknown')}")
        print(f"Confidence Score: {metadata.get('confidence_score', 0)}")

        # Show validation results
        validation = result.get('validation_results', {})
        print(f"Quality Score: {validation.get('quality_score', 0):.1%}")
        print(f"Validation Passed: {validation.get('validation_passed', False)}")

        # Show learning stats
        stats = extractor.get_learning_stats()
        print(f"\nLearning Statistics:")
        print(f"  AI fallback rate: {stats['learning_progress']['ai_fallback_rate']:.1%}")
        print(f"  Pattern learning events: {stats['extraction_stats']['pattern_learning_events']}")
        print(f"  Member corrections: {stats['memory_stats']['member_corrections']}")

        return result

    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_single_file()

    if result and result.get('success') and result.get('votes'):
        print("\n✅ IMPROVEMENT SUCCESSFUL: Votes were extracted!")
    else:
        print("\n❌ STILL NEEDS WORK: No votes extracted")