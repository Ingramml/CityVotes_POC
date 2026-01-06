# Santa Ana Public Documents Extraction - LLM Execution Guide

## Overview
This document provides comprehensive technical instructions for an LLM to programmatically extract agenda and minutes documents from the City of Santa Ana's Laserfiche WebLink 9 public document repository.

---

## Target System Technical Details

### Platform Information
- **System**: Laserfiche WebLink 9
- **Base URL**: `https://publicdocs.santa-ana.org/WebLink/`
- **Technology**: ASP.NET WebForms
- **Session Management**: Cookie-based authentication (cookies REQUIRED)

### Critical Technical Constraints
1. **Cookies are mandatory** - The system will not function without cookies enabled
2. **JavaScript postbacks** - Navigation uses `__doPostBack()` function calls
3. **Session state** - ASP.NET ViewState must be maintained across requests
4. **No public REST API** - Must use web scraping approach via page URLs

---

## URL Structure Reference

### Page Types and Their URLs

| Page | Purpose | URL Pattern |
|------|---------|-------------|
| `Browse.aspx` | Folder navigation | `/WebLink/Browse.aspx?startid={FOLDER_ID}&dbid={DB_ID}` |
| `DocView.aspx` | Document viewer | `/WebLink/DocView.aspx?id={DOC_ID}&dbid={DB_ID}` |
| `ElectronicFile.aspx` | File download | `/WebLink/ElectronicFile.aspx?docid={DOC_ID}&dbid={DB_ID}` |
| `Welcome.aspx` | Landing page | `/WebLink/Welcome.aspx` |
| Folder row | Direct folder access | `/WebLink/1/fol/{FOLDER_ID}/Row1.aspx` |
| Document page | Document page view | `/WebLink/0/doc/{DOC_ID}/Page1.aspx` |

### Key URL Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `startid` | Starting folder ID for Browse.aspx | `startid=32945` |
| `dbid` | Database ID (often 0 or 1 for Santa Ana) | `dbid=1` |
| `id` | Document or folder entry ID | `id=645899` |
| `docid` | Document ID for ElectronicFile.aspx | `docid=12345` |
| `page` | Page number within document | `page=1` |
| `openfile` | Trigger download for electronic files | `openfile=true` |
| `openpdf` | Download as PDF | `openpdf=true` |
| `cr` | Cache refresh flag | `cr=1` |

### Direct Download URL Formats

```
# Download electronic document (PDF, etc.)
https://publicdocs.santa-ana.org/WebLink/DocView.aspx?id={DOC_ID}&dbid=1&openfile=true

# Download as PDF
https://publicdocs.santa-ana.org/WebLink/DocView.aspx?id={DOC_ID}&dbid=1&openpdf=true

# Electronic file direct download
https://publicdocs.santa-ana.org/WebLink/ElectronicFile.aspx?docid={DOC_ID}&dbid=1
```

---

## HTML Structure Analysis

### Folder/Document Browser Table Structure

The document browser uses an HTML table with the following structure:

```html
<tbody>
  <tr ondblclick="__doPostBack('TheDocumentBrowser:_ctl{N}:_ctl3','');">
    <td class="DocumentBrowserCell">
      <a href="1/fol/{FOLDER_ID}/Row1.aspx"
         class="DocumentBrowserNameLink"
         aria-label="{FOLDER_NAME} Folder"
         onclick="__doPostBack('TheDocumentBrowser:_ctl{N}:_ctl3','');">
        <nobr>
          <img src="images/iFolderClosed.gif" class="DocumentBrowserNameImage">
          <span>{FOLDER_NAME}</span>
        </nobr>
      </a>
    </td>
    <td class="DocumentBrowserCell" aria-label="Page count {VALUE}">...</td>
    <td class="DocumentBrowserCell" aria-label="Is indexed {VALUE}">...</td>
    <td class="DocumentBrowserCell" aria-label="Date created {DATE}">...</td>
    <td class="DocumentBrowserCell" aria-label="Date modified {DATE}">...</td>
    <td class="DocumentBrowserCell" aria-label="Volume name {VALUE}">...</td>
    <td class="DocumentBrowserCell" aria-label="Template name {VALUE}">...</td>
  </tr>
</tbody>
```

### Key CSS Classes for Parsing

