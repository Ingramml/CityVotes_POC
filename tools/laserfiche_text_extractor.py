#!/usr/bin/env python3
"""
Laserfiche Text Extractor for Santa Ana

Extracts plain text directly from Laserfiche WebLink using the PageTextData.aspx endpoint.
This bypasses the need to download PDFs and uses the server's built-in OCR text.

Usage:
    python3 laserfiche_text_extractor.py --year 2024 --output ./output
    python3 laserfiche_text_extractor.py --years 2020 2021 2022 2023 2024 --output ./output
    python3 laserfiche_text_extractor.py --doc-id 146671 --output ./output  # Single document
"""

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


class LaserficheTextExtractor:
    """Extract text from Santa Ana Laserfiche documents"""

    BASE_URL = "https://publicdocs.santa-ana.org/WebLink/"

    # Known folder IDs for Santa Ana
    FOLDERS = {
        'minutes': {
            'root': 73985,  # Minutes root folder
            'city_council': 1769,
            'year_ranges': {
                '2020-2029': 116251,
                '2010-2019': 52229,
                '2000-2009': 34478,
            }
        },
        'agendas': {
            'root': 32945,  # Agenda Packets / Staff Reports
            'city_council': 1645,  # City Council agendas (2004-present)
            'years': {
                2025: 225033, 2024: 141781, 2023: 135252, 2022: 130425,
                2021: 125776, 2020: 115105, 2019: 104747, 2018: 97934,
                2017: 91065, 2016: 86119, 2015: 80384, 2014: 74964,
                2013: 70665, 2012: 62063, 2011: 57976, 2010: 52223,
                2009: 49393, 2008: 46438, 2007: 43120, 2006: 51893,
                2005: 51894, 2004: 51895,
            }
        }
    }

    def __init__(self, output_dir: str = "./output", delay: float = 1.0):
        """
        Initialize the extractor

        Args:
            output_dir: Directory to save extracted text files
            delay: Delay between requests in seconds
        """
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.metadata = {
            'extraction_date': datetime.now().isoformat(),
            'source': 'Laserfiche WebLink PageTextData.aspx',
            'documents': []
        }

    def _establish_session(self):
        """Establish session cookies"""
        welcome_url = f"{self.BASE_URL}Welcome.aspx"
        self.session.get(welcome_url, timeout=30)
        print(f"Session established. Cookies: {list(self.session.cookies.keys())}")

    def _parse_folder_page(self, soup: BeautifulSoup) -> list:
        """
        Parse items from a single page of folder contents.

        Args:
            soup: BeautifulSoup object of the page

        Returns:
            List of item dicts with 'name', 'id', 'type'
        """
        items = []
        links = soup.find_all('a', href=True)

        for link in links:
            href = link.get('href', '')
            aria_label = link.get('aria-label', '')

            # Match folder pattern: 1/fol/{ID}/Row1.aspx
            fol_match = re.search(r'1/fol/(\d+)/Row1\.aspx', href)
            if fol_match:
                items.append({
                    'name': aria_label.replace(' Folder', '').strip(),
                    'id': int(fol_match.group(1)),
                    'type': 'folder'
                })
                continue

            # Match document pattern: 1/doc/{ID}/Page1.aspx or 0/doc/{ID}/Page1.aspx
            doc_match = re.search(r'\d/doc/(\d+)/Page1\.aspx', href)
            if doc_match:
                items.append({
                    'name': aria_label.replace(' Document', '').strip(),
                    'id': int(doc_match.group(1)),
                    'type': 'document'
                })

        return items

    def _get_folder_contents(self, folder_id: int, dbid: int = 1) -> list:
        """
        Get contents of a folder, handling pagination via ASP.NET postback.

        Returns list of dicts with 'name', 'id', 'type' (folder/document)
        """
        url = f"{self.BASE_URL}Browse.aspx?startid={folder_id}&dbid={dbid}"
        resp = self.session.get(url, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Parse first page
        all_items = self._parse_folder_page(soup)

        # Check for pagination - look for "Page X of Y" pattern
        pager = soup.find(class_='PagerStripContainer')
        if pager:
            pager_text = pager.text
            page_match = re.search(r'Page\s*(\d+)\s*of\s*(\d+)', pager_text)

            if page_match:
                current_page = int(page_match.group(1))
                total_pages = int(page_match.group(2))

                if total_pages > 1:
                    print(f"    Folder has {total_pages} pages of items")

                    # Get remaining pages using ASP.NET postback
                    for page_num in range(2, total_pages + 1):
                        time.sleep(0.5)  # Small delay between pagination requests

                        # Extract form data for postback
                        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                        viewstate_gen = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
                        event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
                        prev_page = soup.find('input', {'name': '__PREVIOUSPAGE'})

                        if not viewstate:
                            print(f"    Warning: Could not find ViewState for page {page_num}")
                            break

                        # Build postback data
                        # The event target follows pattern: TheDocumentBrowser:_ctl5 for page 2, etc.
                        data = {
                            '__EVENTTARGET': 'TheDocumentBrowser:_ctl5',
                            '__EVENTARGUMENT': str(page_num - 1),  # 0-indexed
                            '__VIEWSTATE': viewstate.get('value', ''),
                            '__VIEWSTATEGENERATOR': viewstate_gen.get('value', '') if viewstate_gen else '',
                            '__EVENTVALIDATION': event_validation.get('value', '') if event_validation else '',
                            '__PREVIOUSPAGE': prev_page.get('value', '') if prev_page else '',
                            'searchBox': '',
                            'searchLoc': '',
                            'searchFolderID': str(folder_id),
                            'TheDocumentBrowser:XScrollPosition': '0',
                            'TheDocumentBrowser:YScrollPosition': '0',
                        }

                        resp = self.session.post(url, data=data, timeout=30)
                        soup = BeautifulSoup(resp.text, 'html.parser')

                        # Parse this page
                        page_items = self._parse_folder_page(soup)

                        # Filter out duplicates and parent folder references
                        for item in page_items:
                            if item['id'] != folder_id and item not in all_items:
                                # Check if we already have this item by ID
                                existing_ids = {i['id'] for i in all_items}
                                if item['id'] not in existing_ids:
                                    all_items.append(item)

                        print(f"    Page {page_num}/{total_pages}: Found {len(page_items)} items")

        return all_items

    def _get_document_info(self, doc_id: int, dbid: int = 1) -> dict:
        """Get document metadata including page count"""
        url = f"{self.BASE_URL}DocView.aspx?id={doc_id}&dbid={dbid}"
        resp = self.session.get(url, timeout=30)

        info = {'id': doc_id, 'dbid': dbid}

        # Extract page count
        match = re.search(r'NumPages["\']?\s*[:=]\s*(\d+)', resp.text)
        if match:
            info['page_count'] = int(match.group(1))
        else:
            info['page_count'] = 0

        # Extract repository name
        match = re.search(r"TheAnalyticsCtrl=new DocViewerAnalytics\('([^']+)'", resp.text)
        if match:
            info['repository'] = match.group(1)
        else:
            info['repository'] = 'Clerk'

        return info

    def _get_page_text(self, doc_id: int, page_num: int, repository: str = 'Clerk', dbid: int = 1) -> str:
        """
        Get text for a single page using PageTextData.aspx

        Args:
            doc_id: Document ID
            page_num: Page number (1-indexed)
            repository: Repository name (usually 'Clerk')
            dbid: Database ID

        Returns:
            Plain text content of the page
        """
        url = f"{self.BASE_URL}PageTextData.aspx"
        params = {
            'r': repository,
            'i': doc_id,
            'dbid': dbid,
            'p': page_num,
            'showAnn': '0'
        }

        resp = self.session.get(url, params=params, timeout=30)

        if resp.status_code == 200 and len(resp.content) > 20:
            soup = BeautifulSoup(resp.text, 'html.parser')
            pre = soup.find('pre')
            if pre:
                return pre.get_text()
            return resp.text
        return ""

    def extract_document_text(self, doc_id: int, dbid: int = 1) -> str:
        """
        Extract full text from a document

        Args:
            doc_id: Document ID
            dbid: Database ID

        Returns:
            Full document text
        """
        # Get document info
        info = self._get_document_info(doc_id, dbid)
        page_count = info.get('page_count', 0)
        repository = info.get('repository', 'Clerk')

        if page_count == 0:
            print(f"  Warning: Could not determine page count for doc {doc_id}")
            page_count = 100  # Try up to 100 pages

        # Extract text from all pages
        pages_text = []
        for page_num in range(1, page_count + 1):
            text = self._get_page_text(doc_id, page_num, repository, dbid)
            if text and len(text.strip()) > 10:
                pages_text.append(text)
            else:
                # No more content
                if page_num > 1:
                    break
            time.sleep(0.1)  # Small delay between pages

        return '\n\n'.join(pages_text)

    def get_year_documents(self, year: int, doc_type: str = 'minutes') -> list:
        """
        Get all documents for a specific year

        Args:
            year: Year (e.g., 2024)
            doc_type: 'minutes' or 'agendas'

        Returns:
            List of document dicts with 'name', 'id', 'type'
        """
        # Navigate to the correct year folder
        if doc_type == 'minutes':
            # Minutes are under City Council -> Year Range -> Year
            city_council_id = self.FOLDERS['minutes']['city_council']

            # Find the right year range
            if 2020 <= year <= 2029:
                year_range_id = self.FOLDERS['minutes']['year_ranges']['2020-2029']
            elif 2010 <= year <= 2019:
                year_range_id = self.FOLDERS['minutes']['year_ranges']['2010-2019']
            elif 2000 <= year <= 2009:
                year_range_id = self.FOLDERS['minutes']['year_ranges']['2000-2009']
            else:
                print(f"Year {year} not supported")
                return []

            # Get year folders in the range
            time.sleep(self.delay)
            year_folders = self._get_folder_contents(year_range_id)

            # Find the specific year folder
            year_folder = None
            for folder in year_folders:
                if folder['type'] == 'folder' and str(year) in folder['name']:
                    year_folder = folder
                    break

            if not year_folder:
                print(f"Year folder for {year} not found")
                return []

            # Get documents in the year folder
            time.sleep(self.delay)
            return self._get_folder_contents(year_folder['id'])

        elif doc_type == 'agendas':
            # Agendas are under City Council -> Year -> Meeting Date Folder -> Documents
            if year not in self.FOLDERS['agendas']['years']:
                print(f"Year {year} not found in agenda folders")
                return []

            year_folder_id = self.FOLDERS['agendas']['years'][year]
            time.sleep(self.delay)
            return self._get_folder_contents(year_folder_id)

        return []

    def get_agenda_documents_for_date(self, year: int, meeting_folder_id: int) -> list:
        """
        Get agenda documents from a meeting date folder.
        Looks for documents named 'Agenda_YYYY-MM-DD' (the main agenda).

        Args:
            year: Year
            meeting_folder_id: Folder ID for the meeting date

        Returns:
            List of agenda documents (typically just the main agenda)
        """
        time.sleep(self.delay)
        items = self._get_folder_contents(meeting_folder_id)

        # Filter for main agenda documents (named "Agenda_YYYY-MM-DD" or "AGENDA_YYYY-MM-DD")
        agendas = []
        for item in items:
            if item['type'] == 'document':
                name = item['name'].strip()
                name_lower = name.lower()
                # Look for "Agenda_" prefix (case-insensitive) - the main agenda document
                if name_lower.startswith('agenda_'):
                    agendas.append(item)

        return agendas

    def extract_year(self, year: int, doc_type: str = 'minutes') -> list:
        """
        Extract all documents for a year

        Args:
            year: Year to extract
            doc_type: 'minutes' or 'agendas'

        Returns:
            List of extraction results
        """
        print(f"\n{'='*60}")
        print(f"Extracting {doc_type} for {year}")
        print(f"{'='*60}")

        # Create output directory
        year_dir = self.output_dir / str(year) / "text" / doc_type
        year_dir.mkdir(parents=True, exist_ok=True)

        # Get documents for the year
        items = self.get_year_documents(year, doc_type)

        # For agendas, we need to look inside each meeting folder
        if doc_type == 'agendas':
            docs_to_extract = []
            meeting_folders = [item for item in items if item['type'] == 'folder']
            print(f"Found {len(meeting_folders)} meeting folders")

            for folder in meeting_folders:
                # Get the main agenda document from each meeting folder
                agendas = self.get_agenda_documents_for_date(year, folder['id'])
                for agenda in agendas:
                    agenda['meeting_folder'] = folder['name']
                    docs_to_extract.append(agenda)

            print(f"Found {len(docs_to_extract)} agenda documents")
        else:
            # For minutes, documents are directly in the year folder
            docs_to_extract = [d for d in items if d['type'] == 'document']
            print(f"Found {len(docs_to_extract)} documents")

        results = []
        for i, doc in enumerate(docs_to_extract, 1):
            doc_name = doc['name']
            doc_id = doc['id']

            # Create filename from document name
            # e.g., "Agenda_2024-01-16" -> "Agenda_2024-01-16.txt"
            safe_name = re.sub(r'[^\w\-]', '_', doc_name.strip())
            filename = f"{safe_name}.txt"
            filepath = year_dir / filename

            # Skip if already exists
            if filepath.exists():
                print(f"  [{i}/{len(docs_to_extract)}] Skipping {doc_name} (already exists)")
                continue

            print(f"  [{i}/{len(docs_to_extract)}] Extracting: {doc_name} (ID: {doc_id})")

            try:
                time.sleep(self.delay)
                text = self.extract_document_text(doc_id)

                if text:
                    # Save text file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(text)

                    print(f"    Saved: {filename} ({len(text):,} chars)")

                    # Record metadata
                    result = {
                        'name': doc_name,
                        'doc_id': doc_id,
                        'year': year,
                        'type': doc_type,
                        'filename': filename,
                        'filepath': str(filepath),
                        'char_count': len(text),
                        'success': True
                    }
                    results.append(result)
                    self.metadata['documents'].append(result)
                else:
                    print(f"    Warning: No text extracted")
                    results.append({
                        'name': doc_name,
                        'doc_id': doc_id,
                        'success': False,
                        'error': 'No text content'
                    })

            except Exception as e:
                print(f"    Error: {e}")
                results.append({
                    'name': doc_name,
                    'doc_id': doc_id,
                    'success': False,
                    'error': str(e)
                })

        return results

    def extract_single_document(self, doc_id: int, output_name: str = None) -> dict:
        """
        Extract a single document by ID

        Args:
            doc_id: Document ID
            output_name: Optional output filename (without extension)

        Returns:
            Extraction result dict
        """
        print(f"\nExtracting document ID: {doc_id}")

        self._establish_session()

        try:
            text = self.extract_document_text(doc_id)

            if text:
                # Save to output directory
                self.output_dir.mkdir(parents=True, exist_ok=True)
                filename = f"{output_name or doc_id}.txt"
                filepath = self.output_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)

                print(f"Saved: {filepath} ({len(text):,} chars)")

                return {
                    'doc_id': doc_id,
                    'filename': filename,
                    'filepath': str(filepath),
                    'char_count': len(text),
                    'success': True
                }
            else:
                return {
                    'doc_id': doc_id,
                    'success': False,
                    'error': 'No text content'
                }

        except Exception as e:
            return {
                'doc_id': doc_id,
                'success': False,
                'error': str(e)
            }

    def run(self, years: list, doc_types: list = None):
        """
        Run extraction for multiple years

        Args:
            years: List of years to extract
            doc_types: List of document types ('minutes', 'agendas')
        """
        if doc_types is None:
            doc_types = ['minutes']

        print(f"\nLaserfiche Text Extractor")
        print(f"{'='*60}")
        print(f"Output directory: {self.output_dir}")
        print(f"Years: {years}")
        print(f"Document types: {doc_types}")
        print(f"Request delay: {self.delay}s")

        # Establish session
        self._establish_session()

        all_results = []

        for year in years:
            for doc_type in doc_types:
                results = self.extract_year(year, doc_type)
                all_results.extend(results)

        # Save metadata
        metadata_path = self.output_dir / "extraction_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)

        # Print summary
        successful = sum(1 for r in all_results if r.get('success'))
        failed = len(all_results) - successful

        print(f"\n{'='*60}")
        print(f"EXTRACTION COMPLETE")
        print(f"{'='*60}")
        print(f"Total documents: {len(all_results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Metadata saved: {metadata_path}")

        return all_results


