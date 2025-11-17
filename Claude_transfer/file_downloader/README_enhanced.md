# Universal File Downloader Workflow

A flexible, intelligent file downloader that can extract URLs from JSON files and download files with smart filename generation. Supports multiple city data structures and formats.

## ✨ Features

### 🔍 Smart Structure Detection
- **Auto-detection modes**: `auto_minutes`, `auto_agenda`, `auto_pdf`
- **Partial key matching**: Find keys containing search terms (case-insensitive)  
- **PDF prioritization**: When multiple keys contain "Minutes", prefers PDF URLs over HTML
- **Multiple JSON structures**: Works with arrays, objects, and nested data

### 🏛️ Multi-City Support
- **Santa Ana** (PrimeGov): `Meeting Date`, `Meeting title`, `Agenda Packet`, `Minutes`
- **Houston** (NovusAgenda): `Meeting Date`, `Download Agenda`, `Minutes Recap`, `Legal Minutes`
- **Columbus** (Legistar): `Meeting Date`, `Agenda`, `Accessible Agenda`, `Minutes`, `Accessible Minutes`
- **Pomona** (Legistar): `Date`, `Agenda`, `Minutes`

### 📁 Smart Filename Generation
Format: `YYYYMMDD_doc_type_meeting_title.pdf`

**Examples:**
- `20241217_agenda_packet_regular_city_council_meeting.pdf`
- `20241203_minutes_council_meeting.pdf`
- `20241119_agenda_special_meeting.pdf`

**Features:**
- Parses multiple date formats: "Dec 25, 2024", "01/15/2024", "January 15, 2024"
- Detects document types from key paths: `agenda`, `minutes`, `packet`, `media`
- Cleans meeting titles from various fields
- Detects file extensions from URLs
- Prevents filename conflicts and handles long names

## 🚀 Usage

### Basic Commands

```bash
# Download Santa Ana agenda packets
python file_downloader.py --input "Santa_Ana_CA/json_files/meetings.json" --key "Agenda Packet" --output "Santa_Ana_CA/PDF"

# Download Houston agendas  
python file_downloader.py --input "Houston_TX/json_files/meetings.json" --key "Download Agenda" --output "Houston_TX/PDF"

# Download Pomona minutes
python file_downloader.py --input "Pomona_CA/json/meetings.json" --key "Minutes" --output "Pomona_CA/PDF"
```

### Auto-Detection Modes

```bash
# Auto-detect and download minutes (prefers PDF URLs)
python file_downloader.py --input "Columbus_OH/meetings.json" --key "auto_minutes" --output "Columbus_OH/PDF"

# Auto-detect and download agendas (prefers downloadable versions)
python file_downloader.py --input "Houston_TX/meetings.json" --key "auto_agenda" --output "Houston_TX/PDF"

# Auto-detect any PDF documents
python file_downloader.py --input "meetings.json" --key "auto_pdf" --output "PDF"
```

### Partial Matching

```bash
# Find keys containing "minutes" (case-insensitive)
python file_downloader.py --input "meetings.json" --key "minutes" --output "docs/"

# Find keys containing "agenda"
python file_downloader.py --input "data.json" --key "agenda" --output "agendas/"
```

### Additional Options

```bash
# Dry run - see what would be downloaded
python file_downloader.py --input "meetings.json" --key "Minutes" --output "docs/" --dry-run

# Custom delay between downloads
python file_downloader.py --input "meetings.json" --key "Agenda" --output "docs/" --delay 2.0

# Multiple concurrent downloads
python file_downloader.py --input "meetings.json" --key "Minutes" --output "docs/" --max-workers 5
```

## 📊 Smart Features in Action

### PDF Preference for Minutes
When multiple keys contain "minutes":
```json
{
  "Minutes Recap": "",  # Empty - skipped
  "Legal Minutes": "https://example.com/minutes.pdf",  # PDF - preferred
  "Minutes Link": "https://example.com/view.html"  # HTML - secondary
}
```
Result: Downloads the PDF version.

### Auto-Agenda Detection
```json
{
  "Online Agenda": "https://example.com/meeting.aspx",  # HTML
  "Download Agenda": "https://example.com/agenda.pdf"  # PDF - preferred  
}
```
Result: Downloads the PDF agenda.

### Flexible Date Parsing
Handles multiple formats:
- `"Dec 25, 2024"` → `20241225`
- `"01/15/2024"` → `20240115`  
- `"January 15, 2024"` → `20240115`

## 📁 Output Structure

```
Santa_Ana_CA/PDF/
├── 20241217_agenda_packet_regular_city_council_meeting.pdf (141.4 MB)
├── 20241203_agenda_packet_council_meeting.pdf (42.2 MB)
└── 20241119_agenda_packet_council_meeting.pdf (327.5 MB)

Columbus_OH/PDF/
├── 20241216_minutes_zoning_committee.pdf
├── 20241216_minutes_columbus_city_council.pdf
└── 20241209_minutes_zoning_committee.pdf
```

## 🛠️ Requirements

```bash
pip install -r requirements.txt
```

**Dependencies:**
- requests >= 2.25.0
- click >= 8.0.0  
- pathlib (built-in)

## 📈 Statistics & Monitoring

The downloader provides comprehensive statistics:
- Files processed and URLs found
- Downloads attempted, successful, skipped, failed
- Total bytes downloaded with human-readable formatting
- Detailed error reporting
- Progress tracking during downloads

## 🔧 Advanced Usage

