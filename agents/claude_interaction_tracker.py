"""
Claude Interaction Tracker Agent

Main orchestrator for tracking Claude conversations, managing sessions,
and coordinating with storage and summarization agents.

Features:
- Real-time conversation capture
- Session management with unique IDs
- Metadata extraction and analysis
- Integration with storage and summary agents
- Configurable privacy controls
"""

import os
import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Types of Claude interactions"""
    CODING = "coding"
    DEBUGGING = "debugging"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    DOCUMENTATION = "documentation"
    LEARNING = "learning"
    OTHER = "other"

@dataclass
class ConversationMetadata:
    """Metadata for a conversation session"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    interaction_type: InteractionType = InteractionType.OTHER
    project_context: Optional[str] = None
    files_modified: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)
    key_topics: List[str] = field(default_factory=list)
    outcome_summary: Optional[str] = None
    quality_rating: Optional[int] = None  # 1-5 scale

@dataclass
class ConversationTurn:
    """Single conversation turn (prompt + response)"""
    turn_id: str
    timestamp: datetime
    user_prompt: str
    claude_response: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    files_read: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    commands_executed: List[str] = field(default_factory=list)
    error_occurred: bool = False
    error_details: Optional[str] = None

@dataclass
class ConversationSession:
    """Complete conversation session"""
    metadata: ConversationMetadata
    turns: List[ConversationTurn] = field(default_factory=list)
    total_turns: int = 0
    total_tokens_estimate: int = 0

    def add_turn(self, turn: ConversationTurn):
        """Add a turn to the session"""
        self.turns.append(turn)
        self.total_turns += 1
        # Rough token estimate (4 chars per token average)
        self.total_tokens_estimate += (len(turn.user_prompt) + len(turn.claude_response)) // 4

