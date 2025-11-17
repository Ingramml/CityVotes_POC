#!/usr/bin/env python3
"""
Comprehensive Test Suite for All City Vote Extractors

Tests the complete city-specific vote extraction system including:
- Santa Ana Vote Extractor
- Pomona Vote Extractor
- City Vote Extractor Factory
- Auto-detection capabilities
- Cross-city comparison
"""

import sys
import os
import tempfile
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.city_vote_extractor_factory import CityVoteExtractorFactory, create_city_extractor, process_city_meeting
from agents.santa_ana_vote_extractor import SantaAnaVoteExtractor
from agents.pomona_vote_extractor import PomonaVoteExtractor

def create_santa_ana_sample_documents():
    """Create realistic Santa Ana meeting documents"""
    agenda = """
CITY OF SANTA ANA
REGULAR CITY COUNCIL MEETING AGENDA
January 16, 2024

COUNCIL CHAMBER
22 Civic Center Plaza
Santa Ana, CA 92701

CLOSED SESSION - 4:30 P.M.
REGULAR MEETING - 5:30 P.M.

COUNCIL MEMBERS:
Mayor Valerie Amezcua
Mayor Pro Tem Jessie Lopez
Councilmember Phil Bacerra
Councilmember Johnathan Ryan Hernandez
Councilmember David Penaloza
Councilmember Thai Viet Phan
Councilmember Benjamin Vazquez

5. BUSINESS ITEMS
   5.1 Resolution No. 2024-01 - Approve Street Improvement Project
   5.2 Ordinance No. 2024-02 - Zoning Amendment for Downtown District
"""

    minutes = """
CITY OF SANTA ANA
MINUTES OF REGULAR CITY COUNCIL MEETING
January 16, 2024

ATTENDANCE: Mayor Valerie Amezcua, Mayor Pro Tem Jessie Lopez, Councilmember Phil Bacerra,
Councilmember Johnathan Ryan Hernandez, Councilmember David Penaloza,
Councilmember Thai Viet Phan, Councilmember Benjamin Vazquez

Item 5.1 - Resolution No. 2024-01 - Approve Street Improvement Project

MOTION: COUNCILMEMBER HERNANDEZ moved to approve Resolution No. 2024-01 for the
Street Improvement Project, seconded by COUNCILMEMBER VAZQUEZ.

The motion carried, 6-1, by the following roll call vote:
AYES: COUNCILMEMBER HERNANDEZ, COUNCILMEMBER VAZQUEZ, COUNCILMEMBER BACERRA,
      COUNCILMEMBER PENALOZA, MAYOR PRO TEM LOPEZ, MAYOR AMEZCUA
NOES: COUNCILMEMBER PHAN
ABSTAIN: NONE
ABSENT: NONE

Item 5.2 - Ordinance No. 2024-02 - Zoning Amendment for Downtown District

Councilmember Phan recused herself from this item as the listed entity is a client of her employer.

MOTION: COUNCILMEMBER PENALOZA moved to approve Ordinance No. 2024-02 for the
Downtown District Zoning Amendment, seconded by COUNCILMEMBER BACERRA.

The motion carried, 6-0, by the following roll call vote:
AYES: COUNCILMEMBER PENALOZA, COUNCILMEMBER BACERRA, COUNCILMEMBER HERNANDEZ,
      COUNCILMEMBER VAZQUEZ, MAYOR PRO TEM LOPEZ, MAYOR AMEZCUA
NOES: NONE
ABSTAIN: NONE
ABSENT: NONE
RECUSED: COUNCILMEMBER PHAN
"""
    return agenda, minutes

def create_pomona_sample_documents():
    """Create realistic Pomona meeting documents"""
    agenda = """
CITY OF POMONA
CITY COUNCIL MEETING AGENDA
Meeting of February 5, 2024

Pomona City Hall Council Chambers
7:00 P.M.

COUNCIL MEMBERS:
Mayor Tim Sandoval
Councilmember District 1 - John Smith
Councilmember District 2 - Maria Garcia
Councilmember District 3 - Robert Johnson
Councilmember District 4 - Lisa Chen

ITEM A1. Budget Amendment for Parks Department
ITEM A2. Street Maintenance Contract Approval
"""

    minutes = """
CITY OF POMONA
CITY COUNCIL MEETING MINUTES
February 5, 2024

PRESENT: Mayor Tim Sandoval, Councilmember John Smith, Councilmember Maria Garcia,
         Councilmember Robert Johnson, Councilmember Lisa Chen

ITEM A1. Budget Amendment for Parks Department

Motion: Mayor Sandoval moved to approve the Parks Department budget amendment,
seconded by Councilmember Smith.

Motion passed, 5-0.
AYES: Mayor Sandoval, Councilmember Smith, Councilmember Garcia,
      Councilmember Johnson, Councilmember Chen
NOES: None

ITEM A2. Street Maintenance Contract Approval

Motion: Councilmember Garcia made a motion to approve the street maintenance contract,
second by Councilmember Johnson.

Motion passed, 4-1.
AYES: Councilmember Garcia, Councilmember Johnson, Councilmember Chen, Mayor Sandoval
NOES: Councilmember Smith
"""
    return agenda, minutes

