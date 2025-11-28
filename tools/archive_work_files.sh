#!/bin/bash
# Archive completed work files back to external storage

EXTERNAL_BASE="/Volumes/Samsung USB/City_extraction/Santa_Ana"
PROJECT_BASE="extractors/santa_ana"

YEAR=$1

if [ -z "$YEAR" ]; then
    echo "Usage: $0 YEAR"
    echo "Example: $0 2024"
    echo ""
    echo "This script archives extraction data (CSV/JSON) from the project"
    echo "back to external storage for permanent backup."
    exit 1
fi

# Check if external drive is mounted
if [ ! -d "$EXTERNAL_BASE" ]; then
    echo "❌ Error: External storage not found at $EXTERNAL_BASE"
    echo "   Please mount Samsung USB drive"
    exit 1
fi

# Create archive directory
mkdir -p "$EXTERNAL_BASE/$YEAR/extractions"

ARCHIVED=0

# Archive CSV files
if ls "$PROJECT_BASE/$YEAR/training_data"/*.csv 1> /dev/null 2>&1; then
    cp "$PROJECT_BASE/$YEAR/training_data"/*.csv \
       "$EXTERNAL_BASE/$YEAR/extractions/"
    echo "✅ Archived CSV files"
    ARCHIVED=$((ARCHIVED + 1))
fi

# Archive JSON files
if ls "$PROJECT_BASE/$YEAR/training_data"/*.json 1> /dev/null 2>&1; then
    cp "$PROJECT_BASE/$YEAR/training_data"/*.json \
       "$EXTERNAL_BASE/$YEAR/extractions/"
    echo "✅ Archived JSON files"
    ARCHIVED=$((ARCHIVED + 1))
fi

# Archive AI results if any
if [ -d "$PROJECT_BASE/$YEAR/ai_results" ] && [ "$(ls -A $PROJECT_BASE/$YEAR/ai_results)" ]; then
    mkdir -p "$EXTERNAL_BASE/$YEAR/ai_results"
    cp "$PROJECT_BASE/$YEAR/ai_results"/* \
       "$EXTERNAL_BASE/$YEAR/ai_results/"
    echo "✅ Archived AI results"
    ARCHIVED=$((ARCHIVED + 1))
fi

# Archive comparison results if any
if [ -d "$PROJECT_BASE/$YEAR/comparisons" ] && [ "$(ls -A $PROJECT_BASE/$YEAR/comparisons)" ]; then
    mkdir -p "$EXTERNAL_BASE/$YEAR/comparisons"
    cp "$PROJECT_BASE/$YEAR/comparisons"/* \
       "$EXTERNAL_BASE/$YEAR/comparisons/"
    echo "✅ Archived comparison results"
    ARCHIVED=$((ARCHIVED + 1))
fi

if [ $ARCHIVED -gt 0 ]; then
    echo ""
    echo "📦 Extraction data archived to external storage:"
    ls -lh "$EXTERNAL_BASE/$YEAR/extractions/"
else
    echo "⚠️  No files found to archive"
    exit 1
fi
