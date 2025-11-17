"""
Santa Ana City Council Vote Extractor

Specialized agent for extracting voting data from Santa Ana City Council
meeting documents. Based on comprehensive analysis of Santa Ana meeting
patterns and formats documented in Santa_Ana_Voteextractor_info.md.

Key Santa Ana Specific Features:
- 7 council members (Mayor + 6 Councilmembers)
- Mayor Pro Tem position with rotation during meetings
- Teleconference participation under Government Code Section 54953(b)
- Closed Session (4:30 PM) + Regular Open Meeting (5:30 PM)
- Special Housing Authority and Successor Agency meetings
- Detailed recusal documentation with reasons
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
class SantaAnaCouncilMember:
    """Santa Ana specific council member representation"""
    name: str
    title: str  # "Mayor", "Councilmember", "Mayor Pro Tem"
    ward: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    term_start: Optional[datetime] = None
    term_end: Optional[datetime] = None

class SantaAnaVoteExtractor(VoteExtractionAgent):
    """
    Specialized vote extractor for Santa Ana City Council meetings.

    Handles Santa Ana specific patterns, member configurations, and
    meeting formats including special sessions and joint meetings.
    """

    def __init__(self):
        super().__init__()
        self.name = "SantaAnaVoteExtractor"
        self.version = "1.0.0"
        self.city_name = "Santa Ana"

        # Santa Ana specific council configuration
        self.council_config = self._initialize_council_config()

        # Override patterns with Santa Ana specific formats
        self.patterns = self._compile_santa_ana_patterns()

        # Santa Ana specific member name corrections
        self.member_name_corrections.update({
            "AMFZCUA": "AMEZCUA",
            "BACFRRA": "BACERRA",
            "HFRNANDEZ": "HERNANDEZ",
            "PFNALOZA": "PENALOZA",
            "VAZQUFZ": "VAZQUEZ"
        })

    def _initialize_council_config(self) -> Dict[str, Any]:
        """Initialize Santa Ana council configuration"""
        return {
            'city_name': 'Santa Ana',
            'state': 'CA',
            'total_members': 7,
            'meeting_location': 'City Council Chamber, 22 Civic Center Plaza Santa Ana, CA 92701',
            'closed_session_time': '4:30 P.M.',
            'regular_meeting_time': '5:30 P.M.',
            'current_council': [
                SantaAnaCouncilMember("Valerie Amezcua", "Mayor"),
                SantaAnaCouncilMember("Jessie Lopez", "Mayor Pro Tem"),
                SantaAnaCouncilMember("Phil Bacerra", "Councilmember", "Ward 1"),
                SantaAnaCouncilMember("Johnathan Ryan Hernandez", "Councilmember", "Ward 2"),
                SantaAnaCouncilMember("David Penaloza", "Councilmember", "Ward 3"),
                SantaAnaCouncilMember("Thai Viet Phan", "Councilmember", "Ward 4"),
                SantaAnaCouncilMember("Benjamin Vazquez", "Councilmember", "Ward 5")
            ],
            'meeting_types': [
                'Regular City Council',
                'Special Housing Authority',
                'Special Successor Agency',
                'Joint Session'
            ]
        }

    def _compile_santa_ana_patterns(self) -> Dict[str, re.Pattern]:
        """Compile Santa Ana specific regex patterns"""
        return {
            # Santa Ana motion pattern with full titles
            'motion': re.compile(
                r"MOTION:\s+(?P<mover>(?:MAYOR(?:\s+PRO\s+TEM)?|COUNCILMEMBER)\s+[A-Z]+)\s+"
                r"moved\s+to\s+(?P<action>.*?),\s+seconded\s+by\s+"
                r"(?P<seconder>(?:MAYOR(?:\s+PRO\s+TEM)?|COUNCILMEMBER)\s+[A-Z]+)",
                re.IGNORECASE | re.DOTALL
            ),

            # Santa Ana vote result pattern
            'vote_result': re.compile(
                r"The\s+motion\s+(?P<outcome>carried|failed),?\s*(?P<vote_count>\d+-\d+),?\s*"
                r"by\s+the\s+following\s+roll\s+call\s+vote:",
                re.IGNORECASE
            ),

            # Santa Ana vote details with multiline support
            'vote_details': re.compile(
                r"AYES:\s+(?P<ayes>.*?)(?=\s*(?:NOES:|ABSTAIN:|ABSENT:|RECUSED:|\n\n|\Z))"
                r"(?:\s*NOES:\s+(?P<noes>.*?)(?=\s*(?:ABSTAIN:|ABSENT:|RECUSED:|\n\n|\Z)))?"
                r"(?:\s*ABSTAIN:\s+(?P<abstain>.*?)(?=\s*(?:ABSENT:|RECUSED:|\n\n|\Z)))?"
                r"(?:\s*ABSENT:\s+(?P<absent>.*?)(?=\s*(?:RECUSED:|\n\n|\Z)))?"
                r"(?:\s*RECUSED:\s+(?P<recused>.*?)(?=\s*(?:\n\n|\Z)))?",
                re.IGNORECASE | re.DOTALL
            ),

            # Santa Ana recusal pattern with detailed reasons
            'recusal': re.compile(
                r"(?P<member>(?:Councilmember|Mayor(?:\s+Pro\s+Tem)?)\s+[A-Z]+)\s+"
                r"recused\s+(?:herself|himself|themselves)\s+.*?"
                r"(?P<reason>as\s+the\s+listed\s+entity\s+is\s+a\s+client\s+of\s+.*?|"
                r"due\s+to\s+.*?|because\s+.*?)(?:\.|$)",
                re.IGNORECASE | re.DOTALL
            ),

            # Santa Ana attendance pattern
            'attendance': re.compile(
                r"ATTENDANCE[:\s]+(?P<attendance>.*?)(?=\n\n|\nROLL\s+CALL|\Z)",
                re.IGNORECASE | re.DOTALL
            ),

            # Santa Ana agenda item pattern
            'agenda_item': re.compile(
                r"(?:ITEM\s+)?(?P<number>\d+\.?\d*)\s*[-.]?\s*(?P<title>.*?)(?=\n\n|\nITEM|\nMOTION|\Z)",
                re.IGNORECASE | re.DOTALL
            ),

            # Santa Ana resolution pattern
            'resolution': re.compile(
                r"Resolution\s+No\.\s+(?P<resolution_number>\d{4}-\d+)\s*[-–]?\s*(?P<title>.*?)(?=\n|\.|$)",
                re.IGNORECASE
            ),

            # Santa Ana ordinance pattern
            'ordinance': re.compile(
                r"Ordinance\s+No\.\s+(?P<ordinance_number>\d{4}-\d+)\s*[-–]?\s*(?P<title>.*?)(?=\n|\.|$)",
                re.IGNORECASE
            ),

            # Santa Ana meeting time pattern
            'meeting_time': re.compile(
                r"(?P<session_type>CLOSED\s+SESSION|REGULAR\s+MEETING)\s*[-–]?\s*(?P<time>\d{1,2}:\d{2}\s*P\.M\.)",
                re.IGNORECASE
            ),

            # Santa Ana teleconference pattern
            'teleconference': re.compile(
                r"teleconference\s+participation.*?Government\s+Code\s+Section\s+54953\(b\)",
                re.IGNORECASE | re.DOTALL
            )
        }

    def process_santa_ana_meeting(self, agenda_path: str, minutes_path: str) -> Dict[str, Any]:
        """
        Process Santa Ana specific meeting documents with enhanced features.

        Args:
            agenda_path: Path to Santa Ana agenda document
            minutes_path: Path to Santa Ana minutes document

        Returns:
            Enhanced extraction results with Santa Ana specific metadata
        """
        logger.info(f"Processing Santa Ana meeting: {agenda_path}, {minutes_path}")

        try:
            # Reset state for new meeting
            self.reset_meeting_state()

            # Load documents
            agenda_content = self._load_document(agenda_path)
            minutes_content = self._load_document(minutes_path)

            # Validate Santa Ana document structure
            validation_result = self._validate_santa_ana_documents(agenda_content, minutes_content)
            if not validation_result['valid']:
                return self._create_error_response(f"Document validation failed: {validation_result['issues']}")

            # Extract Santa Ana specific metadata
            meeting_metadata = self._extract_santa_ana_metadata(agenda_content, minutes_content)

            # Process attendance with Santa Ana council configuration
            self._process_santa_ana_attendance(minutes_content)

            # Extract votes with Santa Ana specific patterns
            vote_records = self._extract_santa_ana_votes(minutes_content, agenda_content)

            # Validate against Santa Ana council rules
            validation_results = self._validate_santa_ana_extraction(vote_records, meeting_metadata)

            # Format output with Santa Ana enhancements
            output = self._format_santa_ana_output(vote_records, meeting_metadata, validation_results)

            logger.info(f"Successfully processed Santa Ana meeting: {len(vote_records)} votes extracted")
            return output

        except Exception as e:
            logger.error(f"Error processing Santa Ana meeting: {str(e)}")
            return self._create_error_response(str(e))

    def _validate_santa_ana_documents(self, agenda_content: str, minutes_content: str) -> Dict[str, Any]:
        """Validate documents against Santa Ana specific requirements"""
        issues = []

        # Check for Santa Ana city identifier
        if "CITY OF SANTA ANA" not in agenda_content.upper():
            issues.append("Agenda missing Santa Ana city identifier")

        if "SANTA ANA" not in minutes_content.upper():
            issues.append("Minutes missing Santa Ana city identifier")

        # Check for expected meeting location (more flexible for real data)
        location_indicators = ["22 Civic Center Plaza", "Council Chamber", "Santa Ana", "City Hall"]
        if not any(indicator in agenda_content for indicator in location_indicators):
            issues.append("Missing expected meeting location indicators")

        # Check for expected council member count (disabled for real data testing)
        # Look for unique council member names rather than all occurrences
        council_member_pattern = re.findall(r"(?:COUNCILMEMBER|MAYOR(?:\s+PRO\s+TEM)?)\s+([A-Z]+)", minutes_content, re.IGNORECASE)
        unique_members = set(name.upper() for name in council_member_pattern)
        # Temporarily disabled strict validation for real data
        # if len(unique_members) > 0 and (len(unique_members) < 5 or len(unique_members) > 15):
        #     issues.append(f"Unexpected unique council member count: {len(unique_members)} (expected 5-15)")

        # Check for mayor presence
        if not re.search(r"MAYOR\s+[A-Z]+", minutes_content, re.IGNORECASE):
            issues.append("Mayor not found in minutes")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'unique_member_count': len(unique_members)
        }

    def _extract_santa_ana_metadata(self, agenda_content: str, minutes_content: str) -> Dict[str, Any]:
        """Extract Santa Ana specific meeting metadata"""
        metadata = {}

        # Extract meeting date with multiple format support
        metadata['date'] = self._extract_meeting_date(agenda_content) or self._extract_meeting_date(minutes_content)

        # Determine meeting type
        metadata['meeting_type'] = self._determine_santa_ana_meeting_type(agenda_content)

        # Extract session times
        time_matches = list(self.patterns['meeting_time'].finditer(agenda_content))
        metadata['session_times'] = {}
        for match in time_matches:
            session_type = match.group('session_type').lower().replace(' ', '_')
            metadata['session_times'][session_type] = match.group('time')

        # Check for teleconference
        metadata['has_teleconference'] = bool(self.patterns['teleconference'].search(agenda_content))

        # Extract agenda items count
        agenda_items = list(self.patterns['agenda_item'].finditer(agenda_content))
        metadata['agenda_items_count'] = len(agenda_items)

        # Extract resolutions and ordinances
        metadata['resolutions'] = self._extract_resolutions(agenda_content)
        metadata['ordinances'] = self._extract_ordinances(agenda_content)

        # Council composition
        metadata['council_composition'] = self._analyze_council_composition(minutes_content)

        return metadata

    def _determine_santa_ana_meeting_type(self, content: str) -> str:
        """Determine Santa Ana specific meeting type"""
        content_lower = content.lower()

        if 'housing authority' in content_lower:
            return 'Special Housing Authority Meeting'
        elif 'successor agency' in content_lower:
            return 'Special Successor Agency Meeting'
        elif 'joint' in content_lower:
            return 'Joint Session'
        elif 'special' in content_lower:
            return 'Special City Council Meeting'
        else:
            return 'Regular City Council Meeting'

    def _extract_resolutions(self, content: str) -> List[Dict[str, str]]:
        """Extract Santa Ana resolution information"""
        resolutions = []
        for match in self.patterns['resolution'].finditer(content):
            resolutions.append({
                'number': match.group('resolution_number'),
                'title': match.group('title').strip()
            })
        return resolutions

    def _extract_ordinances(self, content: str) -> List[Dict[str, str]]:
        """Extract Santa Ana ordinance information"""
        ordinances = []
        for match in self.patterns['ordinance'].finditer(content):
            ordinances.append({
                'number': match.group('ordinance_number'),
                'title': match.group('title').strip()
            })
        return ordinances

    def _process_santa_ana_attendance(self, minutes_content: str):
        """Process attendance with Santa Ana council configuration"""
        # Extract attendance section
        attendance_match = self.patterns['attendance'].search(minutes_content)
        if attendance_match:
            attendance_text = attendance_match.group('attendance')

            # Initialize all expected council members
            for member in self.council_config['current_council']:
                self.member_states[member.name.split()[-1].upper()] = MemberState(
                    name=member.name.split()[-1].title(),
                    title=member.title,
                    present=False
                )

            # Mark present members
            present_pattern = re.compile(
                r'(?:Mayor(?:\s+Pro\s+Tem)?|Councilmember)\s+([A-Z]+)',
                re.IGNORECASE
            )

            for match in present_pattern.finditer(attendance_text):
                member_name = match.group(1).title()
                if member_name.upper() in self.member_states:
                    self.member_states[member_name.upper()].present = True

        # Process recusals with detailed reason tracking
        for recusal_match in self.patterns['recusal'].finditer(minutes_content):
            member = self._clean_member_name(recusal_match.group('member'))
            reason = recusal_match.group('reason').strip()

            member_key = member.upper()
            if member_key in self.member_states:
                self.member_states[member_key].recusal_reasons[reason] = reason
                logger.info(f"Santa Ana recusal recorded: {member} - {reason}")

    def _extract_santa_ana_votes(self, minutes_content: str, agenda_content: str) -> List[VoteRecord]:
        """Extract votes with Santa Ana specific processing"""
        vote_records = []

        # Find all motion blocks with Santa Ana patterns
        motion_blocks = self._identify_santa_ana_motion_blocks(minutes_content)

        for i, block in enumerate(motion_blocks):
            try:
                vote_record = self._process_santa_ana_vote_block(block, agenda_content, i)
                if vote_record:
                    vote_records.append(vote_record)
                    logger.debug(f"Santa Ana vote extracted for item {vote_record.agenda_item_number}")

            except Exception as e:
                logger.warning(f"Failed to process Santa Ana vote block {i}: {str(e)}")
                continue

        return vote_records

    def _identify_santa_ana_motion_blocks(self, content: str) -> List[str]:
        """Identify Santa Ana specific motion blocks"""
        blocks = []

        # Split by MOTION: markers but preserve Santa Ana context
        motion_splits = re.split(r'(?=MOTION:)', content)

        for split in motion_splits:
            if 'MOTION:' in split:
                # Check for Santa Ana specific vote indicators
                if any(indicator in split.upper() for indicator in [
                    'AYES:', 'CARRIED', 'FAILED', 'ROLL CALL VOTE'
                ]):
                    blocks.append(split.strip())

        return blocks

    def _process_santa_ana_vote_block(self, block: str, agenda_content: str, block_index: int) -> Optional[VoteRecord]:
        """Process a Santa Ana specific vote block"""

        # Extract motion with Santa Ana pattern
        motion_match = self.patterns['motion'].search(block)
        if not motion_match:
            return None

        # Extract vote result with Santa Ana format
        result_match = self.patterns['vote_result'].search(block)
        if not result_match:
            return None

        # Extract vote details with Santa Ana formatting
        details_match = self.patterns['vote_details'].search(block)
        if not details_match:
            return None

        # Build Santa Ana motion context
        motion_context = MotionContext(
            id=f"SA{block_index}",
            type="original",
            text=motion_match.group('action').strip(),
            mover=self._clean_member_name(motion_match.group('mover')),
            seconder=self._clean_member_name(motion_match.group('seconder')),
            agenda_item=f"Item {block_index}",
            timestamp=datetime.now()
        )

        # Parse member votes with Santa Ana council
        member_votes = self._parse_santa_ana_member_votes(details_match)

        # Calculate tally
        tally = self._calculate_tally(member_votes)

        # Enhanced agenda correlation for Santa Ana
        agenda_item_number, agenda_item_title = self._correlate_santa_ana_agenda_item(block, agenda_content)

        # Handle recusals
        recusals = {}
        if details_match.group('recused'):
            recused_members = self._extract_member_names(details_match.group('recused'))
            for member in recused_members:
                recusals[member] = "Item-specific recusal"

        # Create Santa Ana vote record
        vote_record = VoteRecord(
            motion_id=motion_context.id,
            agenda_item_number=agenda_item_number,
            agenda_item_title=agenda_item_title,
            outcome="Pass" if result_match.group('outcome').lower() == 'carried' else "Fail",
            vote_count=result_match.group('vote_count'),
            member_votes=member_votes,
            tally=tally,
            recusals=recusals,
            motion_context=motion_context
        )

        # Santa Ana specific validation
        validation_notes = self._validate_santa_ana_vote_record(vote_record)
        vote_record.validation_notes = validation_notes

        return vote_record

    def _parse_santa_ana_member_votes(self, details_match: re.Match) -> Dict[str, str]:
        """Parse member votes with Santa Ana council configuration"""
        member_votes = {}

        # Parse each vote category
        for vote_type, group_name in [
            ('Aye', 'ayes'), ('Nay', 'noes'),
            ('Abstain', 'abstain'), ('Absent', 'absent')
        ]:
            if details_match.group(group_name):
                vote_text = details_match.group(group_name)
                members = self._extract_santa_ana_member_names(vote_text)
                for member in members:
                    member_votes[member] = vote_type

        return member_votes

    def _extract_santa_ana_member_names(self, text: str) -> List[str]:
        """Extract Santa Ana council member names with multiline support"""
        if not text or text.strip().lower() in ['none', 'n/a', '']:
            return []

        # Clean up text: remove extra whitespace and normalize line breaks
        clean_text = re.sub(r'\s+', ' ', text.strip())

        # Remove hyphens that may appear in member names
        clean_text = clean_text.replace(' - ', ' ')

        # Santa Ana specific member pattern - handles full titles with names
        member_pattern = re.compile(
            r'(?:MAYOR(?:\s+PRO\s+TEM)?|COUNCILMEMBER)\s+([A-Z]+(?:\s+[A-Z]+)*)',
            re.IGNORECASE
        )

        members = []
        seen_names = set()  # Avoid duplicates

        for match in member_pattern.finditer(clean_text):
            full_match = match.group(0)
            name_part = match.group(1).strip()

            # Extract just the last name for consistency
            if ' ' in name_part:
                # If multiple words, take the last one as surname
                surname = name_part.split()[-1]
            else:
                surname = name_part

            # Clean and normalize the name
            cleaned_name = self._clean_member_name(f"COUNCILMEMBER {surname}")

            if cleaned_name and cleaned_name not in seen_names:
                members.append(cleaned_name)
                seen_names.add(cleaned_name)

        return members

    def _correlate_santa_ana_agenda_item(self, vote_block: str, agenda_content: str) -> Tuple[str, str]:
        """Enhanced agenda correlation for Santa Ana items"""

        # Look for resolution numbers first
        resolution_match = self.patterns['resolution'].search(vote_block)
        if resolution_match:
            res_number = resolution_match.group('resolution_number')
            return f"Resolution {res_number}", resolution_match.group('title').strip()

        # Look for ordinance numbers
        ordinance_match = self.patterns['ordinance'].search(vote_block)
        if ordinance_match:
            ord_number = ordinance_match.group('ordinance_number')
            return f"Ordinance {ord_number}", ordinance_match.group('title').strip()

        # Standard agenda item correlation
        agenda_items = list(self.patterns['agenda_item'].finditer(agenda_content))
        for item in agenda_items:
            if item.group('number') in vote_block:
                return item.group('number'), item.group('title').strip()

        # Fallback
        return "Unknown", "Santa Ana Council Item"

    def _validate_santa_ana_vote_record(self, vote_record: VoteRecord) -> List[str]:
        """Santa Ana specific vote validation"""
        notes = []

        # Standard validation
        notes.extend(self._validate_vote_record(vote_record))

        # Santa Ana specific validations
        total_votes = sum(vote_record.tally.values())
        expected_total = self.council_config['total_members']

        # Check for expected council size
        if total_votes > expected_total:
            notes.append(f"More votes than council members: {total_votes} > {expected_total}")

        # Check for mayor participation
        mayor_voted = any('AMEZCUA' in member.upper() for member in vote_record.member_votes.keys())
        if not mayor_voted and total_votes > 0:
            notes.append("Mayor vote not recorded")

        # Check for quorum (4 members for Santa Ana)
        participating_votes = vote_record.tally['ayes'] + vote_record.tally['noes']
        if participating_votes < 4:
            notes.append(f"Below quorum: {participating_votes} participating votes")

        return notes

    def _validate_santa_ana_extraction(self, vote_records: List[VoteRecord], metadata: Dict) -> Dict[str, Any]:
        """Santa Ana specific extraction validation"""
        validation = {
            'total_votes': len(vote_records),
            'valid_votes': 0,
            'validation_errors': [],
            'quality_score': 0.0,
            'santa_ana_specific': {
                'meeting_type': metadata.get('meeting_type'),
                'expected_council_size': self.council_config['total_members'],
                'has_teleconference': metadata.get('has_teleconference', False),
                'resolutions_count': len(metadata.get('resolutions', [])),
                'ordinances_count': len(metadata.get('ordinances', []))
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

    def _format_santa_ana_output(self, vote_records: List[VoteRecord], metadata: Dict, validation: Dict) -> Dict[str, Any]:
        """Format output with Santa Ana specific enhancements"""
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
                'recusals': vote.recusals,
                'validation_notes': vote.validation_notes,
                'city_specific': {
                    'city': 'Santa Ana',
                    'council_size': self.council_config['total_members']
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
                    'meeting_location': self.council_config['meeting_location'],
                    'current_council': [
                        {'name': member.name, 'title': member.title, 'ward': member.ward}
                        for member in self.council_config['current_council']
                    ]
                }
            },
            'validation_results': validation,
            'votes': formatted_votes,
            'success': validation['quality_score'] > 0.5,
            'message': f"Santa Ana extraction: {len(formatted_votes)} votes with {validation['quality_score']:.1%} quality"
        }

    def _analyze_council_composition(self, minutes_content: str) -> Dict[str, Any]:
        """Analyze council composition from minutes"""
        composition = {
            'members_present': [],
            'members_absent': [],
            'role_changes': [],
            'total_expected': self.council_config['total_members']
        }

        # Find all member mentions
        member_pattern = re.compile(
            r'(?:Mayor(?:\s+Pro\s+Tem)?|Councilmember)\s+([A-Z]+)',
            re.IGNORECASE
        )

        found_members = set()
        for match in member_pattern.finditer(minutes_content):
            member_name = match.group(1).title()
            found_members.add(member_name)

        composition['members_present'] = list(found_members)

        # Identify missing members
        expected_members = {member.name.split()[-1] for member in self.council_config['current_council']}
        composition['members_absent'] = list(expected_members - found_members)

        # Look for role changes (Mayor Pro Tem changes)
        role_change_pattern = re.compile(
            r'(Councilmember\s+[A-Z]+)\s+became\s+.*?Mayor\s+Pro\s+Tem',
            re.IGNORECASE
        )

        for match in role_change_pattern.finditer(minutes_content):
            composition['role_changes'].append({
                'member': self._clean_member_name(match.group(1)),
                'change': 'Became Mayor Pro Tem'
            })

        return composition

# Test function for Santa Ana extractor
def test_santa_ana_extractor():
    """Test Santa Ana specific extractor functionality"""
    extractor = SantaAnaVoteExtractor()

    # Test Santa Ana specific patterns
    sample_text = "MOTION: COUNCILMEMBER BACERRA moved to approve Resolution No. 2024-01, seconded by MAYOR AMEZCUA."
    motion_match = extractor.patterns['motion'].search(sample_text)
    assert motion_match is not None, "Santa Ana motion pattern should match"

    # Test council configuration
    assert extractor.council_config['total_members'] == 7, "Santa Ana should have 7 council members"
    assert len(extractor.council_config['current_council']) == 7, "Should have 7 configured members"

    # Test member name cleaning
    cleaned = extractor._clean_member_name("COUNCILMEMBER BACERRA")
    assert cleaned == "Bacerra", f"Expected 'Bacerra', got '{cleaned}'"

    print("✓ Santa Ana Vote Extractor tests passed!")

if __name__ == "__main__":
    test_santa_ana_extractor()
    print("Santa Ana Vote Extractor created successfully!")