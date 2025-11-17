#!/usr/bin/env python3
"""
Daily Summarizer for Claude Sessions
Creates comprehensive daily summaries from session data
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List, Any
from pathlib import Path
import glob


class DailySummarizer:
    """Creates daily summaries from Claude session data"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.logs_dir = os.path.join(self.project_root, "daily_claude_logs")

    def generate_daily_summary(self, target_date: date = None) -> Dict:
        """Generate comprehensive daily summary"""
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")

        # Load all sessions for the day
        sessions = self._load_daily_sessions(date_str)

        if not sessions:
            return {"error": f"No sessions found for {date_str}"}

        summary = {
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "project_root": self.project_root,
            "sessions_analyzed": len(sessions),
            "overview": self._generate_overview(sessions),
            "work_accomplished": self._extract_work_accomplished(sessions),
            "files_modified": self._analyze_files_modified(sessions),
            "tools_usage": self._analyze_tools_usage(sessions),
            "conversation_flow": self._analyze_conversation_flow(sessions),
            "learning_patterns": self._extract_learning_patterns(sessions),
            "session_details": self._summarize_sessions(sessions)
        }

        # Save summary
        self._save_daily_summary(summary, date_str)

        return summary

    def _load_daily_sessions(self, date_str: str) -> List[Dict]:
        """Load all session files for a specific date"""
        pattern = os.path.join(self.logs_dir, "raw_conversations", f"{date_str}_*.json")
        session_files = glob.glob(pattern)

        sessions = []
        for file_path in session_files:
            try:
                with open(file_path, 'r') as f:
                    sessions.append(json.load(f))
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        return sessions

    def _generate_overview(self, sessions: List[Dict]) -> Dict:
        """Generate high-level overview of the day"""
        total_interactions = sum(s.get("interaction_count", 0) for s in sessions)
        total_files = len(set().union(*[s.get("files_referenced", []) for s in sessions]))

        # Calculate total session time
        total_duration = 0
        for session in sessions:
            start = datetime.fromisoformat(session.get("session_start", ""))
            end = datetime.fromisoformat(session.get("last_updated", ""))
            total_duration += (end - start).total_seconds() / 60

        all_tools = []
        for session in sessions:
            all_tools.extend(session.get("tools_used", []))

        return {
            "total_sessions": len(sessions),
            "total_interactions": total_interactions,
            "total_duration_minutes": round(total_duration, 1),
            "unique_files_referenced": total_files,
            "total_tool_calls": len(all_tools),
            "unique_tools_used": len(set(t.get("tool", "") for t in all_tools))
        }

    def _extract_work_accomplished(self, sessions: List[Dict]) -> List[Dict]:
        """Extract and categorize work accomplished"""
        work_items = []

        for session in sessions:
            interactions = session.get("interactions", [])

            for interaction in interactions:
                prompt = interaction.get("prompt", "")
                response = interaction.get("response", "")
                tool_calls = interaction.get("tool_calls", [])

                # Identify different types of work
                work_type = self._categorize_work(prompt, response, tool_calls)

                if work_type != "general_conversation":
                    work_items.append({
                        "timestamp": interaction.get("timestamp"),
                        "type": work_type,
                        "description": self._extract_work_description(prompt, response),
                        "tools_used": [t.get("tool_name") for t in tool_calls],
                        "files_involved": interaction.get("files_accessed", [])
                    })

        return work_items

    def _categorize_work(self, prompt: str, response: str, tool_calls: List[Dict]) -> str:
        """Categorize the type of work based on content"""
        prompt_lower = prompt.lower()

        # File operations
        if any(tool.get("tool_name") in ["Write", "Edit", "MultiEdit"] for tool in tool_calls):
            return "file_modification"

        if any(tool.get("tool_name") in ["Read", "Glob", "Grep"] for tool in tool_calls):
            return "file_analysis"

        # Code operations
        if any(word in prompt_lower for word in ["create", "implement", "build", "develop"]):
            return "development"

        if any(word in prompt_lower for word in ["fix", "debug", "error", "issue"]):
            return "debugging"

        if any(word in prompt_lower for word in ["test", "verify", "check"]):
            return "testing"

        if any(tool.get("tool_name") == "Bash" for tool in tool_calls):
            return "system_operations"

        # Research and analysis
        if any(word in prompt_lower for word in ["analyze", "understand", "explain", "how"]):
            return "research_analysis"

        return "general_conversation"

    def _extract_work_description(self, prompt: str, response: str) -> str:
        """Extract concise description of work done"""
        # Take first sentence of prompt as description
        sentences = prompt.split('.')
        if sentences:
            return sentences[0].strip()[:100] + ("..." if len(sentences[0]) > 100 else "")
        return prompt[:100] + ("..." if len(prompt) > 100 else "")

    def _analyze_files_modified(self, sessions: List[Dict]) -> Dict:
        """Analyze files that were modified during the day"""
        all_files = set()
        file_operations = {}

        for session in sessions:
            for interaction in session.get("interactions", []):
                files_accessed = interaction.get("files_accessed", [])
                tool_calls = interaction.get("tool_calls", [])

                for file_path in files_accessed:
                    all_files.add(file_path)

                    if file_path not in file_operations:
                        file_operations[file_path] = {"read": 0, "write": 0, "edit": 0}

                    # Count operation types
                    for tool in tool_calls:
                        tool_name = tool.get("tool_name", "").lower()
                        if tool_name in ["read"]:
                            file_operations[file_path]["read"] += 1
                        elif tool_name in ["write"]:
                            file_operations[file_path]["write"] += 1
                        elif tool_name in ["edit", "multiedit"]:
                            file_operations[file_path]["edit"] += 1

        return {
            "total_files": len(all_files),
            "files_list": list(all_files),
            "operations_summary": file_operations
        }

    def _analyze_tools_usage(self, sessions: List[Dict]) -> Dict:
        """Analyze tool usage patterns"""
        tool_counts = {}
        tool_timeline = []

        for session in sessions:
            for tool_call in session.get("tools_used", []):
                tool_name = tool_call.get("tool")
                if tool_name:
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
                    tool_timeline.append({
                        "tool": tool_name,
                        "timestamp": tool_call.get("timestamp"),
                        "session_id": session.get("session_id")
                    })

        return {
            "tool_counts": tool_counts,
            "most_used_tools": sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "tool_timeline": tool_timeline[-20:]  # Last 20 tool calls
        }

    def _analyze_conversation_flow(self, sessions: List[Dict]) -> Dict:
        """Analyze the flow and progression of conversations"""
        conversation_themes = []
        interaction_patterns = []

        for session in sessions:
            interactions = session.get("interactions", [])

            # Extract conversation themes from prompts
            themes = []
            for interaction in interactions:
                prompt = interaction.get("prompt", "")
                if len(prompt) > 20:  # Skip very short prompts
                    themes.append({
                        "timestamp": interaction.get("timestamp"),
                        "prompt_preview": prompt[:100] + ("..." if len(prompt) > 100 else ""),
                        "response_length": interaction.get("response_length", 0)
                    })

            conversation_themes.extend(themes)

        return {
            "conversation_themes": conversation_themes[-10:],  # Last 10 themes
            "total_conversations": len(conversation_themes)
        }

    def _extract_learning_patterns(self, sessions: List[Dict]) -> Dict:
        """Extract patterns that show learning and problem-solving approaches"""
        patterns = {
            "research_to_implementation": 0,
            "iterative_debugging": 0,
            "file_exploration": 0,
            "systematic_testing": 0
        }

        for session in sessions:
            interactions = session.get("interactions", [])

            # Look for research followed by implementation
            for i, interaction in enumerate(interactions[:-1]):
                current_tools = [t.get("tool_name") for t in interaction.get("tool_calls", [])]
                next_tools = [t.get("tool_name") for t in interactions[i+1].get("tool_calls", [])]

                if any(t in ["Read", "Grep", "Glob"] for t in current_tools) and \
                   any(t in ["Write", "Edit"] for t in next_tools):
                    patterns["research_to_implementation"] += 1

                if "Bash" in current_tools and "Edit" in next_tools:
                    patterns["iterative_debugging"] += 1

        return patterns

    def _summarize_sessions(self, sessions: List[Dict]) -> List[Dict]:
        """Create summary for each individual session"""
        session_summaries = []

        for session in sessions:
            summary = {
                "session_id": session.get("session_id"),
                "start_time": session.get("session_start"),
                "interactions": session.get("interaction_count", 0),
                "files_touched": len(session.get("files_referenced", [])),
                "tools_used": len(set(t.get("tool") for t in session.get("tools_used", []))),
                "key_activities": self._extract_key_activities(session)
            }
            session_summaries.append(summary)

        return session_summaries

    def _extract_key_activities(self, session: Dict) -> List[str]:
        """Extract key activities from a session"""
        activities = []
        interactions = session.get("interactions", [])

        # Look for significant activities
        for interaction in interactions:
            tool_calls = interaction.get("tool_calls", [])
            prompt = interaction.get("prompt", "")

            # File creation/modification
            if any(t.get("tool_name") in ["Write", "Edit"] for t in tool_calls):
                activities.append(f"Modified files")

            # System operations
            if any(t.get("tool_name") == "Bash" for t in tool_calls):
                activities.append(f"Ran system commands")

            # Research/analysis
            if any(t.get("tool_name") in ["Read", "Grep"] for t in tool_calls):
                activities.append(f"Analyzed codebase")

        return list(set(activities))  # Remove duplicates

    def _save_daily_summary(self, summary: Dict, date_str: str):
        """Save daily summary to file"""
        filename = f"daily_summary_{date_str}.json"
        filepath = os.path.join(self.logs_dir, "daily_summaries", filename)

        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)

    def generate_human_readable_summary(self, target_date: date = None) -> str:
        """Generate human-readable daily summary"""
        summary = self.generate_daily_summary(target_date)

        if "error" in summary:
            return f"No activity recorded for {target_date or date.today()}"

        overview = summary["overview"]
        work = summary["work_accomplished"]
        files = summary["files_modified"]
        tools = summary["tools_usage"]

        readable_summary = f"""
# Daily Claude Activity Summary - {summary['date']}

## Overview
- **Sessions**: {overview['total_sessions']} sessions, {overview['total_duration_minutes']} minutes
- **Interactions**: {overview['total_interactions']} total interactions
- **Files**: {overview['unique_files_referenced']} files referenced
- **Tools**: {overview['unique_tools_used']} different tools used ({overview['total_tool_calls']} calls)

## Work Accomplished
"""

        # Group work by type
        work_by_type = {}
        for item in work:
            work_type = item['type']
            if work_type not in work_by_type:
                work_by_type[work_type] = []
            work_by_type[work_type].append(item)

        for work_type, items in work_by_type.items():
            readable_summary += f"\n### {work_type.replace('_', ' ').title()}\n"
            for item in items[:5]:  # Limit to 5 items per type
                readable_summary += f"- {item['description']}\n"

        readable_summary += f"\n## Files Modified\n"
        for file_path in files['files_list'][:10]:  # Show first 10 files
            ops = files['operations_summary'].get(file_path, {})
            readable_summary += f"- {file_path} (R:{ops.get('read',0)} W:{ops.get('write',0)} E:{ops.get('edit',0)})\n"

        readable_summary += f"\n## Most Used Tools\n"
        for tool, count in tools['most_used_tools'][:5]:
            readable_summary += f"- {tool}: {count} times\n"

        return readable_summary