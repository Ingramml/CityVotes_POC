#!/usr/bin/env python3
"""
Learning Insights Tracker for Claude Sessions
Analyzes patterns to understand AI behavior and learning processes
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import re


class LearningInsightsTracker:
    """Tracks and analyzes learning patterns in Claude interactions"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.logs_dir = os.path.join(self.project_root, "daily_claude_logs")
        self.insights_dir = os.path.join(self.logs_dir, "learning_insights")

        # Ensure directory exists
        os.makedirs(self.insights_dir, exist_ok=True)

    def analyze_daily_patterns(self, target_date: date = None) -> Dict:
        """Analyze learning patterns for a specific day"""
        if target_date is None:
            target_date = date.today()

        # Load daily summary
        date_str = target_date.strftime("%Y-%m-%d")
        summary_path = os.path.join(self.logs_dir, "daily_summaries", f"daily_summary_{date_str}.json")

        if not os.path.exists(summary_path):
            return {"error": f"No daily summary found for {date_str}"}

        with open(summary_path, 'r') as f:
            daily_summary = json.load(f)

        # Load raw sessions for detailed analysis
        raw_sessions = self._load_raw_sessions(date_str)

        insights = {
            "date": date_str,
            "generated_at": datetime.now().isoformat(),
            "problem_solving_patterns": self._analyze_problem_solving(raw_sessions),
            "learning_progressions": self._analyze_learning_progressions(raw_sessions),
            "tool_usage_evolution": self._analyze_tool_evolution(raw_sessions),
            "knowledge_gaps": self._identify_knowledge_gaps(raw_sessions),
            "efficiency_patterns": self._analyze_efficiency(raw_sessions),
            "error_recovery": self._analyze_error_recovery(raw_sessions),
            "cognitive_load_indicators": self._analyze_cognitive_load(raw_sessions),
            "collaboration_patterns": self._analyze_collaboration_patterns(raw_sessions)
        }

        # Save insights
        self._save_insights(insights, date_str)

        return insights

    def _load_raw_sessions(self, date_str: str) -> List[Dict]:
        """Load raw session data for analysis"""
        import glob

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

    def _analyze_problem_solving(self, sessions: List[Dict]) -> Dict:
        """Analyze problem-solving approaches and patterns"""
        patterns = {
            "exploration_before_action": 0,
            "iterative_refinement": 0,
            "systematic_debugging": 0,
            "research_driven_solutions": 0,
            "trial_and_error_cycles": 0
        }

        problem_solving_sequences = []

        for session in sessions:
            interactions = session.get("interactions", [])

            # Analyze sequences of interactions
            for i in range(len(interactions) - 2):
                sequence = interactions[i:i+3]
                pattern_type = self._classify_problem_solving_pattern(sequence)

                if pattern_type:
                    patterns[pattern_type] += 1
                    problem_solving_sequences.append({
                        "timestamp": sequence[0].get("timestamp"),
                        "pattern": pattern_type,
                        "sequence_description": self._describe_sequence(sequence)
                    })

        return {
            "pattern_counts": patterns,
            "sequences": problem_solving_sequences[-10:],  # Last 10 sequences
            "dominant_approach": max(patterns, key=patterns.get) if patterns else None
        }

    def _classify_problem_solving_pattern(self, sequence: List[Dict]) -> str:
        """Classify a sequence of interactions as a problem-solving pattern"""
        tools_used = []
        prompts = []

        for interaction in sequence:
            tools_used.append([t.get("tool_name", "") for t in interaction.get("tool_calls", [])])
            prompts.append(interaction.get("prompt", "").lower())

        # Exploration before action: Read/Grep followed by Write/Edit
        if any("read" in tools or "grep" in tools for tools in tools_used[:2]) and \
           any("write" in tools or "edit" in tools for tools in tools_used[1:]):
            return "exploration_before_action"

        # Iterative refinement: Multiple edit operations
        edit_count = sum(1 for tools in tools_used if any("edit" in t.lower() for t in tools))
        if edit_count >= 2:
            return "iterative_refinement"

        # Systematic debugging: Error analysis followed by fix attempts
        if any("error" in prompt or "debug" in prompt or "fix" in prompt for prompt in prompts):
            return "systematic_debugging"

        # Research driven: Multiple read operations before implementation
        read_count = sum(1 for tools in tools_used if any("read" in t.lower() for t in tools))
        if read_count >= 2:
            return "research_driven_solutions"

        return None

    def _describe_sequence(self, sequence: List[Dict]) -> str:
        """Create a human-readable description of an interaction sequence"""
        descriptions = []

        for interaction in sequence:
            tools = [t.get("tool_name", "") for t in interaction.get("tool_calls", [])]
            prompt_preview = interaction.get("prompt", "")[:50] + "..."

            if tools:
                descriptions.append(f"Used {', '.join(tools[:3])} for: {prompt_preview}")
            else:
                descriptions.append(f"Asked: {prompt_preview}")

        return " → ".join(descriptions)

    def _analyze_learning_progressions(self, sessions: List[Dict]) -> Dict:
        """Analyze how understanding progresses through sessions"""
        progressions = {
            "concept_building": [],
            "skill_development": [],
            "knowledge_integration": []
        }

        vocabulary_evolution = []
        complexity_progression = []

        for session in sessions:
            interactions = session.get("interactions", [])

            # Track vocabulary complexity over time
            for interaction in interactions:
                prompt = interaction.get("prompt", "")
                response = interaction.get("response", "")

                # Simple complexity metrics
                prompt_complexity = self._calculate_complexity(prompt)
                response_complexity = self._calculate_complexity(response)

                complexity_progression.append({
                    "timestamp": interaction.get("timestamp"),
                    "prompt_complexity": prompt_complexity,
                    "response_complexity": response_complexity
                })

                # Track technical vocabulary
                vocab = self._extract_technical_vocabulary(prompt + " " + response)
                vocabulary_evolution.append({
                    "timestamp": interaction.get("timestamp"),
                    "vocabulary": vocab
                })

        return {
            "complexity_progression": complexity_progression[-20:],  # Last 20 interactions
            "vocabulary_evolution": vocabulary_evolution[-10:],
            "learning_indicators": self._identify_learning_indicators(sessions)
        }

    def _calculate_complexity(self, text: str) -> Dict:
        """Calculate simple complexity metrics for text"""
        words = text.split()
        sentences = text.split('.')

        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_words_per_sentence": len(words) / max(1, len(sentences)),
            "technical_terms": len(self._extract_technical_vocabulary(text))
        }

    def _extract_technical_vocabulary(self, text: str) -> List[str]:
        """Extract technical vocabulary from text"""
        # Simple technical term detection
        technical_patterns = [
            r'\b\w+\(\)',  # Function calls
            r'\b[A-Z][a-zA-Z]*[A-Z][a-zA-Z]*\b',  # CamelCase
            r'\b\w+\.\w+\b',  # Dot notation
            r'\b\w*[Cc]lass\b',  # Class-related terms
            r'\b\w*[Ff]unction\b',  # Function-related terms
            r'\b\w*[Aa]pi\b',  # API-related terms
        ]

        technical_terms = []
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            technical_terms.extend(matches)

        return list(set(technical_terms))  # Remove duplicates

    def _identify_learning_indicators(self, sessions: List[Dict]) -> List[Dict]:
        """Identify indicators of learning and understanding development"""
        indicators = []

        for session in sessions:
            interactions = session.get("interactions", [])

            for i, interaction in enumerate(interactions):
                prompt = interaction.get("prompt", "").lower()
                response = interaction.get("response", "").lower()

                # Learning indicators
                if any(phrase in prompt for phrase in ["how does", "why does", "what is", "explain"]):
                    indicators.append({
                        "type": "knowledge_seeking",
                        "timestamp": interaction.get("timestamp"),
                        "description": "Asked for explanation or understanding"
                    })

                if any(phrase in response for phrase in ["i understand", "i see", "now i", "this means"]):
                    indicators.append({
                        "type": "understanding_development",
                        "timestamp": interaction.get("timestamp"),
                        "description": "Expressed understanding or insight"
                    })

                if any(phrase in prompt for phrase in ["based on", "following", "using what"]):
                    indicators.append({
                        "type": "knowledge_application",
                        "timestamp": interaction.get("timestamp"),
                        "description": "Applied previous knowledge to new situation"
                    })

        return indicators[-15:]  # Last 15 indicators

    def _analyze_tool_evolution(self, sessions: List[Dict]) -> Dict:
        """Analyze how tool usage evolves during sessions"""
        tool_timeline = []
        tool_combinations = []

        for session in sessions:
            session_tools = []

            for interaction in session.get("interactions", []):
                tools = [t.get("tool_name", "") for t in interaction.get("tool_calls", [])]
                timestamp = interaction.get("timestamp")

                for tool in tools:
                    tool_timeline.append({
                        "tool": tool,
                        "timestamp": timestamp,
                        "session_id": session.get("session_id")
                    })
                    session_tools.append(tool)

                # Track tool combinations within single interactions
                if len(tools) > 1:
                    tool_combinations.append({
                        "tools": tools,
                        "timestamp": timestamp,
                        "combination_size": len(tools)
                    })

            # Analyze tool usage patterns within session
            if session_tools:
                unique_tools = list(set(session_tools))
                tool_diversity = len(unique_tools) / len(session_tools) if session_tools else 0

                # TODO: Add more sophisticated analysis

        return {
            "tool_timeline": tool_timeline[-30:],  # Last 30 tool uses
            "tool_combinations": tool_combinations[-10:],
            "evolution_patterns": self._identify_tool_evolution_patterns(tool_timeline)
        }

    def _identify_tool_evolution_patterns(self, tool_timeline: List[Dict]) -> List[str]:
        """Identify patterns in tool usage evolution"""
        patterns = []

        if len(tool_timeline) < 5:
            return patterns

        # Simple pattern detection
        recent_tools = [t["tool"] for t in tool_timeline[-10:]]
        tool_counts = Counter(recent_tools)

        if len(set(recent_tools)) > len(recent_tools) * 0.7:
            patterns.append("High tool diversity - exploring multiple approaches")

        most_common = tool_counts.most_common(1)[0] if tool_counts else None
        if most_common and most_common[1] > len(recent_tools) * 0.5:
            patterns.append(f"Tool specialization - focusing on {most_common[0]}")

        return patterns

    def _identify_knowledge_gaps(self, sessions: List[Dict]) -> Dict:
        """Identify potential knowledge gaps based on interaction patterns"""
        gaps = {
            "repeated_questions": [],
            "unsuccessful_attempts": [],
            "help_seeking_patterns": []
        }

        question_patterns = defaultdict(int)
        failed_attempts = []

        for session in sessions:
            interactions = session.get("interactions", [])

            for interaction in interactions:
                prompt = interaction.get("prompt", "").lower()
                response = interaction.get("response", "").lower()

                # Track repeated question types
                for pattern in ["how to", "what is", "why does", "how do i"]:
                    if pattern in prompt:
                        question_patterns[pattern] += 1

                # Identify potential failures or confusion
                if any(phrase in response for phrase in ["error", "failed", "couldn't", "unable"]):
                    failed_attempts.append({
                        "timestamp": interaction.get("timestamp"),
                        "prompt": prompt[:100],
                        "failure_indicators": [phrase for phrase in ["error", "failed", "couldn't", "unable"] if phrase in response]
                    })

        gaps["repeated_questions"] = [{"pattern": k, "count": v} for k, v in question_patterns.items() if v > 2]
        gaps["unsuccessful_attempts"] = failed_attempts[-10:]

        return gaps

    def _analyze_efficiency(self, sessions: List[Dict]) -> Dict:
        """Analyze efficiency patterns and improvements"""
        efficiency_metrics = {
            "interactions_per_task": [],
            "time_to_solution": [],
            "tool_efficiency": []
        }

        for session in sessions:
            interactions = session.get("interactions", [])

            if len(interactions) > 1:
                start_time = datetime.fromisoformat(interactions[0].get("timestamp"))
                end_time = datetime.fromisoformat(interactions[-1].get("timestamp"))
                duration_minutes = (end_time - start_time).total_seconds() / 60

                efficiency_metrics["time_to_solution"].append({
                    "session_id": session.get("session_id"),
                    "duration_minutes": duration_minutes,
                    "interactions_count": len(interactions)
                })

        return efficiency_metrics

    def _analyze_error_recovery(self, sessions: List[Dict]) -> Dict:
        """Analyze error recovery patterns"""
        recovery_patterns = {
            "immediate_retry": 0,
            "modified_approach": 0,
            "help_seeking": 0,
            "systematic_debugging": 0
        }

        error_sequences = []

        for session in sessions:
            interactions = session.get("interactions", [])

            for i, interaction in enumerate(interactions):
                response = interaction.get("response", "").lower()

                # Identify error situations
                if any(word in response for word in ["error", "failed", "exception", "traceback"]):
                    # Analyze next few interactions for recovery pattern
                    recovery_sequence = interactions[i:i+3]
                    pattern = self._classify_recovery_pattern(recovery_sequence)

                    if pattern:
                        recovery_patterns[pattern] += 1
                        error_sequences.append({
                            "timestamp": interaction.get("timestamp"),
                            "recovery_pattern": pattern,
                            "sequence_length": len(recovery_sequence)
                        })

        return {
            "recovery_patterns": recovery_patterns,
            "error_sequences": error_sequences[-10:]
        }

    def _classify_recovery_pattern(self, sequence: List[Dict]) -> str:
        """Classify error recovery approach"""
        if len(sequence) < 2:
            return None

        first_prompt = sequence[1].get("prompt", "").lower() if len(sequence) > 1 else ""

        if any(word in first_prompt for word in ["try again", "retry", "once more"]):
            return "immediate_retry"
        elif any(word in first_prompt for word in ["different", "another way", "alternative"]):
            return "modified_approach"
        elif any(word in first_prompt for word in ["help", "how", "what should"]):
            return "help_seeking"
        elif any(word in first_prompt for word in ["debug", "check", "examine", "look at"]):
            return "systematic_debugging"

        return None

    def _analyze_cognitive_load(self, sessions: List[Dict]) -> Dict:
        """Analyze indicators of cognitive load"""
        load_indicators = {
            "complex_requests": 0,
            "context_switching": 0,
            "information_overload": 0
        }

        for session in sessions:
            interactions = session.get("interactions", [])

            for i, interaction in enumerate(interactions):
                prompt = interaction.get("prompt", "")
                response = interaction.get("response", "")

                # Complex request indicators
                if len(prompt.split()) > 50 or prompt.count('?') > 2:
                    load_indicators["complex_requests"] += 1

                # Context switching (topic changes)
                if i > 0:
                    prev_tools = set(t.get("tool_name", "") for t in interactions[i-1].get("tool_calls", []))
                    curr_tools = set(t.get("tool_name", "") for t in interaction.get("tool_calls", []))

                    if prev_tools and curr_tools and not prev_tools.intersection(curr_tools):
                        load_indicators["context_switching"] += 1

                # Information overload indicators
                if len(response.split()) > 500:
                    load_indicators["information_overload"] += 1

        return load_indicators

    def _analyze_collaboration_patterns(self, sessions: List[Dict]) -> Dict:
        """Analyze human-AI collaboration patterns"""
        collaboration_metrics = {
            "directive_vs_exploratory": {"directive": 0, "exploratory": 0},
            "feedback_loops": 0,
            "clarification_requests": 0
        }

        for session in sessions:
            interactions = session.get("interactions", [])

            for interaction in interactions:
                prompt = interaction.get("prompt", "").lower()

                # Directive vs exploratory
                if any(word in prompt for word in ["do", "create", "make", "build", "implement"]):
                    collaboration_metrics["directive_vs_exploratory"]["directive"] += 1
                elif any(word in prompt for word in ["what", "how", "why", "explain", "show"]):
                    collaboration_metrics["directive_vs_exploratory"]["exploratory"] += 1

                # Clarification requests
                if any(phrase in prompt for phrase in ["can you clarify", "what do you mean", "i don't understand"]):
                    collaboration_metrics["clarification_requests"] += 1

        return collaboration_metrics

    def _save_insights(self, insights: Dict, date_str: str):
        """Save learning insights to file"""
        filename = f"learning_insights_{date_str}.json"
        filepath = os.path.join(self.insights_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(insights, f, indent=2)

    def generate_weekly_learning_trends(self, end_date: date = None) -> Dict:
        """Generate learning trends over a week"""
        if end_date is None:
            end_date = date.today()

        start_date = end_date - timedelta(days=6)
        weekly_insights = []

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            insights_file = os.path.join(self.insights_dir, f"learning_insights_{date_str}.json")

            if os.path.exists(insights_file):
                with open(insights_file, 'r') as f:
                    daily_insights = json.load(f)
                    weekly_insights.append(daily_insights)

            current_date += timedelta(days=1)

        if not weekly_insights:
            return {"error": "No insights data found for the week"}

        # Aggregate weekly trends
        trends = self._aggregate_weekly_trends(weekly_insights)

        # Save weekly trends
        week_filename = f"weekly_trends_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.json"
        week_filepath = os.path.join(self.logs_dir, "weekly_reviews", week_filename)

        with open(week_filepath, 'w') as f:
            json.dump(trends, f, indent=2)

        return trends

    def _aggregate_weekly_trends(self, weekly_insights: List[Dict]) -> Dict:
        """Aggregate insights into weekly trends"""
        trends = {
            "week_period": f"{weekly_insights[0]['date']} to {weekly_insights[-1]['date']}",
            "days_analyzed": len(weekly_insights),
            "problem_solving_evolution": {},
            "learning_progression_trends": {},
            "efficiency_improvements": {},
            "dominant_patterns": {}
        }

        # Aggregate problem-solving patterns
        all_patterns = defaultdict(int)
        for daily in weekly_insights:
            patterns = daily.get("problem_solving_patterns", {}).get("pattern_counts", {})
            for pattern, count in patterns.items():
                all_patterns[pattern] += count

        trends["problem_solving_evolution"] = dict(all_patterns)
        trends["dominant_patterns"]["problem_solving"] = max(all_patterns, key=all_patterns.get) if all_patterns else None

        return trends