class ClaudeInteractionTracker:
    """
    Main tracker for Claude interactions with comprehensive logging,
    metadata extraction, and integration capabilities.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.base_path = Path(self.config.get('base_path', 'daily_claude_logs'))
        self.current_session: Optional[ConversationSession] = None
        self.storage_agent = None
        self.summary_agent = None

        # Ensure directories exist
        self._setup_directories()

        # Initialize logging
        self._setup_logging()

        logger.info("Claude Interaction Tracker initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'base_path': 'daily_claude_logs',
            'auto_summarize': True,
            'privacy_mode': False,
            'max_session_duration_hours': 8,
            'auto_categorize': True,
            'track_file_changes': True,
            'track_commands': True,
            'summary_triggers': {
                'min_turns': 5,
                'time_based': True,
                'end_of_day': True
            }
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")

        return default_config

    def _setup_directories(self):
        """Ensure all required directories exist"""
        directories = [
            'raw_conversations',
            'daily_transcripts',
            'daily_summaries',
            'weekly_reviews',
            'learning_insights'
        ]

        for directory in directories:
            path = self.base_path / directory
            path.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self):
        """Setup logging for the tracker"""
        log_file = self.base_path / 'tracker.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def start_session(self,
                     interaction_type: InteractionType = InteractionType.OTHER,
                     project_context: Optional[str] = None) -> str:
        """Start a new conversation session"""

        # End current session if active
        if self.current_session:
            self.end_session()

        session_id = str(uuid.uuid4())[:8]
        metadata = ConversationMetadata(
            session_id=session_id,
            start_time=datetime.now(),
            interaction_type=interaction_type,
            project_context=project_context or self._detect_project_context()
        )

        self.current_session = ConversationSession(metadata=metadata)

        logger.info(f"Started new session: {session_id} ({interaction_type.value})")
        return session_id

    def add_interaction(self,
                       user_prompt: str,
                       claude_response: str,
                       tool_calls: Optional[List[Dict[str, Any]]] = None,
                       files_read: Optional[List[str]] = None,
                       files_modified: Optional[List[str]] = None,
                       commands_executed: Optional[List[str]] = None) -> str:
        """Add an interaction turn to the current session"""

        if not self.current_session:
            # Auto-start session if none exists
            self.start_session()

        turn_id = f"{self.current_session.metadata.session_id}_turn_{len(self.current_session.turns) + 1:03d}"

        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=datetime.now(),
            user_prompt=user_prompt,
            claude_response=claude_response,
            tool_calls=tool_calls or [],
            files_read=files_read or [],
            files_modified=files_modified or [],
            commands_executed=commands_executed or []
        )

        # Extract metadata from the interaction
        self._analyze_turn(turn)

        # Add to current session
        self.current_session.add_turn(turn)

        # Update session metadata
        self._update_session_metadata(turn)

        # Auto-save periodically
        self._auto_save_session()

        logger.debug(f"Added interaction turn: {turn_id}")
        return turn_id

    def end_session(self, outcome_summary: Optional[str] = None, quality_rating: Optional[int] = None):
        """End the current session"""
        if not self.current_session:
            return

        # Update metadata
        self.current_session.metadata.end_time = datetime.now()
        self.current_session.metadata.outcome_summary = outcome_summary
        self.current_session.metadata.quality_rating = quality_rating

        # Save session
        self._save_session(self.current_session)

        # Trigger summarization if configured
        if self.config.get('auto_summarize') and self._should_trigger_summary():
            self._trigger_summary()

        session_id = self.current_session.metadata.session_id
        logger.info(f"Ended session: {session_id}")

        self.current_session = None

    def _analyze_turn(self, turn: ConversationTurn):
        """Analyze a conversation turn for metadata"""

        # Detect interaction type from content
        if not turn.claude_response:
            return

        response_lower = turn.claude_response.lower()
        prompt_lower = turn.user_prompt.lower()

        # Simple keyword-based categorization
        coding_keywords = ['function', 'class', 'import', 'def ', 'return', 'variable']
        debugging_keywords = ['error', 'debug', 'fix', 'issue', 'problem', 'bug']
        research_keywords = ['research', 'analyze', 'study', 'investigate', 'explore']

        if any(keyword in prompt_lower or keyword in response_lower for keyword in coding_keywords):
            if self.current_session.metadata.interaction_type == InteractionType.OTHER:
                self.current_session.metadata.interaction_type = InteractionType.CODING
        elif any(keyword in prompt_lower or keyword in response_lower for keyword in debugging_keywords):
            if self.current_session.metadata.interaction_type == InteractionType.OTHER:
                self.current_session.metadata.interaction_type = InteractionType.DEBUGGING
        elif any(keyword in prompt_lower or keyword in response_lower for keyword in research_keywords):
            if self.current_session.metadata.interaction_type == InteractionType.OTHER:
                self.current_session.metadata.interaction_type = InteractionType.RESEARCH

    def _update_session_metadata(self, turn: ConversationTurn):
        """Update session metadata based on the turn"""
        metadata = self.current_session.metadata

        # Aggregate file changes
        for file_path in turn.files_modified:
            if file_path not in metadata.files_modified:
                metadata.files_modified.append(file_path)

        # Aggregate commands
        for command in turn.commands_executed:
            if command not in metadata.commands_executed:
                metadata.commands_executed.append(command)

    def _detect_project_context(self) -> Optional[str]:
        """Auto-detect project context from current directory"""
        cwd = os.getcwd()
        project_indicators = {
            'package.json': 'Node.js',
            'requirements.txt': 'Python',
            'Cargo.toml': 'Rust',
            'pom.xml': 'Java/Maven',
            'go.mod': 'Go',
            '.git': 'Git Repository'
        }

        for indicator, project_type in project_indicators.items():
            if os.path.exists(os.path.join(cwd, indicator)):
                return f"{project_type} - {os.path.basename(cwd)}"

        return os.path.basename(cwd)

    def _save_session(self, session: ConversationSession):
        """Save session to JSON file"""
        date_str = session.metadata.start_time.strftime('%Y-%m-%d')
        session_file = self.base_path / 'raw_conversations' / f"{date_str}_session_{session.metadata.session_id}.json"

        # Convert to serializable format
        session_data = {
            'metadata': asdict(session.metadata),
            'turns': [asdict(turn) for turn in session.turns],
            'total_turns': session.total_turns,
            'total_tokens_estimate': session.total_tokens_estimate
        }

        # Handle datetime serialization
        for key, value in session_data['metadata'].items():
            if isinstance(value, datetime):
                session_data['metadata'][key] = value.isoformat()

        for turn in session_data['turns']:
            if isinstance(turn['timestamp'], datetime):
                turn['timestamp'] = turn['timestamp'].isoformat()

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Session saved: {session_file}")
        except Exception as e:
            logger.error(f"Failed to save session: {e}")

    def _auto_save_session(self):
        """Auto-save session periodically"""
        if not self.current_session or len(self.current_session.turns) % 5 != 0:
            return

        # Save intermediate state
        temp_file = self.base_path / 'raw_conversations' / f"temp_session_{self.current_session.metadata.session_id}.json"
        session_copy = ConversationSession(
            metadata=self.current_session.metadata,
            turns=self.current_session.turns.copy(),
            total_turns=self.current_session.total_turns,
            total_tokens_estimate=self.current_session.total_tokens_estimate
        )

        try:
            self._save_session(session_copy)
        except Exception as e:
            logger.warning(f"Auto-save failed: {e}")

    def _should_trigger_summary(self) -> bool:
        """Determine if summary should be triggered"""
        if not self.current_session:
            return False

        triggers = self.config.get('summary_triggers', {})

        # Minimum turns threshold
        if self.current_session.total_turns >= triggers.get('min_turns', 5):
            return True

        # Time-based trigger (end of day)
        if triggers.get('end_of_day') and datetime.now().hour >= 22:
            return True

        return False

    def _trigger_summary(self):
        """Trigger summary generation"""
        try:
            if not self.summary_agent:
                from .daily_summary_agent import DailySummaryAgent
                self.summary_agent = DailySummaryAgent(self.base_path)

            date_str = self.current_session.metadata.start_time.strftime('%Y-%m-%d')
            self.summary_agent.generate_daily_summary(date_str)
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")

    def get_daily_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific day"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        conversations_dir = self.base_path / 'raw_conversations'
        session_files = list(conversations_dir.glob(f"{date}_session_*.json"))

        stats = {
            'date': date,
            'total_sessions': len(session_files),
            'total_turns': 0,
            'total_tokens_estimate': 0,
            'interaction_types': {},
            'files_modified': set(),
            'commands_executed': set(),
            'duration_hours': 0
        }

        start_time = None
        end_time = None

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                stats['total_turns'] += session_data['total_turns']
                stats['total_tokens_estimate'] += session_data['total_tokens_estimate']

                # Track interaction types
                interaction_type = session_data['metadata']['interaction_type']
                stats['interaction_types'][interaction_type] = stats['interaction_types'].get(interaction_type, 0) + 1

                # Track files and commands
                stats['files_modified'].update(session_data['metadata']['files_modified'])
                stats['commands_executed'].update(session_data['metadata']['commands_executed'])

                # Track time range
                session_start = datetime.fromisoformat(session_data['metadata']['start_time'])
                session_end_str = session_data['metadata'].get('end_time')
                if session_end_str:
                    session_end = datetime.fromisoformat(session_end_str)

                    if not start_time or session_start < start_time:
                        start_time = session_start
                    if not end_time or session_end > end_time:
                        end_time = session_end

            except Exception as e:
                logger.warning(f"Could not process session file {session_file}: {e}")

        # Convert sets to lists for JSON serialization
        stats['files_modified'] = list(stats['files_modified'])
        stats['commands_executed'] = list(stats['commands_executed'])

        # Calculate duration
        if start_time and end_time:
            stats['duration_hours'] = (end_time - start_time).total_seconds() / 3600

        return stats

    def generate_transcript(self, date: Optional[str] = None) -> str:
        """Generate a full transcript for a day"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        conversations_dir = self.base_path / 'raw_conversations'
        session_files = sorted(conversations_dir.glob(f"{date}_session_*.json"))

        transcript_lines = [
            f"# Claude Interaction Transcript - {date}",
            "",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Sessions: {len(session_files)}",
            ""
        ]

        for i, session_file in enumerate(session_files, 1):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                metadata = session_data['metadata']
                transcript_lines.extend([
                    f"## Session {i}: {metadata['start_time'][:19]}",
                    f"**Context**: {metadata.get('project_context', 'Unknown')}",
                    f"**Type**: {metadata.get('interaction_type', 'other')}",
                    f"**Duration**: {self._format_duration(metadata)}",
                    ""
                ])

                for turn_data in session_data['turns']:
                    transcript_lines.extend([
                        f"### {turn_data['timestamp'][:19]}",
                        "",
                        "**User:**",
                        turn_data['user_prompt'],
                        "",
                        "**Claude:**",
                        turn_data['claude_response'],
                        ""
                    ])

                    if turn_data.get('files_modified'):
                        transcript_lines.extend([
                            "**Files Modified:**",
                            ", ".join(turn_data['files_modified']),
                            ""
                        ])

                transcript_lines.append("---\n")

            except Exception as e:
                logger.warning(f"Could not process session file {session_file}: {e}")

        return "\n".join(transcript_lines)

    def _format_duration(self, metadata: Dict[str, Any]) -> str:
        """Format session duration"""
        start_str = metadata['start_time']
        end_str = metadata.get('end_time')

        if not end_str:
            return "Ongoing"

        try:
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)
            duration = end - start

            hours = duration.total_seconds() // 3600
            minutes = (duration.total_seconds() % 3600) // 60

            if hours > 0:
                return f"{int(hours)}h {int(minutes)}m"
            else:
                return f"{int(minutes)}m"
        except Exception:
            return "Unknown"

