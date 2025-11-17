#!/usr/bin/env python3
"""
Script to run AI-powered Santa Ana vote extraction on all matched files
"""

import csv
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add the current directory and agents directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'agents'))

from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('santa_ana_extraction.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main extraction process"""

    # Initialize the AI-powered extractor
    logger.info("Initializing AI-powered Santa Ana extractor")
    extractor = AIPoweredSantaAnaExtractor()

    # Load the mapping report
    mapping_file = "santa_ana_mapping_report.csv"
    if not os.path.exists(mapping_file):
        logger.error(f"Mapping file not found: {mapping_file}")
        return

    # Read matched file pairs
    matched_pairs = []
    with open(mapping_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['status'] == 'matched' and row['minutes_file']:
                matched_pairs.append({
                    'agenda_file': row['agenda_file'],
                    'minutes_file': row['minutes_file'],
                    'date': row['date']
                })

    logger.info(f"Found {len(matched_pairs)} matched agenda/minutes pairs")

    # Create output directory
    output_dir = Path("santa_ana_extraction_results")
    output_dir.mkdir(exist_ok=True)

    # Process each pair
    all_results = []
    successful_extractions = 0

    for i, pair in enumerate(matched_pairs, 1):
        logger.info(f"Processing pair {i}/{len(matched_pairs)}: {pair['date']}")

        try:
            # Run extraction
            result = extractor.process_santa_ana_meeting(
                agenda_path=pair['agenda_file'],
                minutes_path=pair['minutes_file']
            )

            # Add metadata
            result['source_files'] = pair
            result['extraction_date'] = datetime.now().isoformat()

            # Save individual result
            output_file = output_dir / f"santa_ana_votes_{pair['date']}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)

            all_results.append(result)

            if result.get('success', False):
                successful_extractions += 1
                logger.info(f"✓ Successfully extracted {len(result.get('votes', []))} votes")
            else:
                logger.warning(f"⚠ Extraction failed: {result.get('message', 'Unknown error')}")

        except Exception as e:
            logger.error(f"✗ Error processing {pair['date']}: {str(e)}")
            error_result = {
                'success': False,
                'message': f"Processing error: {str(e)}",
                'votes': [],
                'source_files': pair,
                'extraction_date': datetime.now().isoformat()
            }
            all_results.append(error_result)

    # Save combined results
    combined_output = {
        'extraction_summary': {
            'total_meetings': len(matched_pairs),
            'successful_extractions': successful_extractions,
            'failed_extractions': len(matched_pairs) - successful_extractions,
            'extraction_timestamp': datetime.now().isoformat(),
            'extractor_used': 'AIPoweredSantaAnaExtractor'
        },
        'learning_stats': extractor.get_learning_stats(),
        'results': all_results
    }

    combined_file = output_dir / "santa_ana_all_results.json"
    with open(combined_file, 'w') as f:
        json.dump(combined_output, f, indent=2)

    # Export learning data
    learning_export = output_dir / "santa_ana_learning_data.json"
    extractor.export_learning_data(str(learning_export))

    # Print summary
    logger.info("\n" + "="*60)
    logger.info("EXTRACTION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total meetings processed: {len(matched_pairs)}")
    logger.info(f"Successful extractions: {successful_extractions}")
    logger.info(f"Failed extractions: {len(matched_pairs) - successful_extractions}")
    logger.info(f"Success rate: {successful_extractions/len(matched_pairs)*100:.1f}%")

    total_votes = sum(len(result.get('votes', [])) for result in all_results)
    logger.info(f"Total votes extracted: {total_votes}")

    logger.info(f"\nResults saved to: {output_dir}")
    logger.info(f"Combined results: {combined_file}")
    logger.info(f"Learning data: {learning_export}")

    # Learning statistics
    stats = extractor.get_learning_stats()
    logger.info(f"\nLearning Statistics:")
    logger.info(f"AI fallback rate: {stats['learning_progress']['ai_fallback_rate']:.1%}")
    logger.info(f"Pattern learning rate: {stats['learning_progress']['pattern_learning_rate']:.1%}")
    logger.info(f"Quality trend: {stats['learning_progress']['quality_trend']}")

if __name__ == "__main__":
    main()