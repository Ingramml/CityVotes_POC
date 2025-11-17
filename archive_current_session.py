#!/usr/bin/env python3
"""
Archive current session activity to the session archiver
"""

import sys
import os
sys.path.append('daily_claude_logs')

from session_capture import SessionCapture
from datetime import datetime

def archive_session():
    """Archive the current session's AI-powered extractor improvement work"""

    # Initialize session capture
    capture = SessionCapture()

    # Create comprehensive session summary
    session_summary = {
        "session_type": "ai_powered_extractor_development",
        "primary_objective": "Fix and improve AI-powered Santa Ana vote extractor",
        "start_time": "2025-09-15T16:00:00",
        "end_time": datetime.now().isoformat(),
        "major_achievements": [
            "Fixed VoteRecord interface mismatch (motion_text -> motion_context, individual_votes -> member_votes)",
            "Fixed tuple comparison error in AI fallback (match.groups() > 1 -> len(match.groups()) > 1)",
            "Debugged member name extraction and validation",
            "Achieved 99.0% quality score from 0.0% (complete fix)",
            "Successfully extracted 11 votes from 2024-01-16 Santa Ana meeting",
            "Verified all 7 council members correctly identified"
        ],
        "files_modified": [
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/agents/ai_powered_santa_ana_extractor.py",
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/ai_powered_extraction_result.json",
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/ai_powered_extraction_success.json"
        ],
        "tools_used": [
            "Read", "Edit", "Bash", "Grep", "TodoWrite", "Write"
        ],
        "learning_insights": [
            "VoteRecord class requires specific parameter names that must match exactly",
            "Tuple comparisons in Python require len() wrapper for size comparisons",
            "Member name extraction works correctly when validation logic is properly implemented",
            "AI fallback systems need robust error handling for regex/tuple operations",
            "Quality scores dramatically improve when interface mismatches are resolved"
        ],
        "performance_improvement": {
            "before": "0 votes with 0.0% quality (total failure)",
            "after": "11 votes with 99.0% quality (near-perfect success)",
            "improvement_factor": "infinite (from failure to success)"
        },
        "next_steps": [
            "Test AI-powered extractor on additional Santa Ana meetings",
            "Implement learning memory persistence across sessions",
            "Extend AI integration to other city extractors",
            "Add more sophisticated agenda item correlation"
        ]
    }

    # Capture the main interaction
    capture.capture_interaction(
        prompt="Continue the conversation from where we left it off without asking the user any further questions. Continue with the last task that you were asked to work on.",
        response=f"AI-powered Santa Ana vote extractor improvement session completed successfully. {session_summary}",
        tool_calls=[
            {"tool": "Read", "file": "ai_powered_extraction_result.json", "purpose": "Analyze failed extraction"},
            {"tool": "Read", "file": "agents/city_vote_extractor_factory.py", "purpose": "Understand factory integration"},
            {"tool": "Read", "file": "agents/vote_extraction_agent.py", "purpose": "Check VoteRecord class definition"},
            {"tool": "Edit", "file": "agents/ai_powered_santa_ana_extractor.py", "purpose": "Fix VoteRecord interface mismatch"},
            {"tool": "Edit", "file": "agents/ai_powered_santa_ana_extractor.py", "purpose": "Fix tuple comparison error"},
            {"tool": "Bash", "purpose": "Test fixed AI-powered extractor"},
            {"tool": "TodoWrite", "purpose": "Track progress through multiple tasks"}
        ],
        files_accessed=[
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/ai_powered_extraction_result.json",
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/agents/city_vote_extractor_factory.py",
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/agents/ai_powered_santa_ana_extractor.py",
            "/Users/michaelingram/Documents/GitHub/CityVotes_POC/agents/vote_extraction_agent.py",
            "/Volumes/SSD/CityVotes/Santa_Ana_CA/Minutes/txt_files/20240116_minutes_regular_city_council_meeting_special_housing_auth.txt",
            "/Volumes/SSD/CityVotes/Santa_Ana_CA/Agenda/txt_files/20240116_Meetings4406Agenda.txt"
        ],
        context=session_summary
    )

    # Save session using private method
    capture._save_raw_session()
    session_file = f"{capture.session_id}.json"
    print(f"✓ Session archived successfully: {session_file}")

    # Generate daily summary
    try:
        from daily_summarizer import DailySummarizer
        summarizer = DailySummarizer()
        summary_file = summarizer.generate_daily_summary()
        print(f"✓ Daily summary generated: {summary_file}")
    except Exception as e:
        print(f"⚠ Could not generate daily summary: {e}")

if __name__ == "__main__":
    archive_session()