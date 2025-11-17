#!/usr/bin/env python3
"""
Universal File Downloader Workflow

A flexible file downloader that can extract URLs from JSON files or directories
and download the files. Supports various JSON structures and custom key mapping.

Usage:
    python file_downloader.py --input file.json --key "agenda_url" --output downloads/
    python file_downloader.py --input data/ --key "minutes_url" --output docs/
    python file_downloader.py --input meetings.json --key "documents.pdf_url" --output files/
"""

import argparse
import os
import json
import sys
import glob
import time
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from urllib.parse import urlparse, unquote
import requests
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FileDownloader:
    """Handles file downloading with proper error handling and retry logic"""
    
    def __init__(self, user_agent=None, verify_ssl=False, timeout=30):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.session.verify = verify_ssl
        self.timeout = timeout
    
    def download_file(self, url: str, filepath: str, chunk_size: int = 8192) -> tuple:
        """
        Download a file from URL to filepath
        
        Args:
            url: URL to download from
            filepath: Local path to save file
            chunk_size: Size of chunks to download
            
        Returns:
            tuple: (success: bool, file_size: int, error_message: str)
        """
        try:
            # Skip if file already exists
            if os.path.exists(filepath):
                return True, os.path.getsize(filepath), "File already exists"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Make request
            response = self.session.get(url, stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            # Download file in chunks
            total_size = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            return True, total_size, "Success"
            
        except requests.exceptions.RequestException as e:
            return False, 0, f"Request error: {str(e)}"
        except IOError as e:
            return False, 0, f"File error: {str(e)}"
        except Exception as e:
            return False, 0, f"Unexpected error: {str(e)}"


class JSONParser:
    """Handles parsing JSON files and extracting URLs using flexible key mapping"""
    
    def __init__(self, key_path: str):
        """
        Initialize JSON parser with key path
        
        Args:
            key_path: Dot-notation path to URL field (e.g., "agenda_url", "documents.pdf_url")
                     Special keywords: "auto_minutes", "auto_agenda", "auto_pdf" for smart detection
        """
        self.key_path = key_path
        self.key_parts = key_path.split('.')
        self.is_auto_mode = key_path.lower().startswith('auto_')
    
    def find_matching_keys(self, data: dict, search_term: str) -> List[str]:
        """
        Find all keys that contain a search term (case-insensitive)
        
        Args:
            data: Dictionary to search
            search_term: Term to search for in keys
            
        Returns:
            List of matching keys
        """
        search_lower = search_term.lower()
        return [key for key in data.keys() if search_lower in key.lower()]
    
    def is_pdf_url(self, url: str) -> bool:
        """Check if URL likely points to a PDF"""
        if not url or not isinstance(url, str):
            return False
        
        url_lower = url.lower()
        # Check for PDF indicators
        pdf_indicators = [
            '.pdf',
            'pdf',
            'displayagendapdf',
            'view.ashx?m=a',  # Legistar agenda
            'view.ashx?m=m',  # Legistar minutes
            'compileddocument',  # PrimeGov documents
            'downloadpdf'
        ]
        
        return any(indicator in url_lower for indicator in pdf_indicators)
    
    def auto_detect_best_key(self, data: dict, category: str) -> Optional[str]:
        """
        Automatically detect the best key for a category (minutes, agenda, etc.)
        
        Args:
            data: Meeting data dictionary
            category: Category to search for ('minutes', 'agenda', 'pdf')
            
        Returns:
            Best matching key or None
        """
        if category == 'minutes':
            # Look for minutes-related keys
            minutes_keys = self.find_matching_keys(data, 'minutes')
            
            # Prioritize PDF URLs
            for key in minutes_keys:
                if data.get(key) and self.is_pdf_url(data[key]):
                    return key
            
            # Fall back to any minutes key with content
            for key in minutes_keys:
                if data.get(key) and data[key].strip():
                    return key
                    
        elif category == 'agenda':
            # Look for agenda-related keys
            agenda_keys = self.find_matching_keys(data, 'agenda')
            
            # Prioritize downloadable/PDF URLs
            pdf_agenda_keys = []
            for key in agenda_keys:
                if data.get(key) and self.is_pdf_url(data[key]):
                    pdf_agenda_keys.append(key)
            
            # Prefer "Download" or "Packet" versions
            for key in pdf_agenda_keys:
                if any(term in key.lower() for term in ['download', 'packet', 'pdf']):
                    return key
            
            # Fall back to first PDF agenda
            if pdf_agenda_keys:
                return pdf_agenda_keys[0]
                
            # Fall back to any agenda key with content
            for key in agenda_keys:
                if data.get(key) and data[key].strip():
                    return key
                    
        elif category == 'pdf':
            # Look for any PDF URLs
            for key, value in data.items():
                if value and self.is_pdf_url(value):
                    return key
        
        return None
    
    def extract_value(self, data: dict, key_path: Optional[str] = None) -> Optional[str]:
        """
        Extract value from nested dictionary using dot notation or auto-detection
        
        Args:
            data: Dictionary to search
            key_path: Override key path (uses instance key_path if None)
            
        Returns:
            Found value or None
        """
        if key_path is None:
            key_path = self.key_path
            
        # Handle auto-detection modes
        if key_path.lower().startswith('auto_'):
            category = key_path.lower().replace('auto_', '')
            best_key = self.auto_detect_best_key(data, category)
            if best_key:
                return data.get(best_key)
            return None
            
        # Handle exact key match (case-insensitive)
        for key in data.keys():
            if key.lower() == key_path.lower():
                return data.get(key)
        
        # Handle dot notation for nested keys
        key_parts = key_path.split('.')
        if len(key_parts) > 1:
            current = data
            for part in key_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
            return current if isinstance(current, str) else None
            
        # Partial matching - find key containing the search term
        matching_keys = self.find_matching_keys(data, key_path)
        if matching_keys:
            # If multiple matches for "minutes", prefer PDF URLs
            if 'minutes' in key_path.lower() and len(matching_keys) > 1:
                for key in matching_keys:
                    if data.get(key) and self.is_pdf_url(data[key]):
                        return data.get(key)
            
            # Return first match with content
            for key in matching_keys:
                value = data.get(key)
                if value and value.strip():
                    return value
        
        return None

    def parse_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parse JSON file and extract documents with URLs
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of document dictionaries with metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                # JSON array
                for i, item in enumerate(data):
                    url = self.extract_value(item)
                    if url:
                        documents.append({
                            'url': url,
                            'source_file': file_path,
                            'index': i,
                            'metadata': item
                        })
            
            elif isinstance(data, dict):
                # Single object or object with nested data
                
                # Check for common data containers
                containers = ['meetings', 'documents', 'data', 'items', 'results']
                found_container = False
                
                for container in containers:
                    if container in data and isinstance(data[container], list):
                        for i, item in enumerate(data[container]):
                            url = self.extract_value(item)
                            if url:
                                documents.append({
                                    'url': url,
                                    'source_file': file_path,
                                    'container': container,
                                    'index': i,
                                    'metadata': item
                                })
                        found_container = True
                        break
                
                # If no container found, treat as single document
                if not found_container:
                    url = self.extract_value(data)
                    if url:
                        documents.append({
                            'url': url,
                            'source_file': file_path,
                            'index': 0,
                            'metadata': data
                        })
            
            return documents
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error in {file_path}: {e}")
            return []
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return []


class DownloadWorkflow:
    """Main workflow orchestrator"""
    
    def __init__(self, output_dir: str, delay: float = 0.5, max_workers: int = 3):
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.max_workers = max_workers
        self.downloader = FileDownloader()
        
        # Statistics
        self.stats = {
            'files_processed': 0,
            'urls_found': 0,
            'downloads_attempted': 0,
            'downloads_successful': 0,
            'downloads_failed': 0,
            'downloads_skipped': 0,
            'total_bytes': 0,
            'errors': []
        }
    
    def create_filename(self, url: str, metadata: dict, key_path: str = "", index: int = 0) -> str:
        """
        Create a filename in format: YYYYMMDD_doc_type_meeting_title.pdf
        
        Args:
            url: Source URL
            metadata: Document metadata (should contain Date, Meeting Details, etc.)
            key_path: The key path used to find the URL (helps determine doc type)
            index: Document index
            
        Returns:
            Generated filename in format: YYYYMMDD_doc_type_meeting_title.pdf
        """
        # Parse date to YYYYMMDD format
        date_str = "00000000"  # Default if no date found
        date_fields = ['Meeting Date', 'Date', 'meeting_date', 'date']
        
        for field in date_fields:
            if field in metadata and metadata[field]:
                try:
                    date_value = metadata[field]
                    # Handle formats like "Dec 25, 2024", "01/15/2024", "1/15/2024", "January 15, 2024"
                    for date_format in ['%b %d, %Y', '%B %d, %Y', '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d']:
                        try:
                            parsed_date = datetime.strptime(date_value, date_format)
                            date_str = parsed_date.strftime('%Y%m%d')
                            break
                        except ValueError:
                            continue
                    if date_str != "00000000":  # If we found a valid date, break out of field loop
                        break
                except:
                    pass
        
        # Determine document type from key path or URL
        doc_type = "minutes"  # Default
        if key_path:
            key_lower = key_path.lower()
            if 'agenda' in key_lower and 'packet' in key_lower:
                doc_type = "agenda_packet"
            elif 'agenda' in key_lower:
                doc_type = "agenda"
            elif 'packet' in key_lower:
                doc_type = "packet"
            elif 'minutes' in key_lower:
                doc_type = "minutes"
            elif 'audio' in key_lower or 'video' in key_lower:
                doc_type = "media"
        
        # Extract meeting title/details
        meeting_title = "meeting"  # Default
        title_fields = ['Meeting title', 'Title', 'meeting_title', 'Meeting Details', 'Subject']
        
        for field in title_fields:
            if field in metadata and metadata[field]:
                title = metadata[field]
                if field == 'Meeting Details' and 'MeetingDetail.aspx' in title:
                    # Handle URL-based meeting details
                    if 'MeetingDetail.aspx' in title:
                        meeting_title = "council_meeting"
                    elif 'special' in title.lower():
                        meeting_title = "special_meeting"
                    elif 'workshop' in title.lower():
                        meeting_title = "workshop"
                    break
                else:
                    # Clean and use the title directly
                    title = title[:50]  # Limit length
                    meeting_title = re.sub(r'[^\w\s-]', '', title).strip()
                    meeting_title = re.sub(r'\s+', '_', meeting_title).lower()
                    # Remove common prefixes
                    meeting_title = meeting_title.replace('cancelled_-_', '').replace('canceled_-_', '')
                    break
        
        # Get file extension from URL
        extension = ".pdf"  # Default
        parsed_url = urlparse(url)
        url_path = unquote(parsed_url.path).lower()
        if url_path.endswith('.pdf'):
            extension = ".pdf"
        elif url_path.endswith(('.doc', '.docx')):
            extension = ".docx"
        elif url_path.endswith(('.xls', '.xlsx')):
            extension = ".xlsx"
        elif url_path.endswith('.txt'):
            extension = ".txt"
        elif url_path.endswith(('.mp3', '.wav', '.m4a')):
            extension = ".mp3"
        elif url_path.endswith(('.mp4', '.avi', '.mov')):
            extension = ".mp4"
        
        # Combine parts: YYYYMMDD_doc_type_meeting_title.ext
        filename = f"{date_str}_{doc_type}_{meeting_title}{extension}"
        
        # Clean filename - remove invalid characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        safe_filename = re.sub(r'\s+', '_', safe_filename)
        safe_filename = re.sub(r'_{2,}', '_', safe_filename)  # Replace multiple underscores
        
        # Ensure it doesn't exceed filesystem limits
        if len(safe_filename) > 200:
            name_part = safe_filename.rsplit('.', 1)[0][:190]
            ext_part = safe_filename.rsplit('.', 1)[1] if '.' in safe_filename else 'pdf'
            safe_filename = f"{name_part}.{ext_part}"
        
        return safe_filename
    
    def process_input(self, input_path: str, key_path: str) -> List[Dict[str, Any]]:
        """
        Process input file or directory
        
        Args:
            input_path: Path to file or directory
            key_path: JSON key path for URLs
            
        Returns:
            List of documents to download
        """
        path_obj = Path(input_path)
        parser = JSONParser(key_path)
        all_documents = []
        
        if path_obj.is_file():
            if path_obj.suffix.lower() == '.json':
                documents = parser.parse_json_file(str(path_obj))
                all_documents.extend(documents)
                self.stats['files_processed'] += 1
            else:
                print(f"⚠️  Unsupported file type: {path_obj}")
        
        elif path_obj.is_dir():
            # Process all JSON files in directory
            json_files = list(path_obj.glob("*.json"))
            print(f"📂 Found {len(json_files)} JSON files in directory")
            
            for json_file in json_files:
                print(f"📄 Processing: {json_file.name}")
                documents = parser.parse_json_file(str(json_file))
                all_documents.extend(documents)
                self.stats['files_processed'] += 1
        
        else:
            print(f"❌ Input path not found: {path_obj}")
            return []
        
        self.stats['urls_found'] = len(all_documents)
        return all_documents
    
    def download_documents(self, documents: List[Dict[str, Any]], key_path: str = "", dry_run: bool = False) -> None:
        """
        Download all documents
        
        Args:
            documents: List of document dictionaries
            key_path: The key path used to find URLs (helps with filename generation)
            dry_run: If True, only show what would be downloaded
        """
        if not documents:
            print("📭 No documents to download")
            return
        
        print(f"📥 {'Planning to download' if dry_run else 'Downloading'} {len(documents)} documents...")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if dry_run:
            for i, doc in enumerate(documents, 1):
                filename = self.create_filename(doc['url'], doc['metadata'], key_path, doc['index'])
                filepath = self.output_dir / filename
                print(f"  {i:3d}. {doc['url']} -> {filepath}")
            return
        
        # Download files
        for i, doc in enumerate(documents, 1):
            filename = self.create_filename(doc['url'], doc['metadata'], key_path, doc['index'])
            filepath = self.output_dir / filename
            
            print(f"📥 ({i}/{len(documents)}) {filename}")
            
            success, size, message = self.downloader.download_file(doc['url'], str(filepath))
            
            if success:
                if "already exists" in message:
                    print(f"    ⏭️  Skipped: {message}")
                    self.stats['downloads_skipped'] += 1
                else:
                    print(f"    ✅ Downloaded: {self.format_size(size)}")
                    self.stats['downloads_successful'] += 1
                    self.stats['total_bytes'] += size
            else:
                print(f"    ❌ Failed: {message}")
                self.stats['downloads_failed'] += 1
                self.stats['errors'].append(f"{filename}: {message}")
            
            self.stats['downloads_attempted'] += 1
            
            # Respectful delay
            if i < len(documents) and self.delay > 0:
                time.sleep(self.delay)
    
    def format_size(self, bytes_size: int) -> str:
        """Format file size in human readable format"""
        size_float = float(bytes_size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} TB"
    
    def print_summary(self) -> None:
        """Print download summary"""
        print(f"\n{'='*60}")
        print("DOWNLOAD SUMMARY")
        print(f"{'='*60}")
        print(f"📂 Files processed: {self.stats['files_processed']}")
        print(f"🔗 URLs found: {self.stats['urls_found']}")
        print(f"📥 Downloads attempted: {self.stats['downloads_attempted']}")
        print(f"✅ Downloads successful: {self.stats['downloads_successful']}")
        print(f"⏭️  Downloads skipped: {self.stats['downloads_skipped']}")
        print(f"❌ Downloads failed: {self.stats['downloads_failed']}")
        print(f"💾 Total downloaded: {self.format_size(self.stats['total_bytes'])}")
        
        if self.stats['errors']:
            print(f"\n❌ ERRORS ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(self.stats['errors']) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Download files from URLs found in JSON files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python file_downloader.py --input meetings.json --key "Agenda" --output downloads/
  python file_downloader.py --input data/ --key "Minutes" --output docs/
  
  # Auto-detection modes
  python file_downloader.py --input meetings.json --key "auto_minutes" --output docs/
  python file_downloader.py --input data/ --key "auto_agenda" --output agendas/
  python file_downloader.py --input files.json --key "auto_pdf" --output pdfs/
  
  # Nested keys
  python file_downloader.py --input file.json --key "documents.pdf_url" --output files/
  
  # Dry run
  python file_downloader.py --input data.json --key "Minutes" --output ./ --dry-run
  
  # Multiple city support
  python file_downloader.py --input Houston_TX/meetings.json --key "Download Agenda" --output Houston_TX/PDF/
  python file_downloader.py --input Columbus_OH/meetings.json --key "auto_minutes" --output Columbus_OH/PDF/
  python file_downloader.py --input Pomona_CA/meetings.json --key "Minutes" --output Pomona_CA/PDF/
        """
    )
    
    parser.add_argument('--input', required=True, help='Input JSON file or directory')
    parser.add_argument('--key', required=True, help='JSON key path to URL field (e.g., "Minutes", "Download Agenda", "auto_minutes", "documents.pdf")')
    parser.add_argument('--output', required=True, help='Output directory for downloaded files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded without downloading')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between downloads (seconds)')
    parser.add_argument('--max-workers', type=int, default=3, help='Maximum concurrent downloads')
    
    args = parser.parse_args()
    
    print(f"🚀 File Downloader Workflow")
    print(f"📂 Input: {args.input}")
    print(f"🔑 Key: {args.key}")
    print(f"📁 Output: {args.output}")
    print(f"⏱️  Delay: {args.delay}s")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be downloaded")
    
    # Initialize workflow
    workflow = DownloadWorkflow(args.output, args.delay, args.max_workers)
    
    # Process input and extract documents
    documents = workflow.process_input(args.input, args.key)
    
    # Download documents
    workflow.download_documents(documents, args.key, args.dry_run)
    
    # Print summary
    workflow.print_summary()


if __name__ == "__main__":
    main()
