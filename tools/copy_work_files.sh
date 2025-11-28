#!/bin/bash
# Copy specific text files from external storage to project

EXTERNAL_BASE="/Volumes/Samsung USB/City_extraction/Santa_Ana"
PROJECT_BASE="extractors/santa_ana"

# Usage: ./copy_work_files.sh 2024 20240220
YEAR=$1
MEETING_DATE=$2

if [ -z "$YEAR" ] || [ -z "$MEETING_DATE" ]; then
    echo "Usage: $0 YEAR MEETING_DATE"
    echo "Example: $0 2024 20240220"
    echo ""
    echo "This script copies text files from external storage to the project"
    echo "for active work on specific meetings."
    exit 1
fi

# Check if external drive is mounted
if [ ! -d "$EXTERNAL_BASE" ]; then
    echo "❌ Error: External storage not found at $EXTERNAL_BASE"
    echo "   Please mount Samsung USB drive"
    exit 1
fi

# Create target directory
mkdir -p "$PROJECT_BASE/$YEAR/source_documents"

COPIED=0

# Copy minutes
if ls "$EXTERNAL_BASE/$YEAR/text/minutes/${MEETING_DATE}_minutes"*.txt 1> /dev/null 2>&1; then
    cp "$EXTERNAL_BASE/$YEAR/text/minutes/${MEETING_DATE}_minutes"*.txt \
       "$PROJECT_BASE/$YEAR/source_documents/"
    echo "✅ Copied minutes file"
    COPIED=$((COPIED + 1))
else
    echo "⚠️  No minutes file found for $MEETING_DATE"
fi

# Copy agenda
if ls "$EXTERNAL_BASE/$YEAR/text/agenda/${MEETING_DATE}_agenda"*.txt 1> /dev/null 2>&1; then
    cp "$EXTERNAL_BASE/$YEAR/text/agenda/${MEETING_DATE}_agenda"*.txt \
       "$PROJECT_BASE/$YEAR/source_documents/"
    echo "✅ Copied agenda file"
    COPIED=$((COPIED + 1))
else
    echo "⚠️  No agenda file found for $MEETING_DATE"
fi

if [ $COPIED -gt 0 ]; then
    echo ""
    echo "📄 Files copied for $YEAR/$MEETING_DATE:"
    ls -lh "$PROJECT_BASE/$YEAR/source_documents/${MEETING_DATE}"*
else
    echo "❌ No files copied"
    exit 1
fi
