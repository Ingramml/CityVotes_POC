#!/usr/bin/env python3
"""
Script to match agenda files with their corresponding minutes files based on naming conventions
and generate a mapping report.
"""

import os
from pathlib import Path
from datetime import datetime
import re
import csv
from typing import Dict, List, Tuple, Optional
import logging

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def extract_date_from_filename(filename: str) -> Optional[datetime]:
    """
    Extract date from filename using various patterns.
    Returns None if no date pattern is found.
    """
    # Common date patterns in filenames
    patterns = [
        r'(\d{4})[-_]?(\d{2})[-_]?(\d{2})',  # YYYY-MM-DD or YYYYMMDD
        r'(\d{2})[-_]?(\d{2})[-_]?(\d{4})',  # MM-DD-YYYY or MMDDYYYY
        r'([A-Za-z]+)\s+(\d{1,2})[,\s]+(\d{4})',  # Month DD, YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            groups = match.groups()
            try:
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    return datetime(int(groups[0]), int(groups[1]), int(groups[2]))
                elif len(groups[0]) == 2:  # MM-DD-YYYY
                    return datetime(int(groups[2]), int(groups[0]), int(groups[1]))
                else:  # Month DD, YYYY
                    month_str = groups[0].capitalize()
                    datetime_str = f"{month_str} {groups[1]} {groups[2]}"
                    return datetime.strptime(datetime_str, "%B %d %Y")
            except (ValueError, TypeError):
                continue
    return None

def find_matching_files(agenda_dir: Path, minutes_dir: Path, logger: logging.Logger) -> Dict[str, dict]:
    """
    Find matching agenda and minutes files based on dates and naming patterns.
    Returns a dictionary of matches with metadata.
    """
    matches = {}
    
    # Get all text files
    agenda_files = list(agenda_dir.glob('*.txt'))
    minutes_files = list(minutes_dir.glob('*.txt'))
    
    logger.info(f"Found {len(agenda_files)} agenda files and {len(minutes_files)} minutes files")
    
    # Create a dictionary of minutes files by date
    minutes_by_date = {}
    for minutes_file in minutes_files:
        date = extract_date_from_filename(minutes_file.name)
        if date:
            minutes_by_date[date] = minutes_file
    
    # Match agenda files with minutes
    for agenda_file in agenda_files:
        date = extract_date_from_filename(agenda_file.name)
        if not date:
            logger.warning(f"Could not extract date from agenda file: {agenda_file.name}")
            continue
            
        matching_minutes = minutes_by_date.get(date)
        
        matches[agenda_file.name] = {
            'agenda_file': str(agenda_file),
            'minutes_file': str(matching_minutes) if matching_minutes else None,
            'date': date.strftime('%Y-%m-%d'),
            'status': 'matched' if matching_minutes else 'unmatched'
        }
    
    return matches

def export_matches(matches: Dict[str, dict], output_path: Path, logger: logging.Logger):
    """Export the matches to a CSV file."""
    fieldnames = ['agenda_file', 'minutes_file', 'date', 'status']
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for match_data in matches.values():
            writer.writerow(match_data)
    
    logger.info(f"Exported matches to {output_path}")

def generate_summary(matches: Dict[str, dict], logger: logging.Logger):
    """Generate and log a summary of the matching results."""
    total = len(matches)
    matched = sum(1 for m in matches.values() if m['status'] == 'matched')
    unmatched = total - matched
    
    logger.info("=== Matching Summary ===")
    logger.info(f"Total agenda files: {total}")
    logger.info(f"Matched files: {matched}")
    logger.info(f"Unmatched files: {unmatched}")
    logger.info(f"Match rate: {(matched/total)*100:.1f}%")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Match agenda files with corresponding minutes files.')
    parser.add_argument('agenda_dir', type=str, help='Directory containing agenda text files')
    parser.add_argument('minutes_dir', type=str, help='Directory containing minutes text files')
    parser.add_argument('--output', type=str, default='mapping_report.csv',
                      help='Output CSV file path (default: mapping_report.csv)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    logger = setup_logging(args.verbose)
    
    agenda_dir = Path(args.agenda_dir)
    minutes_dir = Path(args.minutes_dir)
    output_path = Path(args.output)
    
    if not agenda_dir.exists() or not minutes_dir.exists():
        logger.error("One or both input directories do not exist!")
        return 1
    
    try:
        # Find matching files
        matches = find_matching_files(agenda_dir, minutes_dir, logger)
        
        # Generate summary
        generate_summary(matches, logger)
        
        # Export results
        export_matches(matches, output_path, logger)
        
        return 0
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return 1

if __name__ == '__main__':
    exit(main())