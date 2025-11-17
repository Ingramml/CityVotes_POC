"""
Conversation Storage Agent

Handles structured storage of Claude conversations with advanced features:
- SQLite database for fast querying
- Full-text search capabilities
- Data archival and compression
- Export functionality
- Privacy controls
"""

import os
import json
import sqlite3
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ConversationStorageAgent:
    """
    Advanced storage agent for Claude conversations with database backend,
    search capabilities, and archival features.
    """

    def __init__(self, base_path: str = "daily_claude_logs"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "conversations.db"
        self.archive_path = self.base_path / "archived"

        # Ensure directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        logger.info("Conversation Storage Agent initialized")

    def _init_database(self):
        """Initialize SQLite database with conversation schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        interaction_type TEXT,
                        project_context TEXT,
                        total_turns INTEGER,
                        total_tokens INTEGER,
                        outcome_summary TEXT,
                        quality_rating INTEGER,
                        files_modified TEXT, -- JSON array
                        commands_executed TEXT, -- JSON array
                        key_topics TEXT, -- JSON array
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS turns (
                        turn_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        timestamp TIMESTAMP,
                        user_prompt TEXT,
                        claude_response TEXT,
                        tool_calls TEXT, -- JSON
                        files_read TEXT, -- JSON array
                        files_modified TEXT, -- JSON array
                        commands_executed TEXT, -- JSON array
                        error_occurred BOOLEAN,
                        error_details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                    )
                """)

                # Create indexes for better query performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(start_time)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions(interaction_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_timestamp ON turns(timestamp)")

                # Enable full-text search
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(
                        turn_id,
                        user_prompt,
                        claude_response,
                        content='turns',
                        content_rowid='rowid'
                    )
                """)

                conn.commit()

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def store_session(self, session_data: Dict[str, Any]) -> bool:
        """Store a complete conversation session in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Prepare session data
                metadata = session_data['metadata']
                session_row = (
                    metadata['session_id'],
                    metadata['start_time'],
                    metadata.get('end_time'),
                    metadata.get('interaction_type'),
                    metadata.get('project_context'),
                    session_data['total_turns'],
                    session_data['total_tokens_estimate'],
                    metadata.get('outcome_summary'),
                    metadata.get('quality_rating'),
                    json.dumps(metadata.get('files_modified', [])),
                    json.dumps(metadata.get('commands_executed', [])),
                    json.dumps(metadata.get('key_topics', []))
                )

                # Insert session
                conn.execute("""
                    INSERT OR REPLACE INTO sessions (
                        session_id, start_time, end_time, interaction_type,
                        project_context, total_turns, total_tokens, outcome_summary,
                        quality_rating, files_modified, commands_executed, key_topics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, session_row)

                # Insert turns
                for turn in session_data['turns']:
                    turn_row = (
                        turn['turn_id'],
                        metadata['session_id'],
                        turn['timestamp'],
                        turn['user_prompt'],
                        turn['claude_response'],
                        json.dumps(turn.get('tool_calls', [])),
                        json.dumps(turn.get('files_read', [])),
                        json.dumps(turn.get('files_modified', [])),
                        json.dumps(turn.get('commands_executed', [])),
                        turn.get('error_occurred', False),
                        turn.get('error_details')
                    )

                    conn.execute("""
                        INSERT OR REPLACE INTO turns (
                            turn_id, session_id, timestamp, user_prompt, claude_response,
                            tool_calls, files_read, files_modified, commands_executed,
                            error_occurred, error_details
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, turn_row)

                    # Update FTS index
                    conn.execute("""
                        INSERT OR REPLACE INTO turns_fts (turn_id, user_prompt, claude_response)
                        VALUES (?, ?, ?)
                    """, (turn['turn_id'], turn['user_prompt'], turn['claude_response']))

                conn.commit()

            logger.info(f"Stored session: {metadata['session_id']} with {len(session_data['turns'])} turns")
            return True

        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a complete conversation session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Get session metadata
                session_row = conn.execute("""
                    SELECT * FROM sessions WHERE session_id = ?
                """, (session_id,)).fetchone()

                if not session_row:
                    return None

                # Get turns
                turn_rows = conn.execute("""
                    SELECT * FROM turns WHERE session_id = ? ORDER BY timestamp
                """, (session_id,)).fetchall()

                # Reconstruct session data
                session_data = {
                    'metadata': {
                        'session_id': session_row['session_id'],
                        'start_time': session_row['start_time'],
                        'end_time': session_row['end_time'],
                        'interaction_type': session_row['interaction_type'],
                        'project_context': session_row['project_context'],
                        'outcome_summary': session_row['outcome_summary'],
                        'quality_rating': session_row['quality_rating'],
                        'files_modified': json.loads(session_row['files_modified'] or '[]'),
                        'commands_executed': json.loads(session_row['commands_executed'] or '[]'),
                        'key_topics': json.loads(session_row['key_topics'] or '[]')
                    },
                    'turns': [],
                    'total_turns': session_row['total_turns'],
                    'total_tokens_estimate': session_row['total_tokens']
                }

                for turn_row in turn_rows:
                    turn_data = {
                        'turn_id': turn_row['turn_id'],
                        'timestamp': turn_row['timestamp'],
                        'user_prompt': turn_row['user_prompt'],
                        'claude_response': turn_row['claude_response'],
                        'tool_calls': json.loads(turn_row['tool_calls'] or '[]'),
                        'files_read': json.loads(turn_row['files_read'] or '[]'),
                        'files_modified': json.loads(turn_row['files_modified'] or '[]'),
                        'commands_executed': json.loads(turn_row['commands_executed'] or '[]'),
                        'error_occurred': turn_row['error_occurred'],
                        'error_details': turn_row['error_details']
                    }
                    session_data['turns'].append(turn_data)

                return session_data

        except Exception as e:
            logger.error(f"Failed to retrieve session {session_id}: {e}")
            return None

    def search_conversations(self,
                           query: str,
                           date_range: Optional[Tuple[str, str]] = None,
                           interaction_type: Optional[str] = None,
                           project_context: Optional[str] = None,
                           limit: int = 50) -> List[Dict[str, Any]]:
        """Search conversations using full-text search and filters"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                # Build query
                sql_parts = []
                params = []

                # Full-text search
                if query.strip():
                    sql_parts.append("""
                        SELECT DISTINCT s.*, t.turn_id, t.user_prompt, t.claude_response,
                               rank(matchinfo(turns_fts, 'pcnalx')) as rank
                        FROM sessions s
                        JOIN turns t ON s.session_id = t.session_id
                        JOIN turns_fts ON turns_fts.turn_id = t.turn_id
                        WHERE turns_fts MATCH ?
                    """)
                    params.append(query)
                else:
                    sql_parts.append("""
                        SELECT DISTINCT s.*, '' as turn_id, '' as user_prompt,
                               '' as claude_response, 0 as rank
                        FROM sessions s
                        WHERE 1=1
                    """)

                # Add filters
                if date_range:
                    sql_parts.append("AND s.start_time BETWEEN ? AND ?")
                    params.extend(date_range)

                if interaction_type:
                    sql_parts.append("AND s.interaction_type = ?")
                    params.append(interaction_type)

                if project_context:
                    sql_parts.append("AND s.project_context LIKE ?")
                    params.append(f"%{project_context}%")

                # Complete query
                full_query = " ".join(sql_parts)
                if query.strip():
                    full_query += " ORDER BY rank DESC"
                else:
                    full_query += " ORDER BY s.start_time DESC"
                full_query += f" LIMIT {limit}"

                results = conn.execute(full_query, params).fetchall()

                # Format results
                formatted_results = []
                for row in results:
                    result = {
                        'session_id': row['session_id'],
                        'start_time': row['start_time'],
                        'interaction_type': row['interaction_type'],
                        'project_context': row['project_context'],
                        'total_turns': row['total_turns'],
                        'outcome_summary': row['outcome_summary'],
                        'quality_rating': row['quality_rating']
                    }

                    if query.strip():
                        result['matched_content'] = {
                            'turn_id': row['turn_id'],
                            'user_prompt': row['user_prompt'][:200] + "..." if len(row['user_prompt']) > 200 else row['user_prompt'],
                            'claude_response': row['claude_response'][:200] + "..." if len(row['claude_response']) > 200 else row['claude_response'],
                            'rank': row['rank']
                        }

                    formatted_results.append(result)

                return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_daily_sessions(self, date: str) -> List[Dict[str, Any]]:
        """Get all sessions for a specific date"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                start_date = f"{date} 00:00:00"
                end_date = f"{date} 23:59:59"

                results = conn.execute("""
                    SELECT * FROM sessions
                    WHERE start_time BETWEEN ? AND ?
                    ORDER BY start_time
                """, (start_date, end_date)).fetchall()

                sessions = []
                for row in results:
                    session = {
                        'session_id': row['session_id'],
                        'start_time': row['start_time'],
                        'end_time': row['end_time'],
                        'interaction_type': row['interaction_type'],
                        'project_context': row['project_context'],
                        'total_turns': row['total_turns'],
                        'total_tokens': row['total_tokens'],
                        'outcome_summary': row['outcome_summary'],
                        'quality_rating': row['quality_rating'],
                        'files_modified': json.loads(row['files_modified'] or '[]'),
                        'commands_executed': json.loads(row['commands_executed'] or '[]'),
                        'key_topics': json.loads(row['key_topics'] or '[]')
                    }
                    sessions.append(session)

                return sessions

        except Exception as e:
            logger.error(f"Failed to get daily sessions for {date}: {e}")
            return []

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get usage statistics for the last N days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

                # Basic stats
                stats = conn.execute("""
                    SELECT
                        COUNT(*) as total_sessions,
                        SUM(total_turns) as total_turns,
                        SUM(total_tokens) as total_tokens,
                        AVG(quality_rating) as avg_quality
                    FROM sessions
                    WHERE start_time >= ?
                """, (cutoff_date,)).fetchone()

                # Interaction type distribution
                type_stats = conn.execute("""
                    SELECT interaction_type, COUNT(*) as count
                    FROM sessions
                    WHERE start_time >= ?
                    GROUP BY interaction_type
                    ORDER BY count DESC
                """, (cutoff_date,)).fetchall()

                # Daily activity
                daily_stats = conn.execute("""
                    SELECT
                        DATE(start_time) as date,
                        COUNT(*) as sessions,
                        SUM(total_turns) as turns
                    FROM sessions
                    WHERE start_time >= ?
                    GROUP BY DATE(start_time)
                    ORDER BY date DESC
                """, (cutoff_date,)).fetchall()

                return {
                    'period_days': days,
                    'total_sessions': stats[0],
                    'total_turns': stats[1] or 0,
                    'total_tokens': stats[2] or 0,
                    'avg_quality': round(stats[3] or 0, 2),
                    'interaction_types': [{'type': row[0], 'count': row[1]} for row in type_stats],
                    'daily_activity': [{'date': row[0], 'sessions': row[1], 'turns': row[2]} for row in daily_stats]
                }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def export_data(self,
                   output_path: str,
                   date_range: Optional[Tuple[str, str]] = None,
                   format_type: str = "json") -> bool:
        """Export conversation data in various formats"""
        try:
            # Get sessions to export
            if date_range:
                sessions = self.search_conversations("", date_range=date_range, limit=1000)
            else:
                sessions = self.search_conversations("", limit=1000)

            # Get full session data
            full_sessions = []
            for session_info in sessions:
                full_session = self.get_session(session_info['session_id'])
                if full_session:
                    full_sessions.append(full_session)

            # Export based on format
            if format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(full_sessions, f, indent=2, ensure_ascii=False)

            elif format_type.lower() == "markdown":
                self._export_markdown(full_sessions, output_path)

            else:
                raise ValueError(f"Unsupported format: {format_type}")

            logger.info(f"Exported {len(full_sessions)} sessions to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    def _export_markdown(self, sessions: List[Dict[str, Any]], output_path: str):
        """Export sessions as markdown"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Claude Conversation Export\n\n")
            f.write(f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Sessions: {len(sessions)}\n\n")

            for i, session in enumerate(sessions, 1):
                metadata = session['metadata']
                f.write(f"## Session {i}: {metadata['session_id']}\n\n")
                f.write(f"**Start Time**: {metadata['start_time']}\n")
                f.write(f"**Type**: {metadata['interaction_type']}\n")
                f.write(f"**Project**: {metadata.get('project_context', 'Unknown')}\n")
                f.write(f"**Turns**: {session['total_turns']}\n\n")

                for turn in session['turns']:
                    f.write(f"### {turn['timestamp']}\n\n")
                    f.write("**User:**\n")
                    f.write(f"{turn['user_prompt']}\n\n")
                    f.write("**Claude:**\n")
                    f.write(f"{turn['claude_response']}\n\n")

                f.write("---\n\n")

    def archive_old_data(self, days_to_keep: int = 90) -> int:
        """Archive conversations older than specified days"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get sessions to archive
                old_sessions = conn.execute("""
                    SELECT session_id FROM sessions WHERE start_time < ?
                """, (cutoff_date,)).fetchall()

                archived_count = 0
                for session_row in old_sessions:
                    session_id = session_row[0]

                    # Get full session data
                    session_data = self.get_session(session_id)
                    if session_data:
                        # Save to compressed archive
                        archive_file = self.archive_path / f"session_{session_id}.json.gz"
                        with gzip.open(archive_file, 'wt', encoding='utf-8') as f:
                            json.dump(session_data, f, indent=2)

                        # Remove from active database
                        conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
                        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                        conn.execute("DELETE FROM turns_fts WHERE turn_id LIKE ?", (f"{session_id}_%",))

                        archived_count += 1

                conn.commit()

            logger.info(f"Archived {archived_count} old sessions")
            return archived_count

        except Exception as e:
            logger.error(f"Archival failed: {e}")
            return 0

    def cleanup_database(self):
        """Perform database maintenance tasks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Rebuild FTS index
                conn.execute("INSERT INTO turns_fts(turns_fts) VALUES('rebuild')")

                # Vacuum database
                conn.execute("VACUUM")

                # Analyze for query optimization
                conn.execute("ANALYZE")

                conn.commit()

            logger.info("Database maintenance completed")

        except Exception as e:
            logger.error(f"Database cleanup failed: {e}")

# Test function
def test_storage_agent():
    """Test the Conversation Storage Agent"""
    storage = ConversationStorageAgent()

    # Test data
    test_session = {
        'metadata': {
            'session_id': 'test123',
            'start_time': '2024-01-15T10:00:00',
            'end_time': '2024-01-15T10:30:00',
            'interaction_type': 'coding',
            'project_context': 'Test Project',
            'outcome_summary': 'Created test function',
            'quality_rating': 4,
            'files_modified': ['test.py'],
            'commands_executed': ['python test.py'],
            'key_topics': ['testing', 'python']
        },
        'turns': [{
            'turn_id': 'test123_turn_001',
            'timestamp': '2024-01-15T10:05:00',
            'user_prompt': 'Help me create a test function',
            'claude_response': 'Here is a test function...',
            'tool_calls': [],
            'files_read': [],
            'files_modified': ['test.py'],
            'commands_executed': ['python test.py'],
            'error_occurred': False,
            'error_details': None
        }],
        'total_turns': 1,
        'total_tokens_estimate': 100
    }

    # Test storage
    assert storage.store_session(test_session)
    print("✓ Session stored successfully")

    # Test retrieval
    retrieved = storage.get_session('test123')
    assert retrieved is not None
    assert retrieved['metadata']['session_id'] == 'test123'
    print("✓ Session retrieved successfully")

    # Test search
    results = storage.search_conversations("test function")
    assert len(results) > 0
    print("✓ Search works")

    # Test statistics
    stats = storage.get_statistics(7)
    assert stats['total_sessions'] >= 1
    print("✓ Statistics generated")

    print("All tests passed!")

if __name__ == "__main__":
    test_storage_agent()