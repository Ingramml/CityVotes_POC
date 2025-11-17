"""
City Vote Extractor Factory

Factory pattern for creating city-specific vote extractors. Automatically
selects and configures the appropriate extractor based on city identification,
document content analysis, or explicit city specification.

Supported Cities:
- Santa Ana: SantaAnaVoteExtractor (7 members, specific patterns)
- Pomona: PomonaVoteExtractor (5 members, different format)
- Generic: VoteExtractionAgent (fallback for other cities)

Usage:
    factory = CityVoteExtractorFactory()
    extractor = factory.create_extractor("santa_ana")
    result = extractor.process_meeting_documents(agenda_path, minutes_path)
"""

import re
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Import all extractors
from .vote_extraction_agent import VoteExtractionAgent
from .santa_ana_vote_extractor import SantaAnaVoteExtractor
from .ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor
from .pomona_vote_extractor import PomonaVoteExtractor

logger = logging.getLogger(__name__)

class CityVoteExtractorFactory:
    """
    Factory for creating city-specific vote extractors.

    Provides automatic city detection, extractor selection, and
    configuration management for multiple city council formats.
    """

    def __init__(self):
        self.name = "CityVoteExtractorFactory"
        self.version = "1.0.0"

        # Registry of available extractors
        self.extractors = {
            'santa_ana': SantaAnaVoteExtractor,
            'santa_ana_ai': AIPoweredSantaAnaExtractor,  # AI-powered version
            'pomona': PomonaVoteExtractor,
            'generic': VoteExtractionAgent
        }

        # Use AI-powered extractor by default for Santa Ana
        self.use_ai_extractor = True

        # City identification patterns
        self.city_patterns = {
            'santa_ana': [
                r'CITY\s+OF\s+SANTA\s+ANA',
                r'Santa\s+Ana\s+City\s+Council',
                r'22\s+Civic\s+Center\s+Plaza',
                r'COUNCILMEMBER\s+BACERRA',
                r'COUNCILMEMBER\s+HERNANDEZ',
                r'COUNCILMEMBER\s+PENALOZA',
                r'COUNCILMEMBER\s+PHAN',
                r'COUNCILMEMBER\s+VAZQUEZ',
                r'MAYOR\s+AMEZCUA'
            ],
            'pomona': [
                r'CITY\s+OF\s+POMONA',
                r'Pomona\s+City\s+Council',
                r'Pomona\s+City\s+Hall',
                r'Mayor\s+Sandoval',
                r'District\s+\d+',
                # Add more Pomona-specific patterns as identified
            ]
        }

        # City configuration metadata
        self.city_configs = {
            'santa_ana': {
                'name': 'Santa Ana',
                'state': 'CA',
                'council_size': 7,
                'extractor_class': 'SantaAnaVoteExtractor',
                'confidence_threshold': 3
            },
            'pomona': {
                'name': 'Pomona',
                'state': 'CA',
                'council_size': 5,
                'extractor_class': 'PomonaVoteExtractor',
                'confidence_threshold': 2
            },
            'generic': {
                'name': 'Generic',
                'state': 'Unknown',
                'council_size': 'Variable',
                'extractor_class': 'VoteExtractionAgent',
                'confidence_threshold': 0
            }
        }

    def create_extractor(self, city_identifier: Optional[str] = None) -> VoteExtractionAgent:
        """
        Create appropriate city-specific vote extractor.

        Args:
            city_identifier: Optional city identifier ('santa_ana', 'pomona', etc.)
                           If None, will attempt auto-detection

        Returns:
            Configured vote extractor instance

        Example:
            extractor = factory.create_extractor("santa_ana")
            extractor = factory.create_extractor()  # Auto-detect
        """
        if city_identifier:
            # Use explicit city identifier
            city_key = city_identifier.lower()

            # Use AI-powered version for Santa Ana if available
            if city_key == 'santa_ana' and self.use_ai_extractor:
                city_key = 'santa_ana_ai'
                logger.info(f"Using AI-powered Santa Ana extractor")

            if city_key in self.extractors:
                extractor_class = self.extractors[city_key]
                logger.info(f"Creating {extractor_class.__name__} for {city_identifier}")
                return extractor_class()
            else:
                logger.warning(f"Unknown city identifier: {city_identifier}, using generic extractor")
                return self.extractors['generic']()
        else:
            # Auto-detection mode - return generic for now
            logger.info("No city identifier provided, using generic extractor")
            return self.extractors['generic']()

    def auto_detect_city(self, document_content: str) -> str:
        """
        Automatically detect city from document content.

        Args:
            document_content: Text content from agenda or minutes document

        Returns:
            Detected city identifier ('santa_ana', 'pomona', 'generic')
        """
        content_upper = document_content.upper()

        # Score each city based on pattern matches
        city_scores = {}

        for city, patterns in self.city_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, content_upper, re.IGNORECASE):
                    score += 1

            city_scores[city] = score
            logger.debug(f"City detection - {city}: {score} matches")

        # Find best match
        if city_scores:
            best_city = max(city_scores, key=city_scores.get)
            best_score = city_scores[best_city]

            # Check if score meets confidence threshold
            threshold = self.city_configs[best_city]['confidence_threshold']
            if best_score >= threshold:
                logger.info(f"Auto-detected city: {best_city} (score: {best_score})")
                return best_city
            else:
                logger.warning(f"Low confidence for {best_city} (score: {best_score}, threshold: {threshold})")

        logger.info("Could not auto-detect city, using generic extractor")
        return 'generic'

    def create_extractor_from_documents(self, agenda_path: str, minutes_path: str) -> VoteExtractionAgent:
        """
        Create extractor by analyzing document content for city identification.

        Args:
            agenda_path: Path to agenda document
            minutes_path: Path to minutes document

        Returns:
            Appropriate city-specific extractor
        """
        try:
            # Read both documents for analysis
            combined_content = ""

            for doc_path in [agenda_path, minutes_path]:
                if Path(doc_path).exists():
                    try:
                        with open(doc_path, 'r', encoding='utf-8') as f:
                            combined_content += f.read() + "\n"
                    except Exception as e:
                        logger.warning(f"Could not read {doc_path}: {str(e)}")

            if combined_content:
                # Auto-detect city from combined content
                detected_city = self.auto_detect_city(combined_content)
                return self.create_extractor(detected_city)
            else:
                logger.warning("Could not read any documents, using generic extractor")
                return self.create_extractor('generic')

        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            return self.create_extractor('generic')

    def process_meeting_documents(self, agenda_path: str, minutes_path: str,
                                city_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete processing pipeline with automatic extractor selection.

        Args:
            agenda_path: Path to agenda document
            minutes_path: Path to minutes document
            city_hint: Optional city hint to prefer during detection

        Returns:
            Complete extraction results with city-specific processing
        """
        try:
            # Create appropriate extractor
            if city_hint:
                extractor = self.create_extractor(city_hint)
            else:
                extractor = self.create_extractor_from_documents(agenda_path, minutes_path)

            # Process documents with selected extractor
            if hasattr(extractor, 'process_santa_ana_meeting') and (isinstance(extractor, SantaAnaVoteExtractor) or isinstance(extractor, AIPoweredSantaAnaExtractor)):
                result = extractor.process_santa_ana_meeting(agenda_path, minutes_path)
            elif hasattr(extractor, 'process_pomona_meeting') and isinstance(extractor, PomonaVoteExtractor):
                result = extractor.process_pomona_meeting(agenda_path, minutes_path)
            else:
                result = extractor.process_meeting_documents(agenda_path, minutes_path)

            # Add factory metadata
            result['factory_metadata'] = {
                'factory_version': self.version,
                'extractor_used': extractor.__class__.__name__,
                'city_detected': getattr(extractor, 'city_name', 'Unknown'),
                'auto_detection': city_hint is None
            }

            return result

        except Exception as e:
            logger.error(f"Factory processing failed: {str(e)}")
            return {
                'success': False,
                'message': f"Factory processing error: {str(e)}",
                'factory_metadata': {
                    'factory_version': self.version,
                    'error': str(e)
                }
            }

    def get_supported_cities(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all supported cities.

        Returns:
            Dictionary of city configurations and capabilities
        """
        return {
            city: {
                'config': config,
                'extractor_available': city in self.extractors,
                'patterns_count': len(self.city_patterns.get(city, [])),
                'description': self._get_city_description(city)
            }
            for city, config in self.city_configs.items()
        }

    def _get_city_description(self, city: str) -> str:
        """Get description for city extractor"""
        descriptions = {
            'santa_ana': 'Santa Ana City Council - 7 members, detailed recusal tracking, special session support',
            'pomona': 'Pomona City Council - 5 members, district-based representation, simplified format',
            'generic': 'Generic council extractor - flexible patterns, configurable thresholds'
        }
        return descriptions.get(city, 'Unknown city extractor')

    def validate_extractor_capabilities(self, city: str, requirements: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate that a city extractor meets specific requirements.

        Args:
            city: City identifier
            requirements: Dictionary of requirements to check

        Returns:
            Validation results for each requirement
        """
        if city not in self.city_configs:
            return {'supported': False}

        config = self.city_configs[city]
        results = {'supported': True}

        # Check council size requirement
        if 'council_size' in requirements:
            required_size = requirements['council_size']
            actual_size = config['council_size']
            results['council_size_match'] = (
                actual_size == required_size or
                actual_size == 'Variable'
            )

        # Check pattern availability
        if 'patterns_required' in requirements:
            available_patterns = len(self.city_patterns.get(city, []))
            required_patterns = requirements['patterns_required']
            results['sufficient_patterns'] = available_patterns >= required_patterns

        # Check extractor features
        if 'features' in requirements:
            extractor_class = self.extractors[city]
            for feature in requirements['features']:
                results[f'has_{feature}'] = hasattr(extractor_class, feature)

        return results

    def get_extraction_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about factory usage and extractor performance.

        Returns:
            Statistics dictionary
        """
        return {
            'factory_version': self.version,
            'supported_cities': len(self.extractors),
            'total_patterns': sum(len(patterns) for patterns in self.city_patterns.values()),
            'cities': {
                city: {
                    'patterns': len(self.city_patterns.get(city, [])),
                    'confidence_threshold': config['confidence_threshold'],
                    'council_size': config['council_size']
                }
                for city, config in self.city_configs.items()
            }
        }

# Convenience functions for easy usage
def create_city_extractor(city: str) -> VoteExtractionAgent:
    """
    Convenience function to create city-specific extractor.

    Args:
        city: City identifier ('santa_ana', 'pomona', 'generic')

    Returns:
        Configured vote extractor
    """
    factory = CityVoteExtractorFactory()
    return factory.create_extractor(city)

def process_city_meeting(agenda_path: str, minutes_path: str,
                        city: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for complete meeting processing.

    Args:
        agenda_path: Path to agenda document
        minutes_path: Path to minutes document
        city: Optional city identifier

    Returns:
        Complete extraction results
    """
    factory = CityVoteExtractorFactory()
    return factory.process_meeting_documents(agenda_path, minutes_path, city)

# Test function
def test_factory():
    """Test factory functionality"""
    factory = CityVoteExtractorFactory()

    # Test extractor creation
    santa_ana_extractor = factory.create_extractor('santa_ana')
    assert isinstance(santa_ana_extractor, SantaAnaVoteExtractor), "Should create Santa Ana extractor"

    pomona_extractor = factory.create_extractor('pomona')
    assert isinstance(pomona_extractor, PomonaVoteExtractor), "Should create Pomona extractor"

    generic_extractor = factory.create_extractor('generic')
    assert isinstance(generic_extractor, VoteExtractionAgent), "Should create generic extractor"

    # Test city detection
    santa_ana_content = "CITY OF SANTA ANA\nCOUNCILMEMBER BACERRA\nMAYOR AMEZCUA"
    detected = factory.auto_detect_city(santa_ana_content)
    assert detected == 'santa_ana', f"Should detect santa_ana, got {detected}"

    # Test supported cities
    supported = factory.get_supported_cities()
    assert 'santa_ana' in supported, "Should support Santa Ana"
    assert 'pomona' in supported, "Should support Pomona"

    print("✓ City Vote Extractor Factory tests passed!")

if __name__ == "__main__":
    test_factory()
    print("City Vote Extractor Factory created successfully!")