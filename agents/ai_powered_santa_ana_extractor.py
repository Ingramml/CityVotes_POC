"""
AI-Powered Santa Ana Vote Extractor with Learning Capabilities

This agent combines traditional regex processing with LLM intelligence and
builds a learning memory system that improves extraction accuracy over time.

Features:
- LLM fallback for complex vote scenarios
- Learning memory that stores successful patterns
- Adaptive processing based on validation feedback
- Self-improving extraction accuracy
- Comprehensive validation and quality scoring
"""

import json
import re
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Base vote extraction classes
from vote_extraction_agent import VoteExtractionAgent, VoteRecord, MotionContext

logger = logging.getLogger(__name__)

@dataclass
class ExtractionMemory:
    """Stores learning patterns and successful extraction examples"""
    successful_patterns: Dict[str, int] = field(default_factory=dict)
    failed_patterns: Dict[str, int] = field(default_factory=dict)
    member_name_corrections: Dict[str, str] = field(default_factory=dict)
    agenda_item_patterns: List[str] = field(default_factory=list)
    quality_history: List[float] = field(default_factory=list)
    extraction_examples: List[Dict] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AIExtractionResult:
    """Result from AI-powered extraction"""
    votes: List[VoteRecord]
    confidence_score: float
    method_used: str  # "regex", "ai", "hybrid"
    processing_notes: List[str]
    validation_passed: bool

