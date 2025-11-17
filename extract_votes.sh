#!/bin/bash
# Quick Vote Extraction Shortcut
# Usage: ./extract_votes.sh [auto|manual] [options]

PROJECT_DIR="/Users/michaelingram/Documents/GitHub/CityVotes_POC"
cd "$PROJECT_DIR"

echo "🗳️  Vote Extraction Shortcut"
echo "Current directory: $(pwd)"
echo "=============================="

case "$1" in
    "auto")
        echo "🤖 Running automated extraction..."
        python vote_extraction_shortcut.py --auto --limit ${2:-10}
        ;;
    "manual")
        echo "🧠 Setting up manual analysis..."
        if [ -z "$2" ]; then
            echo "❌ Please provide date: ./extract_votes.sh manual 2024-01-16"
            exit 1
        fi
        echo "📅 Date: $2"
        echo "💡 Use Claude to analyze the minutes file for this date"
        echo "   Look for: motion, vote, aye, nay, pass, carried, approved"
        ;;
    "quick")
        echo "⚡ Quick extraction on Santa Ana mapping..."
        python -c "
from agents.city_vote_extractor_factory import CityVoteExtractorFactory
import csv

factory = CityVoteExtractorFactory()
with open('santa_ana_mapping_report.csv', 'r') as f:
    pairs = [r for r in csv.DictReader(f) if r['status'] == 'matched'][-3:]  # Last 3

for pair in pairs:
    result = factory.process_meeting_documents(pair['agenda_file'], pair['minutes_file'])
    votes = len(result.get('votes', []))
    print(f'{pair[\"date\"]}: {votes} votes ({'✅' if votes > 0 else '⚪'})')
"
        ;;
    "archive")
        echo "📝 Generating daily archive..."
        cd daily_claude_logs
        python claude_session_archiver.py --daily-summary
        python claude_session_archiver.py --stats
        ;;
    *)
        echo "Usage: ./extract_votes.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  auto [limit]    - Run automated extraction (default limit: 10)"
        echo "  manual <date>   - Set up manual analysis for specific date"
        echo "  quick          - Quick test on last 3 meetings"
        echo "  archive        - Generate daily archive and stats"
        echo ""
        echo "Examples:"
        echo "  ./extract_votes.sh auto 5"
        echo "  ./extract_votes.sh manual 2024-01-16"
        echo "  ./extract_votes.sh quick"
        echo "  ./extract_votes.sh archive"
        ;;
esac