#!/usr/bin/env python3
"""
Santa Ana Processing Results Analyzer

This script analyzes all processed Santa Ana meeting files and generates
a comprehensive summary report including quality metrics, vote extraction
statistics, and processing effectiveness.
"""

import json
import glob
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

def load_csv_mapping() -> Dict[str, Dict]:
    """Load the original CSV mapping for reference"""
    mapping = {}
    try:
        with open('santa_ana_mapping_report.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row['date'].strip()
                mapping[date] = {
                    'agenda_file': row['agenda_file'].strip(),
                    'minutes_file': row['minutes_file'].strip(),
                    'status': row['status'].strip()
                }
    except Exception as e:
        print(f"Warning: Could not load CSV mapping: {e}")

    return mapping

def analyze_processed_files() -> Dict[str, Any]:
    """Analyze all processed Santa Ana vote files"""

    # Find all processed files in the correct directory
    votes_dir = '/Users/michaelingram/Documents/GitHub/CityVotes_POC/CA/Santa_ANA/votes'
    files = glob.glob(f'{votes_dir}/santa_ana_votes_*.json')
    print(f"Found {len(files)} processed Santa Ana files")

    # Load CSV mapping for reference
    csv_mapping = load_csv_mapping()

    # Initialize analysis data
    analysis = {
        'summary': {
            'total_files_processed': len(files),
            'total_votes_extracted': 0,
            'meetings_with_votes': 0,
            'meetings_without_votes': 0,
            'average_quality_score': 0.0,
            'date_range': {'earliest': None, 'latest': None},
            'processing_methods': defaultdict(int),
            'extractor_versions': defaultdict(int)
        },
        'detailed_results': [],
        'quality_analysis': {
            'high_quality_meetings': [],  # quality >= 0.8
            'medium_quality_meetings': [],  # 0.5 <= quality < 0.8
            'low_quality_meetings': [],  # 0 < quality < 0.5
            'no_votes_meetings': []  # quality = 0 (no votes found)
        },
        'error_analysis': {
            'processing_errors': [],
            'validation_failures': [],
            'file_access_issues': []
        },
        'temporal_analysis': {
            'by_year': defaultdict(lambda: {'meetings': 0, 'votes': 0, 'avg_quality': 0.0}),
            'by_month': defaultdict(lambda: {'meetings': 0, 'votes': 0, 'avg_quality': 0.0})
        }
    }

    quality_scores = []
    dates = []

    # Process each file
    for file_path in sorted(files):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Extract basic information
            votes = data.get('votes', [])
            vote_count = len(votes)
            quality_score = data.get('validation_results', {}).get('quality_score', 0.0)
            meeting_date = data.get('batch_metadata', {}).get('meeting_date',
                          data.get('factory_metadata', {}).get('meeting_date', 'Unknown'))

            # Handle file naming extraction if date not in metadata
            if meeting_date == 'Unknown':
                filename = Path(file_path).stem
                if 'santa_ana_votes_' in filename:
                    meeting_date = filename.replace('santa_ana_votes_', '')

            success = data.get('success', False)
            method_used = data.get('extraction_metadata', {}).get('method_used', 'unknown')
            extractor_version = data.get('extraction_metadata', {}).get('agent_version', 'unknown')

            # Update summary statistics
            analysis['summary']['total_votes_extracted'] += vote_count
            if vote_count > 0:
                analysis['summary']['meetings_with_votes'] += 1
            else:
                analysis['summary']['meetings_without_votes'] += 1

            analysis['summary']['processing_methods'][method_used] += 1
            analysis['summary']['extractor_versions'][extractor_version] += 1

            # Track quality scores and dates
            if quality_score > 0:
                quality_scores.append(quality_score)
            if meeting_date != 'Unknown':
                dates.append(meeting_date)

            # Detailed result record
            result_record = {
                'file': file_path,
                'meeting_date': meeting_date,
                'vote_count': vote_count,
                'quality_score': quality_score,
                'success': success,
                'method_used': method_used,
                'extractor_version': extractor_version,
                'agenda_file': data.get('factory_metadata', {}).get('document_sources', {}).get('agenda_file', 'Unknown'),
                'minutes_file': data.get('factory_metadata', {}).get('document_sources', {}).get('minutes_file', 'Unknown'),
                'processing_notes': data.get('validation_results', {}).get('processing_notes', [])
            }
            analysis['detailed_results'].append(result_record)

            # Quality categorization
            if quality_score >= 0.8:
                analysis['quality_analysis']['high_quality_meetings'].append(result_record)
            elif quality_score >= 0.5:
                analysis['quality_analysis']['medium_quality_meetings'].append(result_record)
            elif quality_score > 0:
                analysis['quality_analysis']['low_quality_meetings'].append(result_record)
            else:
                analysis['quality_analysis']['no_votes_meetings'].append(result_record)

            # Temporal analysis
            if meeting_date != 'Unknown' and len(meeting_date) >= 4:
                try:
                    year = meeting_date[:4]
                    month = meeting_date[:7]  # YYYY-MM

                    analysis['temporal_analysis']['by_year'][year]['meetings'] += 1
                    analysis['temporal_analysis']['by_year'][year]['votes'] += vote_count
                    if quality_score > 0:
                        analysis['temporal_analysis']['by_year'][year]['avg_quality'] += quality_score

                    analysis['temporal_analysis']['by_month'][month]['meetings'] += 1
                    analysis['temporal_analysis']['by_month'][month]['votes'] += vote_count
                    if quality_score > 0:
                        analysis['temporal_analysis']['by_month'][month]['avg_quality'] += quality_score

                except:
                    pass

            # Error analysis
            if not success:
                analysis['error_analysis']['processing_errors'].append({
                    'date': meeting_date,
                    'file': file_path,
                    'message': data.get('message', 'Unknown error')
                })

            validation_passed = data.get('validation_results', {}).get('validation_passed', True)
            if not validation_passed:
                analysis['error_analysis']['validation_failures'].append(result_record)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            analysis['error_analysis']['file_access_issues'].append({
                'file': file_path,
                'error': str(e)
            })

    # Calculate final statistics
    if quality_scores:
        analysis['summary']['average_quality_score'] = sum(quality_scores) / len(quality_scores)

    if dates:
        analysis['summary']['date_range']['earliest'] = min(dates)
        analysis['summary']['date_range']['latest'] = max(dates)

    # Convert defaultdicts to regular dicts for JSON serialization
    analysis['summary']['processing_methods'] = dict(analysis['summary']['processing_methods'])
    analysis['summary']['extractor_versions'] = dict(analysis['summary']['extractor_versions'])
    analysis['temporal_analysis']['by_year'] = dict(analysis['temporal_analysis']['by_year'])
    analysis['temporal_analysis']['by_month'] = dict(analysis['temporal_analysis']['by_month'])

    return analysis

def print_analysis_summary(analysis: Dict[str, Any]):
    """Print formatted analysis summary"""
    summary = analysis['summary']
    quality = analysis['quality_analysis']

    print("\n" + "="*80)
    print("SANTA ANA PROCESSING RESULTS ANALYSIS")
    print("="*80)

    print(f"\nOVERALL STATISTICS:")
    print(f"  Total files processed:        {summary['total_files_processed']}")
    print(f"  Total votes extracted:        {summary['total_votes_extracted']}")
    print(f"  Meetings with votes:          {summary['meetings_with_votes']}")
    print(f"  Meetings without votes:       {summary['meetings_without_votes']}")
    print(f"  Average quality score:        {summary['average_quality_score']:.3f}")

    if summary['date_range']['earliest']:
        print(f"  Date range:                   {summary['date_range']['earliest']} to {summary['date_range']['latest']}")

    print(f"\nQUALITY BREAKDOWN:")
    print(f"  High quality (≥0.8):          {len(quality['high_quality_meetings'])}")
    print(f"  Medium quality (0.5-0.8):     {len(quality['medium_quality_meetings'])}")
    print(f"  Low quality (0-0.5):          {len(quality['low_quality_meetings'])}")
    print(f"  No votes found:               {len(quality['no_votes_meetings'])}")

    print(f"\nPROCESSING METHODS:")
    for method, count in summary['processing_methods'].items():
        print(f"  {method}:                      {count}")

    print(f"\nEXTRACTOR VERSIONS:")
    for version, count in summary['extractor_versions'].items():
        print(f"  {version}:                     {count}")

    # Show meetings with votes
    if quality['high_quality_meetings'] or quality['medium_quality_meetings']:
        print(f"\nMEETINGS WITH SUCCESSFUL VOTE EXTRACTION:")
        successful_meetings = quality['high_quality_meetings'] + quality['medium_quality_meetings']
        for meeting in successful_meetings:
            print(f"  {meeting['meeting_date']}: {meeting['vote_count']} votes (quality: {meeting['quality_score']:.2f})")

    # Show temporal distribution
    print(f"\nTEMPORAL DISTRIBUTION BY YEAR:")
    for year, stats in sorted(analysis['temporal_analysis']['by_year'].items()):
        avg_qual = stats['avg_quality'] / max(1, stats['meetings']) if stats['avg_quality'] > 0 else 0
        print(f"  {year}: {stats['meetings']} meetings, {stats['votes']} votes, avg quality: {avg_qual:.2f}")

    print("="*80)

def main():
    """Main analysis function"""
    print("Starting Santa Ana processing results analysis...")

    # Perform analysis
    analysis = analyze_processed_files()

    # Print summary
    print_analysis_summary(analysis)

    # Save detailed analysis report in the correct directory
    votes_dir = '/Users/michaelingram/Documents/GitHub/CityVotes_POC/CA/Santa_ANA/votes'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"{votes_dir}/santa_ana_analysis_report_{timestamp}.json"

    with open(report_filename, 'w') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nDetailed analysis report saved to: {report_filename}")

    # Also create a CSV summary for easy viewing
    csv_filename = f"{votes_dir}/santa_ana_summary_{timestamp}.csv"
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Meeting Date', 'Vote Count', 'Quality Score', 'Method Used', 'Extractor Version', 'Success'])

        for result in analysis['detailed_results']:
            writer.writerow([
                result['meeting_date'],
                result['vote_count'],
                result['quality_score'],
                result['method_used'],
                result['extractor_version'],
                result['success']
            ])

    print(f"CSV summary saved to: {csv_filename}")

if __name__ == "__main__":
    main()