| Class | Purpose |
|-------|---------|
| `DocumentBrowserCell` | Table cell containing data |
| `DocumentBrowserNameLink` | Clickable link to folder/document |
| `DocumentBrowserNameImage` | Icon indicating folder/document type |
| `DocumentBrowserAlternateRow` | Alternating row styling |
| `DocumentBrowserError` | Error message container |

### Icon Types

| Icon File | Meaning |
|-----------|---------|
| `iFolderClosed.gif` | Folder (closed) |
| `iFolderOpen.gif` | Folder (open) |
| `iDocument.gif` | Standard document |
| `iPDF.gif` | PDF document |

### Extracting Entry Information

From each row, extract:
1. **Entry ID**: From `href` attribute - pattern `1/fol/{ID}/Row1.aspx` or `0/doc/{ID}/Page1.aspx`
2. **Entry Name**: From `<span>` inside the link or `aria-label` attribute
3. **Entry Type**: From icon image filename or href pattern (`fol` = folder, `doc` = document)
4. **Dates**: From `aria-label` attributes containing "Date created" and "Date modified"

---

## Document Categories and Folder IDs

### Primary Folders

| Folder Name | Folder ID | Direct URL |
|-------------|-----------|------------|
| **Agenda Packets / Staff Reports** | 32945 | `Browse.aspx?startid=32945&dbid=1` |
| **Minutes** | 73985 | `Browse.aspx?startid=73985` |
| Articles of Incorporation | 31974 | `Browse.aspx?startid=31974` |
| Contracts / Agreements | 6 | `Browse.aspx?startid=6` |
| eComments | 113669 | `Browse.aspx?startid=113669` |
| Lobbyist Registration Forms | 136109 | `Browse.aspx?startid=136109` |
| Ordinances | 3 | `Browse.aspx?startid=3` |
| PBA | 53154 | `Browse.aspx?startid=53154` |
| Policies | 82479 | `Browse.aspx?startid=82479` |
| Resolutions | 4 | `Browse.aspx?startid=4` |
| Open Calendars | 73475 | `Browse.aspx?startid=73475` |

---

## Task 1: Extract Agenda Files

### Source Information
- **Starting URL**: `https://publicdocs.santa-ana.org/WebLink/Browse.aspx?startid=32945&dbid=1`
- **Folder Path**: `1/fol/32945/Row1.aspx`
- **Target Folder Name**: "Agenda Packets / Staff Reports"

### Folder Hierarchy
```
Agenda Packets / Staff Reports (ID: 32945)
└── [Year Folders] (e.g., "2024", "2023", etc.)
    └── [Meeting Date Folders] (e.g., "January 15, 2024")
        ├── Agenda_YYYY-MM-DD.pdf
        └── [Staff Report files]
```

### File Identification
- **Naming Pattern**: `Agenda_YYYY-MM-DD` (e.g., `Agenda_2024-01-15`)
- **File Type**: PDF documents
- **Text Access**: Look for "View Plain Text" link option on document page

### Extraction Algorithm

```
1. Navigate to Browse.aspx?startid=32945&dbid=1
2. Parse HTML to find all folder rows (class="DocumentBrowserNameLink", href contains "fol")
3. For each YEAR FOLDER found:
   a. Extract folder ID from href pattern "1/fol/{ID}/Row1.aspx"
   b. Navigate to that folder
   c. Parse to find MEETING DATE FOLDERS
   d. For each MEETING FOLDER:
      i. Navigate to folder
      ii. Find documents matching "Agenda_" pattern
      iii. For each agenda document:
          - Extract document ID from href pattern "0/doc/{ID}/Page1.aspx"
          - Access DocView.aspx?id={DOC_ID}&dbid=1
          - Look for "View Plain Text" link
          - Extract plain text content
          - Save to file: Agenda_YYYY-MM-DD.txt
4. Implement pagination handling if folder has multiple pages
```

---

## Task 2: Extract Minutes Files

### Source Information
- **Starting URL**: `https://publicdocs.santa-ana.org/WebLink/Browse.aspx?startid=73985`
- **Folder Path**: `1/fol/73985/Row1.aspx`
- **Target Folder Name**: "Minutes"

### Folder Hierarchy
```
Minutes (ID: 73985)
└── [Year Range Folders] (e.g., "2020-2024", "2015-2019")
    └── [Individual Year Folders] (e.g., "2024", "2023")
        └── Minutes_YYYY-MM-DD.pdf (or similar naming)
```