### Directory Processing
```bash
# Process all JSON files in a directory
python file_downloader.py --input "data_directory/" --key "auto_minutes" --output "downloads/"
```

### Nested Key Paths
```bash
# Access nested JSON structures
python file_downloader.py --input "complex.json" --key "documents.meeting.pdf_url" --output "files/"
```

### Custom Document Types
The filename generator automatically detects document types:
- `agenda` → Creates filenames with "agenda"
- `minutes` → Creates filenames with "minutes"  
- `packet` → Creates filenames with "packet"
- `Agenda Packet` → Creates filenames with "agenda_packet"

## 🎯 Perfect For

- **City Council Data**: Multiple cities, different platforms
- **Meeting Documentation**: Agendas, minutes, packets
- **Bulk Downloads**: Process hundreds of documents efficiently  
- **Data Archiving**: Organized filename structure for easy retrieval
- **Research Projects**: Consistent data collection across sources

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_enhanced_downloader.py
```

Tests include:
- Columbus auto-minutes detection (62 documents)
- Houston auto-agenda detection with PDF preference (15 documents)
- Pomona partial matching for "Minutes" (32 documents)
- Santa Ana agenda packet matching (31 documents)
- Houston auto-PDF detection across all keys (15 documents)

## 🔄 Supported JSON Structures

### Simple Array Structure
```json
[
  {
    "Date": "Dec 17, 2024",
    "Meeting title": "Regular City Council Meeting", 
    "Agenda Packet": "https://example.com/agenda.pdf",
    "Minutes": "https://example.com/minutes.pdf"
  }
]
```

### Object with Extraction Info
```json
{
  "extraction_info": {
    "total_meetings": 25,
    "date_extracted": "2024-08-10"
  },
  "meetings": [
    {
      "Date": "01/15/2024",
      "Agenda": "https://example.com/agenda1.pdf"
    }
  ]
}
```

### Multi-Key Minutes Structure (Houston)
```json
{
  "Meeting Date": "January 9, 2024",
  "Download Agenda": "https://example.com/agenda.pdf",
  "Minutes Recap": "",
  "Legal Minutes": "https://example.com/legal_minutes.pdf"
}
```

### Legistar Structure (Columbus/Pomona)
```json
{
  "Meeting Date": "12/16/2024",
  "Agenda": "https://example.com/ViewAgenda.aspx?id=123",
  "Minutes": "https://example.com/ViewMinutes.pdf",
  "Accessible Minutes": "https://example.com/AccessibleMinutes.pdf"
}
```

## 🔧 Configuration Options

### Auto-Detection Mode Details

| Mode | Purpose | Logic |
|------|---------|-------|
| `auto_minutes` | Find best minutes key | Prefers PDF over HTML, handles empty values |
| `auto_agenda` | Find best agenda key | Prefers "Download" over "Online", PDF over HTML |
| `auto_pdf` | Find any PDF document | Searches all keys for PDF URLs |

### Filename Components

1. **Date** (YYYYMMDD): Parsed from meeting date fields
2. **Document Type**: Extracted from key name (agenda, minutes, packet)
3. **Meeting Title**: Cleaned from title/name fields, limited length
4. **Extension**: Detected from URL or defaults to .pdf

## 📚 Integration Examples

### With Existing Scrapers
```bash
# After running Pomona scraper
python scrapers/pomona_scraper.py
python file_downloader/file_downloader.py --input "Pomona_CA/json/" --key "auto_minutes" --output "Pomona_CA/PDF/"

# After running Santa Ana scraper  
python scrapers/santa_ana_scraper.py
python file_downloader/file_downloader.py --input "Santa_Ana_CA/json/" --key "Agenda Packet" --output "Santa_Ana_CA/PDF/"
```

### Batch Processing Multiple Cities
```bash
#!/bin/bash
# Download minutes from all cities
python file_downloader.py --input "Columbus_OH/json/" --key "auto_minutes" --output "Columbus_OH/PDF/"
python file_downloader.py --input "Houston_TX/json/" --key "auto_minutes" --output "Houston_TX/PDF/"
python file_downloader.py --input "Pomona_CA/json/" --key "Minutes" --output "Pomona_CA/PDF/"
python file_downloader.py --input "Santa_Ana_CA/json/" --key "Minutes" --output "Santa_Ana_CA/PDF/"
```

## 📞 Error Handling & Troubleshooting

### Common Issues

**No URLs found:**
- Check if the key name matches exactly (case-sensitive unless using partial matching)
- Try `auto_minutes` or `auto_agenda` modes for automatic detection
- Use `--dry-run` to see what keys are available

**Empty downloads:**
- Many JSON entries have empty URL values - this is normal
- The tool automatically skips empty URLs and reports statistics

**Filename conflicts:**
- Tool automatically handles duplicates by adding suffixes
- Long filenames are truncated to prevent filesystem issues

### Debug Mode
```bash
# See detailed processing information
python file_downloader.py --input "data.json" --key "Minutes" --output "docs/" --dry-run
```

## 🎉 Success Stories

- **Columbus**: Successfully downloaded 62 PDF minutes using auto-detection
- **Houston**: Intelligently selected PDF agendas over HTML versions (15 documents)  
- **Santa Ana**: Downloaded large agenda packets (100+ MB files) with proper filenames
- **Pomona**: Processed 32 minutes documents with flexible key matching

## 📄 License

Part of the CityData_extraction project. Use responsibly and respect website terms of service.
