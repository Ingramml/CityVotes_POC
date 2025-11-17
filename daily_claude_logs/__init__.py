"""
Claude Session Archiver Package
Global daily session archiver for Claude interactions across all projects
"""

from .claude_session_archiver import (
    ClaudeSessionArchiver,
    quick_capture,
    generate_daily_report,
    generate_weekly_report
)

from .session_capture import SessionCapture
from .daily_summarizer import DailySummarizer
from .file_reference_system import FileReferenceSystem
from .learning_insights_tracker import LearningInsightsTracker
from .weekly_review_generator import WeeklyReviewGenerator
from .setup_archiver import ArchiverSetup

__version__ = "1.0.0"
__author__ = "Claude Session Archiver System"

# Default archiver instance for easy use
_default_archiver = None

def get_default_archiver(project_root=None):
    """Get or create default archiver instance"""
    global _default_archiver
    if _default_archiver is None or (project_root and _default_archiver.project_root != project_root):
        _default_archiver = ClaudeSessionArchiver(project_root)
    return _default_archiver

# Convenience functions using default archiver
def start_session(project_root=None):
    """Start a session using default archiver"""
    return get_default_archiver(project_root).start_session()

def end_session(project_root=None):
    """End session using default archiver"""
    return get_default_archiver(project_root).end_session()

def capture(prompt, response, tool_calls=None, files_accessed=None, context=None, project_root=None):
    """Capture interaction using default archiver"""
    return get_default_archiver(project_root).capture_interaction(
        prompt, response, tool_calls, files_accessed, context
    )

def daily_summary(project_root=None, target_date=None):
    """Generate daily summary using default archiver"""
    return get_default_archiver(project_root).generate_daily_summary(target_date)

def weekly_review(project_root=None, end_date=None):
    """Generate weekly review using default archiver"""
    return get_default_archiver(project_root).generate_weekly_review(end_date)

def project_stats(project_root=None):
    """Get project statistics using default archiver"""
    return get_default_archiver(project_root).get_project_stats()

__all__ = [
    'ClaudeSessionArchiver',
    'SessionCapture',
    'DailySummarizer',
    'FileReferenceSystem',
    'LearningInsightsTracker',
    'WeeklyReviewGenerator',
    'ArchiverSetup',
    'quick_capture',
    'generate_daily_report',
    'generate_weekly_report',
    'get_default_archiver',
    'start_session',
    'end_session',
    'capture',
    'daily_summary',
    'weekly_review',
    'project_stats'
]