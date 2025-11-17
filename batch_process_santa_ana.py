#!/usr/bin/env python3
"""
Santa Ana Meeting Batch Processor

This script processes all Santa Ana meeting files from the santa_ana_mapping_report.csv
using the AI-powered extractor. It handles error recovery, progress tracking, and
generates comprehensive reporting.

Features:
- Skips already processed meetings
- Uses AI-powered Santa Ana extractor
- Comprehensive error handling
- Detailed progress logging
- Quality score tracking
- Summary report generation
"""

import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.city_vote_extractor_factory import CityVoteExtractorFactory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('santa_ana_batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SantaAnaBatchProcessor:
    """Batch processor for Santa Ana meetings"""

    def __init__(self, csv_file: str = "santa_ana_mapping_report.csv",
                 output_dir: str = "/Users/michaelingram/Documents/GitHub/CityVotes_POC/CA/Santa_ANA/votes"):
        self.csv_file = csv_file
        self.output_dir = Path(output_dir)
        self.factory = CityVoteExtractorFactory()

        # Processing statistics
        self.stats = {
            'total_meetings': 0,
            'matched_meetings': 0,
            'already_processed': 0,
            'successfully_processed': 0,
            'failed_processing': 0,
            'errors': [],
            'quality_scores': [],
            'start_time': datetime.now(),
            'end_time': None
        }

        # Results storage
        self.results = []

    def load_meetings_from_csv(self) -> List[Dict[str, str]]:
        """Load meeting data from CSV file"""
        meetings = []

        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean up field names
                    clean_row = {
                        'agenda_file': row.get('agenda_file', '').strip(),
                        'minutes_file': row.get('minutes_file', '').strip(),
                        'date': row.get('date', '').strip(),
                        'status': row.get('status', '').strip()
                    }
                    meetings.append(clean_row)

            logger.info(f"Loaded {len(meetings)} meetings from {self.csv_file}")
            self.stats['total_meetings'] = len(meetings)

            return meetings

        except Exception as e:
            logger.error(f"Failed to load CSV file {self.csv_file}: {str(e)}")
            self.stats['errors'].append(f"CSV loading error: {str(e)}")
            return []

    def get_output_filename(self, date: str) -> str:
        """Generate output filename for a given date"""
        return f"santa_ana_votes_{date}.json"

    def is_already_processed(self, date: str) -> bool:
        """Check if meeting has already been processed"""
        output_file = self.output_dir / self.get_output_filename(date)
        return output_file.exists()

    def validate_file_paths(self, agenda_path: str, minutes_path: str) -> Tuple[bool, str]:
        """Validate that input files exist"""
        issues = []

        if not agenda_path or not Path(agenda_path).exists():
            issues.append(f"Agenda file not found: {agenda_path}")

        if not minutes_path or not Path(minutes_path).exists():
            issues.append(f"Minutes file not found: {minutes_path}")

        if issues:
            return False, "; ".join(issues)

        return True, "Files validated"

    def process_single_meeting(self, meeting: Dict[str, str]) -> Dict[str, Any]:
        """Process a single meeting and return results"""
        date = meeting['date']
        agenda_path = meeting['agenda_file']
        minutes_path = meeting['minutes_file']

        result = {
            'date': date,
            'agenda_path': agenda_path,
            'minutes_path': minutes_path,
            'success': False,
            'message': '',
            'output_file': '',
            'quality_score': 0.0,
            'processing_time': 0.0,
            'vote_count': 0,
            'error_details': None
        }

        start_time = datetime.now()

        try:
            # Validate file paths
            files_valid, validation_message = self.validate_file_paths(agenda_path, minutes_path)
            if not files_valid:
                result['message'] = f"File validation failed: {validation_message}"
                logger.warning(f"Skipping {date}: {validation_message}")
                return result

            logger.info(f"Processing meeting for {date}...")

            # Process using factory with Santa Ana AI extractor
            extraction_result = self.factory.process_meeting_documents(
                agenda_path, minutes_path, 'santa_ana'
            )

            if extraction_result.get('success', False):
                # Save results to JSON file
                output_filename = self.get_output_filename(date)
                output_path = self.output_dir / output_filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(extraction_result, f, indent=2, ensure_ascii=False)

                # Update result tracking
                result['success'] = True
                result['output_file'] = str(output_path)
                result['quality_score'] = extraction_result.get('quality_score', 0.0)
                result['vote_count'] = len(extraction_result.get('votes', []))
                result['message'] = f"Successfully processed {result['vote_count']} votes"

                # Track quality score
                if result['quality_score'] > 0:
                    self.stats['quality_scores'].append(result['quality_score'])

                logger.info(f"✓ {date}: {result['message']} (Quality: {result['quality_score']:.2f})")

            else:
                result['message'] = extraction_result.get('message', 'Unknown processing error')
                result['error_details'] = extraction_result
                logger.error(f"✗ {date}: {result['message']}")

        except Exception as e:
            result['message'] = f"Exception during processing: {str(e)}"
            result['error_details'] = str(e)
            logger.error(f"✗ {date}: Exception - {str(e)}")

        finally:
            end_time = datetime.now()
            result['processing_time'] = (end_time - start_time).total_seconds()

        return result

    def process_all_meetings(self) -> Dict[str, Any]:
        """Process all meetings from the CSV file"""
        logger.info("Starting Santa Ana meeting batch processing...")

        # Load meetings from CSV
        meetings = self.load_meetings_from_csv()
        if not meetings:
            return self.generate_summary_report()

        # Filter to only matched meetings
        matched_meetings = [m for m in meetings if m['status'] == 'matched']
        self.stats['matched_meetings'] = len(matched_meetings)

        logger.info(f"Found {len(matched_meetings)} matched meetings to process")

        # Process each meeting
        for i, meeting in enumerate(matched_meetings, 1):
            date = meeting['date']
            logger.info(f"\n--- Processing {i}/{len(matched_meetings)}: {date} ---")

            # Skip if already processed
            if self.is_already_processed(date):
                logger.info(f"Skipping {date}: already processed")
                self.stats['already_processed'] += 1
                continue

            # Process the meeting
            result = self.process_single_meeting(meeting)
            self.results.append(result)

            # Update statistics
            if result['success']:
                self.stats['successfully_processed'] += 1
            else:
                self.stats['failed_processing'] += 1
                self.stats['errors'].append({
                    'date': date,
                    'error': result['message'],
                    'details': result.get('error_details')
                })

        # Complete processing
        self.stats['end_time'] = datetime.now()

        logger.info("\n" + "="*60)
        logger.info("BATCH PROCESSING COMPLETED")
        logger.info("="*60)

        return self.generate_summary_report()

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        processing_time = (
            self.stats['end_time'] - self.stats['start_time']
        ).total_seconds() if self.stats['end_time'] else 0

        # Calculate quality statistics
        quality_stats = {}
        if self.stats['quality_scores']:
            quality_stats = {
                'average_quality': sum(self.stats['quality_scores']) / len(self.stats['quality_scores']),
                'min_quality': min(self.stats['quality_scores']),
                'max_quality': max(self.stats['quality_scores']),
                'quality_count': len(self.stats['quality_scores'])
            }

        report = {
            'batch_processing_summary': {
                'start_time': self.stats['start_time'].isoformat(),
                'end_time': self.stats['end_time'].isoformat() if self.stats['end_time'] else None,
                'total_processing_time_seconds': processing_time,
                'csv_file': self.csv_file,
                'output_directory': str(self.output_dir)
            },
            'meeting_statistics': {
                'total_meetings_in_csv': self.stats['total_meetings'],
                'matched_meetings': self.stats['matched_meetings'],
                'already_processed': self.stats['already_processed'],
                'newly_processed': self.stats['successfully_processed'],
                'failed_processing': self.stats['failed_processing'],
                'processing_rate': (
                    self.stats['successfully_processed'] /
                    max(1, self.stats['matched_meetings'] - self.stats['already_processed'])
                ) * 100 if self.stats['matched_meetings'] > self.stats['already_processed'] else 0
            },
            'quality_statistics': quality_stats,
            'errors_and_failures': self.stats['errors'],
            'detailed_results': self.results,
            'factory_metadata': {
                'extractor_used': 'AIPoweredSantaAnaExtractor',
                'city': 'santa_ana',
                'factory_version': self.factory.version
            }
        }

        # Save detailed report
        report_filename = f"santa_ana_batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.output_dir / report_filename

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        # Print summary to console
        self.print_summary(report)

        logger.info(f"Detailed report saved to: {report_path}")

        return report

    def print_summary(self, report: Dict[str, Any]):
        """Print formatted summary to console"""
        stats = report['meeting_statistics']
        quality = report.get('quality_statistics', {})

        print("\n" + "="*60)
        print("SANTA ANA BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"Total meetings in CSV:     {stats['total_meetings_in_csv']}")
        print(f"Matched meetings:          {stats['matched_meetings']}")
        print(f"Already processed:         {stats['already_processed']}")
        print(f"Newly processed:           {stats['newly_processed']}")
        print(f"Failed processing:         {stats['failed_processing']}")
        print(f"Processing success rate:   {stats['processing_rate']:.1f}%")

        if quality:
            print(f"\nQuality Statistics:")
            print(f"Average quality score:     {quality['average_quality']:.2f}")
            print(f"Quality range:             {quality['min_quality']:.2f} - {quality['max_quality']:.2f}")
            print(f"Meetings with quality:     {quality['quality_count']}")

        if report['errors_and_failures']:
            print(f"\nErrors encountered:        {len(report['errors_and_failures'])}")
            for error in report['errors_and_failures'][:3]:  # Show first 3 errors
                print(f"  - {error['date']}: {error['error']}")
            if len(report['errors_and_failures']) > 3:
                print(f"  ... and {len(report['errors_and_failures']) - 3} more errors")

        print("="*60)

def main():
    """Main execution function"""
    try:
        # Initialize processor
        processor = SantaAnaBatchProcessor()

        # Ensure output directory exists
        processor.output_dir.mkdir(parents=True, exist_ok=True)

        # Process all meetings
        summary = processor.process_all_meetings()

        # Exit with appropriate code
        failed_count = summary['meeting_statistics']['failed_processing']
        if failed_count > 0:
            logger.warning(f"Processing completed with {failed_count} failures")
            sys.exit(1)
        else:
            logger.info("All meetings processed successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error during batch processing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()