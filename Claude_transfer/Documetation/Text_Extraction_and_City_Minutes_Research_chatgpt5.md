# Deep Research: Text Extraction & City Council Minutes Production
*Prepared: 2025-09-12*

---

## Executive Summary
This report covers two domains:

1. **Text Extraction (from PDFs and web-published records)** — practical pipelines, tools, and models for converting agendas/minutes into structured data (roll calls, motions, outcomes).  
2. **City Minutes Production** — how municipalities create, approve, publish, retain, and make minutes accessible; key laws, workflows, and data standards.

It closes with **recommended architectures** and **model choices** for high‑accuracy, scalable extraction, plus evaluation checklists.

---

## Part I — Text Extraction (Agendas & Minutes)

### 1) Source Types & Challenges
- **Born-digital PDFs** (vector, selectable text): Prefer direct text extraction; preserve layout (headings, page numbers, footers).
- **Scanned PDFs** (raster images): Require OCR; be wary of rotation, skew, low DPI, highlights, stamps, and marginalia.
- **Hybrid PDFs** (text + image): Detect per-page/per-region whether OCR is needed (e.g., attachments, exhibits, signatures).
- **Portals & Variability**: Cities use platforms like Granicus/PrimeGov and Hyland OnBase/Agenda Online; templates and exports vary by city, year, and department.
- **Layout Diversity**: Minutes may include narrative paragraphs, action summaries, **roll‑call tables**, embedded motions, amendments, and late addenda.

### 2) End‑to‑End Extraction Pipeline (recommended)
1. **Ingest & Pre‑flight**
   - Normalize filenames; capture source URL, meeting date, body, agenda item IDs.
   - Detect text layer vs. image per page (e.g., PyMuPDF checks).
2. **Text Layer Extraction (if present)**
   - Use **PyMuPDF** or **pdfminer.six/pdfplumber** for faithful text and font/coords.
   - For tables: try pdfplumber; fall back to camelot/tabula when lines/ruled tables exist.
3. **OCR (when needed)**
   - Prefer **PaddleOCR (PP‑OCRv5)** or commercial OCR (Azure Document Intelligence / AWS Textract / Google Document AI) for noisy scans; ensure ≥300 DPI.
   - Preprocess: de‑skew, binarize, denoise; split long pages; correct rotation.
4. **Layout Analysis**
   - Detect blocks, headers/footers, page numbers, columns, and tables (layoutparser / DocLLM‑style parsers).
5. **Semantic Parsing**
   - Identify **meeting metadata** (date, body, location), **agenda items**, **motions**, **movers/seconds**, **vote outcomes**, and **individual votes**.
   - Use a hybrid: rules/regex for recurring phrases (”moved by…”, ”roll call”, ”ayes/noes/abstain/absent”), plus LLM prompts tuned on your city’s style.
6. **Schema Mapping**
   - Map to a consistent schema (see Part II Data Model), preserving **lineage**: page number, char offsets, table cell coordinates, and source file hash.
7. **Validation & QA**
   - Cross‑check totals (ayes + noes + abstain + absent = members present), quorum, motion pass/fail rules (simple majority, supermajority).
   - Human‑in‑the‑loop review for low‑confidence items; store confidences and diffs.
8. **Storage & Publishing**
   - Write normalized JSON + relational tables (Items, Motions, Votes, Members, Meeting). Retain original PDF and any OCR JSON for auditability.

### 3) Tooling Landscape (2025 snapshot)
- **Python libraries**
  - **PyMuPDF**: Fast, accurate text/coords; good for born‑digital.  
  - **pdfplumber**: Fine‑grained text & table heuristics; best when tables have explicit lines; struggles with borderless or irregular tables.  
  - **Camelot/Tabula**: Effective on ruled tables; less reliable on borderless tables.  
- **OCR engines**
  - **PaddleOCR (PP‑OCRv5)**: Strong accuracy‑to‑speed, multilingual; good on scans and receipts‑like structure.
  - **Tesseract**: Mature and free; needs careful configs; accuracy lower on tough layouts vs modern engines.
  - **Commercial**: **Azure AI Document Intelligence**, **Google Document AI**, **Amazon Textract** — superior layout, table, and key‑value extraction; offer confidence scores, training/customization, and SLAs.
- **Layout‑aware models**
  - **DocLLM / LayoutLM family / Donut / DocFormer**: Incorporate spatial layout with text for better reasoning about document structure; useful for locating roll‑call blocks, agenda headers, and signature pages.

