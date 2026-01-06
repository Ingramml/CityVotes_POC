#!/usr/bin/env python3
"""
Simple Data Validation Sub-Agent for CityVotes POC
Validates basic JSON structure for voting data
"""

import json
from typing import Dict, List, Tuple, Any

class DataValidationAgent:
    """Simple sub-agent to validate uploaded voting data JSON files"""

    def __init__(self):
        """Initialize with basic required fields"""
        self.required_fields = [
            'agenda_item_number',
            'agenda_item_title',
            'outcome',
            'tally',
            'member_votes'
        ]

        self.valid_outcomes = ['PASS', 'FAIL', 'FLAG', 'CONTINUED', 'REMOVED', 'TIE']

    def validate_json(self, file_data: Dict, city_name: str) -> Tuple[bool, List[str]]:
        """
        Validate uploaded JSON file data

        Args:
            file_data: Dictionary from uploaded JSON file
            city_name: Name of the city (for context)

        Returns:
            Tuple of (is_valid: bool, errors: List[str])
        """
        errors = []

        # Check if data has votes array
        if 'votes' not in file_data:
            errors.append("Missing 'votes' array in JSON file")
            return False, errors

        votes = file_data['votes']
        if not isinstance(votes, list):
            errors.append("'votes' must be an array")
            return False, errors

        if len(votes) == 0:
            errors.append("No vote data found")
            return False, errors

        # Validate each vote
        for i, vote in enumerate(votes):
            vote_errors = self._validate_single_vote(vote, i)
            errors.extend(vote_errors)

        # Return results
        is_valid = len(errors) == 0
        return is_valid, errors

    def _validate_single_vote(self, vote: Dict, vote_index: int) -> List[str]:
        """Validate a single vote entry"""
        errors = []
        vote_prefix = f"Vote {vote_index + 1}"

        # Check required fields
        for field in self.required_fields:
            if field not in vote:
                errors.append(f"{vote_prefix}: Missing required field '{field}'")

        # Validate outcome if present
        if 'outcome' in vote:
            if vote['outcome'] not in self.valid_outcomes:
                errors.append(f"{vote_prefix}: Invalid outcome '{vote['outcome']}'. Must be one of: {', '.join(self.valid_outcomes)}")

        # Validate tally structure if present
        if 'tally' in vote:
            tally_errors = self._validate_tally(vote['tally'], vote_prefix)
            errors.extend(tally_errors)

        # Validate member_votes if present
        if 'member_votes' in vote:
            member_errors = self._validate_member_votes(vote['member_votes'], vote_prefix)
            errors.extend(member_errors)

        return errors

    def _validate_tally(self, tally: Any, vote_prefix: str) -> List[str]:
        """Validate tally structure"""
        errors = []

        if not isinstance(tally, dict):
            errors.append(f"{vote_prefix}: 'tally' must be an object")
            return errors

        # Check for expected tally fields
        expected_fields = ['ayes', 'noes']
        for field in expected_fields:
            if field not in tally:
                errors.append(f"{vote_prefix}: Tally missing '{field}' count")
            elif not isinstance(tally[field], int) or tally[field] < 0:
                errors.append(f"{vote_prefix}: Tally '{field}' must be a non-negative integer")

        return errors

    def _validate_member_votes(self, member_votes: Any, vote_prefix: str) -> List[str]:
        """Validate member votes structure"""
        errors = []

        if not isinstance(member_votes, dict):
            errors.append(f"{vote_prefix}: 'member_votes' must be an object")
            return errors

        if len(member_votes) == 0:
            errors.append(f"{vote_prefix}: 'member_votes' cannot be empty")

        # Validate each member vote
        valid_vote_choices = ['AYE', 'NAY', 'ABSTAIN', 'ABSENT', 'RECUSAL']
        for member, vote_choice in member_votes.items():
            if vote_choice not in valid_vote_choices:
                errors.append(f"{vote_prefix}: Invalid vote '{vote_choice}' for member '{member}'. Must be one of: {', '.join(valid_vote_choices)}")

        return errors

    def get_validation_summary(self, file_data: Dict) -> Dict:
        """Get a summary of the data structure for debugging"""
        if 'votes' not in file_data:
            return {'error': 'No votes array found'}

        votes = file_data['votes']
        return {
            'total_votes': len(votes),
            'has_required_structure': 'votes' in file_data,
            'sample_vote_keys': list(votes[0].keys()) if votes else [],
            'first_vote_preview': votes[0] if votes else None
        }


# Simple test function
def test_agent():
    """Basic test for the validation agent"""
    agent = DataValidationAgent()

    # Test valid data
    valid_data = {
        'votes': [{
            'agenda_item_number': '1',
            'agenda_item_title': 'Test Motion',
            'outcome': 'Pass',
            'tally': {'ayes': 4, 'noes': 1},
            'member_votes': {
                'Mayor Smith': 'Aye',
                'Council Member Jones': 'Aye'
            }
        }]
    }

    is_valid, errors = agent.validate_json(valid_data, 'test_city')
    print(f"Valid data test: {is_valid}, Errors: {errors}")

    # Test invalid data
    invalid_data = {
        'votes': [{
            'agenda_item_number': '1'
            # Missing required fields
        }]
    }

    is_valid, errors = agent.validate_json(invalid_data, 'test_city')
    print(f"Invalid data test: {is_valid}, Errors: {errors}")


if __name__ == '__main__':
    test_agent()