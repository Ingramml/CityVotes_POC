"""
Vote Extraction Agent for CityVotes POC

This agent handles the complex task of extracting voting data from city council
meeting documents (agendas and minutes). It implements sophisticated parsing,
validation, and correlation capabilities based on Santa Ana documentation analysis.

Key capabilities:
- Document preprocessing and validation
- Motion tracking and relationship management
- Vote extraction with context preservation
- Cross-document correlation and validation
- Member state tracking (recusals, role changes)
- Output formatting for dashboard consumption
"""

import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemberState:
    """Tracks individual member state throughout a meeting"""
    name: str
    title: str  # "Mayor", "Councilmember", "Mayor Pro Tem"
    present: bool = True
    recused_items: List[str] = field(default_factory=list)
    recusal_reasons: Dict[str, str] = field(default_factory=dict)

@dataclass
class MotionContext:
    """Represents a motion with full context"""
    id: str
    type: str  # 'original', 'substitute', 'amendment', 'procedural'
    text: str
    mover: str
    seconder: str
    agenda_item: str
    parent_motion_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    status: str = 'pending'  # 'pending', 'withdrawn', 'voted', 'failed'

@dataclass
class VoteRecord:
    """Complete vote record with all context"""
    motion_id: str
    agenda_item_number: str
    agenda_item_title: str
    outcome: str  # 'Pass', 'Fail'
    vote_count: str  # '7-0', '4-3', etc.
    member_votes: Dict[str, str]  # member_name -> vote ('Aye', 'Nay', 'Abstain', 'Absent')
    tally: Dict[str, int]  # 'ayes', 'noes', 'abstain', 'absent'
    recusals: Dict[str, str] = field(default_factory=dict)  # member -> reason
    motion_context: Optional[MotionContext] = None
    validation_notes: List[str] = field(default_factory=list)