### 4) Practical Patterns for Minutes
- **Roll‑call detection**: search for anchors (“Roll Call”, “Rollcall”, “Roll‑Call”, “Ayes”, “Nays”, “Absent”, “Abstain”), then parse nearby table/paragraph.
- **Motion parsing**: detect ”Moved by …, Seconded by …”; track amendments and substitute motions; tie the motion to the current agenda item.
- **Name normalization**: maintain a members dictionary with aliases/nicknames and historic rosters by term; join on nearest meeting date.
- **Edge cases**: consent agendas (bulk actions), tie votes (mayor breaks ties), recusals (conflicts), voice votes without individual roll calls, split votes across multi‑part motions.

### 5) Evaluation & Benchmarks
- **Document‑level**: precision/recall/F1 on (a) agenda item segmentation, (b) motions detected, (c) outcomes.  
- **Vote‑level**: accuracy on each member’s recorded vote; confusion with “absent vs. abstain vs. recused”.  
- **Page‑level**: OCR word/character error rate (CER/WER).  
- **Human QA rate**: % of items needing reviewer edits; target <5–10% after tuning.
- **Throughput**: pages/hour per core; GPU acceleration for OCR if needed.

---

## Part II — City Minutes Production (How Minutes Are Made & Published)

### 1) Legal & Policy Backdrop (U.S.)
- **Open Meeting / Sunshine laws** (state‑level) generally require public notice, agendas, and **written minutes** with date/time/place, attendees, and votes.  
- **ADA Title II (2024 DOJ rule)**: state & local government web content and mobile apps must be accessible; practical implication: **minutes and agenda PDFs must meet WCAG 2.2 AA** and **PDF/UA** where feasible.  
- **Section 508 (federal)**: accessibility requirements often adopted by local governments as best practice, especially for grants or shared portals.
- **Records retention**: state archives publish schedules designating permanent retention for approved minutes (and often recordings) and defining destruction workflows for drafts/notes.

### 2) Workflow in Clerk’s Offices
1. **Pre‑meeting**: agenda development, routing, packet assembly (staff reports, attachments), posting to portal ≥24–72 hours in advance (varies by state).  
2. **During meeting**: roll call; motions/moves/seconds; votes; public comment; timer and speaker management in the meeting system.  
3. **Post‑meeting**: draft minutes, legal review, approval at next meeting, **publication** (portal + PDF + sometimes HTML and video bookmarks), archival (records repository), and retention logging.

**Common platforms**: **Granicus (Peak/OneMeeting/PrimeGov)** and **Hyland OnBase/Agenda Online** — provide templates for agendas/minutes, voting modules, and integrated publishing (PDF + web portal + video markers).

### 3) Accessibility & Format Requirements
- **PDF/UA & tagged PDFs**: headings, lists, tables correctly tagged; reading order set; images with alt text; tables with header cells; embedded fonts.  
- **WCAG 2.2 AA** (if using HTML portals): keyboard navigation, focus visibility, target sizes, error prevention, proper link names.  
- **Testing**: use Acrobat Accessibility Checker + PAC, plus manual screen‑reader tests; fix failures before publication.
- **Video**: captions/transcripts; link timestamps to agenda items when possible.

### 4) Records Retention & Archiving
- Approved minutes are typically **permanent records**; recordings often retained for a defined period (e.g., months/years) per state schedule.  
- Maintain **authenticity & integrity**: store original export plus a checksum; keep metadata (meeting date, body, agenda item IDs).  
- Follow state archives guidance for destruction of drafts and the logging of destroyed records.

### 5) Data & Metadata Model (recommended)
Core tables:
- **Meeting**: id, body, date/time, location, quorum present, source URLs, file hashes.  
- **Member**: id, name, seat (district/at‑large), role (mayor, chair), term start/end.  
- **AgendaItem**: id, meeting_id, number, title, department, category, consent flag.  
- **Motion**: id, agenda_item_id, text, moved_by, seconded_by, type (main/amendment/substitute), requires_supermajority flag.  
- **Vote**: id, motion_id, member_id, value (Y/N/Abstain/Absent/Recused), timestamp/page ref, confidence.  
- **Attachment**: id, agenda_item_id, type, url/path, checksum.  

