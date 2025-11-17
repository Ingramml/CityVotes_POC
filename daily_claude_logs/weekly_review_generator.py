#!/usr/bin/env python3
"""
Weekly Review Generator for Claude Sessions
Creates comprehensive weekly analysis and reports
"""

import json
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict, Counter
import glob


class WeeklyReviewGenerator:
    """Generates comprehensive weekly reviews from daily logs"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.logs_dir = os.path.join(self.project_root, "daily_claude_logs")
        self.weekly_dir = os.path.join(self.logs_dir, "weekly_reviews")

        # Ensure directory exists
        os.makedirs(self.weekly_dir, exist_ok=True)

    def generate_weekly_review(self, end_date: date = None) -> Dict:
        """Generate comprehensive weekly review"""
        if end_date is None:
            end_date = date.today()

        start_date = end_date - timedelta(days=6)

        # Load all daily summaries for the week
        daily_summaries = self._load_weekly_summaries(start_date, end_date)

        if not daily_summaries:
            return {"error": f"No daily summaries found for week {start_date} to {end_date}"}

        # Load learning insights for the week
        learning_insights = self._load_weekly_insights(start_date, end_date)

        review = {
            "week_period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days_with_activity": len(daily_summaries)
            },
            "generated_at": datetime.now().isoformat(),
            "project_root": self.project_root,
            "executive_summary": self._generate_executive_summary(daily_summaries, learning_insights),
            "productivity_analysis": self._analyze_weekly_productivity(daily_summaries),
            "learning_evolution": self._analyze_learning_evolution(learning_insights),
            "technical_achievements": self._extract_technical_achievements(daily_summaries),
            "collaboration_patterns": self._analyze_collaboration_patterns(daily_summaries),
            "efficiency_trends": self._analyze_efficiency_trends(daily_summaries),
            "knowledge_development": self._track_knowledge_development(learning_insights),
            "challenges_and_solutions": self._identify_challenges_solutions(daily_summaries, learning_insights),
            "recommendations": self._generate_recommendations(daily_summaries, learning_insights),
            "weekly_metrics": self._calculate_weekly_metrics(daily_summaries)
        }

        # Save weekly review
        self._save_weekly_review(review, start_date, end_date)

        return review

    def _load_weekly_summaries(self, start_date: date, end_date: date) -> List[Dict]:
        """Load all daily summaries for the week"""
        summaries = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            summary_path = os.path.join(self.logs_dir, "daily_summaries", f"daily_summary_{date_str}.json")

            if os.path.exists(summary_path):
                try:
                    with open(summary_path, 'r') as f:
                        summary = json.load(f)
                        summaries.append(summary)
                except Exception as e:
                    print(f"Error loading summary for {date_str}: {e}")

            current_date += timedelta(days=1)

        return summaries

    def _load_weekly_insights(self, start_date: date, end_date: date) -> List[Dict]:
        """Load all learning insights for the week"""
        insights = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            insights_path = os.path.join(self.logs_dir, "learning_insights", f"learning_insights_{date_str}.json")

            if os.path.exists(insights_path):
                try:
                    with open(insights_path, 'r') as f:
                        insight = json.load(f)
                        insights.append(insight)
                except Exception as e:
                    print(f"Error loading insights for {date_str}: {e}")

            current_date += timedelta(days=1)

        return insights

    def _generate_executive_summary(self, daily_summaries: List[Dict], learning_insights: List[Dict]) -> Dict:
        """Generate high-level executive summary of the week"""
        total_sessions = sum(d.get("overview", {}).get("total_sessions", 0) for d in daily_summaries)
        total_interactions = sum(d.get("overview", {}).get("total_interactions", 0) for d in daily_summaries)
        total_duration = sum(d.get("overview", {}).get("total_duration_minutes", 0) for d in daily_summaries)

        # Aggregate work types
        all_work = []
        for daily in daily_summaries:
            all_work.extend(daily.get("work_accomplished", []))

        work_by_type = defaultdict(int)
        for work_item in all_work:
            work_by_type[work_item.get("type", "unknown")] += 1

        # Most productive day
        most_productive_day = max(daily_summaries,
                                key=lambda d: d.get("overview", {}).get("total_interactions", 0),
                                default={})

        return {
            "week_overview": {
                "active_days": len(daily_summaries),
                "total_sessions": total_sessions,
                "total_interactions": total_interactions,
                "total_duration_hours": round(total_duration / 60, 1)
            },
            "work_distribution": dict(work_by_type),
            "most_productive_day": {
                "date": most_productive_day.get("date", "N/A"),
                "interactions": most_productive_day.get("overview", {}).get("total_interactions", 0)
            },
            "primary_focus_areas": self._identify_primary_focus_areas(all_work),
            "learning_highlights": self._extract_learning_highlights(learning_insights)
        }

    def _identify_primary_focus_areas(self, all_work: List[Dict]) -> List[str]:
        """Identify the primary areas of focus during the week"""
        focus_areas = []

        # Analyze work types and descriptions
        work_types = Counter(work.get("type", "") for work in all_work)
        descriptions = [work.get("description", "") for work in all_work]

        # Extract common themes
        common_words = Counter()
        for desc in descriptions:
            words = desc.lower().split()
            common_words.update(word for word in words if len(word) > 4)

        # Combine type analysis and content analysis
        top_types = [work_type for work_type, _ in work_types.most_common(3)]
        top_themes = [word for word, _ in common_words.most_common(3)]

        focus_areas.extend(top_types)
        focus_areas.extend(top_themes)

        return focus_areas[:5]  # Top 5 focus areas

    def _extract_learning_highlights(self, learning_insights: List[Dict]) -> List[str]:
        """Extract key learning highlights from the week"""
        highlights = []

        all_patterns = defaultdict(int)
        for insight in learning_insights:
            patterns = insight.get("problem_solving_patterns", {}).get("pattern_counts", {})
            for pattern, count in patterns.items():
                all_patterns[pattern] += count

        # Identify dominant learning patterns
        if all_patterns:
            dominant_pattern = max(all_patterns, key=all_patterns.get)
            highlights.append(f"Primary problem-solving approach: {dominant_pattern.replace('_', ' ')}")

        # Extract knowledge development indicators
        all_indicators = []
        for insight in learning_insights:
            indicators = insight.get("learning_progressions", {}).get("learning_indicators", [])
            all_indicators.extend(indicators)

        if all_indicators:
            indicator_types = Counter(ind.get("type", "") for ind in all_indicators)
            top_indicator = indicator_types.most_common(1)[0] if indicator_types else None
            if top_indicator:
                highlights.append(f"Most common learning activity: {top_indicator[0].replace('_', ' ')}")

        return highlights[:3]  # Top 3 highlights

    def _analyze_weekly_productivity(self, daily_summaries: List[Dict]) -> Dict:
        """Analyze productivity patterns throughout the week"""
        daily_productivity = []

        for summary in daily_summaries:
            date_str = summary.get("date", "")
            overview = summary.get("overview", {})

            productivity_score = self._calculate_productivity_score(overview)

            daily_productivity.append({
                "date": date_str,
                "productivity_score": productivity_score,
                "interactions": overview.get("total_interactions", 0),
                "duration_minutes": overview.get("total_duration_minutes", 0),
                "files_modified": overview.get("unique_files_referenced", 0)
            })

        # Identify patterns
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        productivity_by_weekday = defaultdict(list)

        for prod in daily_productivity:
            date_obj = datetime.strptime(prod["date"], "%Y-%m-%d").date()
            weekday = weekdays[date_obj.weekday()]
            productivity_by_weekday[weekday].append(prod["productivity_score"])

        # Average productivity by weekday
        avg_productivity_by_weekday = {}
        for weekday, scores in productivity_by_weekday.items():
            avg_productivity_by_weekday[weekday] = sum(scores) / len(scores) if scores else 0

        return {
            "daily_productivity": daily_productivity,
            "average_by_weekday": avg_productivity_by_weekday,
            "most_productive_day": max(daily_productivity, key=lambda x: x["productivity_score"], default={}),
            "productivity_trend": self._calculate_productivity_trend(daily_productivity)
        }

    def _calculate_productivity_score(self, overview: Dict) -> float:
        """Calculate a simple productivity score based on activity metrics"""
        interactions = overview.get("total_interactions", 0)
        duration = overview.get("total_duration_minutes", 1)  # Avoid division by zero
        files = overview.get("unique_files_referenced", 0)
        tools = overview.get("unique_tools_used", 0)

        # Simple weighted score
        score = (interactions * 1.0) + (files * 2.0) + (tools * 1.5) + (60 / max(duration, 1))

        return round(score, 2)

    def _calculate_productivity_trend(self, daily_productivity: List[Dict]) -> str:
        """Calculate overall productivity trend for the week"""
        if len(daily_productivity) < 2:
            return "insufficient_data"

        scores = [p["productivity_score"] for p in daily_productivity]
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]

        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0

        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _analyze_learning_evolution(self, learning_insights: List[Dict]) -> Dict:
        """Analyze how learning patterns evolved during the week"""
        evolution = {
            "problem_solving_evolution": {},
            "knowledge_gaps_progression": {},
            "efficiency_improvements": {},
            "learning_pattern_changes": []
        }

        if not learning_insights:
            return evolution

        # Track problem-solving pattern changes
        pattern_timeline = []
        for insight in learning_insights:
            date_str = insight.get("date", "")
            patterns = insight.get("problem_solving_patterns", {}).get("pattern_counts", {})
            pattern_timeline.append({"date": date_str, "patterns": patterns})

        evolution["problem_solving_evolution"] = pattern_timeline

        # Track knowledge gap progression
        gap_progression = []
        for insight in learning_insights:
            date_str = insight.get("date", "")
            gaps = insight.get("knowledge_gaps", {})
            gap_count = len(gaps.get("repeated_questions", [])) + len(gaps.get("unsuccessful_attempts", []))
            gap_progression.append({"date": date_str, "gap_indicators": gap_count})

        evolution["knowledge_gaps_progression"] = gap_progression

        return evolution

    def _extract_technical_achievements(self, daily_summaries: List[Dict]) -> Dict:
        """Extract and categorize technical achievements"""
        achievements = {
            "files_created": [],
            "systems_implemented": [],
            "bugs_fixed": [],
            "features_added": [],
            "tools_mastered": []
        }

        all_work = []
        for summary in daily_summaries:
            all_work.extend(summary.get("work_accomplished", []))

        # Categorize achievements
        for work_item in all_work:
            work_type = work_item.get("type", "")
            description = work_item.get("description", "")
            files_involved = work_item.get("files_involved", [])

            if work_type == "file_modification" and files_involved:
                achievements["files_created"].extend(files_involved)

            if work_type == "development":
                achievements["systems_implemented"].append(description)

            if work_type == "debugging":
                achievements["bugs_fixed"].append(description)

            if "implement" in description.lower() or "create" in description.lower():
                achievements["features_added"].append(description)

        # Deduplicate
        for key in achievements:
            if isinstance(achievements[key], list):
                achievements[key] = list(set(achievements[key]))

        return achievements

    def _analyze_collaboration_patterns(self, daily_summaries: List[Dict]) -> Dict:
        """Analyze human-AI collaboration patterns throughout the week"""
        collaboration = {
            "interaction_styles": defaultdict(int),
            "feedback_patterns": [],
            "knowledge_transfer_moments": []
        }

        # This would require more detailed interaction analysis
        # For now, provide basic framework

        total_interactions = sum(s.get("overview", {}).get("total_interactions", 0) for s in daily_summaries)
        avg_session_length = sum(s.get("overview", {}).get("total_duration_minutes", 0) for s in daily_summaries) / len(daily_summaries) if daily_summaries else 0

        collaboration["interaction_patterns"] = {
            "total_interactions": total_interactions,
            "average_session_length_minutes": round(avg_session_length, 1),
            "collaboration_intensity": "high" if total_interactions > 100 else "moderate" if total_interactions > 50 else "low"
        }

        return collaboration

    def _analyze_efficiency_trends(self, daily_summaries: List[Dict]) -> Dict:
        """Analyze efficiency trends throughout the week"""
        efficiency_metrics = []

        for summary in daily_summaries:
            overview = summary.get("overview", {})
            date_str = summary.get("date", "")

            interactions = overview.get("total_interactions", 0)
            duration = overview.get("total_duration_minutes", 1)
            files = overview.get("unique_files_referenced", 0)

            efficiency = {
                "date": date_str,
                "interactions_per_minute": round(interactions / duration, 2) if duration > 0 else 0,
                "files_per_interaction": round(files / interactions, 2) if interactions > 0 else 0,
                "overall_efficiency_score": self._calculate_efficiency_score(overview)
            }

            efficiency_metrics.append(efficiency)

        return {
            "daily_efficiency": efficiency_metrics,
            "efficiency_trend": self._calculate_trend([e["overall_efficiency_score"] for e in efficiency_metrics])
        }

    def _calculate_efficiency_score(self, overview: Dict) -> float:
        """Calculate efficiency score based on output per input metrics"""
        interactions = overview.get("total_interactions", 0)
        duration = overview.get("total_duration_minutes", 1)
        files = overview.get("unique_files_referenced", 0)
        tools = overview.get("total_tool_calls", 0)

        # Efficiency = output/input ratio
        output_score = files + (tools * 0.5)
        input_score = duration + (interactions * 0.1)

        return round(output_score / max(input_score, 1), 2)

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "insufficient_data"

        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2) if values else 0
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2) if values else 0

        if second_half_avg > first_half_avg * 1.1:
            return "improving"
        elif second_half_avg < first_half_avg * 0.9:
            return "declining"
        else:
            return "stable"

    def _track_knowledge_development(self, learning_insights: List[Dict]) -> Dict:
        """Track knowledge development patterns"""
        knowledge_development = {
            "vocabulary_growth": [],
            "concept_mastery": [],
            "skill_progression": []
        }

        for insight in learning_insights:
            date_str = insight.get("date", "")
            progressions = insight.get("learning_progressions", {})

            # Track vocabulary evolution
            vocab_evolution = progressions.get("vocabulary_evolution", [])
            if vocab_evolution:
                latest_vocab = vocab_evolution[-1]
                knowledge_development["vocabulary_growth"].append({
                    "date": date_str,
                    "vocabulary_count": len(latest_vocab.get("vocabulary", []))
                })

        return knowledge_development

    def _identify_challenges_solutions(self, daily_summaries: List[Dict], learning_insights: List[Dict]) -> Dict:
        """Identify challenges faced and solutions found"""
        challenges_solutions = {
            "recurring_challenges": [],
            "successful_solutions": [],
            "learning_breakthroughs": []
        }

        # Extract from learning insights
        for insight in learning_insights:
            knowledge_gaps = insight.get("knowledge_gaps", {})
            repeated_questions = knowledge_gaps.get("repeated_questions", [])
            unsuccessful_attempts = knowledge_gaps.get("unsuccessful_attempts", [])

            for question in repeated_questions:
                if question.get("count", 0) > 3:
                    challenges_solutions["recurring_challenges"].append({
                        "challenge": question.get("pattern", ""),
                        "frequency": question.get("count", 0),
                        "date": insight.get("date", "")
                    })

        return challenges_solutions

    def _generate_recommendations(self, daily_summaries: List[Dict], learning_insights: List[Dict]) -> List[str]:
        """Generate recommendations based on weekly analysis"""
        recommendations = []

        # Analyze productivity patterns
        if daily_summaries:
            avg_duration = sum(s.get("overview", {}).get("total_duration_minutes", 0) for s in daily_summaries) / len(daily_summaries)

            if avg_duration > 120:  # More than 2 hours average
                recommendations.append("Consider breaking sessions into shorter, focused blocks for better efficiency")

            # Check tool usage diversity
            all_tool_counts = []
            for summary in daily_summaries:
                tools_used = summary.get("overview", {}).get("unique_tools_used", 0)
                all_tool_counts.append(tools_used)

            avg_tools = sum(all_tool_counts) / len(all_tool_counts) if all_tool_counts else 0
            if avg_tools < 3:
                recommendations.append("Explore using more diverse tools to improve workflow efficiency")

        # Analyze learning patterns
        if learning_insights:
            all_knowledge_gaps = []
            for insight in learning_insights:
                gaps = insight.get("knowledge_gaps", {}).get("repeated_questions", [])
                all_knowledge_gaps.extend(gaps)

            if len(all_knowledge_gaps) > 10:
                recommendations.append("Focus on addressing recurring knowledge gaps through dedicated learning sessions")

        # Default recommendations
        if not recommendations:
            recommendations.append("Continue current workflow - patterns show consistent progress")

        return recommendations[:5]  # Limit to 5 recommendations

    def _calculate_weekly_metrics(self, daily_summaries: List[Dict]) -> Dict:
        """Calculate comprehensive weekly metrics"""
        if not daily_summaries:
            return {}

        total_sessions = sum(s.get("overview", {}).get("total_sessions", 0) for s in daily_summaries)
        total_interactions = sum(s.get("overview", {}).get("total_interactions", 0) for s in daily_summaries)
        total_duration = sum(s.get("overview", {}).get("total_duration_minutes", 0) for s in daily_summaries)
        total_files = len(set().union(*[set(s.get("files_modified", {}).get("files_list", [])) for s in daily_summaries]))

        return {
            "totals": {
                "sessions": total_sessions,
                "interactions": total_interactions,
                "duration_hours": round(total_duration / 60, 1),
                "unique_files": total_files
            },
            "averages": {
                "sessions_per_day": round(total_sessions / len(daily_summaries), 1),
                "interactions_per_day": round(total_interactions / len(daily_summaries), 1),
                "duration_per_day_minutes": round(total_duration / len(daily_summaries), 1)
            },
            "efficiency": {
                "interactions_per_hour": round(total_interactions / max(total_duration / 60, 0.1), 1),
                "files_per_session": round(total_files / max(total_sessions, 1), 1)
            }
        }

    def _save_weekly_review(self, review: Dict, start_date: date, end_date: date):
        """Save weekly review to file"""
        filename = f"weekly_review_{start_date.strftime('%Y-%m-%d')}_to_{end_date.strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(self.weekly_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(review, f, indent=2)

    def generate_human_readable_review(self, end_date: date = None) -> str:
        """Generate human-readable weekly review"""
        review = self.generate_weekly_review(end_date)

        if "error" in review:
            return f"No activity recorded for the requested week"

        week_period = review["week_period"]
        executive = review["executive_summary"]
        productivity = review["productivity_analysis"]
        metrics = review["weekly_metrics"]

        readable_review = f"""
