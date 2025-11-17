"""
Pomona City Council Vote Extractor

Specialized agent for extracting voting data from Pomona City Council
meeting documents. Configured for Pomona's specific council structure,
meeting formats, and document patterns.

Key Pomona Specific Features:
- 5 council members (Mayor + 4 Councilmembers)
- District-based representation
- Different meeting format and timing patterns
- Specific motion and voting language
- Unique agenda item numbering system
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

# Import base classes from the general vote extraction agent
from .vote_extraction_agent import VoteExtractionAgent, VoteRecord, MotionContext, MemberState

logger = logging.getLogger(__name__)

@dataclass
class PomonaCouncilMember:
    """Pomona specific council member representation"""
    name: str
    title: str  # "Mayor", "Councilmember"
    district: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    term_start: Optional[datetime] = None
    term_end: Optional[datetime] = None

class PomonaVoteExtractor(VoteExtractionAgent):
    """
    Specialized vote extractor for Pomona City Council meetings.

    Handles Pomona specific patterns, 5-member council configuration,
    district-based representation, and unique meeting formats.
    """

    def __init__(self):
        super().__init__()
        self.name = "PomonaVoteExtractor"
        self.version = "1.0.0"
        self.city_name = "Pomona"

        # Pomona specific council configuration
        self.council_config = self._initialize_pomona_council_config()

        # Override patterns with Pomona specific formats
        self.patterns = self._compile_pomona_patterns()

        # Pomona specific member name corrections
        self.member_name_corrections.update({
            # Add Pomona specific OCR corrections as identified
        })

    def _initialize_pomona_council_config(self) -> Dict[str, Any]:
        """Initialize Pomona council configuration"""
        return {
            'city_name': 'Pomona',
            'state': 'CA',
            'total_members': 5,
            'meeting_location': 'Pomona City Hall Council Chambers',
            'regular_meeting_time': '7:00 P.M.',
            'current_council': [
                PomonaCouncilMember("Tim Sandoval", "Mayor"),
                PomonaCouncilMember("Council Member 1", "Councilmember", "District 1"),
                PomonaCouncilMember("Council Member 2", "Councilmember", "District 2"),
                PomonaCouncilMember("Council Member 3", "Councilmember", "District 3"),
                PomonaCouncilMember("Council Member 4", "Councilmember", "District 4")
            ],
            'meeting_types': [
                'Regular City Council',
                'Special Meeting',
                'Study Session',
                'Joint Meeting'
            ],
            'quorum': 3  # Majority of 5 members
        }

    def _compile_pomona_patterns(self) -> Dict[str, re.Pattern]:
        """Compile Pomona specific regex patterns"""
        return {
            # Pomona motion pattern (may be different from Santa Ana)
            'motion': re.compile(
                r"(?:MOTION|Motion):\s*(?P<mover>(?:Mayor|Councilmember|Council\s*Member)\s+[A-Za-z\s]+)\s+"
                r"(?:moved|made\s+a\s+motion)\s+to\s+(?P<action>.*?),?\s*"
                r"(?:seconded|second)\s+by\s+(?P<seconder>(?:Mayor|Councilmember|Council\s*Member)\s+[A-Za-z\s]+)",
                re.IGNORECASE | re.DOTALL
            ),

            # Pomona vote result pattern
            'vote_result': re.compile(
                r"(?:Motion|The\s+motion)\s+(?P<outcome>passed|failed|carried|denied),?\s*"
                r"(?P<vote_count>\d+-\d+)?",
                re.IGNORECASE
            ),

            # Pomona vote details pattern
            'vote_details': re.compile(
                r"(?:AYES?|Yes):\s*(?P<ayes>.*?)(?:\s*(?:NOES?|No):\s*(?P<noes>.*?))?"
                r"(?:\s*(?:ABSTAIN|Abstain):\s*(?P<abstain>.*?))?"
                r"(?:\s*(?:ABSENT|Absent):\s*(?P<absent>.*?))?",
                re.IGNORECASE | re.DOTALL
            ),

            # Pomona attendance pattern
            'attendance': re.compile(
                r"(?:PRESENT|Present|ATTENDANCE)[:.\s]*(?P<attendance>.*?)(?=\n\n|ABSENT|$)",
                re.IGNORECASE | re.DOTALL
            ),

            # Pomona agenda item pattern
            'agenda_item': re.compile(
                r"(?:ITEM|Item)\s*(?P<number>[A-Z]?\d+(?:\.\d+)?)\s*[-.:]\s*(?P<title>.*?)(?=\n(?:ITEM|Item)|\n\n|$)",
                re.IGNORECASE | re.DOTALL
            ),

            # Pomona meeting date pattern
            'meeting_date': re.compile(
                r"(?:Meeting\s+of\s+|Date:\s*)?(?P<date>(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})",
                re.IGNORECASE
            ),

            # Pomona roll call pattern
            'roll_call': re.compile(
                r"(?:ROLL\s+CALL|Roll\s+Call)[:.\s]*(?P<roll_call>.*?)(?=\n\n|MOTION|$)",
                re.IGNORECASE | re.DOTALL
            )
        }

    def process_pomona_meeting(self, agenda_path: str, minutes_path: str) -> Dict[str, Any]:
        """
        Process Pomona specific meeting documents.

        Args:
            agenda_path: Path to Pomona agenda document
            minutes_path: Path to Pomona minutes document

        Returns:
            Enhanced extraction results with Pomona specific metadata
        """
        logger.info(f"Processing Pomona meeting: {agenda_path}, {minutes_path}")

        try:
            # Reset state for new meeting
            self.reset_meeting_state()

            # Load documents
            agenda_content = self._load_document(agenda_path)
            minutes_content = self._load_document(minutes_path)

            # Validate Pomona document structure
            validation_result = self._validate_pomona_documents(agenda_content, minutes_content)
            if not validation_result['valid']:
                return self._create_error_response(f"Document validation failed: {validation_result['issues']}")

            # Extract Pomona specific metadata
            meeting_metadata = self._extract_pomona_metadata(agenda_content, minutes_content)

            # Process attendance with Pomona council configuration
            self._process_pomona_attendance(minutes_content)

            # Extract votes with Pomona specific patterns
            vote_records = self._extract_pomona_votes(minutes_content, agenda_content)

            # Validate against Pomona council rules
            validation_results = self._validate_pomona_extraction(vote_records, meeting_metadata)

            # Format output with Pomona enhancements
            output = self._format_pomona_output(vote_records, meeting_metadata, validation_results)

            logger.info(f"Successfully processed Pomona meeting: {len(vote_records)} votes extracted")
            return output

        except Exception as e:
            logger.error(f"Error processing Pomona meeting: {str(e)}")
            return self._create_error_response(str(e))

    def _validate_pomona_documents(self, agenda_content: str, minutes_content: str) -> Dict[str, Any]:
        """Validate documents against Pomona specific requirements"""
        issues = []

        # Check for Pomona city identifier
        if "POMONA" not in agenda_content.upper() and "POMONA" not in minutes_content.upper():
            issues.append("Missing Pomona city identifier")

        # Check for expected council member count (5 for Pomona)
        council_member_count = len(re.findall(r"(?:Councilmember|Council\s*Member)\s+[A-Za-z\s]+", minutes_content, re.IGNORECASE))
        if council_member_count > 0 and (council_member_count < 4 or council_member_count > 5):
            issues.append(f"Unexpected council member count: {council_member_count} (expected 4-5)")

        # Check for mayor presence
        if not re.search(r"Mayor\s+[A-Za-z\s]+", minutes_content, re.IGNORECASE):
            issues.append("Mayor not found in minutes")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'council_member_count': council_member_count
        }

    def _extract_pomona_metadata(self, agenda_content: str, minutes_content: str) -> Dict[str, Any]:
        """Extract Pomona specific meeting metadata"""
        metadata = {}

        # Extract meeting date
        date_match = self.patterns['meeting_date'].search(agenda_content) or self.patterns['meeting_date'].search(minutes_content)
        metadata['date'] = date_match.group('date') if date_match else None

        # Determine meeting type
        metadata['meeting_type'] = self._determine_pomona_meeting_type(agenda_content)

        # Extract agenda items
        agenda_items = list(self.patterns['agenda_item'].finditer(agenda_content))
        metadata['agenda_items_count'] = len(agenda_items)

        # Council composition
        metadata['council_composition'] = self._analyze_pomona_council_composition(minutes_content)

        # Meeting location and time
        metadata['meeting_location'] = self.council_config['meeting_location']
        metadata['meeting_time'] = self.council_config['regular_meeting_time']

        return metadata

    def _determine_pomona_meeting_type(self, content: str) -> str:
        """Determine Pomona specific meeting type"""
        content_lower = content.lower()

        if 'study session' in content_lower:
            return 'Study Session'
        elif 'special' in content_lower:
            return 'Special Meeting'
        elif 'joint' in content_lower:
            return 'Joint Meeting'
        else:
            return 'Regular City Council Meeting'

    def _process_pomona_attendance(self, minutes_content: str):
        """Process attendance with Pomona council configuration"""
        # Initialize all expected council members
        for member in self.council_config['current_council']:
            member_key = member.name.split()[-1].upper()
            self.member_states[member_key] = MemberState(
                name=member.name.split()[-1].title(),
                title=member.title,
                present=False
            )

        # Extract attendance section
        attendance_match = self.patterns['attendance'].search(minutes_content)
        if attendance_match:
            attendance_text = attendance_match.group('attendance')

            # Mark present members
            present_pattern = re.compile(
                r'(?:Mayor|Councilmember|Council\s*Member)\s+([A-Za-z\s]+)',
                re.IGNORECASE
            )

            for match in present_pattern.finditer(attendance_text):
                member_name = match.group(1).strip()
                # Use last name as key
                member_key = member_name.split()[-1].upper()
                if member_key in self.member_states:
                    self.member_states[member_key].present = True

        # Also check roll call section
        roll_call_match = self.patterns['roll_call'].search(minutes_content)
        if roll_call_match:
            roll_call_text = roll_call_match.group('roll_call')

            present_pattern = re.compile(
                r'(?:Mayor|Councilmember|Council\s*Member)\s+([A-Za-z\s]+)',
                re.IGNORECASE
            )

            for match in present_pattern.finditer(roll_call_text):
                member_name = match.group(1).strip()
                member_key = member_name.split()[-1].upper()
                if member_key in self.member_states:
                    self.member_states[member_key].present = True

    def _extract_pomona_votes(self, minutes_content: str, agenda_content: str) -> List[VoteRecord]:
        """Extract votes with Pomona specific processing"""
        vote_records = []

        # Find all motion blocks with Pomona patterns
        motion_blocks = self._identify_pomona_motion_blocks(minutes_content)

        for i, block in enumerate(motion_blocks):
            try:
                vote_record = self._process_pomona_vote_block(block, agenda_content, i)
                if vote_record:
                    vote_records.append(vote_record)
                    logger.debug(f"Pomona vote extracted for item {vote_record.agenda_item_number}")

            except Exception as e:
                logger.warning(f"Failed to process Pomona vote block {i}: {str(e)}")
                continue

        return vote_records

    def _identify_pomona_motion_blocks(self, content: str) -> List[str]:
        """Identify Pomona specific motion blocks"""
        blocks = []

        # Split by motion markers
        motion_splits = re.split(r'(?=(?:MOTION|Motion):)', content)

        for split in motion_splits:
            if re.search(r'(?:MOTION|Motion):', split):
                # Check for Pomona specific vote indicators
                if any(indicator in split.lower() for indicator in [
                    'ayes', 'yes', 'passed', 'failed', 'carried', 'denied'
                ]):
                    blocks.append(split.strip())

        return blocks

    def _process_pomona_vote_block(self, block: str, agenda_content: str, block_index: int) -> Optional[VoteRecord]:
        """Process a Pomona specific vote block"""

        # Extract motion with Pomona pattern
        motion_match = self.patterns['motion'].search(block)
        if not motion_match:
            return None

        # Extract vote result with Pomona format
        result_match = self.patterns['vote_result'].search(block)
        if not result_match:
            return None

        # Extract vote details (may be optional in some Pomona documents)
        details_match = self.patterns['vote_details'].search(block)

        # Build Pomona motion context
        motion_context = MotionContext(
            id=f"PO{block_index}",
            type="original",
            text=motion_match.group('action').strip(),
            mover=self._clean_pomona_member_name(motion_match.group('mover')),
            seconder=self._clean_pomona_member_name(motion_match.group('seconder')),
            agenda_item=f"Item {block_index}",
            timestamp=datetime.now()
        )

        # Parse member votes if details are available
        member_votes = {}
        tally = {'ayes': 0, 'noes': 0, 'abstain': 0, 'absent': 0}

        if details_match:
            member_votes = self._parse_pomona_member_votes(details_match)
            tally = self._calculate_tally(member_votes)
        else:
            # Try to infer from vote count if available
            vote_count = result_match.group('vote_count')
            if vote_count:
                vote_parts = vote_count.split('-')
                if len(vote_parts) == 2:
                    tally['ayes'] = int(vote_parts[0])
                    tally['noes'] = int(vote_parts[1])

        # Enhanced agenda correlation for Pomona
        agenda_item_number, agenda_item_title = self._correlate_pomona_agenda_item(block, agenda_content)

        # Create Pomona vote record
        vote_record = VoteRecord(
            motion_id=motion_context.id,
            agenda_item_number=agenda_item_number,
            agenda_item_title=agenda_item_title,
            outcome="Pass" if result_match.group('outcome').lower() in ['passed', 'carried'] else "Fail",
            vote_count=result_match.group('vote_count') or f"{tally['ayes']}-{tally['noes']}",
            member_votes=member_votes,
            tally=tally,
            motion_context=motion_context
        )

        # Pomona specific validation
        validation_notes = self._validate_pomona_vote_record(vote_record)
        vote_record.validation_notes = validation_notes

        return vote_record

    def _clean_pomona_member_name(self, name: str) -> str:
        """Clean Pomona member names"""
        if not name:
            return ""

        # Remove titles
        name = re.sub(r'(?:Mayor|Councilmember|Council\s*Member)\s*', '', name, flags=re.IGNORECASE)
        name = name.strip()

        # Return last name only for consistency
        return name.split()[-1].title() if name else ""

    def _parse_pomona_member_votes(self, details_match: re.Match) -> Dict[str, str]:
        """Parse member votes with Pomona council configuration"""
        member_votes = {}

        # Parse each vote category
        for vote_type, group_name in [
            ('Aye', 'ayes'), ('Nay', 'noes'),
            ('Abstain', 'abstain'), ('Absent', 'absent')
        ]:
            if details_match.group(group_name):
                vote_text = details_match.group(group_name)
                members = self._extract_pomona_member_names(vote_text)
                for member in members:
                    member_votes[member] = vote_type

        return member_votes

    def _extract_pomona_member_names(self, text: str) -> List[str]:
        """Extract Pomona council member names"""
        if not text or text.strip().lower() in ['none', 'n/a', '']:
            return []

        # Pomona member pattern (more flexible than Santa Ana)
        member_pattern = re.compile(
            r'(?:Mayor|Councilmember|Council\s*Member)?\s*([A-Za-z\s]+)',
            re.IGNORECASE
        )

        members = []
        for match in member_pattern.finditer(text):
            member_name = self._clean_pomona_member_name(match.group(0))
            if member_name and len(member_name) > 1:  # Avoid single letters
                members.append(member_name)

        return members

    def _correlate_pomona_agenda_item(self, vote_block: str, agenda_content: str) -> Tuple[str, str]:
        """Enhanced agenda correlation for Pomona items"""

        # Look for agenda item references in the vote block
        agenda_items = list(self.patterns['agenda_item'].finditer(agenda_content))
        for item in agenda_items:
            if item.group('number') in vote_block:
                return item.group('number'), item.group('title').strip()

        # Fallback
        return "Unknown", "Pomona Council Item"

    def _validate_pomona_vote_record(self, vote_record: VoteRecord) -> List[str]:
        """Pomona specific vote validation"""
        notes = []

        # Standard validation
        notes.extend(self._validate_vote_record(vote_record))

        # Pomona specific validations
        total_votes = sum(vote_record.tally.values())
        expected_total = self.council_config['total_members']

        # Check for expected council size
        if total_votes > expected_total:
            notes.append(f"More votes than council members: {total_votes} > {expected_total}")

        # Check for quorum (3 members for Pomona)
        participating_votes = vote_record.tally['ayes'] + vote_record.tally['noes']
        if participating_votes > 0 and participating_votes < self.council_config['quorum']:
            notes.append(f"Below quorum: {participating_votes} participating votes (need {self.council_config['quorum']})")

        return notes

    def _validate_pomona_extraction(self, vote_records: List[VoteRecord], metadata: Dict) -> Dict[str, Any]:
        """Pomona specific extraction validation"""
        validation = {
            'total_votes': len(vote_records),
            'valid_votes': 0,
            'validation_errors': [],
            'quality_score': 0.0,
            'pomona_specific': {
                'meeting_type': metadata.get('meeting_type'),
                'expected_council_size': self.council_config['total_members'],
                'quorum_requirement': self.council_config['quorum']
            }
        }

        valid_count = 0
        for vote in vote_records:
            if not vote.validation_notes:
                valid_count += 1
            else:
                validation['validation_errors'].extend(vote.validation_notes)

        validation['valid_votes'] = valid_count
        validation['quality_score'] = valid_count / len(vote_records) if vote_records else 0.0

        return validation

    def _format_pomona_output(self, vote_records: List[VoteRecord], metadata: Dict, validation: Dict) -> Dict[str, Any]:
        """Format output with Pomona specific enhancements"""
        formatted_votes = []

        for vote in vote_records:
            formatted_vote = {
                'agenda_item_number': vote.agenda_item_number,
                'agenda_item_title': vote.agenda_item_title,
                'outcome': vote.outcome,
                'tally': vote.tally,
                'member_votes': vote.member_votes,
                'vote_count': vote.vote_count,
                'motion_text': vote.motion_context.text if vote.motion_context else "",
                'mover': vote.motion_context.mover if vote.motion_context else "",
                'seconder': vote.motion_context.seconder if vote.motion_context else "",
                'validation_notes': vote.validation_notes,
                'city_specific': {
                    'city': 'Pomona',
                    'council_size': self.council_config['total_members'],
                    'quorum': self.council_config['quorum']
                }
            }
            formatted_votes.append(formatted_vote)

        return {
            'extraction_metadata': {
                'agent_name': self.name,
                'agent_version': self.version,
                'city': self.city_name,
                'extraction_timestamp': datetime.now().isoformat(),
                'meeting_metadata': metadata,
                'council_configuration': {
                    'total_members': self.council_config['total_members'],
                    'quorum': self.council_config['quorum'],
                    'meeting_location': self.council_config['meeting_location'],
                    'current_council': [
                        {'name': member.name, 'title': member.title, 'district': member.district}
                        for member in self.council_config['current_council']
                    ]
                }
            },
            'validation_results': validation,
            'votes': formatted_votes,
            'success': validation['quality_score'] > 0.3,  # Lower threshold for Pomona
            'message': f"Pomona extraction: {len(formatted_votes)} votes with {validation['quality_score']:.1%} quality"
        }

    def _analyze_pomona_council_composition(self, minutes_content: str) -> Dict[str, Any]:
        """Analyze Pomona council composition from minutes"""
        composition = {
            'members_present': [],
            'members_absent': [],
            'total_expected': self.council_config['total_members']
        }

        # Find all member mentions
        member_pattern = re.compile(
            r'(?:Mayor|Councilmember|Council\s*Member)\s+([A-Za-z\s]+)',
            re.IGNORECASE
        )

        found_members = set()
        for match in member_pattern.finditer(minutes_content):
            member_name = match.group(1).strip()
            if member_name and len(member_name) > 1:
                found_members.add(member_name.split()[-1].title())

        composition['members_present'] = list(found_members)

        # Identify missing members
        expected_members = {member.name.split()[-1] for member in self.council_config['current_council']}
        composition['members_absent'] = list(expected_members - found_members)

        return composition

# Test function for Pomona extractor
def test_pomona_extractor():
    """Test Pomona specific extractor functionality"""
    extractor = PomonaVoteExtractor()

    # Test Pomona specific patterns
    sample_text = "Motion: Mayor Sandoval moved to approve the budget, seconded by Councilmember Smith."
    motion_match = extractor.patterns['motion'].search(sample_text)
    assert motion_match is not None, "Pomona motion pattern should match"

    # Test council configuration
    assert extractor.council_config['total_members'] == 5, "Pomona should have 5 council members"
    assert len(extractor.council_config['current_council']) == 5, "Should have 5 configured members"

    # Test member name cleaning
    cleaned = extractor._clean_pomona_member_name("Councilmember Smith")
    assert cleaned == "Smith", f"Expected 'Smith', got '{cleaned}'"

    print("✓ Pomona Vote Extractor tests passed!")

if __name__ == "__main__":
    test_pomona_extractor()
    print("Pomona Vote Extractor created successfully!")