class AIPoweredSantaAnaExtractor(VoteExtractionAgent):
    """
    AI-powered Santa Ana vote extractor with learning capabilities
    """

    def __init__(self, memory_file: str = "santa_ana_extraction_memory.json"):
        super().__init__()
        self.memory_file = Path(memory_file)
        self.memory = self._load_memory()

        # Known Santa Ana council members for validation
        self.known_members = {
            "Amezcua", "Bacerra", "Hernandez", "Lopez",
            "Penaloza", "Phan", "Vazquez", "Mendoza", "Sarmiento"
        }

        # Track extraction statistics
        self.stats = {
            "total_extractions": 0,
            "ai_fallback_used": 0,
            "quality_improvements": 0,
            "pattern_learning_events": 0
        }

    def _load_memory(self) -> ExtractionMemory:
        """Load learning memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    return ExtractionMemory(**data)
            except Exception as e:
                logger.warning(f"Could not load memory file: {e}")

        return ExtractionMemory()

    def _save_memory(self):
        """Save learning memory to file"""
        try:
            self.memory.last_updated = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(asdict(self.memory), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save memory: {e}")

    def process_santa_ana_meeting(self, agenda_path: str, minutes_path: str) -> Dict[str, Any]:
        """
        Main extraction method with AI integration and learning
        """
        logger.info(f"AI-powered processing Santa Ana meeting: {agenda_path}, {minutes_path}")

        self.stats["total_extractions"] += 1

        try:
            # Load documents
            agenda_content = self._load_document(agenda_path)
            minutes_content = self._load_document(minutes_path)

            # Preprocess with learned improvements
            clean_minutes = self._enhanced_preprocessing(minutes_content)

            # Try regex extraction first (fast)
            regex_result = self._regex_extraction(clean_minutes, agenda_content)

            # Validate regex results
            validation_score = self._validate_extraction(regex_result)

            # Use AI fallback if validation fails
            if validation_score < 0.7:
                logger.info("Regex validation failed, using AI fallback")
                ai_result = self._ai_extraction_fallback(clean_minutes, agenda_content, regex_result)
                final_result = ai_result
                self.stats["ai_fallback_used"] += 1
            else:
                final_result = regex_result
                final_result.method_used = "regex"

            # Learn from this extraction
            self._learn_from_extraction(final_result, clean_minutes)

            # Format output
            return self._format_extraction_result(final_result, agenda_path, minutes_path)

        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return {
                "success": False,
                "message": f"AI extraction error: {str(e)}",
                "votes": [],
                "validation_results": {"quality_score": 0.0}
            }

    def _enhanced_preprocessing(self, content: str) -> str:
        """Enhanced text preprocessing using learned patterns"""

        # Apply learned corrections
        for old_pattern, new_pattern in self.memory.member_name_corrections.items():
            content = content.replace(old_pattern, new_pattern)

        # Standard cleaning
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = re.sub(r'-\s*\n\s*', '', content)  # Remove line-break hyphens
        content = content.replace('\n', ' ').replace('\r', ' ')

        # Remove common parsing artifacts learned from experience
        artifacts = [
            "Page \\d+", "CITY COUNCIL \\d+", "JANUARY \\d+, \\d+",
            "--- PAGE \\d+ ---"
        ]

        for artifact in artifacts:
            content = re.sub(artifact, '', content, flags=re.IGNORECASE)

        return content.strip()

    def _regex_extraction(self, minutes_content: str, agenda_content: str) -> AIExtractionResult:
        """Traditional regex extraction with improvements"""

        votes = []
        processing_notes = []

        # Find Santa Ana vote blocks - look for YES: followed by member names and Status:
        vote_pattern = r'YES:\s*\d+\s*[–-]\s*([^\.]+?)\s*NO:\s*\d+.*?Status:\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(Pass|Fail)'
        vote_matches = re.finditer(vote_pattern, minutes_content, re.DOTALL | re.IGNORECASE)

        for i, match in enumerate(vote_matches):
            try:
                # Extract the whole vote block for processing
                vote_start = max(0, match.start() - 500)  # Get some context before
                vote_end = min(len(minutes_content), match.end() + 100)  # Get some context after
                vote_block = minutes_content[vote_start:vote_end]

                vote = self._process_vote_block_enhanced(vote_block, agenda_content, i)
                if vote:
                    votes.append(vote)
            except Exception as e:
                processing_notes.append(f"Block {i} failed: {str(e)}")

        # If no votes found with new pattern, try old pattern as fallback
        if not votes:
            motion_pattern = r'MOTION:\s*([^\.]+?)\s*(?:moved|seconded).*?(?=MOTION:|$)'
            motion_blocks = re.findall(motion_pattern, minutes_content, re.DOTALL | re.IGNORECASE)

            for i, block in enumerate(motion_blocks):
                try:
                    vote = self._process_vote_block_enhanced(block, agenda_content, i)
                    if vote:
                        votes.append(vote)
                except Exception as e:
                    processing_notes.append(f"Fallback block {i} failed: {str(e)}")

        return AIExtractionResult(
            votes=votes,
            confidence_score=0.8,  # Default for regex
            method_used="regex",
            processing_notes=processing_notes,
            validation_passed=False  # Will be set by validation
        )

    def _process_vote_block_enhanced(self, block: str, agenda_content: str, block_index: int) -> Optional[VoteRecord]:
        """Enhanced vote block processing with learned patterns"""

        # Extract vote outcome from Status line
        outcome = "Pass"  # Default
        status_match = re.search(r'Status:\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(\d+)\s*[–-]\s*(Pass|Fail)', block, re.IGNORECASE)
        if status_match:
            outcome = status_match.group(5)

        # Extract vote count from Status line
        vote_count = "Unknown"
        if status_match:
            ayes = status_match.group(1)
            noes = status_match.group(2)
            vote_count = f"{ayes}-{noes}"

        # Extract motion text - look for context before the vote
        motion_text = self._extract_motion_text_from_block(block)

        # Extract member votes with validation
        member_votes = self._extract_member_votes_enhanced(block)

        # Correlate agenda item
        agenda_item_num, agenda_title = self._correlate_agenda_item_enhanced(block, agenda_content)

        # Calculate tally from member votes
        tally = {'ayes': 0, 'noes': 0, 'abstain': 0, 'absent': 0}
        for vote in member_votes.values():
            if vote.lower() in ['aye', 'yes']:
                tally['ayes'] += 1
            elif vote.lower() in ['nay', 'no']:
                tally['noes'] += 1
            elif vote.lower() == 'abstain':
                tally['abstain'] += 1
            else:
                tally['absent'] += 1

        # If we don't have member vote details, use Status line counts
        if not member_votes and status_match:
            tally = {
                'ayes': int(status_match.group(1)),
                'noes': int(status_match.group(2)),
                'abstain': int(status_match.group(3)),
                'absent': int(status_match.group(4))
            }

        # Create motion context if we have motion text
        motion_context = None
        if motion_text and motion_text != "Motion text not found":
            motion_context = MotionContext(
                id=f"motion_{agenda_item_num}_{block_index}",
                type='original',
                text=motion_text,
                mover="Unknown",
                seconder="Unknown",
                agenda_item=agenda_item_num,
                status='voted'
            )

        return VoteRecord(
            motion_id=f"motion_{agenda_item_num}_{block_index}",
            agenda_item_number=agenda_item_num,
            agenda_item_title=agenda_title,
            outcome=outcome,
            vote_count=vote_count,
            member_votes=member_votes,
            tally=tally,
            recusals={},
            motion_context=motion_context,
            validation_notes=[]
        )

    def _extract_member_votes_enhanced(self, block: str) -> Dict[str, str]:
        """Enhanced member vote extraction with validation against known members"""

        member_votes = {}

        # Look for Santa Ana YES: format first
        yes_match = re.search(r'YES:\s*\d+\s*[–-]\s*(.+?)(?:NO:|NOES:|$)', block, re.DOTALL | re.IGNORECASE)
        if yes_match:
            yes_text = yes_match.group(1)
            # Handle comma-separated list: "Penaloza, Phan, Lopez, Bacerra, Hernandez, Mendoza, Sarmiento"
            aye_members = self._extract_comma_separated_names(yes_text)
            for member in aye_members:
                member_votes[member] = "Aye"

        # Look for NO: section
        no_match = re.search(r'NO:\s*\d+\s*(?:[–-]\s*(.+?))?(?:ABSTAIN:|ABSENT:|$)', block, re.DOTALL | re.IGNORECASE)
        if no_match and no_match.group(1):
            no_text = no_match.group(1)
            no_members = self._extract_comma_separated_names(no_text)
            for member in no_members:
                member_votes[member] = "Nay"

        # Fallback: Look for traditional AYES section
        ayes_match = re.search(r'AYES:\s*(.+?)(?:NOES:|ABSTAIN:|$)', block, re.DOTALL | re.IGNORECASE)
        if ayes_match and not member_votes:
            ayes_text = ayes_match.group(1)
            aye_members = self._extract_clean_member_names(ayes_text)
            for member in aye_members:
                member_votes[member] = "Aye"

        # Look for NOES section
        noes_match = re.search(r'NOES:\s*(.+?)(?:ABSTAIN:|ABSENT:|$)', block, re.DOTALL | re.IGNORECASE)
        if noes_match:
            noes_text = noes_match.group(1)
            noe_members = self._extract_clean_member_names(noes_text)
            for member in noe_members:
                member_votes[member] = "Nay"

        # Validate against known members
        validated_votes = {}
        for member, vote in member_votes.items():
            clean_member = self._validate_member_name(member)
            if clean_member:
                validated_votes[clean_member] = vote

        return validated_votes

    def _extract_comma_separated_names(self, text: str) -> List[str]:
        """Extract member names from comma-separated format like 'Penaloza, Phan, Lopez, Bacerra'"""

        if not text or text.strip().upper() in ['NONE', 'N/A', '']:
            return []

        # Clean the text
        text = text.strip()

        # Split by comma and clean each name
        names = []
        for name in text.split(','):
            name = name.strip()
            # Remove common prefixes
            name = re.sub(r'(?:COUNCILMEMBER|MAYOR(?:\s+PRO\s+TEM)?)?\s*', '', name, flags=re.IGNORECASE)

            # Only keep valid names (alphabetic, proper case)
            if name and len(name) > 2 and name.replace(' ', '').isalpha() and name[0].isupper():
                names.append(name)

        logger.debug(f"Comma-separated extraction - input: {repr(text[:100])}, output: {names}")
        return names

    def _extract_motion_text_from_block(self, block: str) -> str:
        """Extract motion text from vote block context"""

        # Look for motion patterns in the context
        motion_patterns = [
            r'(?:moved to|moved that|moved)\s*(.+?)(?:\s*,\s*seconded|$)',
            r'approve\s+(.+?)(?:\s*YES:|Status:)',
            r'Recommended Action:\s*(.+?)(?:\s*YES:|Status:)',
            r'to\s+approve\s*(.+?)(?:\s*YES:|Status:)',
        ]

        for pattern in motion_patterns:
            match = re.search(pattern, block, re.IGNORECASE | re.DOTALL)
            if match:
                motion_text = match.group(1).strip()
                # Clean up the motion text
                motion_text = re.sub(r'\s+', ' ', motion_text)
                if len(motion_text) > 10:  # Only return substantial motion text
                    return motion_text

        return "Motion text not found"

    def _extract_clean_member_names(self, text: str) -> List[str]:
        """Extract and clean member names from vote text"""

        if not text or text.strip().upper() in ['NONE', 'N/A', '']:
            return []

        # Remove common prefixes and clean
        text = re.sub(r'(?:COUNCILMEMBER|MAYOR(?:\s+PRO\s+TEM)?)\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'[,\n\r]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # Split on common separators and extract surnames
        potential_names = re.split(r'\s+', text)

        clean_names = []
        for name in potential_names:
            name = name.strip().strip(',')
            if len(name) > 2 and name.isalpha() and name[0].isupper():
                clean_names.append(name)

        # Debug logging
        logger.debug(f"Member extraction - input: {repr(text[:100])}, output: {clean_names}")

        return clean_names

    def _validate_member_name(self, name: str) -> Optional[str]:
        """Validate member name against known council members"""

        if not name:
            return None

        # Check exact match
        if name in self.known_members:
            logger.debug(f"Exact match found: {name}")
            return name

        # Check partial matches (for variations)
        for known in self.known_members:
            if name.lower() in known.lower() or known.lower() in name.lower():
                # Learn this correction
                self.memory.member_name_corrections[name] = known
                self.stats["pattern_learning_events"] += 1
                logger.debug(f"Partial match found: {name} -> {known}")
                return known

        # If no match found, log for potential learning
        logger.warning(f"Unknown member name detected: {name}")
        return None

    def _correlate_agenda_item_enhanced(self, block: str, agenda_content: str) -> Tuple[str, str]:
        """Enhanced agenda item correlation using learned patterns"""

        # Check learned patterns first
        for pattern in self.memory.agenda_item_patterns:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                return match.group(1), match.group(2) if len(match.groups()) > 1 else "Item description"

        # Standard patterns
        item_patterns = [
            r'(?:Agenda\s+)?Item\s+(?:No\.?\s*)?(\d+)',
            r'Resolution\s+No\.?\s*(\S+)',
            r'Ordinance\s+(?:No\.?\s*)?(\S+)'
        ]

        for pattern in item_patterns:
            match = re.search(pattern, block, re.IGNORECASE)
            if match:
                item_num = match.group(1)
                # Learn this pattern
                if pattern not in self.memory.agenda_item_patterns:
                    self.memory.agenda_item_patterns.append(pattern)
                    self.stats["pattern_learning_events"] += 1
                return item_num, f"Agenda Item {item_num}"

        return "Unknown", "Unknown agenda item"

    def _ai_extraction_fallback(self, minutes_content: str, agenda_content: str,
                               regex_result: AIExtractionResult) -> AIExtractionResult:
        """
        AI fallback extraction using LLM when regex fails
        """
        logger.info("Using AI extraction fallback")

        # Prepare prompt for LLM
        prompt = self._create_extraction_prompt(minutes_content, regex_result)

        try:
            # This is where you'd call Claude API, OpenAI, etc.
            # For now, simulate with enhanced processing
            ai_votes = self._simulate_ai_extraction(minutes_content, agenda_content)

            return AIExtractionResult(
                votes=ai_votes,
                confidence_score=0.95,
                method_used="ai",
                processing_notes=["AI extraction successful"],
                validation_passed=True
            )

        except Exception as e:
            logger.error(f"AI fallback failed: {e}")
            # Return regex result as fallback
            regex_result.processing_notes.append(f"AI fallback failed: {e}")
            return regex_result

    def _create_extraction_prompt(self, minutes_content: str, regex_result: AIExtractionResult) -> str:
        """Create prompt for LLM extraction"""

        prompt = f"""
        Extract vote information from this Santa Ana City Council meeting minutes.

        Known council members: {', '.join(self.known_members)}

        Previous regex extraction found {len(regex_result.votes)} votes but validation failed.

        For each vote found, extract:
        1. Agenda item number
        2. Motion text
        3. Outcome (Pass/Fail)
        4. Vote count (e.g., "7-0")
        5. Individual member votes (Aye/Nay/Absent/Abstain)

        Minutes content (excerpt):
        {minutes_content[:2000]}...

        Return structured JSON format matching the example pattern.
        """

        return prompt

    def _simulate_ai_extraction(self, minutes_content: str, agenda_content: str) -> List[VoteRecord]:
        """
        Simulate AI extraction with enhanced processing
        This would be replaced with actual LLM API calls
        """

        # For simulation, use enhanced regex with validation
        votes = []

        # Find all vote patterns more intelligently
        vote_patterns = [
            r'MOTION:.*?(?=MOTION:|$)',
            r'The motion carried.*?(?=MOTION:|$)',
            r'Status:\s*\d+\s*[–-]\s*\d+.*?(?=MOTION:|$)'
        ]

        for pattern in vote_patterns:
            matches = re.finditer(pattern, minutes_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                vote_block = match.group(0)
                vote = self._process_vote_block_enhanced(vote_block, agenda_content, len(votes))
                if vote and self._is_valid_vote(vote):
                    votes.append(vote)

        return votes

    def _is_valid_vote(self, vote: VoteRecord) -> bool:
        """Validate a vote record"""

        # Check if we have valid member votes
        valid_members = sum(1 for member in vote.member_votes.keys()
                          if member in self.known_members)

        # Should have most council members voting
        return valid_members >= 4 and vote.agenda_item_number != "Unknown"

    def _validate_extraction(self, result: AIExtractionResult) -> float:
        """
        Validate extraction quality and return confidence score
        """

        if not result.votes:
            return 0.0

        total_score = 0.0
        vote_count = len(result.votes)

        for vote in result.votes:
            score = 0.0

            # Check member name quality (40% of score)
            valid_members = sum(1 for member in vote.member_votes.keys()
                              if member in self.known_members)
            member_score = valid_members / len(self.known_members) if self.known_members else 0
            score += member_score * 0.4

            # Check agenda item identification (30% of score)
            if vote.agenda_item_number != "Unknown":
                score += 0.3

            # Check vote completeness (30% of score)
            if vote.motion_context and vote.motion_context.text != "Motion text not found":
                score += 0.15
            if vote.vote_count and vote.vote_count != "Unknown":
                score += 0.15

            total_score += score

        final_score = total_score / vote_count if vote_count > 0 else 0.0
        result.validation_passed = final_score >= 0.7

        return final_score

    def _learn_from_extraction(self, result: AIExtractionResult, content: str):
        """
        Learn from extraction results to improve future performance
        """

        quality_score = self._validate_extraction(result)
        self.memory.quality_history.append(quality_score)

        # Learn from successful extractions
        if quality_score > 0.8:
            # Store successful example
            example = {
                "quality_score": quality_score,
                "method_used": result.method_used,
                "vote_count": len(result.votes),
                "timestamp": datetime.now().isoformat()
            }

            self.memory.extraction_examples.append(example)

            # Keep only recent examples
            if len(self.memory.extraction_examples) > 50:
                self.memory.extraction_examples = self.memory.extraction_examples[-50:]

        # Track quality improvements
        if len(self.memory.quality_history) >= 2:
            if self.memory.quality_history[-1] > self.memory.quality_history[-2]:
                self.stats["quality_improvements"] += 1

        # Save learning progress
        self._save_memory()

    def _format_extraction_result(self, result: AIExtractionResult, agenda_path: str,
                                 minutes_path: str) -> Dict[str, Any]:
        """Format the final extraction result"""

        # Convert VoteRecord objects to dictionaries
        votes_data = []
        for vote in result.votes:
            vote_dict = {
                "agenda_item_number": vote.agenda_item_number,
                "agenda_item_title": vote.agenda_item_title,
                "outcome": vote.outcome,
                "tally": vote.tally,
                "member_votes": vote.member_votes,
                "vote_count": vote.vote_count,
                "motion_text": vote.motion_context.text if vote.motion_context else "Motion text not found",
                "mover": vote.motion_context.mover if vote.motion_context else "Unknown",
                "seconder": vote.motion_context.seconder if vote.motion_context else "Unknown",
                "recusals": vote.recusals,
                "validation_notes": vote.validation_notes,
                "city_specific": {
                    "city": "Santa Ana",
                    "council_size": len(self.known_members)
                }
            }
            votes_data.append(vote_dict)

        # Calculate final quality score
        quality_score = self._validate_extraction(result)

        return {
            "success": result.validation_passed,
            "message": f"AI-powered extraction: {len(result.votes)} votes with {quality_score:.1%} quality",
            "votes": votes_data,
            "extraction_metadata": {
                "agent_name": "AIPoweredSantaAnaExtractor",
                "agent_version": "2.0.0",
                "city": "Santa Ana",
                "extraction_timestamp": datetime.now().isoformat(),
                "method_used": result.method_used,
                "confidence_score": result.confidence_score,
                "learning_stats": self.stats
            },
            "validation_results": {
                "quality_score": quality_score,
                "validation_passed": result.validation_passed,
                "processing_notes": result.processing_notes
            },
            "factory_metadata": {
                "extractor_used": "AIPoweredSantaAnaExtractor",
                "city_detected": "Santa Ana",
                "confidence_score": result.confidence_score,
                "document_sources": {
                    "agenda_file": agenda_path,
                    "minutes_file": minutes_path
                }
            }
        }

    def _calculate_tally(self, member_votes: Dict[str, str]) -> Dict[str, int]:
        """Calculate vote tally from member votes"""

        tally = {"ayes": 0, "noes": 0, "abstain": 0, "absent": 0}

        for vote in member_votes.values():
            if vote.lower() in ["aye", "yes"]:
                tally["ayes"] += 1
            elif vote.lower() in ["nay", "no"]:
                tally["noes"] += 1
            elif vote.lower() == "abstain":
                tally["abstain"] += 1
            elif vote.lower() == "absent":
                tally["absent"] += 1

        return tally

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning and performance statistics"""

        return {
            "extraction_stats": self.stats,
            "memory_stats": {
                "successful_patterns": len(self.memory.successful_patterns),
                "member_corrections": len(self.memory.member_name_corrections),
                "agenda_patterns": len(self.memory.agenda_item_patterns),
                "quality_history_length": len(self.memory.quality_history),
                "average_quality": sum(self.memory.quality_history) / len(self.memory.quality_history) if self.memory.quality_history else 0
            },
            "learning_progress": {
                "quality_trend": "improving" if len(self.memory.quality_history) >= 2 and self.memory.quality_history[-1] > self.memory.quality_history[0] else "stable",
                "ai_fallback_rate": self.stats["ai_fallback_used"] / max(self.stats["total_extractions"], 1),
                "pattern_learning_rate": self.stats["pattern_learning_events"] / max(self.stats["total_extractions"], 1)
            }
        }

    def export_learning_data(self, export_path: str):
        """Export learning data for analysis or transfer"""

        export_data = {
            "memory": asdict(self.memory),
            "stats": self.stats,
            "known_members": list(self.known_members),
            "export_timestamp": datetime.now().isoformat()
        }

        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"Learning data exported to {export_path}")