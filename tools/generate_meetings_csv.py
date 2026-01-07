#!/usr/bin/env python3
"""
Generate meetings CSV with PrimeGov URLs for agenda, minutes, and video.

This script fetches meeting data from Santa Ana's PrimeGov portal and generates
a CSV file with URLs that can be imported into the meetings table.

Usage:
    python3 tools/generate_meetings_csv.py --year 2024
    python3 tools/generate_meetings_csv.py --year 2024 --output meetings_2024.csv
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path

import requests


class PrimeGovMeetingsFetcher:
    """Fetch meeting URLs from Santa Ana PrimeGov portal"""

    BASE_URL = "https://santa-ana.primegov.com"
    API_URL = f"{BASE_URL}/api/v2/PublicPortal/ListArchivedMeetings"
    PORTAL_URL = f"{BASE_URL}/public/portal"

    ALLOWED_MEETING_TYPES = [
        "Regular City Council Meeting",
        "Regular City Council and Special Housing Authority Meeting",
        "Special City Council Meeting"
    ]

    def __init__(self, delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_meetings_api(self, year):
        """Fetch meetings list from API to get video URLs and document URLs"""
        print(f"Fetching meetings from API for year {year}...")

        try:
            response = self.session.get(f"{self.API_URL}?year={year}", timeout=30)
            response.raise_for_status()
            data = response.json()

            meetings_by_date = {}
            for meeting in data:
                title = meeting.get('title', '')
                if not self._is_allowed_meeting_type(title):
                    continue

                # Parse date
                date_str = meeting.get('dateTime', '')
                if date_str:
                    # Format: "2024-01-16T16:00:00"
                    try:
                        dt = datetime.fromisoformat(date_str.replace('Z', ''))
                        meeting_date = dt.strftime('%Y-%m-%d')
                    except:
                        continue
                else:
                    continue

                video_url = meeting.get('videoUrl', '')
                meeting_id = meeting.get('id', '')

                # Extract document URLs from documentList
                agenda_url = None
                minutes_url = None

                # API uses 'documentList' field
                doc_list = meeting.get('documentList', [])
                for doc in doc_list:
                    doc_id = doc.get('id')
                    template_name = doc.get('templateName', '').lower()

                    if not doc_id:
                        continue

                    # Build the CompiledDocument URL
                    doc_url = f"{self.BASE_URL}/Public/CompiledDocument/{doc_id}"

                    if 'minute' in template_name:
                        minutes_url = doc_url
                    elif 'agenda' in template_name and 'packet' not in template_name:
                        agenda_url = doc_url

                meetings_by_date[meeting_date] = {
                    'id': meeting_id,
                    'title': title,
                    'date': meeting_date,
                    'video_url': video_url if video_url else None,
                    'portal_url': f"{self.PORTAL_URL}#meetingId={meeting_id}" if meeting_id else None,
                    'agenda_url': agenda_url,
                    'minutes_url': minutes_url
                }

            print(f"  Found {len(meetings_by_date)} City Council meetings from API")
            return meetings_by_date

        except Exception as e:
            print(f"  Error fetching from API: {e}")
            return {}

    def _is_allowed_meeting_type(self, title):
        """Check if meeting type is in allowed list"""
        title_lower = title.lower()
        for allowed in self.ALLOWED_MEETING_TYPES:
            if allowed.lower() in title_lower:
                return True
        return False

    def generate_csv(self, year, output_path):
        """Generate CSV with meeting URLs"""

        # Fetch data from API (includes both meeting info and documents)
        meetings = self.fetch_meetings_api(year)

        if not meetings:
            print("No meetings found!")
            return False

        # Build rows - match meetings table schema exactly
        # Schema: city_id, meeting_date, meeting_type, agenda_url, minutes_url, video_url
        rows = []
        for date, meeting_data in sorted(meetings.items()):
            # Determine meeting type
            title = meeting_data.get('title', '')
            if 'special' in title.lower():
                meeting_type = 'special'
            else:
                meeting_type = 'regular'

            # Skip cancelled meetings (no data to import)
            if 'cancel' in title.lower():
                continue

            row = {
                'city_id': 1,  # Santa Ana city_id (set after cities table is populated)
                'meeting_date': date,
                'meeting_type': meeting_type,
                'agenda_url': meeting_data.get('agenda_url', '') or '',
                'minutes_url': meeting_data.get('minutes_url', '') or '',
                'video_url': meeting_data.get('video_url', '') or '',
            }
            rows.append(row)

        # Write CSV - columns match meetings table for direct import
        fieldnames = ['city_id', 'meeting_date', 'meeting_type', 'agenda_url', 'minutes_url', 'video_url']

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"\nGenerated CSV with {len(rows)} meetings: {output_path}")

        # Print summary
        agenda_count = sum(1 for r in rows if r['agenda_url'])
        minutes_count = sum(1 for r in rows if r['minutes_url'])
        video_count = sum(1 for r in rows if r['video_url'])

        print(f"\nURL Summary:")
        print(f"  Meetings: {len(rows)}")
        print(f"  With agenda URL: {agenda_count}")
        print(f"  With minutes URL: {minutes_count}")
        print(f"  With video URL: {video_count}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description='Generate meetings CSV with PrimeGov URLs'
    )
    parser.add_argument(
        '--year',
        type=int,
        required=True,
        help='Year to fetch meetings for'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV file path (default: extractors/santa_ana/{year}/meetings_{year}.csv)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between requests in seconds'
    )

    args = parser.parse_args()

    # Default output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"extractors/santa_ana/{args.year}/meetings_{args.year}.csv")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Fetch and generate
    fetcher = PrimeGovMeetingsFetcher(delay=args.delay)
    fetcher.generate_csv(args.year, output_path)


if __name__ == '__main__':
    main()