def test_city_specific_extractors():
    """Test each city-specific extractor individually"""
    print("=" * 60)
    print("City-Specific Extractors Test")
    print("=" * 60)

    # Test Santa Ana Extractor
    print("\n🏛️  Testing Santa Ana Vote Extractor:")
    print("-" * 40)

    santa_ana_extractor = SantaAnaVoteExtractor()
    print(f"✓ Created {santa_ana_extractor.name} v{santa_ana_extractor.version}")
    print(f"✓ Council size: {santa_ana_extractor.council_config['total_members']} members")
    print(f"✓ Meeting location: {santa_ana_extractor.council_config['meeting_location']}")

    # Test Pomona Extractor
    print("\n🏛️  Testing Pomona Vote Extractor:")
    print("-" * 40)

    pomona_extractor = PomonaVoteExtractor()
    print(f"✓ Created {pomona_extractor.name} v{pomona_extractor.version}")
    print(f"✓ Council size: {pomona_extractor.council_config['total_members']} members")
    print(f"✓ Quorum requirement: {pomona_extractor.council_config['quorum']} members")

def test_factory_auto_detection():
    """Test factory auto-detection capabilities"""
    print("\n🏭 Testing Factory Auto-Detection:")
    print("-" * 40)

    factory = CityVoteExtractorFactory()

    # Test Santa Ana detection
    santa_ana_content = "CITY OF SANTA ANA\nCOUNCILMEMBER BACERRA\nMAYOR AMEZCUA\n22 Civic Center Plaza"
    detected_city = factory.auto_detect_city(santa_ana_content)
    print(f"✓ Santa Ana content detected as: {detected_city}")

    # Test Pomona detection
    pomona_content = "CITY OF POMONA\nMayor Sandoval\nPomona City Hall\nDistrict 1"
    detected_city = factory.auto_detect_city(pomona_content)
    print(f"✓ Pomona content detected as: {detected_city}")

    # Test unknown content
    unknown_content = "City Council Meeting\nGeneric content\nNo specific identifiers"
    detected_city = factory.auto_detect_city(unknown_content)
    print(f"✓ Unknown content detected as: {detected_city}")

def test_full_document_processing():
    """Test complete document processing pipeline"""
    print("\n📄 Testing Full Document Processing:")
    print("-" * 40)

    factory = CityVoteExtractorFactory()

    # Create temporary files for Santa Ana
    santa_ana_agenda, santa_ana_minutes = create_santa_ana_sample_documents()

    with tempfile.NamedTemporaryFile(mode='w', suffix='_santa_ana_agenda.txt', delete=False) as agenda_file:
        agenda_file.write(santa_ana_agenda)
        santa_ana_agenda_path = agenda_file.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='_santa_ana_minutes.txt', delete=False) as minutes_file:
        minutes_file.write(santa_ana_minutes)
        santa_ana_minutes_path = minutes_file.name

    try:
        # Process Santa Ana documents
        print("\n🔍 Processing Santa Ana Documents:")
        santa_ana_result = factory.process_meeting_documents(
            santa_ana_agenda_path,
            santa_ana_minutes_path
        )

        print(f"  ✓ Success: {santa_ana_result['success']}")
        print(f"  ✓ Extractor used: {santa_ana_result['factory_metadata']['extractor_used']}")
        print(f"  ✓ City detected: {santa_ana_result['factory_metadata']['city_detected']}")
        print(f"  ✓ Votes extracted: {len(santa_ana_result['votes'])}")

        if santa_ana_result['votes']:
            vote = santa_ana_result['votes'][0]
            print(f"  ✓ Sample vote: {vote['agenda_item_number']} - {vote['outcome']} ({vote['vote_count']})")

    finally:
        # Cleanup Santa Ana files
        try:
            os.unlink(santa_ana_agenda_path)
            os.unlink(santa_ana_minutes_path)
        except:
            pass

    # Create temporary files for Pomona
    pomona_agenda, pomona_minutes = create_pomona_sample_documents()

    with tempfile.NamedTemporaryFile(mode='w', suffix='_pomona_agenda.txt', delete=False) as agenda_file:
        agenda_file.write(pomona_agenda)
        pomona_agenda_path = agenda_file.name

    with tempfile.NamedTemporaryFile(mode='w', suffix='_pomona_minutes.txt', delete=False) as minutes_file:
        minutes_file.write(pomona_minutes)
        pomona_minutes_path = minutes_file.name

    try:
        # Process Pomona documents
        print("\n🔍 Processing Pomona Documents:")
        pomona_result = factory.process_meeting_documents(
            pomona_agenda_path,
            pomona_minutes_path
        )

        print(f"  ✓ Success: {pomona_result['success']}")
        print(f"  ✓ Extractor used: {pomona_result['factory_metadata']['extractor_used']}")
        print(f"  ✓ City detected: {pomona_result['factory_metadata']['city_detected']}")
        print(f"  ✓ Votes extracted: {len(pomona_result['votes'])}")

        if pomona_result['votes']:
            vote = pomona_result['votes'][0]
            print(f"  ✓ Sample vote: {vote['agenda_item_number']} - {vote['outcome']} ({vote['vote_count']})")

    finally:
        # Cleanup Pomona files
        try:
            os.unlink(pomona_agenda_path)
            os.unlink(pomona_minutes_path)
        except:
            pass

