#!/usr/bin/env python3
"""
Santa Ana Meeting Downloader using Selenium
Downloads agendas and minutes from PrimeGov portal using browser automation

Requires: pip install selenium
Optional: brew install chromedriver (or use Firefox/Safari)

Usage:
    python3 download_santa_ana_selenium.py --year 2024 --output "/Volumes/Samsung USB/City_extraction/Santa_Ana"
    python3 download_santa_ana_selenium.py --years 2024 2023 --types minutes  # Minutes only
    python3 download_santa_ana_selenium.py --year 2024 --dry-run  # Test first
"""

import argparse
import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class SantAnaSeleniumDownloader:
    """Download Santa Ana meetings using Selenium browser automation"""

    PORTAL_URL = "https://santa-ana.primegov.com/public/portal"

    # Allowed meeting types
    ALLOWED_MEETING_TYPES = [
        "Regular City Council Meeting",
        "Regular City Council and Special Housing Authority Meeting",
        "Special City Council Meeting"
    ]

    def __init__(self, output_dir, download_dir=None, dry_run=False, headless=True, debug=False):
        """
        Initialize downloader

        Args:
            output_dir: Base directory for organized files
            download_dir: Temporary download directory (default: ~/Downloads)
            dry_run: If True, show what would be downloaded
            headless: If True, run browser in headless mode
            debug: If True, print detailed debug information
        """
        self.output_dir = Path(output_dir)
        self.download_dir = Path(download_dir or Path.home() / "Downloads")
        self.dry_run = dry_run
        self.headless = headless
        self.debug = debug

        self.driver = None

        # Statistics - overall and per-year
        self.stats = {
            'meetings_found': 0,
            'meetings_filtered': 0,
            'agendas_downloaded': 0,
            'minutes_downloaded': 0,
            'errors': 0,
            'skipped': 0
        }

        # Detailed tracking per year
        self.year_stats = {}
        self.downloaded_files = []  # List of downloaded files with details

    def setup_driver(self):
        """Setup Selenium WebDriver"""
        try:
            # Try Chrome first
            options = webdriver.ChromeOptions()

            if self.headless:
                options.add_argument('--headless')

            # Set download directory
            prefs = {
                'download.default_directory': str(self.download_dir),
                'download.prompt_for_download': False,
                'plugins.always_open_pdf_externally': True
            }
            options.add_experimental_option('prefs', prefs)

            self.driver = webdriver.Chrome(options=options)
            print(f"✅ Using Chrome WebDriver")

        except Exception as chrome_error:
            print(f"⚠️  Chrome not available: {chrome_error}")

            try:
                # Try Firefox as fallback
                options = webdriver.FirefoxOptions()

                if self.headless:
                    options.add_argument('--headless')

                # Set download directory
                options.set_preference('browser.download.folderList', 2)
                options.set_preference('browser.download.dir', str(self.download_dir))
                options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf')

                self.driver = webdriver.Firefox(options=options)
                print(f"✅ Using Firefox WebDriver")

            except Exception as firefox_error:
                print(f"❌ Firefox not available: {firefox_error}")
                raise Exception("No WebDriver available. Install Chrome or Firefox driver.")

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()

    def is_allowed_meeting_type(self, meeting_title):
        """Check if meeting type is allowed"""
        title_lower = meeting_title.lower()

        for allowed_type in self.ALLOWED_MEETING_TYPES:
            if allowed_type.lower() in title_lower:
                return True

        return False

    def navigate_to_year(self, year):
        """Navigate to specific year tab"""
        try:
            # Find and click year tab
            year_tabs = self.driver.find_elements(By.CSS_SELECTOR, '.changeArchivedYear')

            for tab in year_tabs:
                if tab.get_attribute('data-year') == str(year):
                    tab.click()
                    print(f"  📅 Navigated to year {year}")

                    # Wait for table to load
                    time.sleep(3)
                    return True

            print(f"  ⚠️  Year {year} not found in tabs")
            return False

        except Exception as e:
            print(f"  ❌ Error navigating to year: {e}")
            return False

    def get_meetings_from_page(self):
        """Extract meetings from current page"""
        meetings = []

        try:
            # Wait for table to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'tr[role="row"]'))
            )

            # Find all meeting rows
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'tr[role="row"]')

            for row in rows:
                try:
                    # Extract meeting title
                    title_cell = row.find_element(By.CSS_SELECTOR, 'td.meeting-title')
                    meeting_title = title_cell.get_attribute('title') or title_cell.text

                    if not meeting_title:
                        if self.debug:
                            print(f"        DEBUG: Skipping row - no meeting title")
                        continue

                    if self.debug:
                        print(f"        DEBUG: Found meeting title: {meeting_title[:60]}")

                    # Extract date
                    date_cells = row.find_elements(By.TAG_NAME, 'td')
                    if len(date_cells) < 2:
                        if self.debug:
                            print(f"        DEBUG: Skipping - insufficient date cells")
                        continue

                    date_text = date_cells[1].text.strip()

                    if self.debug:
                        print(f"        DEBUG: Date text: {date_text}")

                    # Parse date: "May 07, 2024 04:00 PM" or "Nov 24, 2025 05:30 PM"
                    try:
                        # Try full month name first
                        date_obj = datetime.strptime(date_text, '%B %d, %Y %I:%M %p')
                        meeting_date = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try abbreviated month name
                            date_obj = datetime.strptime(date_text, '%b %d, %Y %I:%M %p')
                            meeting_date = date_obj.strftime('%Y-%m-%d')
                        except Exception as e:
                            if self.debug:
                                print(f"        DEBUG: Date parse failed: {e}")
                            continue

                    # Find document links
                    doc_container = row.find_element(By.CSS_SELECTOR, 'div.docContainer')
                    links = doc_container.find_elements(By.TAG_NAME, 'a')

                    documents = {}

                    if self.debug:
                        print(f"        DEBUG: Found {len(links)} links in docContainer")

                    for link in links:
                        href = link.get_attribute('href')
                        # Get text - try multiple methods since it might be after icon element
                        text = link.text.strip().lower()

                        # If text is empty, try getting textContent via JavaScript
                        if not text:
                            try:
                                text = self.driver.execute_script("return arguments[0].textContent;", link).strip().lower()
                            except:
                                pass

                        class_name = link.get_attribute('class') or ''

                        if self.debug:
                            print(f"        DEBUG: Link text='{text}', class='{class_name}', href='{href[:80] if href else None}...'")

                        # Check if it's a document link (has CompiledDocument or is a PDF)
                        if not href:
                            if self.debug:
                                print(f"        DEBUG: Skipping - no href")
                            continue

                        # Look for CompiledDocument links (the actual download links)
                        if 'CompiledDocument' not in href and not href.endswith('.pdf'):
                            if self.debug:
                                print(f"        DEBUG: Skipping - not a document link (no CompiledDocument)")
                            continue

                        # Classify document type based on link text or context
                        # Note: text might be empty if link contains only an icon

                        # If text is STILL empty, try parent or use position
                        if not text:
                            # Try getting parent element text (list item or container)
                            try:
                                parent = link.find_element(By.XPATH, '..')
                                parent_text = parent.text.strip().lower()
                                if self.debug:
                                    print(f"        DEBUG: Empty text, checking parent text: '{parent_text}'")
                                # Extract just the relevant word from parent text
                                if 'agenda' in parent_text and 'minutes' not in parent_text:
                                    text = 'agenda'
                                elif 'minutes' in parent_text:
                                    text = 'minutes'
                                else:
                                    text = parent_text
                            except:
                                # If we already have an agenda, this is likely minutes
                                # (documents typically appear in order: agenda, then minutes)
                                if 'agenda' in documents and 'minutes' not in documents:
                                    text = 'minutes'
                                    if self.debug:
                                        print(f"        DEBUG: Empty text and agenda exists, assuming minutes")
                                else:
                                    if self.debug:
                                        print(f"        DEBUG: Cannot determine document type")
                                    continue

                        if 'minutes' in text:
                            documents['minutes'] = href
                            if self.debug:
                                print(f"        DEBUG: ✅ Found MINUTES link")
                        elif 'agenda' in text:
                            # Exclude agenda packets
                            if 'packet' not in text and 'packet' not in href.lower():
                                documents['agenda'] = href
                                if self.debug:
                                    print(f"        DEBUG: ✅ Found AGENDA link")
                            elif self.debug:
                                print(f"        DEBUG: Skipping - agenda packet")
                        elif self.debug:
                            print(f"        DEBUG: Could not classify - text: '{text}'")

                    # Extract video link if available
                    video_link = None
                    try:
                        video_links = row.find_elements(By.CSS_SELECTOR, 'a[href*="Video"]')
                        if not video_links:
                            # Try alternative selectors
                            video_links = row.find_elements(By.CSS_SELECTOR, 'a[title*="video" i]')
                        if video_links:
                            video_link = video_links[0].get_attribute('href')
                            if self.debug:
                                print(f"        DEBUG: Found video link: {video_link[:80]}...")
                    except:
                        pass

                    meeting_data = {
                        'title': meeting_title,
                        'date': meeting_date,
                        'documents': documents,
                        'video_link': video_link,
                        'row_element': row
                    }

                    meetings.append(meeting_data)

                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"    ⚠️  Error extracting meeting: {e}")
                    continue

        except TimeoutException:
            print(f"  ⚠️  Timeout waiting for meeting table")

        return meetings

    def has_next_page(self):
        """Check if there's a next page button"""
        try:
            next_button = self.driver.find_element(By.ID, 'archivedMeetingsTable_next')
            return 'disabled' not in next_button.get_attribute('class')
        except:
            return False

    def click_next_page(self):
        """Click next page button"""
        try:
            next_button = self.driver.find_element(By.ID, 'archivedMeetingsTable_next')
            next_button.click()

            # Wait for page to load
            time.sleep(2)
            return True

        except Exception as e:
            print(f"  ⚠️  Error clicking next page: {e}")
            return False

    def download_document(self, url, doc_type, meeting_title, meeting_date, video_link=None):
        """
        Download a document

        Args:
            url: Document URL
            doc_type: 'agenda' or 'minutes'
            meeting_title: Meeting title for filename
            meeting_date: Meeting date for filename
            video_link: Optional video link for the meeting

        Returns:
            bool: Success status
        """
        try:
            # Generate target filename
            date_obj = datetime.strptime(meeting_date, '%Y-%m-%d')
            year = date_obj.year
            date_prefix = date_obj.strftime('%Y%m%d')

            # Generate meeting name slug
            title = meeting_title.lower()
            title = re.sub(r'[^\w\s-]', '', title)
            title = re.sub(r'[-\s]+', '_', title)
            # No truncation - keep full meeting name

            filename = f"{date_prefix}_{doc_type}_{title}.pdf"

            # Target path
            target_path = self.output_dir / str(year) / "PDFs" / doc_type / filename

            # Check if already exists
            if target_path.exists():
                print(f"      ⏭️  Skipped: already exists")
                self.stats['skipped'] += 1
                return False

            if self.dry_run:
                print(f"      [DRY RUN] Would download to: {filename}")
                return True

            # Download file
            print(f"      📥 Downloading...")
            self.driver.get(url)

            # Wait for download to complete
            time.sleep(3)

            # Find downloaded file (look for most recent PDF in download dir)
            pdf_files = list(self.download_dir.glob("*.pdf"))
            if not pdf_files:
                print(f"      ❌ Download failed - no PDF found")
                self.stats['errors'] += 1
                return False

            # Get most recent file
            latest_file = max(pdf_files, key=lambda p: p.stat().st_mtime)

            # Move to target location (use shutil.move for cross-filesystem moves)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(latest_file), str(target_path))

            file_size = target_path.stat().st_size
            print(f"      ✅ Downloaded: {file_size:,} bytes")

            if doc_type == 'agenda':
                self.stats['agendas_downloaded'] += 1
            elif doc_type == 'minutes':
                self.stats['minutes_downloaded'] += 1

            # Track downloaded file details
            self.downloaded_files.append({
                'filename': filename,
                'path': str(target_path),
                'type': doc_type,
                'meeting_title': meeting_title,
                'meeting_date': meeting_date,
                'year': year,
                'size_bytes': file_size,
                'download_url': url,
                'video_link': video_link or ''
            })

            return True

        except Exception as e:
            print(f"      ❌ Error: {e}")
            self.stats['errors'] += 1
            return False

    def download_year(self, year, doc_types=['agenda', 'minutes']):
        """
        Download all meetings for a specific year

        Args:
            year: Year to download
            doc_types: List of document types to download

        Returns:
            int: Number of meetings processed
        """
        print(f"\n📅 Processing Year {year}")
        print(f"{'='*60}")

        # Initialize year-specific stats
        self.year_stats[year] = {
            'meetings_found': 0,
            'meetings_filtered': 0,
            'meetings_processed': 0,
            'agendas_downloaded': 0,
            'minutes_downloaded': 0,
            'errors': 0,
            'skipped': 0
        }

        # Navigate to year
        if not self.navigate_to_year(year):
            return 0

        all_meetings = []
        page_num = 1

        # Get meetings from all pages
        while True:
            print(f"\n  📄 Page {page_num}")

            meetings = self.get_meetings_from_page()
            all_meetings.extend(meetings)

            print(f"     Found {len(meetings)} meetings on this page")

            if not self.has_next_page():
                break

            if not self.click_next_page():
                break

            page_num += 1

        self.stats['meetings_found'] += len(all_meetings)
        self.year_stats[year]['meetings_found'] = len(all_meetings)

        # Filter by meeting type
        filtered_meetings = []
        for meeting in all_meetings:
            if self.is_allowed_meeting_type(meeting['title']):
                filtered_meetings.append(meeting)
            else:
                self.stats['meetings_filtered'] += 1
                self.year_stats[year]['meetings_filtered'] += 1

        # Filter by year - only keep meetings from the requested year
        year_filtered_meetings = []
        for meeting in filtered_meetings:
            meeting_year = datetime.strptime(meeting['date'], '%Y-%m-%d').year
            if meeting_year == year:
                year_filtered_meetings.append(meeting)
            else:
                self.stats['meetings_filtered'] += 1
                self.year_stats[year]['meetings_filtered'] += 1
                if self.debug:
                    print(f"  DEBUG: Filtering out meeting from year {meeting_year}: {meeting['title']}")

        filtered_meetings = year_filtered_meetings
        self.year_stats[year]['meetings_processed'] = len(filtered_meetings)

        print(f"\n  ✅ Total meetings found: {len(all_meetings)}")
        print(f"  ✅ Matching meeting types: {len(filtered_meetings)}")
        print(f"  ⏭️  Filtered out: {self.year_stats[year]['meetings_filtered']}")

        if not filtered_meetings:
            print(f"\n  ⚠️  No meetings matched the meeting type filter!")
            return 0

        # Process each meeting
        print(f"\n  🔄 Processing {len(filtered_meetings)} meetings...\n")

        # Track counts before processing
        agendas_before = self.stats['agendas_downloaded']
        minutes_before = self.stats['minutes_downloaded']
        errors_before = self.stats['errors']
        skipped_before = self.stats['skipped']

        for i, meeting in enumerate(filtered_meetings, 1):
            title = meeting['title']
            date = meeting['date']
            video_link = meeting.get('video_link')

            print(f"\n  [{i}/{len(filtered_meetings)}] {date}: {title}")

            documents = meeting['documents']

            for doc_type in doc_types:
                url = documents.get(doc_type)

                if not url:
                    print(f"    ⏭️  No {doc_type} found")
                    continue

                print(f"    📥 Downloading {doc_type}...")
                self.download_document(url, doc_type, title, date, video_link)

                # Small delay between downloads
                time.sleep(1)

        # Update year-specific stats
        self.year_stats[year]['agendas_downloaded'] = self.stats['agendas_downloaded'] - agendas_before
        self.year_stats[year]['minutes_downloaded'] = self.stats['minutes_downloaded'] - minutes_before
        self.year_stats[year]['errors'] = self.stats['errors'] - errors_before
        self.year_stats[year]['skipped'] = self.stats['skipped'] - skipped_before

        return len(filtered_meetings)

    def download_all(self, years, doc_types=['agenda', 'minutes']):
        """
        Download meetings for multiple years

        Args:
            years: List of years to download
            doc_types: List of document types to download
        """
        print(f"\n📥 Santa Ana Meeting Downloader (Selenium)")
        print(f"{'='*60}")
        print(f"Output directory: {self.output_dir}")
        print(f"Download directory: {self.download_dir}")
        print(f"Document types: {', '.join(doc_types)}")
        print(f"Years: {years}")
        print(f"Meeting types filter:")
        for mt in self.ALLOWED_MEETING_TYPES:
            print(f"  - {mt}")
        print(f"Dry run: {self.dry_run}")
        print(f"Headless: {self.headless}\n")

        # Setup browser
        print(f"🌐 Setting up browser...")
        self.setup_driver()

        # Navigate to portal
        print(f"🌐 Loading portal...")
        self.driver.get(self.PORTAL_URL)

        # Wait for page to load
        time.sleep(5)

        # Process each year
        for year in years:
            try:
                self.download_year(year, doc_types=doc_types)
            except Exception as e:
                print(f"\n❌ Error processing year {year}: {e}")
                import traceback
                traceback.print_exc()

        # Close browser
        self.close_driver()

        # Print summary and generate report
        self.print_summary()
        if not self.dry_run and self.downloaded_files:
            self.generate_report()

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

        # Per-year breakdown
        if self.year_stats:
            print(f"\n📅 Year-by-Year Breakdown:")
            for year in sorted(self.year_stats.keys()):
                stats = self.year_stats[year]
                print(f"\n  {year}:")
                print(f"    Meetings found: {stats['meetings_found']}")
                print(f"    Meetings processed: {stats['meetings_processed']}")
                print(f"    Agendas downloaded: {stats['agendas_downloaded']}")
                print(f"    Minutes downloaded: {stats['minutes_downloaded']}")
                if stats['skipped'] > 0:
                    print(f"    Skipped: {stats['skipped']}")
                if stats['errors'] > 0:
                    print(f"    Errors: {stats['errors']}")

        print(f"\n✅ Complete!\n")

    def generate_report(self):
        """Generate detailed download report as JSON file"""
        from datetime import datetime
        import json

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.output_dir / f"download_report_{timestamp}.json"

        # Calculate total size
        total_size = sum(f['size_bytes'] for f in self.downloaded_files)

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_meetings_found': self.stats['meetings_found'],
                'total_meetings_filtered': self.stats['meetings_filtered'],
                'total_meetings_processed': self.stats['meetings_found'] - self.stats['meetings_filtered'],
                'total_agendas_downloaded': self.stats['agendas_downloaded'],
                'total_minutes_downloaded': self.stats['minutes_downloaded'],
                'total_files_downloaded': len(self.downloaded_files),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'errors': self.stats['errors'],
                'skipped': self.stats['skipped']
            },
            'year_stats': self.year_stats,
            'downloaded_files': self.downloaded_files
        }

        # Save report
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Detailed report saved to: {report_file}")
        print(f"   Total size downloaded: {report['summary']['total_size_mb']} MB")

        # Generate CSV spreadsheet
        self.generate_csv_report(timestamp)

    def generate_csv_report(self, timestamp):
        """Generate CSV spreadsheet with file locations and video links"""
        import csv

        csv_file = self.output_dir / f"download_report_{timestamp}.csv"

        # Write CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['meeting_date', 'meeting_title', 'year', 'document_type', 'filename', 'file_path', 'size_mb', 'download_url', 'video_link']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for file_info in self.downloaded_files:
                writer.writerow({
                    'meeting_date': file_info['meeting_date'],
                    'meeting_title': file_info['meeting_title'],
                    'year': file_info['year'],
                    'document_type': file_info['type'],
                    'filename': file_info['filename'],
                    'file_path': file_info['path'],
                    'size_mb': round(file_info['size_bytes'] / (1024 * 1024), 2),
                    'download_url': file_info.get('download_url', ''),
                    'video_link': file_info.get('video_link', '')
                })

        print(f"📊 CSV spreadsheet saved to: {csv_file}")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description='Download Santa Ana meetings using Selenium browser automation'
    )

    parser.add_argument(
        '--years',
        nargs='+',
        type=int,
        required=True,
        help='Years to download (e.g., 2024 2023)'
    )

    parser.add_argument(
        '--output',
        default='/Volumes/Samsung USB/City_extraction/Santa_Ana',
        help='Base directory for organized files'
    )

    parser.add_argument(
        '--download-dir',
        help='Temporary download directory (default: ~/Downloads)'
    )

    parser.add_argument(
        '--types',
        nargs='+',
        choices=['agenda', 'minutes'],
        default=['agenda', 'minutes'],
        help='Document types to download'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be downloaded without actually downloading'
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (default is headless)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Print detailed debug information'
    )

    args = parser.parse_args()

    # Check if output directory exists (if not dry run)
    if not args.dry_run:
        output_path = Path(args.output)
        if not output_path.exists():
            print(f"⚠️  Warning: Output directory does not exist: {output_path}")
            response = input("Create it? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
            output_path.mkdir(parents=True, exist_ok=True)

    # Create downloader and run
    downloader = SantAnaSeleniumDownloader(
        output_dir=args.output,
        download_dir=args.download_dir,
        dry_run=args.dry_run,
        headless=not args.no_headless,
        debug=args.debug
    )

    downloader.download_all(years=args.years, doc_types=args.types)


if __name__ == '__main__':
    main()