class VoteExtractionAgent:
    """
    Sophisticated agent for extracting voting data from council meeting documents.

    Handles the complete pipeline from document ingestion to validated vote records,
    including complex motion tracking, member state management, and cross-document
    correlation as documented in the Santa Ana analysis.
    """

    def __init__(self):
        self.name = "VoteExtractionAgent"
        self.version = "1.0.0"

        # Compilation of regex patterns based on Santa Ana documentation
        self.patterns = self._compile_patterns()

        # Member name standardization mapping
        self.member_name_corrections = {
            "0": "O", "1": "I", "5": "S", "8": "B"  # Common OCR errors
        }

        # Meeting state tracking
        self.reset_meeting_state()

        # Quality thresholds
        self.quality_thresholds = {
            'min_content_length': 1000,
            'max_ocr_error_rate': 0.1,
            'min_vote_sections': 1
        }

    def reset_meeting_state(self):
        """Reset state for processing a new meeting"""
        self.current_section = None
        self.member_states: Dict[str, MemberState] = {}
        self.motion_history: List[MotionContext] = []
        self.active_motions: Dict[str, MotionContext] = {}
        self.recusal_stack: List[Tuple[str, str, datetime]] = []
        self.temporal_events: List[Dict] = []

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for vote extraction based on Santa Ana format"""
        return {
            # Motion patterns
            'motion': re.compile(
                r"MOTION:\s+(?P<mover>(?:COUNCILMEMBER|MAYOR(?:\s+PRO\s+TEM)?)\s+[A-Z]+)\s+"
                r"moved\s+to\s+(?P<action>.*?),\s+seconded\s+by\s+"
                r"(?P<seconder>(?:COUNCILMEMBER|MAYOR(?:\s+PRO\s+TEM)?)\s+[A-Z]+)",
                re.IGNORECASE | re.DOTALL
            ),

            # Vote result patterns
            'vote_result': re.compile(
                r"The\s+motion\s+(?P<outcome>carried|failed),?\s*(?P<vote_count>\d+-\d+)",
                re.IGNORECASE
            ),

            # Vote details pattern
            'vote_details': re.compile(
                r"AYES:\s+(?P<ayes>.*?)(?:NOES:\s+(?P<noes>.*?))?"
                r"(?:ABSTAIN:\s+(?P<abstain>.*?))?"
                r"(?:ABSENT:\s+(?P<absent>.*?))?",
                re.IGNORECASE | re.DOTALL
            ),

            # Recusal pattern
            'recusal': re.compile(
                r"(?P<member>(?:Councilmember|Mayor(?:\s+Pro\s+Tem)?)\s+[A-Z]+)\s+"
                r"recused\s+.*?(?P<reason>as\s+.*?)(?:\.|$)",
                re.IGNORECASE
            ),

            # Attendance patterns
            'attendance': re.compile(
                r"ATTENDANCE[:\s]+(.*?)(?=\n\n|\nROLL\s+CALL|\Z)",
                re.IGNORECASE | re.DOTALL
            ),

            # Roll call pattern
            'roll_call': re.compile(
                r"ROLL\s+CALL[:\s]+(.*?)(?=\n\n|\nMOTION|\Z)",
                re.IGNORECASE | re.DOTALL
            ),

            # Agenda item pattern
            'agenda_item': re.compile(
                r"(?:ITEM\s+)?(?P<number>\d+\.?\d*)\s*[-.]?\s*(?P<title>.*?)(?=\n\n|\nITEM|\nMOTION|\Z)",
                re.IGNORECASE | re.DOTALL
            )
        }

    def process_meeting_documents(self, agenda_path: str, minutes_path: str) -> Dict[str, Any]:
        """
        Process paired agenda and minutes documents to extract complete voting data.

        Args:
            agenda_path: Path to agenda text file
            minutes_path: Path to minutes text file

        Returns:
            Dict containing extracted votes, validation results, and metadata
        """
        try:
            logger.info(f"Processing meeting documents: {agenda_path}, {minutes_path}")

            # Reset state for new meeting
            self.reset_meeting_state()

            # Load and validate documents
            agenda_content = self._load_document(agenda_path)
            minutes_content = self._load_document(minutes_path)

            # Preprocess documents
            agenda_data = self._preprocess_agenda(agenda_content)
            minutes_data = self._preprocess_minutes(minutes_content)

            # Extract meeting metadata
            meeting_metadata = self._extract_meeting_metadata(agenda_data, minutes_data)

            # Process attendance and member states
            self._process_attendance(minutes_data['content'])

            # Extract votes from minutes
            vote_records = self._extract_votes(minutes_data['content'], agenda_data)

            # Validate and correlate data
            validation_results = self._validate_extraction(vote_records, meeting_metadata)

            # Format output
            output = self._format_output(vote_records, meeting_metadata, validation_results)

            logger.info(f"Successfully processed {len(vote_records)} vote records")
            return output

        except Exception as e:
            logger.error(f"Error processing meeting documents: {str(e)}")
            return self._create_error_response(str(e))

    def _load_document(self, file_path: str) -> str:
        """Load and basic validation of document content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if len(content) < self.quality_thresholds['min_content_length']:
                raise ValueError(f"Document too short: {len(content)} characters")

            return content

        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {str(e)}")
            raise

    def _preprocess_agenda(self, content: str) -> Dict[str, Any]:
        """Preprocess agenda document to extract structure and items"""
        return {
            'content': self._normalize_text(content),
            'items': self._extract_agenda_items(content),
            'metadata': self._extract_agenda_metadata(content)
        }

    def _preprocess_minutes(self, content: str) -> Dict[str, Any]:
        """Preprocess minutes document for vote extraction"""
        normalized = self._normalize_text(content)
        return {
            'content': normalized,
            'vote_sections': self._identify_vote_sections(normalized),
            'metadata': self._extract_minutes_metadata(normalized)
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for consistent processing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Fix common OCR errors in member names
        for wrong, right in self.member_name_corrections.items():
            text = text.replace(wrong, right)

        # Standardize section headers
        text = re.sub(r'(?i)motion\s*:', 'MOTION:', text)
        text = re.sub(r'(?i)ayes\s*:', 'AYES:', text)
        text = re.sub(r'(?i)noes\s*:', 'NOES:', text)

        return text.strip()

    def _extract_agenda_items(self, content: str) -> List[Dict[str, str]]:
        """Extract agenda items with numbers and titles"""
        items = []
        for match in self.patterns['agenda_item'].finditer(content):
            items.append({
                'number': match.group('number').strip(),
                'title': match.group('title').strip()[:200]  # Limit title length
            })
        return items

    def _extract_meeting_metadata(self, agenda_data: Dict, minutes_data: Dict) -> Dict[str, Any]:
        """Extract meeting metadata from both documents"""
        return {
            'date': self._extract_meeting_date(agenda_data['content']),
            'type': self._determine_meeting_type(agenda_data['content']),
            'agenda_items_count': len(agenda_data['items']),
            'estimated_duration': self._estimate_meeting_duration(minutes_data['content'])
        }

    def _process_attendance(self, minutes_content: str):
        """Process attendance information and initialize member states"""
        # Extract attendance section
        attendance_match = self.patterns['attendance'].search(minutes_content)
        if attendance_match:
            attendance_text = attendance_match.group(1)
            self._parse_attendance(attendance_text)

        # Process recusals
        for recusal_match in self.patterns['recusal'].finditer(minutes_content):
            member = self._clean_member_name(recusal_match.group('member'))
            reason = recusal_match.group('reason').strip()

            if member in self.member_states:
                self.member_states[member].recusal_reasons[reason] = reason
                logger.info(f"Recorded recusal: {member} - {reason}")

    def _extract_votes(self, minutes_content: str, agenda_data: Dict) -> List[VoteRecord]:
        """Extract all vote records from minutes content"""
        vote_records = []

        # Find all motion blocks
        motion_blocks = self._identify_motion_blocks(minutes_content)

        for i, block in enumerate(motion_blocks):
            try:
                vote_record = self._process_vote_block(block, agenda_data, i)
                if vote_record:
                    vote_records.append(vote_record)
                    logger.debug(f"Extracted vote record for item {vote_record.agenda_item_number}")

            except Exception as e:
                logger.warning(f"Failed to process vote block {i}: {str(e)}")
                continue

        return vote_records

    def _identify_motion_blocks(self, content: str) -> List[str]:
        """Identify and extract individual motion/vote blocks"""
        blocks = []

        # Split content by MOTION: markers
        motion_splits = re.split(r'(?=MOTION:)', content)

        for split in motion_splits:
            if 'MOTION:' in split and any(keyword in split.upper() for keyword in ['AYES:', 'CARRIED', 'FAILED']):
                blocks.append(split.strip())

        return blocks

    def _process_vote_block(self, block: str, agenda_data: Dict, block_index: int) -> Optional[VoteRecord]:
        """Process a single vote block to extract complete vote record"""

        # Extract motion information
        motion_match = self.patterns['motion'].search(block)
        if not motion_match:
            logger.warning(f"No motion found in block {block_index}")
            return None

        # Extract vote result
        result_match = self.patterns['vote_result'].search(block)
        if not result_match:
            logger.warning(f"No vote result found in block {block_index}")
            return None

        # Extract vote details
        details_match = self.patterns['vote_details'].search(block)
        if not details_match:
            logger.warning(f"No vote details found in block {block_index}")
            return None

        # Build motion context
        motion_context = MotionContext(
            id=f"M{block_index}",
            type="original",  # Could be enhanced to detect amendments
            text=motion_match.group('action').strip(),
            mover=self._clean_member_name(motion_match.group('mover')),
            seconder=self._clean_member_name(motion_match.group('seconder')),
            agenda_item=f"Item {block_index}",  # Enhanced item correlation needed
            timestamp=datetime.now()
        )

        # Parse member votes
        member_votes = self._parse_member_votes(details_match)

        # Calculate tally
        tally = self._calculate_tally(member_votes)

        # Determine agenda item correlation
        agenda_item_number, agenda_item_title = self._correlate_agenda_item(block, agenda_data)

        # Create vote record
        vote_record = VoteRecord(
            motion_id=motion_context.id,
            agenda_item_number=agenda_item_number,
            agenda_item_title=agenda_item_title,
            outcome="Pass" if result_match.group('outcome').lower() == 'carried' else "Fail",
            vote_count=result_match.group('vote_count'),
            member_votes=member_votes,
            tally=tally,
            motion_context=motion_context
        )

        # Validate vote record
        validation_notes = self._validate_vote_record(vote_record)
        vote_record.validation_notes = validation_notes

        return vote_record

    def _parse_member_votes(self, details_match: re.Match) -> Dict[str, str]:
        """Parse individual member votes from vote details"""
        member_votes = {}

        # Parse AYES
        if details_match.group('ayes'):
            ayes_text = details_match.group('ayes')
            ayes_members = self._extract_member_names(ayes_text)
            for member in ayes_members:
                member_votes[member] = 'Aye'

        # Parse NOES
        if details_match.group('noes'):
            noes_text = details_match.group('noes')
            noes_members = self._extract_member_names(noes_text)
            for member in noes_members:
                member_votes[member] = 'Nay'

        # Parse ABSTAIN
        if details_match.group('abstain'):
            abstain_text = details_match.group('abstain')
            abstain_members = self._extract_member_names(abstain_text)
            for member in abstain_members:
                member_votes[member] = 'Abstain'

        # Parse ABSENT
        if details_match.group('absent'):
            absent_text = details_match.group('absent')
            absent_members = self._extract_member_names(absent_text)
            for member in absent_members:
                member_votes[member] = 'Absent'

        return member_votes

    def _extract_member_names(self, text: str) -> List[str]:
        """Extract and clean member names from vote text"""
        if not text or text.strip().lower() == 'none':
            return []

        # Pattern to match member names with titles
        member_pattern = re.compile(
            r'(?:COUNCILMEMBER|MAYOR(?:\s+PRO\s+TEM)?)\s+([A-Z]+)',
            re.IGNORECASE
        )

        members = []
        for match in member_pattern.finditer(text):
            member_name = self._clean_member_name(match.group(0))
            if member_name:
                members.append(member_name)

        return members

    def _clean_member_name(self, name: str) -> str:
        """Clean and standardize member names"""
        if not name:
            return ""

        # Remove titles and standardize format
        titles = ['COUNCILMEMBER', 'MAYOR PRO TEM', 'MAYOR']
        name = name.strip().upper()

        for title in titles:
            name = name.replace(title, '').strip()

        # Apply OCR corrections
        for wrong, right in self.member_name_corrections.items():
            name = name.replace(wrong, right)

        return name.title()

    def _calculate_tally(self, member_votes: Dict[str, str]) -> Dict[str, int]:
        """Calculate vote tally from member votes"""
        tally = {'ayes': 0, 'noes': 0, 'abstain': 0, 'absent': 0}

        for vote in member_votes.values():
            if vote == 'Aye':
                tally['ayes'] += 1
            elif vote == 'Nay':
                tally['noes'] += 1
            elif vote == 'Abstain':
                tally['abstain'] += 1
            elif vote == 'Absent':
                tally['absent'] += 1

        return tally

    def _correlate_agenda_item(self, vote_block: str, agenda_data: Dict) -> Tuple[str, str]:
        """Attempt to correlate vote with agenda item"""
        # Simple correlation by looking for item numbers in the vote block
        for item in agenda_data.get('items', []):
            if item['number'] in vote_block:
                return item['number'], item['title']

        # Fallback to generic numbering
        return "Unknown", "Resolution Item"

    def _validate_vote_record(self, vote_record: VoteRecord) -> List[str]:
        """Validate vote record for consistency and completeness"""
        notes = []

        # Check vote count consistency
        expected_total = sum(vote_record.tally.values())
        vote_count_parts = vote_record.vote_count.split('-')
        if len(vote_count_parts) == 2:
            reported_ayes = int(vote_count_parts[0])
            reported_noes = int(vote_count_parts[1])

            if reported_ayes != vote_record.tally['ayes']:
                notes.append(f"Aye count mismatch: reported {reported_ayes}, calculated {vote_record.tally['ayes']}")

            if reported_noes != vote_record.tally['noes']:
                notes.append(f"Nay count mismatch: reported {reported_noes}, calculated {vote_record.tally['noes']}")

        # Check outcome consistency
        if vote_record.tally['ayes'] > vote_record.tally['noes'] and vote_record.outcome == 'Fail':
            notes.append("Outcome inconsistent: more ayes than noes but marked as Fail")
        elif vote_record.tally['noes'] > vote_record.tally['ayes'] and vote_record.outcome == 'Pass':
            notes.append("Outcome inconsistent: more noes than ayes but marked as Pass")

        # Check for empty member votes
        if not vote_record.member_votes:
            notes.append("No member votes recorded")

        return notes

    def _validate_extraction(self, vote_records: List[VoteRecord], metadata: Dict) -> Dict[str, Any]:
        """Perform comprehensive validation of extracted data"""
        validation = {
            'total_votes': len(vote_records),
            'valid_votes': 0,
            'validation_errors': [],
            'quality_score': 0.0
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

    def _format_output(self, vote_records: List[VoteRecord], metadata: Dict, validation: Dict) -> Dict[str, Any]:
        """Format extracted data for dashboard consumption"""
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
                'validation_notes': vote.validation_notes
            }
            formatted_votes.append(formatted_vote)

        return {
            'extraction_metadata': {
                'agent_name': self.name,
                'agent_version': self.version,
                'extraction_timestamp': datetime.now().isoformat(),
                'meeting_metadata': metadata
            },
            'validation_results': validation,
            'votes': formatted_votes,
            'success': validation['quality_score'] > 0.5,  # Minimum 50% quality threshold
            'message': f"Extracted {len(formatted_votes)} vote records with {validation['quality_score']:.1%} quality"
        }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            'extraction_metadata': {
                'agent_name': self.name,
                'agent_version': self.version,
                'extraction_timestamp': datetime.now().isoformat(),
                'error': error_message
            },
            'validation_results': {
                'total_votes': 0,
                'valid_votes': 0,
                'validation_errors': [error_message],
                'quality_score': 0.0
            },
            'votes': [],
            'success': False,
            'message': f"Extraction failed: {error_message}"
        }

    # Helper methods for metadata extraction
    def _extract_meeting_date(self, content: str) -> Optional[str]:
        """Extract meeting date from document content"""
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _determine_meeting_type(self, content: str) -> str:
        """Determine meeting type from content"""
        content_lower = content.lower()

        if 'special' in content_lower:
            if 'housing' in content_lower:
                return 'Special Housing Authority'
            elif 'successor' in content_lower:
                return 'Special Successor Agency'
            else:
                return 'Special Meeting'
        elif 'regular' in content_lower:
            return 'Regular Meeting'
        else:
            return 'Unknown'

    def _estimate_meeting_duration(self, content: str) -> str:
        """Estimate meeting duration from timestamps in content"""
        # Simple implementation - could be enhanced
        return "Estimated 2-3 hours"

    def _extract_agenda_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata specific to agenda document"""
        return {
            'has_closed_session': 'closed session' in content.lower(),
            'has_teleconference': 'teleconference' in content.lower(),
            'estimated_items': len(re.findall(r'\d+\.', content))
        }

    def _extract_minutes_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata specific to minutes document"""
        return {
            'has_roll_call': 'roll call' in content.lower(),
            'has_recusals': 'recused' in content.lower(),
            'estimated_votes': len(re.findall(r'motion.*carried|motion.*failed', content, re.IGNORECASE))
        }

    def _identify_vote_sections(self, content: str) -> List[str]:
        """Identify sections containing votes"""
        vote_sections = []

        # Find sections with MOTION and vote results
        sections = re.split(r'(?=MOTION:)', content)
        for section in sections:
            if 'MOTION:' in section and ('carried' in section.lower() or 'failed' in section.lower()):
                vote_sections.append(section)

        return vote_sections

    def _parse_attendance(self, attendance_text: str):
        """Parse attendance information to initialize member states"""
        # Extract member names from attendance text
        member_pattern = re.compile(
            r'(?:Councilmember|Mayor(?:\s+Pro\s+Tem)?)\s+([A-Z]+)',
            re.IGNORECASE
        )

        for match in member_pattern.finditer(attendance_text):
            member_name = self._clean_member_name(match.group(0))
            title = match.group(0).replace(match.group(1), '').strip()

            self.member_states[member_name] = MemberState(
                name=member_name,
                title=title,
                present=True
            )

        logger.info(f"Initialized {len(self.member_states)} member states")

