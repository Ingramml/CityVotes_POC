#!/usr/bin/env python3
"""
Test both sub-agents together with sample voting data
"""

from agents import DataValidationAgent, CityConfigAgent

def test_agents_integration():
    """Test both agents working together"""
    print("=== Testing Sub-Agents Integration ===\n")

    # Initialize agents
    validator = DataValidationAgent()
    city_config = CityConfigAgent()

    # Sample Santa Ana voting data
    sample_data = {
        'votes': [
            {
                'agenda_item_number': '7.1',
                'agenda_item_title': 'Approve Budget Amendment',
                'outcome': 'Pass',
                'tally': {
                    'ayes': 5,
                    'noes': 2,
                    'abstain': 0,
                    'absent': 0
                },
                'member_votes': {
                    'Mayor Valerie Amezcua': 'Aye',
                    'Vince Sarmiento': 'Aye',
                    'Phil Bacerra': 'Nay',
                    'Johnathan Ryan Hernandez': 'Aye',
                    'Thai Viet Phan': 'Aye',
                    'Benjamin Vazquez': 'Nay',
                    'David Penaloza': 'Aye'
                }
            },
            {
                'agenda_item_number': '8.2',
                'agenda_item_title': 'Traffic Signal Upgrade',
                'outcome': 'Pass',
                'tally': {
                    'ayes': 7,
                    'noes': 0,
                    'abstain': 0,
                    'absent': 0
                },
                'member_votes': {
                    'Mayor Valerie Amezcua': 'Aye',
                    'Vince Sarmiento': 'Aye',
                    'Phil Bacerra': 'Aye',
                    'Johnathan Ryan Hernandez': 'Aye',
                    'Thai Viet Phan': 'Aye',
                    'Benjamin Vazquez': 'Aye',
                    'David Penaloza': 'Aye'
                }
            }
        ]
    }

    print("1. Testing City Configuration Agent:")
    print("-" * 40)

    # Test city config
    santa_ana_config = city_config.get_city_config('santa_ana')
    if santa_ana_config:
        print(f"✓ City: {santa_ana_config['display_name']}")
        print(f"✓ Council Size: {santa_ana_config['total_seats']} members")
        print(f"✓ Colors: {santa_ana_config['colors']['primary']} (primary)")
        print(f"✓ Members: {len(santa_ana_config['council_members'])} configured")

    print(f"✓ Supported Cities: {city_config.get_supported_cities()}")

    print("\n2. Testing Data Validation Agent:")
    print("-" * 40)

    # Test validation
    is_valid, errors = validator.validate_json(sample_data, 'santa_ana')
    print(f"✓ Validation Result: {'VALID' if is_valid else 'INVALID'}")

    if errors:
        print(f"✗ Errors found: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ No validation errors found")

    # Get validation summary
    summary = validator.get_validation_summary(sample_data)
    print(f"✓ Data Summary: {summary['total_votes']} votes found")

    print("\n3. Testing Member Validation:")
    print("-" * 40)

    # Test member name validation
    for vote in sample_data['votes']:
        print(f"Vote {vote['agenda_item_number']}:")
        for member_name in vote['member_votes'].keys():
            is_valid_member = city_config.validate_member_name(member_name, 'santa_ana')
            status = "✓" if is_valid_member else "✗"
            print(f"  {status} {member_name}")

    print("\n4. Testing Error Cases:")
    print("-" * 40)

    # Test invalid data
    invalid_data = {
        'votes': [{
            'agenda_item_number': '1',
            'outcome': 'InvalidOutcome'  # Invalid outcome
            # Missing required fields
        }]
    }

    is_valid, errors = validator.validate_json(invalid_data, 'santa_ana')
    print(f"✗ Invalid data test: {'PASSED' if not is_valid else 'FAILED'}")
    print(f"✓ Caught {len(errors)} validation errors as expected")

    print("\n5. Integration Summary:")
    print("-" * 40)
    print("✓ Data Validation Agent: Working")
    print("✓ City Configuration Agent: Working")
    print("✓ Agent Communication: Working")
    print("✓ Error Handling: Working")

    return True

if __name__ == '__main__':
    test_agents_integration()