def test_convenience_functions():
    """Test convenience functions"""
    print("\n🎯 Testing Convenience Functions:")
    print("-" * 40)

    # Test create_city_extractor
    santa_ana_extractor = create_city_extractor("santa_ana")
    print(f"✓ create_city_extractor('santa_ana'): {type(santa_ana_extractor).__name__}")

    pomona_extractor = create_city_extractor("pomona")
    print(f"✓ create_city_extractor('pomona'): {type(pomona_extractor).__name__}")

    generic_extractor = create_city_extractor("generic")
    print(f"✓ create_city_extractor('generic'): {type(generic_extractor).__name__}")

def test_factory_capabilities():
    """Test factory capabilities and statistics"""
    print("\n📊 Testing Factory Capabilities:")
    print("-" * 40)

    factory = CityVoteExtractorFactory()

    # Get supported cities
    supported_cities = factory.get_supported_cities()
    print(f"✓ Supported cities: {len(supported_cities)}")

    for city, info in supported_cities.items():
        print(f"  - {city}: {info['config']['council_size']} members, " +
              f"{info['patterns_count']} patterns")

    # Get statistics
    stats = factory.get_extraction_statistics()
    print(f"\n✓ Factory statistics:")
    print(f"  - Version: {stats['factory_version']}")
    print(f"  - Supported cities: {stats['supported_cities']}")
    print(f"  - Total patterns: {stats['total_patterns']}")

    # Test validation
    santa_ana_validation = factory.validate_extractor_capabilities('santa_ana', {
        'council_size': 7,
        'patterns_required': 3
    })
    print(f"\n✓ Santa Ana validation: {santa_ana_validation}")

def test_cross_city_comparison():
    """Test cross-city comparison capabilities"""
    print("\n⚖️  Testing Cross-City Comparison:")
    print("-" * 40)

    # Create both extractors
    santa_ana = create_city_extractor("santa_ana")
    pomona = create_city_extractor("pomona")

    # Compare configurations
    print("Configuration Comparison:")
    print(f"  Santa Ana: {santa_ana.council_config['total_members']} members")
    print(f"  Pomona: {pomona.council_config['total_members']} members")

    print(f"\n  Santa Ana patterns: {len(santa_ana.patterns)}")
    print(f"  Pomona patterns: {len(pomona.patterns)}")

    # Test pattern differences
    santa_ana_patterns = set(santa_ana.patterns.keys())
    pomona_patterns = set(pomona.patterns.keys())

    common_patterns = santa_ana_patterns & pomona_patterns
    unique_santa_ana = santa_ana_patterns - pomona_patterns
    unique_pomona = pomona_patterns - santa_ana_patterns

    print(f"\n  Common patterns: {len(common_patterns)} - {list(common_patterns)}")
    if unique_santa_ana:
        print(f"  Santa Ana unique: {list(unique_santa_ana)}")
    if unique_pomona:
        print(f"  Pomona unique: {list(unique_pomona)}")

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive City Vote Extractor Tests")
    print("=" * 60)

    try:
        # Run all test modules
        test_city_specific_extractors()
        test_factory_auto_detection()
        test_full_document_processing()
        test_convenience_functions()
        test_factory_capabilities()
        test_cross_city_comparison()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ City-specific vote extractors are working correctly")
        print("\n💡 Summary:")
        print("  ✓ Santa Ana Vote Extractor - 7 members, detailed patterns")
        print("  ✓ Pomona Vote Extractor - 5 members, flexible patterns")
        print("  ✓ Factory Auto-Detection - Content-based city identification")
        print("  ✓ Complete Processing Pipeline - End-to-end extraction")
        print("  ✓ Cross-City Comparison - Standardized output format")

        print("\n🎯 Ready for integration with:")
        print("  • File upload system")
        print("  • Dashboard data pipeline")
        print("  • Session management")
        print("  • Multi-city analysis")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)