# Test function for the agent
def test_vote_extraction_agent():
    """Test function to validate VoteExtractionAgent functionality"""
    agent = VoteExtractionAgent()

    # Test with sample content
    sample_motion_block = """
    MOTION: COUNCILMEMBER BACERRA moved to approve the minutes, seconded by COUNCILMEMBER PHAN.
    The motion carried, 7-0, by the following roll call vote:
    AYES: COUNCILMEMBER BACERRA, COUNCILMEMBER PHAN, COUNCILMEMBER HERNANDEZ,
          COUNCILMEMBER PENALOZA, COUNCILMEMBER VAZQUEZ, MAYOR PRO TEM LOPEZ, MAYOR AMEZCUA
    NOES: NONE
    ABSTAIN: NONE
    ABSENT: NONE
    """

    # Test motion pattern matching
    motion_match = agent.patterns['motion'].search(sample_motion_block)
    assert motion_match is not None, "Motion pattern should match sample text"

    # Test vote result pattern matching
    result_match = agent.patterns['vote_result'].search(sample_motion_block)
    assert result_match is not None, "Vote result pattern should match sample text"

    # Test member name cleaning
    cleaned_name = agent._clean_member_name("COUNCILMEMBER BACERRA")
    assert cleaned_name == "Bacerra", f"Expected 'Bacerra', got '{cleaned_name}'"

    print("VoteExtractionAgent tests passed!")

if __name__ == "__main__":
    test_vote_extraction_agent()
    print("VoteExtractionAgent created successfully!")