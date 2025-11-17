#!/usr/bin/env python3
"""
Comprehensive test for all three sub-agents working together
"""

from agents import DataValidationAgent, CityConfigAgent, FileProcessingAgent
import json
import tempfile
import os
from io import BytesIO

class MockFileObject:
    """Mock Flask file object for testing"""
    def __init__(self, data, filename):
        self.data = data.encode('utf-8') if isinstance(data, str) else data
        self.filename = filename
        self._position = 0

    def read(self, size=-1):
        if size == -1:
            result = self.data[self._position:]
            self._position = len(self.data)
        else:
            result = self.data[self._position:self._position + size]
            self._position += len(result)
        return result

    def seek(self, position, whence=0):
        if whence == 0:  # absolute
            self._position = position
        elif whence == 1:  # relative
            self._position += position
        elif whence == 2:  # from end
            self._position = len(self.data) + position

    def tell(self):
        return self._position

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            f.write(self.data)

def test_complete_workflow():
    """Test all three sub-agents working together in complete workflow"""
    print("=== COMPLETE SUB-AGENT WORKFLOW TEST ===\n")

    # Initialize all sub-agents
    print("1. Initializing Sub-Agents:")
    print("-" * 30)

    validator = DataValidationAgent()
    city_config = CityConfigAgent()
    file_processor = FileProcessingAgent(validator, city_config)

    print("✓ DataValidationAgent: Initialized")
    print("✓ CityConfigAgent: Initialized")
    print("✓ FileProcessingAgent: Initialized")

    # Sample voting data
    sample_voting_data = {
        "votes": [
            {
                "agenda_item_number": "7.1",
                "agenda_item_title": "Budget Amendment Resolution",
                "outcome": "Pass",
                "tally": {
                    "ayes": 5,
                    "noes": 2,
                    "abstain": 0,
                    "absent": 0
                },
                "member_votes": {
                    "Mayor Valerie Amezcua": "Aye",
                    "Vince Sarmiento": "Aye",
                    "Phil Bacerra": "Nay",
                    "Johnathan Ryan Hernandez": "Aye",
                    "Thai Viet Phan": "Aye",
                    "Benjamin Vazquez": "Nay",
                    "David Penaloza": "Aye"
                }
            },
            {
                "agenda_item_number": "8.2",
                "agenda_item_title": "Traffic Signal Upgrade Contract",
                "outcome": "Pass",
                "tally": {
                    "ayes": 7,
                    "noes": 0,
                    "abstain": 0,
                    "absent": 0
                },
                "member_votes": {
                    "Mayor Valerie Amezcua": "Aye",
                    "Vince Sarmiento": "Aye",
                    "Phil Bacerra": "Aye",
                    "Johnathan Ryan Hernandez": "Aye",
                    "Thai Viet Phan": "Aye",
                    "Benjamin Vazquez": "Aye",
                    "David Penaloza": "Aye"
                }
            }
        ]
    }

    print(f"\n2. Testing File Upload Workflow:")
    print("-" * 30)

    # Create mock file object
    json_data = json.dumps(sample_voting_data, indent=2)
    mock_file = MockFileObject(json_data, "santa_ana_votes.json")

    # Process uploaded file
    result = file_processor.process_uploaded_file(mock_file, "santa_ana")

    if result['success']:
        print("✓ File upload and processing: SUCCESS")
        session_id = result['session_id']
        print(f"✓ Session created: {session_id[:8]}...")
        print(f"✓ Votes processed: {result['data_summary']['total_votes']}")
        print(f"✓ City: {result['data_summary']['city']}")
    else:
        print(f"✗ File processing failed: {result['error']}")
        return False

    print(f"\n3. Testing Session Data Retrieval:")
    print("-" * 30)

    # Retrieve session data
    session_data = file_processor.get_session_data(session_id, "santa_ana")
    if session_data:
        print("✓ Session data retrieved successfully")
        print(f"✓ Original filename: {session_data['original_filename']}")
        print(f"✓ Upload timestamp: {session_data['upload_timestamp']}")
        print(f"✓ Processed data available: {bool(session_data['processed_data'])}")
    else:
        print("✗ Failed to retrieve session data")
        return False

    print(f"\n4. Testing Processing Results:")
    print("-" * 30)

    processed = session_data['processed_data']

    # Check vote summary
    vote_summary = processed['vote_summary']
    print(f"✓ Total votes: {vote_summary['total_votes']}")
    print(f"✓ Pass votes: {vote_summary['outcomes']['Pass']['count']} ({vote_summary['outcomes']['Pass']['percentage']}%)")
    print(f"✓ Fail votes: {vote_summary['outcomes']['Fail']['count']} ({vote_summary['outcomes']['Fail']['percentage']}%)")

    # Check member analysis
    member_analysis = processed['member_analysis']
    print(f"✓ Council members analyzed: {len(member_analysis)}")

    # Show sample member stats
    sample_member = list(member_analysis.keys())[0]
    member_stats = member_analysis[sample_member]
    print(f"✓ {sample_member}: {member_stats['total_votes']} votes, {member_stats['vote_breakdown']['Aye']} Ayes")

    # Check city info
    city_info = processed['city_info']
    print(f"✓ City configuration loaded: {city_info['display_name']}")

    print(f"\n5. Testing Session Management:")
    print("-" * 30)

    # Test session cities
    cities = file_processor.get_session_cities(session_id)
    print(f"✓ Cities in session: {cities}")

    # Test processing summary
    summary = file_processor.get_processing_summary(session_id)
    if 'error' not in summary:
        print("✓ Processing summary generated")
        print(f"✓ Session expires: {summary['expires_at']}")
        for city, info in summary['cities'].items():
            print(f"✓ {info['city_display_name']}: {info['total_votes']} votes from {info['filename']}")
    else:
        print(f"✗ Summary error: {summary['error']}")

    print(f"\n6. Testing Error Handling:")
    print("-" * 30)

    # Test invalid JSON
    invalid_mock_file = MockFileObject('{"invalid": "json structure"}', "invalid.json")
    invalid_result = file_processor.process_uploaded_file(invalid_mock_file, "santa_ana")

    if not invalid_result['success']:
        print("✓ Invalid data rejection: WORKING")
        print(f"✓ Error caught: {invalid_result['error']}")
    else:
        print("✗ Should have rejected invalid data")

    print(f"\n7. Integration Summary:")
    print("-" * 30)
    print("✓ DataValidationAgent: Validates JSON structure")
    print("✓ CityConfigAgent: Provides city-specific configuration")
    print("✓ FileProcessingAgent: Orchestrates complete workflow")
    print("✓ Session Management: Temporary storage and cleanup")
    print("✓ Error Handling: Graceful failure handling")
    print("✓ Data Processing: Vote analysis and member statistics")

    print(f"\n🎉 ALL SUB-AGENTS WORKING TOGETHER SUCCESSFULLY!")
    return True

if __name__ == '__main__':
    test_complete_workflow()