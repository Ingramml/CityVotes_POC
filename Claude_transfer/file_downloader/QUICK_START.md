# Quick Start Guide - Universal File Downloader

## 🚀 Most Common Use Cases

### 1. Download All Minutes (Any City)
```bash
python file_downloader.py --input "path/to/json/" --key "auto_minutes" --output "PDF/"
```
**What it does:** Automatically finds the best minutes key, prefers PDF over HTML

### 2. Download All Agendas (Any City)  
```bash
python file_downloader.py --input "path/to/json/" --key "auto_agenda" --output "PDF/"
```
**What it does:** Automatically finds the best agenda key, prefers downloadable versions

### 3. City-Specific Downloads

#### Santa Ana (Large Agenda Packets)
```bash
python file_downloader.py --input "Santa_Ana_CA/json/" --key "Agenda Packet" --output "Santa_Ana_CA/PDF/"
```

#### Houston (Smart Agenda Selection)
```bash
python file_downloader.py --input "Houston_TX/json/" --key "auto_agenda" --output "Houston_TX/PDF/"
# Chooses "Download Agenda" over "Online Agenda" automatically
```

#### Columbus (PDF Minutes Priority)
```bash
python file_downloader.py --input "Columbus_OH/json/" --key "auto_minutes" --output "Columbus_OH/PDF/"
# Chooses "Minutes" over "Accessible Minutes" when both exist
```

#### Pomona (Flexible Matching)
```bash
python file_downloader.py --input "Pomona_CA/json/" --key "Minutes" --output "Pomona_CA/PDF/"
```

## 🔍 Preview Before Downloading
Always test first:
```bash
python file_downloader.py --input "data.json" --key "auto_minutes" --output "PDF/" --dry-run
```

## 📁 Expected Output Filenames
- `20241217_agenda_packet_regular_city_council_meeting.pdf`
- `20241203_minutes_council_meeting.pdf`
- `20241119_agenda_special_meeting.pdf`

## 💡 Pro Tips

1. **Use auto-modes** (`auto_minutes`, `auto_agenda`) for new cities - they're smart!
2. **Always dry-run first** to see what will be downloaded
3. **PDF files are prioritized** automatically when multiple options exist
4. **Empty URLs are skipped** - don't worry about "0 downloads" if many entries are empty
5. **Files are never overwritten** - re-running is safe

## 📊 What Success Looks Like
```
✅ Downloads successful: 23
⏭️  Downloads skipped: 2 (already exist)
❌ Downloads failed: 0
💾 Total downloaded: 145.7 MB
```

## 🆘 Need Help?
- Run with `--dry-run` to see what would happen
- Check the main README_enhanced.md for full documentation
- Try `auto_minutes` or `auto_agenda` if specific keys don't work
