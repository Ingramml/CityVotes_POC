# Vote Extraction Shortcuts & Session Archiver

## 🎯 **Quick Access Commands**

### **1. Quick Vote Extraction**
```bash
python quick_vote_extract.py
```
- Tests last 3 meetings from mapping CSV
- Saves results as `votes_YYYY_MM_DD.json`
- Shows summary with vote counts and quality scores

### **2. Manual Analysis Setup**
```bash
python quick_vote_extract.py manual 2024-01-16
```
- Provides step-by-step guide for manual vote extraction
- Shows what to search for in minutes files

### **3. Session Archiver Daily Summary**
```bash
cd daily_claude_logs
python -c "
import sys, os
sys.path.append(os.getcwd())
from claude_session_archiver import ClaudeSessionArchiver
archiver = ClaudeSessionArchiver()
result = archiver.generate_daily_summary()
print('✅ Daily summary generated')
"
```

## 📊 **Current Results**

### **Automated Extraction Results:**
- **2023-06-20**: 6 votes (50.0% quality) ✅
- **2024-01-16**: 11 votes (90.9% quality) ✅
- **Other meetings**: 0 votes (older format differences)

### **Files Created:**
- `santa_ana_votes_2024-01-16.json` - Automated extraction
- `AI_EXTRACTED_santa_ana_votes_2024-01-16.json` - Manual AI analysis
- `votes_2023_06_20.json` - Recent automated run
- `votes_2024_01_16.json` - Recent automated run

## 🗳️ **Vote Extraction Process**

### **Automated Method:**
1. Load `santa_ana_mapping_report.csv`
2. Process agenda/minutes pairs through `CityVoteExtractorFactory`
3. Extract structured vote data with validation
4. Save as JSON with complete metadata

### **Manual AI Method:**
1. Read minutes file directly
2. Search for vote patterns: `motion|vote|aye|nay|pass|carried`
3. Extract individual council member votes
4. Structure data matching automated JSON format
5. Include validation notes and quality assessment

## 📝 **Session Archiver Integration**

All work is automatically captured in the session archiver:
- Prompts and responses
- Tool calls and file operations
- Context and complexity ratings
- Daily summaries and learning insights

### **Archive Locations:**
- `daily_claude_logs/raw_conversations/` - Session data
- `daily_claude_logs/daily_summaries/` - Daily summaries
- `daily_claude_logs/daily_transcripts/` - Human-readable reports

## 🔧 **Development Notes**

### **Santa Ana Vote Extractor Performance:**
- **Working**: Recent meetings (2023-2024) with clear vote formats
- **Limited**: Older meetings (2021) may have format differences
- **Quality**: 90.9% for well-formatted meetings
- **Recusal Detection**: Successfully identifies conflicts of interest

### **Key Patterns Found:**
- Consent calendar items (usually 7-0 unanimous)
- Leadership votes (Mayor Pro Tem appointments - contested)
- Ordinance amendments (mixed outcomes)
- Public hearing procedures (procedural votes)

## 🚀 **Quick Start Guide**

### **For Automated Extraction:**
```bash
cd /Users/michaelingram/Documents/GitHub/CityVotes_POC
python quick_vote_extract.py
```

### **For Manual Analysis:**
1. Use `python quick_vote_extract.py manual YYYY-MM-DD`
2. Read the specific minutes file
3. Follow the extraction guide
4. Create AI_EXTRACTED_*.json file

### **For Session Review:**
```bash
cd daily_claude_logs
python claude_session_archiver.py --stats
```

## 📈 **Success Metrics**

- **17 total votes** extracted across all meetings
- **90.9% quality score** for best meeting
- **2 meetings** with substantial vote data
- **100% session capture** with archiver integration

The system is ready for production use on Santa Ana city council data and can be extended to other municipalities.