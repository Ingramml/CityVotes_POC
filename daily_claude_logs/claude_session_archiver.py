#!/usr/bin/env python3
"""
Claude Session Archiver - Main Agent Class
Global daily session archiver for Claude interactions across all projects
"""

import json
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import all components
from session_capture import SessionCapture
from daily_summarizer import DailySummarizer
from file_reference_system import FileReferenceSystem
from learning_insights_tracker import LearningInsightsTracker
from weekly_review_generator import WeeklyReviewGenerator


class ClaudeSessionArchiver:
    """
    Main archiver agent that coordinates all logging and analysis components.
    Designed to be global across all projects.
    """

    def __init__(self, project_root: str = None, auto_initialize: bool = True):
        """
        Initialize the Claude Session Archiver

        Args:
            project_root: Root directory of the project. If None, uses current directory
            auto_initialize: Whether to automatically set up directory structure
        """
        self.project_root = project_root or os.getcwd()
        self.logs_dir = os.path.join(self.project_root, "daily_claude_logs")

        # Initialize all components
        self.session_capture = SessionCapture(self.project_root)
        self.daily_summarizer = DailySummarizer(self.project_root)
        self.file_system = FileReferenceSystem(self.project_root)
        self.insights_tracker = LearningInsightsTracker(self.project_root)
        self.weekly_generator = WeeklyReviewGenerator(self.project_root)

        # Current session state
        self.current_session = None
        self.is_active = False

        if auto_initialize:
            self.initialize_project()

    def initialize_project(self):
        """Initialize the daily_claude_logs structure in a new project"""
        try:
            # Create directory structure
            dirs_to_create = [
                "raw_conversations",
                "daily_summaries",
                "daily_transcripts",
                "learning_insights",
                "weekly_reviews",
                "file_references",
                "file_references/content_cache"
            ]

            for dir_name in dirs_to_create:
                dir_path = os.path.join(self.logs_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)

            # Create initialization marker
            init_file = os.path.join(self.logs_dir, "archiver_initialized.json")
            init_data = {
                "initialized_at": datetime.now().isoformat(),
                "project_root": self.project_root,
                "archiver_version": "1.0",
                "components": [
                    "session_capture",
                    "daily_summarizer",
                    "file_reference_system",
                    "learning_insights_tracker",
                    "weekly_review_generator"
                ]
            }

            with open(init_file, 'w') as f:
                json.dump(init_data, f, indent=2)

            return True

        except Exception as e:
            print(f"Error initializing project: {e}")
            return False

    def start_session(self) -> str:
        """Start a new Claude session"""
        if self.is_active:
            self.end_session()

        self.current_session = self.session_capture
        self.is_active = True

        session_id = self.current_session.session_id
        print(f"Started Claude session: {session_id}")
        return session_id

    def end_session(self) -> Dict:
        """End current session and return session statistics"""
        if not self.is_active or not self.current_session:
            return {"error": "No active session"}

        stats = self.current_session.get_session_stats()
        self.is_active = False

        # Auto-generate daily summary if this was a significant session
        if stats.get("interactions", 0) > 5:
            self.generate_daily_summary()

        return stats

    def capture_interaction(self, prompt: str, response: str,
                          tool_calls: List[Dict] = None,
                          files_accessed: List[str] = None,
                          context: Dict = None):
        """
        Capture a Claude interaction with comprehensive logging

        Args:
            prompt: User's prompt/question
            response: Claude's response
            tool_calls: List of tool calls made during interaction
            files_accessed: List of file paths accessed
            context: Additional context information
        """
        if not self.is_active:
            self.start_session()

        # Process file references efficiently
        processed_files = []
        if files_accessed:
            for file_path in files_accessed:
                try:
                    # Read file content if it exists and is reasonable size
                    content = None
                    if os.path.exists(file_path) and os.path.getsize(file_path) < 1024 * 1024:  # < 1MB
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                    # Create efficient file reference
                    file_ref = self.file_system.create_file_reference(
                        file_path, content,
                        operation=self._determine_file_operation(tool_calls, file_path)
                    )
                    processed_files.append(file_ref)

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

        # Capture the interaction
        self.current_session.capture_interaction(
            prompt=prompt,
            response=response,
            tool_calls=tool_calls or [],
            files_accessed=files_accessed or [],
            context=context or {}
        )

        return {
            "captured": True,
            "session_id": self.current_session.session_id,
            "files_processed": len(processed_files)
        }

    def _determine_file_operation(self, tool_calls: List[Dict], file_path: str) -> str:
        """Determine the type of operation performed on a file"""
        if not tool_calls:
            return "unknown"

        for tool_call in tool_calls:
            tool_name = tool_call.get("tool_name", "").lower()
            if tool_name in ["write", "edit", "multiedit"]:
                return "write"
            elif tool_name in ["read"]:
                return "read"
            elif tool_name in ["bash"] and any(cmd in str(tool_call.get("parameters", {})).lower()
                                              for cmd in ["rm", "mv", "cp"]):
                return "system_operation"

        return "read"  # Default assumption

    def generate_daily_summary(self, target_date: date = None) -> Dict:
        """Generate daily summary and insights"""
        try:
            # Generate daily summary
            summary = self.daily_summarizer.generate_daily_summary(target_date)

            # Generate learning insights
            insights = self.insights_tracker.analyze_daily_patterns(target_date)

            # Generate human-readable summary
            readable_summary = self.daily_summarizer.generate_human_readable_summary(target_date)

            # Save readable summary to daily_transcripts
            if target_date is None:
                target_date = date.today()

            date_str = target_date.strftime("%Y-%m-%d")
            transcript_path = os.path.join(self.logs_dir, "daily_transcripts", f"daily_transcript_{date_str}.md")

            with open(transcript_path, 'w') as f:
                f.write(readable_summary)

            return {
                "summary": summary,
                "insights": insights,
                "transcript_saved": transcript_path
            }

        except Exception as e:
            return {"error": f"Failed to generate daily summary: {e}"}

    def generate_weekly_review(self, end_date: date = None) -> Dict:
        """Generate comprehensive weekly review"""
        try:
            review = self.weekly_generator.generate_weekly_review(end_date)

            # Generate human-readable review
            readable_review = self.weekly_generator.generate_human_readable_review(end_date)

            # Save readable review
            if end_date is None:
                end_date = date.today()

            start_date = end_date - date.timedelta(days=6)
            review_filename = f"weekly_review_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.md"
            review_path = os.path.join(self.logs_dir, "weekly_reviews", review_filename)

            with open(review_path, 'w') as f:
                f.write(readable_review)

            return {
                "review": review,
                "readable_review_saved": review_path
            }

        except Exception as e:
            return {"error": f"Failed to generate weekly review: {e}"}

    def get_session_status(self) -> Dict:
        """Get current session status and statistics"""
        if not self.is_active or not self.current_session:
            return {
                "active": False,
                "message": "No active session"
            }

        stats = self.current_session.get_session_stats()

        return {
            "active": True,
            "session_id": stats["session_id"],
            "duration_minutes": stats["duration_minutes"],
            "interactions": stats["interactions"],
            "files_referenced": stats["files_referenced"],
            "tools_used": stats["unique_tools_used"]
        }

    def get_project_stats(self) -> Dict:
        """Get overall project statistics"""
        try:
            # Count files in each directory
            stats = {
                "project_root": self.project_root,
                "logs_directory": self.logs_dir,
                "daily_summaries": len(os.listdir(os.path.join(self.logs_dir, "daily_summaries"))),
                "learning_insights": len(os.listdir(os.path.join(self.logs_dir, "learning_insights"))),
                "weekly_reviews": len(os.listdir(os.path.join(self.logs_dir, "weekly_reviews"))),
                "raw_conversations": len(os.listdir(os.path.join(self.logs_dir, "raw_conversations")))
            }

            # Get file system stats
            storage_stats = self.file_system.get_storage_stats()
            stats["storage_efficiency"] = storage_stats

            return stats

        except Exception as e:
            return {"error": f"Failed to get project stats: {e}"}

    def cleanup_old_data(self, days_old: int = 30):
        """Clean up old cached data"""
        try:
            # Cleanup file references
            self.file_system.cleanup_old_content(days_old)

            return {"success": True, "days_cleaned": days_old}

        except Exception as e:
            return {"error": f"Failed to cleanup: {e}"}

    def export_project_data(self, export_path: str = None) -> Dict:
        """Export all project data to a specified location"""
        if export_path is None:
            export_path = os.path.join(self.project_root, f"claude_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        try:
            import shutil

            # Copy entire logs directory
            shutil.copytree(self.logs_dir, export_path)

            # Create export metadata
            metadata = {
                "exported_at": datetime.now().isoformat(),
                "source_project": self.project_root,
                "export_path": export_path,
                "project_stats": self.get_project_stats()
            }

            metadata_path = os.path.join(export_path, "export_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            return {
                "success": True,
                "export_path": export_path,
                "metadata": metadata
            }

        except Exception as e:
            return {"error": f"Failed to export data: {e}"}

    @classmethod
    def create_global_archiver(cls, base_directory: str = None) -> 'ClaudeSessionArchiver':
        """
        Create a global archiver that can be used across multiple projects

        Args:
            base_directory: Base directory for global logs (default: user home)
        """
        if base_directory is None:
            base_directory = os.path.expanduser("~/.claude_global_logs")

        return cls(project_root=base_directory, auto_initialize=True)

    def __enter__(self):
        """Context manager entry"""
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.end_session()


# Convenience functions for easy usage
def quick_capture(prompt: str, response: str, files_accessed: List[str] = None,
                 project_root: str = None):
    """Quick function to capture a single interaction"""
    archiver = ClaudeSessionArchiver(project_root)
    return archiver.capture_interaction(prompt, response, files_accessed=files_accessed)

def generate_daily_report(project_root: str = None, target_date: date = None):
    """Quick function to generate daily report"""
    archiver = ClaudeSessionArchiver(project_root)
    return archiver.generate_daily_summary(target_date)

def generate_weekly_report(project_root: str = None, end_date: date = None):
    """Quick function to generate weekly report"""
    archiver = ClaudeSessionArchiver(project_root)
    return archiver.generate_weekly_review(end_date)


if __name__ == "__main__":
    """CLI interface for the archiver"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude Session Archiver")
    parser.add_argument("--init", action="store_true", help="Initialize archiver in current directory")
    parser.add_argument("--daily-summary", action="store_true", help="Generate daily summary")
    parser.add_argument("--weekly-review", action="store_true", help="Generate weekly review")
    parser.add_argument("--stats", action="store_true", help="Show project statistics")
    parser.add_argument("--cleanup", type=int, metavar="DAYS", help="Cleanup data older than DAYS")
    parser.add_argument("--export", metavar="PATH", help="Export all data to PATH")
    parser.add_argument("--project-root", metavar="PATH", help="Project root directory")

    args = parser.parse_args()

    archiver = ClaudeSessionArchiver(args.project_root)

    if args.init:
        if archiver.initialize_project():
            print("✅ Archiver initialized successfully")
        else:
            print("❌ Failed to initialize archiver")

    elif args.daily_summary:
        result = archiver.generate_daily_summary()
        if "error" not in result:
            print("✅ Daily summary generated")
            print(f"📄 Transcript saved: {result.get('transcript_saved', 'N/A')}")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.weekly_review:
        result = archiver.generate_weekly_review()
        if "error" not in result:
            print("✅ Weekly review generated")
            print(f"📄 Review saved: {result.get('readable_review_saved', 'N/A')}")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.stats:
        stats = archiver.get_project_stats()
        if "error" not in stats:
            print("📊 Project Statistics:")
            for key, value in stats.items():
                if key != "storage_efficiency":
                    print(f"  {key}: {value}")

            if "storage_efficiency" in stats:
                print("\n💾 Storage Efficiency:")
                for key, value in stats["storage_efficiency"].items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ Error: {stats['error']}")

    elif args.cleanup:
        result = archiver.cleanup_old_data(args.cleanup)
        if result.get("success"):
            print(f"✅ Cleaned up data older than {args.cleanup} days")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    elif args.export:
        result = archiver.export_project_data(args.export)
        if result.get("success"):
            print(f"✅ Data exported to: {result['export_path']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    else:
        parser.print_help()