# CLI wrapper functions for easy integration
def start_logging_session(interaction_type: str = "other", project_context: Optional[str] = None):
    """Start a new logging session - for CLI integration"""
    global _tracker_instance
    if '_tracker_instance' not in globals():
        _tracker_instance = ClaudeInteractionTracker()

    try:
        interaction_type_enum = InteractionType(interaction_type)
    except ValueError:
        interaction_type_enum = InteractionType.OTHER

    return _tracker_instance.start_session(interaction_type_enum, project_context)

def log_interaction(user_prompt: str, claude_response: str, **kwargs):
    """Log a single interaction - for CLI integration"""
    global _tracker_instance
    if '_tracker_instance' not in globals():
        _tracker_instance = ClaudeInteractionTracker()

    return _tracker_instance.add_interaction(user_prompt, claude_response, **kwargs)

def end_logging_session(outcome_summary: Optional[str] = None, quality_rating: Optional[int] = None):
    """End the current logging session - for CLI integration"""
    global _tracker_instance
    if '_tracker_instance' in globals():
        _tracker_instance.end_session(outcome_summary, quality_rating)

# Test function
def test_tracker():
    """Test the Claude Interaction Tracker"""
    tracker = ClaudeInteractionTracker()

    # Test session management
    session_id = tracker.start_session(InteractionType.CODING, "Test Project")
    assert tracker.current_session is not None
    print(f"✓ Started session: {session_id}")

    # Test interaction logging
    turn_id = tracker.add_interaction(
        "Help me create a function",
        "Here's a function that does what you need...",
        files_modified=["test.py"]
    )
    print(f"✓ Added interaction: {turn_id}")

    # Test session ending
    tracker.end_session("Successfully created function", 5)
    assert tracker.current_session is None
    print("✓ Session ended successfully")

    print("All tests passed!")

if __name__ == "__main__":
    test_tracker()