def main():
    parser = argparse.ArgumentParser(
        description='Extract text from Santa Ana Laserfiche documents'
    )

    parser.add_argument(
        '--years', '-y',
        nargs='+',
        type=int,
        help='Years to extract (e.g., 2024 2023 2022)'
    )

    parser.add_argument(
        '--year',
        type=int,
        help='Single year to extract'
    )

    parser.add_argument(
        '--doc-id',
        type=int,
        help='Extract a single document by ID'
    )

    parser.add_argument(
        '--doc-name',
        type=str,
        help='Output filename for single document (without extension)'
    )

    parser.add_argument(
        '--types', '-t',
        nargs='+',
        choices=['minutes', 'agendas'],
        default=['minutes'],
        help='Document types to extract (default: minutes)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='./santa_ana_text',
        help='Output directory (default: ./santa_ana_text)'
    )

    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )

    args = parser.parse_args()

    extractor = LaserficheTextExtractor(
        output_dir=args.output,
        delay=args.delay
    )

    if args.doc_id:
        # Extract single document
        result = extractor.extract_single_document(args.doc_id, args.doc_name)
        if result['success']:
            print(f"\nSuccess! Extracted {result['char_count']:,} characters")
        else:
            print(f"\nFailed: {result.get('error')}")
    else:
        # Extract by year
        years = args.years or ([args.year] if args.year else [2024])
        extractor.run(years, args.types)


if __name__ == '__main__':
    main()
