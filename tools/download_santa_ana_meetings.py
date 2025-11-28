#!/usr/bin/env python3
"""
Santa Ana City Council Meeting Downloader
Downloads agendas and minutes from PrimeGov portal and organizes them by year

Usage:
    python3 download_santa_ana_meetings.py --output-dir "/Volumes/Samsung USB/City_extraction/Santa_Ana"
    python3 download_santa_ana_meetings.py --years 2024 2023 --types agenda minutes
"""

import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class SantaAnaMeetingDownloader:
    """Download meetings from Santa Ana PrimeGov portal"""

    BASE_URL = "https://santa-ana.primegov.com"
    PORTAL_URL = f"{BASE_URL}/public/portal"

    # Allowed meeting types
    ALLOWED_MEETING_TYPES = [
        "Regular City Council Meeting",
        "Regular City Council and Special Housing Authority Meeting",
        "Special City Council Meeting"
    ]

    def __init__(self, output_dir, delay=2.0, dry_run=False, meeting_types=None):
        """
        Initialize downloader

        Args:
            output_dir: Base directory for downloaded files
            delay: Delay between requests (seconds)
            dry_run: If True, show what would be downloaded without downloading
            meeting_types: List of meeting types to include (None = use defaults)
        """
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.dry_run = dry_run
        self.meeting_types = meeting_types or self.ALLOWED_MEETING_TYPES
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        # Statistics
        self.stats = {
            'meetings_found': 0,
            'meetings_filtered': 0,
            'agendas_downloaded': 0,
            'minutes_downloaded': 0,
            'errors': 0,
            'skipped': 0
        }

    def get_csrf_token(self):
        """Get CSRF token from portal page"""
        try:
            response = self.session.get(self.PORTAL_URL)
            response.raise_for_status()

            # Look for CSRF token in page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check for meta tag
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                return csrf_meta.get('content')

            # Check in script tags
            for script in soup.find_all('script'):
                if script.string and 'csrfToken' in script.string:
                    match = re.search(r'csrfToken["\']?\s*[:=]\s*["\']([^"\']+)', script.string)
                    if match:
                        return match.group(1)

            return None

        except Exception as e:
            print(f"⚠️  Error getting CSRF token: {e}")
            return None

    def get_meetings_list(self, year=None):
        """
        Get list of meetings from portal

        Args:
            year: Filter by specific year (optional)

        Returns:
            list: Meeting data dictionaries
        """
        meetings = []

        try:
            # Try to get meetings via API
            api_url = f"{self.BASE_URL}/api/meetings"

            params = {
                'status': 'Published',
                'includeDocuments': True
            }

            if year:
                params['year'] = year

            print(f"  🔍 Fetching meetings list...")
            response = self.session.get(api_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                # Handle different response formats
                if isinstance(data, list):
                    meetings = data
                elif isinstance(data, dict) and 'meetings' in data:
                    meetings = data['meetings']
                elif isinstance(data, dict) and 'data' in data:
                    meetings = data['data']

                print(f"     Found {len(meetings)} meetings")
            else:
                print(f"     API returned status {response.status_code}")

        except Exception as e:
            print(f"  ⚠️  Error fetching meetings: {e}")
            print(f"     Will try alternate method...")

            # Fallback: scrape the portal page
            meetings = self._scrape_portal_page(year=year)

        return meetings

    def _scrape_portal_page(self, year=None):
        """Scrape meetings from portal page (fallback method)"""
        meetings = []

        try:
            response = self.session.get(self.PORTAL_URL, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the meeting table rows
            table_rows = soup.find_all('tr', {'role': 'row'})

            for row in table_rows:
                # Skip header rows
                if not row.find('td', class_='meeting-title'):
                    continue

                # Extract meeting title
                title_cell = row.find('td', class_='meeting-title')
                if not title_cell:
                    continue

                meeting_title = title_cell.get('title', title_cell.get_text(strip=True))

                # Extract meeting date
                date_cell = row.find_all('td')[1] if len(row.find_all('td')) > 1 else None
                if not date_cell:
                    continue

                date_text = date_cell.get_text(strip=True)

                # Parse date: "May 07, 2024 04:00 PM"
                try:
                    date_obj = datetime.strptime(date_text, '%B %d, %Y %I:%M %p')
                    meeting_date = date_obj.strftime('%Y-%m-%d')
                except:
                    # Try alternate format
                    try:
                        date_obj = datetime.strptime(date_text.split()[0:3], '%B %d, %Y')
                        meeting_date = date_obj.strftime('%Y-%m-%d')
                    except:
                        continue

                # Filter by year if specified
                if year and date_obj.year != year:
                    continue

                # Find document links
                doc_container = row.find('div', class_='docContainer')
                if not doc_container:
                    continue

                documents = {}

                # Extract agenda and minutes links
                for link in doc_container.find_all('a'):
                    href = link.get('href', '')
                    text = link.get_text(strip=True).lower()

                    if not href or 'CompiledDocument' not in href:
                        continue

                    # Classify document type
                    if 'minutes' in text:
                        documents['minutes'] = urljoin(self.BASE_URL, href)
                    elif 'agenda' in text and 'packet' not in text:
                        documents['agenda'] = urljoin(self.BASE_URL, href)

                # Create meeting data
                meeting_data = {
                    'title': meeting_title,
                    'date': meeting_date,
                    'documents': documents
                }

                meetings.append(meeting_data)

            print(f"     Scraped {len(meetings)} meetings from portal")

        except Exception as e:
            print(f"  ⚠️  Error scraping portal: {e}")
            import traceback
            traceback.print_exc()

        return meetings

    def get_meeting_documents(self, meeting):
        """
        Get documents (agenda, minutes) for a specific meeting

        Args:
            meeting: Meeting data dict

        Returns:
            dict: Documents with 'agenda' and 'minutes' keys
        """
        # Check if documents are already in meeting data (from scraping)
        if 'documents' in meeting:
            return meeting['documents']

        # Fallback: try to fetch from meeting page
        documents = {
            'agenda': None,
            'minutes': None
        }

        try:
            meeting_id = meeting.get('id')
            if not meeting_id:
                return documents

            meeting_url = meeting.get('url') or f"{self.BASE_URL}/meeting/{meeting_id}"

            print(f"     Checking meeting {meeting_id}...")
            response = self.session.get(meeting_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for document links
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True).lower()

                # Check if it's a PDF
                if not href.endswith('.pdf'):
                    continue

                full_url = urljoin(self.BASE_URL, href)

                # Classify document type
                if 'agenda' in text or 'agenda' in href.lower():
                    documents['agenda'] = full_url
                elif 'minutes' in text or 'minutes' in href.lower():
                    documents['minutes'] = full_url

        except Exception as e:
            print(f"     ⚠️  Error getting documents: {e}")

        return documents

    def download_file(self, url, output_path):
        """
        Download a file from URL to local path

        Args:
            url: URL to download
            output_path: Local file path

        Returns:
            bool: Success status
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = output_path.stat().st_size
            print(f"        ✅ Downloaded: {file_size:,} bytes")
            return True

        except Exception as e:
            print(f"        ❌ Error: {e}")
            return False

    def generate_filename(self, meeting, doc_type):
        """
        Generate filename in format: YYYYMMDD_type_meeting-name.pdf

        Args:
            meeting: Meeting data dict
            doc_type: 'agenda' or 'minutes'

        Returns:
            str: Formatted filename
        """
        # Extract date
        date_str = meeting.get('date', '')
        if not date_str:
            # Try to parse from title
            title = meeting.get('title', '')
            date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', title)
            if date_match:
                month, day, year = date_match.groups()
                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            else:
                date_str = datetime.now().strftime('%Y-%m-%d')

        # Format: YYYYMMDD
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_prefix = date_obj.strftime('%Y%m%d')

        # Generate meeting name slug
        title = meeting.get('title', 'city_council_meeting')
        title = re.sub(r'[^\w\s-]', '', title.lower())
        title = re.sub(r'[-\s]+', '_', title)
        title = title[:60]  # Limit length

        # Format: YYYYMMDD_type_meeting-name.pdf
        filename = f"{date_prefix}_{doc_type}_{title}.pdf"

        return filename

    def process_meeting(self, meeting, doc_types=['agenda', 'minutes']):
        """
        Process a single meeting - download requested document types

        Args:
            meeting: Meeting data dict
            doc_types: List of document types to download

        Returns:
            dict: Download results
        """
        results = {
            'meeting_date': meeting.get('date'),
            'downloads': {}
        }

        # Get meeting year for folder organization
        date_str = meeting.get('date', '')
        if date_str:
            year = datetime.strptime(date_str, '%Y-%m-%d').year
        else:
            year = datetime.now().year

        # Get documents (either from meeting data or fetch them)
        documents = self.get_meeting_documents(meeting)

        # Download each requested type
        for doc_type in doc_types:
            url = documents.get(doc_type)

            if not url:
                print(f"     ⏭️  No {doc_type} found")
                results['downloads'][doc_type] = 'not_found'
                continue

            # Generate filename and path
            filename = self.generate_filename(meeting, doc_type)
            output_path = self.output_dir / str(year) / "PDFs" / doc_type / filename

            # Check if already exists
            if output_path.exists():
                print(f"     ⏭️  Skipped {doc_type}: already exists")
                results['downloads'][doc_type] = 'skipped'
                self.stats['skipped'] += 1
                continue

            print(f"     📥 Downloading {doc_type}...")
            print(f"        URL: {url}")
            print(f"        File: {filename}")

            if self.dry_run:
                print(f"        [DRY RUN] Would download to: {output_path}")
                results['downloads'][doc_type] = 'dry_run'
            else:
                success = self.download_file(url, output_path)

                if success:
                    results['downloads'][doc_type] = 'success'

                    if doc_type == 'agenda':
                        self.stats['agendas_downloaded'] += 1
                    elif doc_type == 'minutes':
                        self.stats['minutes_downloaded'] += 1
                else:
                    results['downloads'][doc_type] = 'error'
                    self.stats['errors'] += 1

            # Delay between downloads
            time.sleep(self.delay)

        return results

    def is_allowed_meeting_type(self, meeting_title):
        """
        Check if meeting type is in allowed list

        Args:
            meeting_title: Meeting title string

        Returns:
            bool: True if meeting type is allowed
        """
        title_lower = meeting_title.lower()

        for allowed_type in self.meeting_types:
            # Check for exact match or substring match
            if allowed_type.lower() in title_lower:
                return True

        return False

    def download_all(self, years=None, doc_types=['agenda', 'minutes']):
        """
        Download all available meetings

        Args:
            years: List of years to download (None = all)
            doc_types: List of document types to download
        """
        print(f"\n📥 Santa Ana Meeting Downloader")
        print(f"{'='*60}")
        print(f"Output directory: {self.output_dir}")
        print(f"Document types: {', '.join(doc_types)}")
        print(f"Years: {years or 'All available'}")
        print(f"Meeting types filter:")
        for mt in self.meeting_types:
            print(f"  - {mt}")
        print(f"Dry run: {self.dry_run}\n")

        # Get CSRF token if needed
        csrf_token = self.get_csrf_token()
        if csrf_token:
            self.session.headers['X-CSRF-Token'] = csrf_token
            print(f"✅ CSRF token obtained\n")

        # Process each year
        if years:
            all_meetings = []
            for year in years:
                print(f"\n📅 Fetching {year} meetings...")
                meetings = self.get_meetings_list(year=year)
                all_meetings.extend(meetings)
        else:
            print(f"\n📅 Fetching all meetings...")
            all_meetings = self.get_meetings_list()

        self.stats['meetings_found'] = len(all_meetings)

        if not all_meetings:
            print("\n⚠️  No meetings found!")
            return

        # Filter by meeting type
        filtered_meetings = []
        for meeting in all_meetings:
            title = meeting.get('title', '')
            if self.is_allowed_meeting_type(title):
                filtered_meetings.append(meeting)
            else:
                self.stats['meetings_filtered'] += 1

        print(f"\n✅ Found {len(all_meetings)} total meetings")
        print(f"✅ Filtered to {len(filtered_meetings)} matching meeting types")
        print(f"⏭️  Skipped {self.stats['meetings_filtered']} non-matching meetings\n")

        if not filtered_meetings:
            print("\n⚠️  No meetings matched the meeting type filter!")
            return

        print(f"\n🔄 Processing {len(filtered_meetings)} meetings...\n")

        # Process each meeting
        for i, meeting in enumerate(filtered_meetings, 1):
            title = meeting.get('title', 'Unknown')
            date = meeting.get('date', 'Unknown date')

            print(f"\n[{i}/{len(filtered_meetings)}] {date}: {title}")

            result = self.process_meeting(meeting, doc_types=doc_types)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print download statistics"""
        print(f"\n{'='*60}")
        print(f"📊 Download Summary")
        print(f"{'='*60}")
        print(f"Meetings found: {self.stats['meetings_found']}")
        print(f"Meetings filtered out: {self.stats['meetings_filtered']}")
        print(f"Meetings processed: {self.stats['meetings_found'] - self.stats['meetings_filtered']}")
        print(f"Agendas downloaded: {self.stats['agendas_downloaded']}")
        print(f"Minutes downloaded: {self.stats['minutes_downloaded']}")
        print(f"Skipped (already exist): {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"\n✅ Complete!\n")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Download Santa Ana city council meetings from PrimeGov portal'
    )

    parser.add_argument(
        '--output-dir',
        default='/Volumes/Samsung USB/City_extraction/Santa_Ana',
        help='Base directory for downloaded files'
    )

    parser.add_argument(
        '--years',
        nargs='+',
        type=int,
        help='Specific years to download (e.g., 2024 2023)'
    )

    parser.add_argument(
        '--types',
        nargs='+',
        choices=['agenda', 'minutes'],
        default=['agenda', 'minutes'],
        help='Document types to download'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between downloads in seconds (default: 2.0)'
    )

    parser.add_argument(
        '--meeting-types',
        nargs='+',
        help='Specific meeting types to include (default: Regular/Special City Council)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be downloaded without actually downloading'
    )

    args = parser.parse_args()

    # Check if output directory exists (if not dry run)
    if not args.dry_run:
        output_path = Path(args.output_dir)
        if not output_path.exists():
            print(f"⚠️  Warning: Output directory does not exist: {output_path}")
            response = input("Create it? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
            output_path.mkdir(parents=True, exist_ok=True)

    # Create downloader and run
    downloader = SantaAnaMeetingDownloader(
        output_dir=args.output_dir,
        delay=args.delay,
        dry_run=args.dry_run,
        meeting_types=args.meeting_types
    )

    downloader.download_all(years=args.years, doc_types=args.types)


if __name__ == '__main__':
    main()
