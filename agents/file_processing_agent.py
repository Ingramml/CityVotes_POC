#!/usr/bin/env python3
"""
File Processing Sub-Agent for CityVotes POC
Handles file upload workflow: upload → validate → process → store
"""

import json
import uuid
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import shutil

class FileProcessingAgent:
    """Sub-agent to handle file upload, processing, and session management"""

    def __init__(self, data_validator=None, city_config=None):
        """
        Initialize with other sub-agents for coordination

        Args:
            data_validator: DataValidationAgent instance
            city_config: CityConfigAgent instance
        """
        self.data_validator = data_validator
        self.city_config = city_config

        # Session storage (in production, use Redis or database)
        self.sessions = {}

        # Temporary file storage
        self.temp_dir = Path(tempfile.gettempdir()) / "cityvotes_poc"
        self.temp_dir.mkdir(exist_ok=True)

        # Session settings
        self.session_timeout = timedelta(hours=2)  # 2-hour session timeout
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit

    def process_uploaded_file(self, file_object, city_name: str, session_id: str = None) -> Dict:
        """
        Main workflow: upload → validate → process → store

        Args:
            file_object: Flask file object from request.files
            city_name: Target city for processing
            session_id: Session identifier (creates new if None)

        Returns:
            Dict with processing results
        """
        if not session_id:
            session_id = self._create_session()

        try:
            # Step 1: Basic file validation
            file_check = self._validate_uploaded_file(file_object)
            if not file_check['valid']:
                return {
                    'success': False,
                    'error': file_check['error'],
                    'session_id': session_id
                }

            # Step 2: Save file temporarily
            temp_file_path = self._save_temp_file(file_object, session_id)

            # Step 3: Parse JSON
            try:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Invalid JSON format: {str(e)}',
                    'session_id': session_id
                }

            # Step 4: Validate with DataValidationAgent
            if self.data_validator:
                is_valid, validation_errors = self.data_validator.validate_json(file_data, city_name)
                if not is_valid:
                    return {
                        'success': False,
                        'error': 'Data validation failed',
                        'validation_errors': validation_errors,
                        'session_id': session_id
                    }
            else:
                # Basic validation if no validator available
                if 'votes' not in file_data:
                    return {
                        'success': False,
                        'error': 'JSON must contain "votes" array',
                        'session_id': session_id
                    }

            # Step 5: Process with city configuration
            processed_data = self._process_with_city_config(file_data, city_name)

            # Step 6: Store in session
            self._store_session_data(session_id, city_name, {
                'original_filename': file_object.filename,
                'upload_timestamp': datetime.now().isoformat(),
                'raw_data': file_data,
                'processed_data': processed_data,
                'city': city_name,
                'temp_file_path': str(temp_file_path)
            })

            # Step 7: Cleanup temp file
            self._cleanup_temp_file(temp_file_path)

            return {
                'success': True,
                'message': 'File processed successfully',
                'session_id': session_id,
                'data_summary': {
                    'total_votes': len(file_data.get('votes', [])),
                    'city': city_name,
                    'filename': file_object.filename,
                    'processed_at': datetime.now().isoformat()
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'session_id': session_id
            }

    def get_session_data(self, session_id: str, city: str = None) -> Optional[Dict]:
        """
        Retrieve processed data for dashboard display

        Args:
            session_id: Session identifier
            city: Specific city data to retrieve (optional)

        Returns:
            Session data or None if not found/expired
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]

        # Check expiration
        if datetime.now() > session['expires_at']:
            self._cleanup_session(session_id)
            return None

        if city and city in session['data']:
            return session['data'][city]

        return session['data']

    def get_session_cities(self, session_id: str) -> List[str]:
        """Get list of cities with data in this session"""
        session_data = self.get_session_data(session_id)
        return list(session_data.keys()) if session_data else []

    def get_processing_summary(self, session_id: str) -> Dict:
        """Get summary of all processed data in session"""
        if session_id not in self.sessions:
            return {'error': 'Session not found'}

        session = self.sessions[session_id]
        if datetime.now() > session['expires_at']:
            return {'error': 'Session expired'}

        summary = {
            'session_id': session_id,
            'created_at': session['created_at'],
            'expires_at': session['expires_at'].isoformat(),
            'cities': {}
        }

        for city, data in session['data'].items():
            summary['cities'][city] = {
                'filename': data['original_filename'],
                'upload_time': data['upload_timestamp'],
                'total_votes': len(data['raw_data'].get('votes', [])),
                'city_display_name': self._get_city_display_name(city)
            }

        return summary

    def cleanup_expired_sessions(self):
        """Remove expired sessions and their temporary files"""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            if current_time > session['expires_at']:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self._cleanup_session(session_id)

        return len(expired_sessions)

    def _create_session(self) -> str:
        """Create new session with unique ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'expires_at': datetime.now() + self.session_timeout,
            'data': {}
        }
        return session_id

    def _validate_uploaded_file(self, file_object) -> Dict:
        """Basic file validation before processing"""
        if not file_object or not file_object.filename:
            return {'valid': False, 'error': 'No file provided'}

        if not file_object.filename.lower().endswith('.json'):
            return {'valid': False, 'error': 'File must be JSON format (.json extension)'}

        # Check file size (approximate)
        file_object.seek(0, 2)  # Seek to end
        file_size = file_object.tell()
        file_object.seek(0)  # Reset to beginning

        if file_size > self.max_file_size:
            return {'valid': False, 'error': f'File too large (max {self.max_file_size // (1024*1024)}MB)'}

        if file_size == 0:
            return {'valid': False, 'error': 'File is empty'}

        return {'valid': True}

    def _save_temp_file(self, file_object, session_id: str) -> Path:
        """Save uploaded file temporarily"""
        # Create session-specific temp directory
        session_dir = self.temp_dir / session_id
        session_dir.mkdir(exist_ok=True)

        # Generate safe filename
        safe_filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        temp_file_path = session_dir / safe_filename

        # Save file
        file_object.save(str(temp_file_path))
        return temp_file_path

    def _process_with_city_config(self, file_data: Dict, city_name: str) -> Dict:
        """Process data with city-specific configuration"""
        processed = {
            'vote_summary': self._calculate_vote_summary(file_data),
            'member_analysis': self._analyze_members(file_data, city_name),
            'city_info': self._get_city_info(city_name)
        }
        return processed

    def _calculate_vote_summary(self, file_data: Dict) -> Dict:
        """Calculate basic vote statistics"""
        votes = file_data.get('votes', [])

        summary = {
            'total_votes': len(votes),
            'outcomes': {'Pass': 0, 'Fail': 0, 'Tie': 0, 'Continued': 0}
        }

        for vote in votes:
            outcome = vote.get('outcome', 'Unknown')
            if outcome in summary['outcomes']:
                summary['outcomes'][outcome] += 1

        # Calculate percentages
        if summary['total_votes'] > 0:
            for outcome, count in summary['outcomes'].items():
                summary['outcomes'][outcome] = {
                    'count': count,
                    'percentage': round((count / summary['total_votes']) * 100, 1)
                }

        return summary

    def _analyze_members(self, file_data: Dict, city_name: str) -> Dict:
        """Analyze council member voting patterns"""
        votes = file_data.get('votes', [])
        member_stats = {}

        for vote in votes:
            member_votes = vote.get('member_votes', {})
            for member, vote_choice in member_votes.items():
                if member not in member_stats:
                    member_stats[member] = {
                        'total_votes': 0,
                        'vote_breakdown': {'Aye': 0, 'Nay': 0, 'Abstain': 0, 'Absent': 0}
                    }

                member_stats[member]['total_votes'] += 1
                if vote_choice in member_stats[member]['vote_breakdown']:
                    member_stats[member]['vote_breakdown'][vote_choice] += 1

        return member_stats

    def _get_city_info(self, city_name: str) -> Dict:
        """Get city configuration information"""
        if self.city_config:
            return self.city_config.get_city_config(city_name) or {}
        return {'name': city_name}

    def _get_city_display_name(self, city_name: str) -> str:
        """Get display name for city"""
        if self.city_config:
            config = self.city_config.get_city_config(city_name)
            return config['display_name'] if config else city_name.title()
        return city_name.title()

    def _store_session_data(self, session_id: str, city_name: str, data: Dict):
        """Store processed data in session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created_at': datetime.now().isoformat(),
                'expires_at': datetime.now() + self.session_timeout,
                'data': {}
            }

        self.sessions[session_id]['data'][city_name] = data

    def _cleanup_temp_file(self, temp_file_path: Path):
        """Remove temporary file"""
        try:
            if temp_file_path.exists():
                temp_file_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors

    def _cleanup_session(self, session_id: str):
        """Remove session and associated temporary files"""
        if session_id in self.sessions:
            # Clean up temp files for this session
            session_dir = self.temp_dir / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir, ignore_errors=True)

            # Remove session data
            del self.sessions[session_id]


# Simple test function
def test_agent():
    """Basic test for the file processing agent"""
    from data_validation_agent import DataValidationAgent
    from city_config_agent import CityConfigAgent

    # Initialize dependencies
    validator = DataValidationAgent()
    city_config = CityConfigAgent()

    # Initialize file processor
    processor = FileProcessingAgent(validator, city_config)

    print("✓ File Processing Agent initialized")
    print(f"✓ Temp directory: {processor.temp_dir}")
    print(f"✓ Session timeout: {processor.session_timeout}")
    print(f"✓ Max file size: {processor.max_file_size // (1024*1024)}MB")

    # Test session creation
    session_id = processor._create_session()
    print(f"✓ Test session created: {session_id[:8]}...")

    # Test cleanup
    processor.cleanup_expired_sessions()
    print("✓ Cleanup function working")


if __name__ == '__main__':
    test_agent()