# Weekly Claude Activity Review
## Week of {week_period['start_date']} to {week_period['end_date']}

### Executive Summary
**Active Days:** {week_period['days_with_activity']}/7
**Total Activity:** {executive['week_overview']['total_sessions']} sessions, {executive['week_overview']['total_interactions']} interactions
**Time Invested:** {executive['week_overview']['total_duration_hours']} hours

**Primary Focus Areas:**
{chr(10).join(f"- {area}" for area in executive['primary_focus_areas'])}

### Productivity Highlights
**Most Productive Day:** {productivity['most_productive_day'].get('date', 'N/A')} ({productivity['most_productive_day'].get('interactions', 0)} interactions)
**Productivity Trend:** {productivity['productivity_trend']}

### Weekly Metrics
**Totals:**
- Sessions: {metrics['totals']['sessions']}
- Interactions: {metrics['totals']['interactions']}
- Files Modified: {metrics['totals']['unique_files']}
- Time Spent: {metrics['totals']['duration_hours']} hours

**Daily Averages:**
- Sessions: {metrics['averages']['sessions_per_day']}
- Interactions: {metrics['averages']['interactions_per_day']}
- Duration: {metrics['averages']['duration_per_day_minutes']} minutes

### Recommendations
{chr(10).join(f"- {rec}" for rec in review['recommendations'])}

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return readable_review