Metadata standards to consider: **DCAT‑US** for dataset publishing; **NIEM/IEPD** approach if exchanging structured minutes between systems; **Akoma Ntoso** concepts for legislative acts (adapted to local‑gov context).

---

## Part III — Reference Architectures

### A) Cost‑sensitive, Open‑source First
- Extract with **PyMuPDF** (text + coordinates); **pdfplumber** for tables; OCR fallback with **PaddleOCR**.  
- Layout detection with **layoutparser**; LLM (**DocLLM‑style** open implementations) to label sections; rules for motions/votes.  
- Store JSON + Postgres (with lineage) and surface a human review UI (Streamlit/FastAPI).

### B) Accuracy‑first, Cloud Document AI
- Ingest to **Azure AI Document Intelligence** or **Google Document AI**: use OCR + table extraction + **Custom Extractor/Adapter** to learn your city’s template patterns.  
- Post‑process with a general LLM only for light normalization and edge‑case reasoning.  
- Benefit: higher table/kv accuracy, confidence scores, and ongoing model updates; trade‑off: vendor cost + data residency constraints.

### C) Hybrid
- Route by **document quality**: born‑digital → PyMuPDF path; scanned/noisy → cloud OCR path; always normalize & validate in the same schema.  
- Maintain gold‑truth samples and periodic evaluation to keep drift in check.

---

## Part IV — Model Recommendations (What’s “best”?)

**For structured extraction at scale from heterogeneous minutes (PDFs with tables & narrative):**  
- **Best-in-class** today is a **specialized Document AI service** (Azure AI Document Intelligence _Custom_ / Google Document AI _Custom Extractor_ / AWS Textract with adapters) for OCR + table/KV capture, **plus** a light LLM/rule layer to interpret motions and outcomes. These systems consistently outperform general chat models on table fidelity, cell spanning, and confidence reporting, and they ship with dashboards for ongoing evaluation.  
- **Open-source stack**: **PaddleOCR (PP‑OCRv5)** + **PyMuPDF/pdfplumber** + a **layout‑aware model** (DocLLM/LayoutLMv3/Donut) can achieve strong accuracy with tuning, zero vendor lock‑in, and lower marginal cost—at the expense of more engineering and MLOps.
- **Where a chat model shines**: summarization, cross‑checking logic (e.g., quorum math), and drafting exception reports—**after** high‑quality extraction has produced structured data.

**Bottom line**: choose **Cloud Document AI + custom extractor** if you need reliability with minimal ML ops; choose **Open‑source hybrid** if you want control and can invest in pipeline tuning. Use an LLM (like GPT‑class) as the reasoning layer, not your primary table parser.

---

## Part V — Implementation Checklists

### Extraction QA
- [ ] DPI ≥ 300; skew < 1°; no page rotation issues.  
- [ ] Tag detection: roll‑call/”ayes/noes/abstain/absent/recused”.  
- [ ] Vote sums match members present; quorum satisfied; majority threshold met.  
- [ ] All agenda items mapped; consent agenda expanded.  
- [ ] Lineage stored: page#, bbox/coords, table cell id, source checksum.

### Accessibility & Publishing
- [ ] PDFs are tagged (PDF/UA where feasible), pass automated checks, and have manual screen‑reader verification.  
- [ ] HTML portal meets **WCAG 2.2 AA** (keyboard, focus, target size, labels).  
- [ ] Video captions/transcripts linked to items; timestamps verified.  
- [ ] Retention schedule applied; destruction logs maintained for drafts.

---

## Selected Sources (linked)
- Open meeting/notice/minutes requirements (example state FAQs & guides).  
- ADA Title II 2024 final rule for state/local web content.  
- Section 508 & accessible PDF how‑tos.  
- PDF/UA standard & updates; WCAG 2.2.  
- Municipal platforms: **Granicus (Peak/OneMeeting/PrimeGov)**; **Hyland OnBase/Agenda Online**.  
- Tools & benchmarks: PyMuPDF, pdfplumber, PaddleOCR/PP‑OCRv5, Azure Document Intelligence, Google Document AI, AWS Textract; layout‑aware research (DocLLM).

> **Tip:** Keep a small gold‑standard set of minutes across years and bodies to continuously evaluate pipeline changes. Log every parser decision with confidence and expose a one‑click “show me the page region” in your review UI.

---

*© 2025. Prepared for research and engineering planning. This report is not legal advice; verify compliance with your jurisdiction’s statutes and retention schedules.*