### Extraction Algorithm

```
1. Navigate to Browse.aspx?startid=73985
2. Parse HTML to find YEAR RANGE folders
3. For each YEAR RANGE FOLDER:
   a. Navigate into folder
   b. Find INDIVIDUAL YEAR folders
   c. For each YEAR FOLDER:
      i. Navigate to folder
      ii. Find all PDF documents
      iii. For each document:
          - Extract document ID
          - Access DocView.aspx?id={DOC_ID}&dbid=1
          - Look for "View Plain Text" link
          - Extract plain text content
          - Save with original filename + .txt extension
4. Handle pagination for large folders
```

---

## Technical Implementation Guidance

### HTTP Request Requirements

```
Required Headers:
- User-Agent: [Standard browser user agent]
- Accept: text/html,application/xhtml+xml,application/xml
- Accept-Language: en-US,en
- Cookie: [Session cookies - must persist across requests]

Cookie Handling:
- Accept all cookies from initial request
- Maintain cookie jar throughout session
- ASP.NET_SessionId cookie is critical
```

### ViewState Handling

ASP.NET WebForms uses ViewState for state management:
1. Extract `__VIEWSTATE` and `__VIEWSTATEGENERATOR` from each page
2. Include these in POST requests for navigation
3. For postback navigation, POST to same URL with:
   - `__EVENTTARGET`: The control identifier (e.g., `TheDocumentBrowser:_ctl41:_ctl3`)
   - `__EVENTARGUMENT`: Usually empty
   - `__VIEWSTATE`: The full viewstate string
   - `__VIEWSTATEGENERATOR`: The generator value

### Postback Navigation

When JavaScript `__doPostBack('control','arg')` is encountered:
```
POST to current page URL with form data:
__EVENTTARGET=control (replace : with $ for form field)
__EVENTARGUMENT=arg
__VIEWSTATE=[current viewstate]
__VIEWSTATEGENERATOR=[current generator]
```

### Rate Limiting Recommendations
- Minimum 1-2 second delay between requests
- Respect any retry-after headers
- Implement exponential backoff on errors

### Error Handling
- Handle HTTP 500 errors (common with invalid viewstate)
- Retry on timeout errors
- Log all failed document IDs for later retry
- Check for "session expired" messages

---

## Output Specifications

### Directory Structure
```
output/
├── agendas/
│   ├── 2024/
│   │   ├── Agenda_2024-01-15.txt
│   │   └── Agenda_2024-02-05.txt
│   ├── 2023/
│   └── ...
├── minutes/
│   ├── 2024/
│   │   ├── Minutes_2024-01-15.txt
│   │   └── ...
│   └── ...
└── metadata.json
```

### Metadata JSON Format
```json
{
  "extraction_date": "2024-XX-XX",
  "documents": [
    {
      "type": "agenda",
      "doc_id": 12345,
      "filename": "Agenda_2024-01-15.txt",
      "original_url": "...",
      "date_created": "...",
      "date_modified": "..."
    }
  ]
}
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Cookies not enabled" error | Missing or expired cookies | Refresh session, ensure cookie persistence |
| Empty page response | Invalid ViewState | Re-fetch page to get fresh ViewState |
| 500 Internal Server Error | Malformed postback request | Check EVENTTARGET format (use $ not :) |
| Missing documents | Pagination not handled | Check for pagination controls on page |
| Text not available | No plain text option | Download PDF and use OCR/PDF extraction |

### Testing Recommendations
1. Test with single document first
2. Verify cookie persistence across requests
3. Log all request/response cycles for debugging
4. Test pagination with folders known to have many items

---

## Resources

- [Laserfiche WebLink Documentation](https://doc.laserfiche.com/laserfiche.documentation/11/userguide/en-us/Subsystems/WebLink/Content/Introduction.htm)
- [WebLink URL Parameters](https://support.laserfiche.com/kb/1001086/constructing-a-weblink-url-that-links-to-a-document-or-folder)
- [Laserfiche Developer Documentation](https://developer.laserfiche.com/)
- [WebLink Direct Download Discussion](https://answers.laserfiche.com/questions/173968/Laserfiche-Weblink-9-direct-download)
- [WebLink Pages Reference](https://answers.laserfiche.com/questions/55684/Weblink-pages)
