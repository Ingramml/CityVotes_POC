#!/usr/bin/env python3
"""
Session Capture Module for Daily Claude Logs
Captures prompts, responses, and file operations for analysis
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class SessionCapture:
    """Captures Claude session data for daily archiving"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.logs_dir = os.path.join(self.project_root, "daily_claude_logs")
        self.session_id = self._generate_session_id()
        self.session_start = datetime.now()
        self.interactions = []
        self.files_referenced = set()
        self.tools_used = []

        # Ensure directory structure exists
        self._ensure_directories()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_part = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{hash_part}"

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            "raw_conversations",
            "daily_transcripts",
            "daily_summaries",
            "learning_insights",
            "weekly_reviews"
        ]

        for dir_name in dirs:
            os.makedirs(os.path.join(self.logs_dir, dir_name), exist_ok=True)

    def capture_interaction(self, prompt: str, response: str, tool_calls: List[Dict] = None,
                          files_accessed: List[str] = None, context: Dict = None):
        """Capture a single prompt-response interaction"""

        interaction = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "tool_calls": tool_calls or [],
            "files_accessed": files_accessed or [],
            "context": context or {},
            "response_length": len(response),
            "prompt_length": len(prompt)
        }

        # Track file references
        if files_accessed:
            self.files_referenced.update(files_accessed)

        # Track tool usage
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call.get("tool_name"):
                    self.tools_used.append({
                        "tool": tool_call["tool_name"],
                        "timestamp": interaction["timestamp"],
                        "parameters": tool_call.get("parameters", {})
                    })

        self.interactions.append(interaction)

        # Auto-save after each interaction
        self._save_raw_session()

    def _save_raw_session(self):
        """Save current session to raw conversations"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{today}_{self.session_id}.json"
        filepath = os.path.join(self.logs_dir, "raw_conversations", filename)

        session_data = {
            "session_id": self.session_id,
            "project_root": self.project_root,
            "session_start": self.session_start.isoformat(),
            "last_updated": datetime.now().isoformat(),
            "interaction_count": len(self.interactions),
            "files_referenced": list(self.files_referenced),
            "tools_used": self.tools_used,
            "interactions": self.interactions
        }

        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)

    def create_file_reference(self, filepath: str, content: str = None) -> Dict:
        """Create space-efficient file reference"""
        abs_path = os.path.abspath(filepath)
        rel_path = os.path.relpath(abs_path, self.project_root)

        file_ref = {
            "path": rel_path,
            "absolute_path": abs_path,
            "exists": os.path.exists(abs_path),
            "timestamp": datetime.now().isoformat()
        }

        if os.path.exists(abs_path):
            stat = os.stat(abs_path)
            file_ref.update({
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_hash": self._get_file_hash(abs_path)
            })

        # Store content hash instead of full content to save space
        if content:
            file_ref["content_hash"] = hashlib.sha256(content.encode()).hexdigest()
            file_ref["content_length"] = len(content)

            # Only store first/last few lines for reference
            lines = content.split('\n')
            if len(lines) > 20:
                file_ref["content_preview"] = {
                    "first_10_lines": lines[:10],
                    "last_10_lines": lines[-10:],
                    "total_lines": len(lines)
                }
            else:
                file_ref["content_preview"] = {
                    "all_lines": lines,
                    "total_lines": len(lines)
                }

        return file_ref

    def _get_file_hash(self, filepath: str) -> str:
        """Get SHA256 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return "error_reading_file"

    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        now = datetime.now()
        duration = now - self.session_start

        return {
            "session_id": self.session_id,
            "duration_minutes": duration.total_seconds() / 60,
            "interactions": len(self.interactions),
            "total_prompt_chars": sum(i["prompt_length"] for i in self.interactions),
            "total_response_chars": sum(i["response_length"] for i in self.interactions),
            "files_referenced": len(self.files_referenced),
            "unique_tools_used": len(set(t["tool"] for t in self.tools_used)),
            "tools_usage_count": len(self.tools_used)
        }