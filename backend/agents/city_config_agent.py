#!/usr/bin/env python3
"""
Simple City Configuration Sub-Agent for CityVotes POC
Manages basic city-specific settings and council member info
"""

from typing import Dict, List, Optional

class CityConfigAgent:
    """Simple sub-agent to manage city-specific configurations"""

    def __init__(self):
        """Initialize with basic city configurations"""
        self.configs = {
            'santa_ana': {
                'name': 'Santa Ana',
                'display_name': 'Santa Ana, CA',
                'council_members': [
                    'Mayor Valerie Amezcua',
                    'Johnathan Ryan Hernandez',
                    'Jessie Lopez',
                    'David Penaloza',
                    'Benjamin Vazquez',
                    'Thai Viet Phan',
                    'Phil Bacerra'
                ],
                'colors': {
                    'primary': '#1f4e79',    # Blue
                    'secondary': '#f4b942',   # Gold
                    'success': '#28a745',     # Green
                    'danger': '#dc3545'       # Red
                },
                'total_seats': 7
            }
        }

    def get_city_config(self, city_name: str) -> Optional[Dict]:
        """
        Get complete configuration for a city

        Args:
            city_name: Name of the city (e.g., 'santa_ana', 'pomona')

        Returns:
            Dictionary with city configuration or None if city not found
        """
        city_key = city_name.lower().replace(' ', '_')
        return self.configs.get(city_key)

    def get_supported_cities(self) -> List[str]:
        """Get list of all supported cities"""
        return list(self.configs.keys())

    def get_city_display_names(self) -> Dict[str, str]:
        """Get mapping of city keys to display names"""
        return {
            key: config['display_name']
            for key, config in self.configs.items()
        }

    def validate_member_name(self, member_name: str, city_name: str) -> bool:
        """
        Check if a member name exists in a city's roster

        Args:
            member_name: Name of the council member
            city_name: Name of the city

        Returns:
            True if member exists in city roster, False otherwise
        """
        config = self.get_city_config(city_name)
        if not config:
            return False

        # Simple name matching (case-insensitive)
        member_names = [name.lower() for name in config['council_members']]
        return member_name.lower() in member_names

    def get_city_colors(self, city_name: str) -> Dict[str, str]:
        """Get color scheme for a city"""
        config = self.get_city_config(city_name)
        if not config:
            # Return default colors if city not found
            return {
                'primary': '#6c757d',     # Gray
                'secondary': '#e9ecef',   # Light gray
                'success': '#28a745',     # Green
                'danger': '#dc3545'       # Red
            }
        return config['colors']

    def get_council_size(self, city_name: str) -> int:
        """Get total number of council seats for a city"""
        config = self.get_city_config(city_name)
        return config['total_seats'] if config else 0

    def add_city_config(self, city_key: str, config_data: Dict) -> bool:
        """
        Add a new city configuration (for future expansion)

        Args:
            city_key: Unique key for the city (e.g., 'riverside')
            config_data: Dictionary with city configuration

        Returns:
            True if added successfully, False if city already exists
        """
        if city_key in self.configs:
            return False

        # Validate required fields
        required_fields = ['name', 'display_name', 'council_members', 'colors', 'total_seats']
        if not all(field in config_data for field in required_fields):
            return False

        self.configs[city_key] = config_data
        return True

    def get_config_summary(self) -> Dict:
        """Get summary of all configured cities"""
        summary = {}
        for city_key, config in self.configs.items():
            summary[city_key] = {
                'display_name': config['display_name'],
                'council_size': config['total_seats'],
                'members_configured': len(config['council_members'])
            }
        return summary


# Simple test function
def test_agent():
    """Basic test for the city configuration agent"""
    agent = CityConfigAgent()

    # Test getting city config
    santa_ana_config = agent.get_city_config('santa_ana')
    print(f"Santa Ana config: {santa_ana_config['name']} with {santa_ana_config['total_seats']} seats")

    # Test supported cities
    cities = agent.get_supported_cities()
    print(f"Supported cities: {cities}")

    # Test member validation
    valid_member = agent.validate_member_name('Mayor Valerie Amezcua', 'santa_ana')
    invalid_member = agent.validate_member_name('John Doe', 'santa_ana')
    print(f"Valid member test: {valid_member}")
    print(f"Invalid member test: {invalid_member}")

    # Test colors
    colors = agent.get_city_colors('santa_ana')
    print(f"Santa Ana colors: {colors}")

    # Test summary
    summary = agent.get_config_summary()
    print(f"Config summary: {summary}")


if __name__ == '__main__':
    test_agent()