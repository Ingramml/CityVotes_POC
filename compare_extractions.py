#!/usr/bin/env python3
"""
Extraction Comparison Tool

Compares manual vote extractions with AI-powered extractor results
to identify accuracy gaps and improvement opportunities.

Usage:
    python compare_extractions.py <manual_extraction.json> <agenda_file.txt> <minutes_file.txt>
    python compare_extractions.py --batch manual_extractions/
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from agents.ai_powered_santa_ana_extractor import AIPoweredSantaAnaExtractor

class ExtractionComparator:
    """Compares manual and AI extractions to identify differences"""

    def __init__(self):
        self.ai_extractor = AIPoweredSantaAnaExtractor()
        self.differences = []

    def load_manual_extraction(self, filepath: str) -> Dict:
        """Load manual extraction JSON"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def run_ai_extraction(self, agenda_file: str, minutes_file: str) -> Dict:
        """Run AI extractor on the same documents"""
        result = self.ai_extractor.process_meeting(agenda_file, minutes_file)

        return {
            'votes': [vars(vote) for vote in result.votes],
            'confidence': result.confidence_score,
            'method': result.method_used,
            'notes': result.processing_notes
        }

    def compare_votes(self, manual: Dict, ai: Dict) -> Dict:
        """Compare manual vs AI extractions"""

        manual_votes = manual.get('votes', [])
        ai_votes = ai.get('votes', [])

        comparison = {
            'summary': {
                'manual_vote_count': len(manual_votes),
                'ai_vote_count': len(ai_votes),
                'vote_count_match': len(manual_votes) == len(ai_votes),
                'ai_confidence': ai.get('confidence', 0),
                'ai_method': ai.get('method', 'unknown')
            },
            'differences': [],
            'missing_in_ai': [],
            'extra_in_ai': [],
            'accuracy_metrics': {}
        }

        # Create quick lookup by agenda item
        manual_by_item = {v.get('agenda_item_number'): v for v in manual_votes}
        ai_by_item = {v.get('agenda_item_number'): v for v in ai_votes}

        # Find missing votes
        manual_items = set(manual_by_item.keys())
        ai_items = set(ai_by_item.keys())

        missing = manual_items - ai_items
        extra = ai_items - manual_items

        for item in missing:
            comparison['missing_in_ai'].append({
                'agenda_item': item,
                'title': manual_by_item[item].get('agenda_item_title', 'N/A')
            })

        for item in extra:
            comparison['extra_in_ai'].append({
                'agenda_item': item,
                'title': ai_by_item[item].get('agenda_item_title', 'N/A')
            })

        # Compare matching votes
        matching_items = manual_items & ai_items

        for item in matching_items:
            manual_vote = manual_by_item[item]
            ai_vote = ai_by_item[item]

            diff = self._compare_single_vote(item, manual_vote, ai_vote)
            if diff['has_differences']:
                comparison['differences'].append(diff)

        # Calculate accuracy metrics
        if len(manual_votes) > 0:
            comparison['accuracy_metrics'] = {
                'vote_detection_rate': len(ai_items) / len(manual_items) if manual_items else 0,
                'false_positive_rate': len(extra) / len(ai_items) if ai_items else 0,
                'exact_match_rate': (len(matching_items) - len(comparison['differences'])) / len(manual_items) if manual_items else 0,
                'total_discrepancies': len(comparison['differences']) + len(missing) + len(extra)
            }

        return comparison

    def _compare_single_vote(self, item_number: str, manual: Dict, ai: Dict) -> Dict:
        """Compare a single vote in detail"""

        diff = {
            'agenda_item': item_number,
            'has_differences': False,
            'discrepancies': []
        }

        # Compare outcome
        manual_outcome = manual.get('outcome')
        ai_outcome = ai.get('outcome')
        if manual_outcome != ai_outcome:
            diff['has_differences'] = True
            diff['discrepancies'].append({
                'field': 'outcome',
                'manual': manual_outcome,
                'ai': ai_outcome
            })

        # Compare tally
        manual_tally = manual.get('tally', {})
        ai_tally = ai.get('tally', {})

        for key in ['ayes', 'noes', 'abstain', 'absent']:
            if manual_tally.get(key) != ai_tally.get(key):
                diff['has_differences'] = True
                diff['discrepancies'].append({
                    'field': f'tally.{key}',
                    'manual': manual_tally.get(key),
                    'ai': ai_tally.get(key)
                })

        # Compare member votes
        manual_members = manual.get('member_votes', {})
        ai_members = ai.get('member_votes', {})

        all_members = set(manual_members.keys()) | set(ai_members.keys())

        for member in all_members:
            manual_vote = manual_members.get(member)
            ai_vote = ai_members.get(member)

            if manual_vote != ai_vote:
                diff['has_differences'] = True
                diff['discrepancies'].append({
                    'field': f'member_vote.{member}',
                    'manual': manual_vote,
                    'ai': ai_vote
                })

        return diff

    def generate_report(self, comparison: Dict, output_file: str = None) -> str:
        """Generate human-readable comparison report"""

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("EXTRACTION COMPARISON REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")

        # Summary
        summary = comparison['summary']
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Manual Votes: {summary['manual_vote_count']}")
        report_lines.append(f"AI Votes: {summary['ai_vote_count']}")
        report_lines.append(f"Vote Count Match: {'✓' if summary['vote_count_match'] else '✗'}")
        report_lines.append(f"AI Confidence: {summary['ai_confidence']:.1%}")
        report_lines.append(f"AI Method: {summary['ai_method']}")
        report_lines.append("")

        # Accuracy Metrics
        if comparison['accuracy_metrics']:
            metrics = comparison['accuracy_metrics']
            report_lines.append("ACCURACY METRICS")
            report_lines.append("-" * 80)
            report_lines.append(f"Vote Detection Rate: {metrics['vote_detection_rate']:.1%}")
            report_lines.append(f"False Positive Rate: {metrics['false_positive_rate']:.1%}")
            report_lines.append(f"Exact Match Rate: {metrics['exact_match_rate']:.1%}")
            report_lines.append(f"Total Discrepancies: {metrics['total_discrepancies']}")
            report_lines.append("")

        # Missing votes
        if comparison['missing_in_ai']:
            report_lines.append("VOTES MISSED BY AI")
            report_lines.append("-" * 80)
            for vote in comparison['missing_in_ai']:
                report_lines.append(f"  • {vote['agenda_item']}: {vote['title']}")
            report_lines.append("")

        # Extra votes
        if comparison['extra_in_ai']:
            report_lines.append("EXTRA VOTES FROM AI (False Positives)")
            report_lines.append("-" * 80)
            for vote in comparison['extra_in_ai']:
                report_lines.append(f"  • {vote['agenda_item']}: {vote['title']}")
            report_lines.append("")

        # Differences in matched votes
        if comparison['differences']:
            report_lines.append("DISCREPANCIES IN MATCHED VOTES")
            report_lines.append("-" * 80)
            for diff in comparison['differences']:
                report_lines.append(f"\nAgenda Item: {diff['agenda_item']}")
                for disc in diff['discrepancies']:
                    report_lines.append(f"  {disc['field']}:")
                    report_lines.append(f"    Manual: {disc['manual']}")
                    report_lines.append(f"    AI:     {disc['ai']}")
            report_lines.append("")

        report = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"✓ Report saved: {output_file}")

        return report

    def compare_extraction(self, manual_file: str, agenda_file: str, minutes_file: str,
                          output_dir: str = "comparison_reports") -> Dict:
        """Complete comparison workflow"""

        print(f"📋 Comparing extraction for: {Path(manual_file).stem}")
        print(f"   Manual file: {manual_file}")
        print(f"   Agenda: {agenda_file}")
        print(f"   Minutes: {minutes_file}")
        print()

        # Load manual extraction
        print("1. Loading manual extraction...")
        manual = self.load_manual_extraction(manual_file)

        # Run AI extraction
        print("2. Running AI extraction on same documents...")
        ai = self.run_ai_extraction(agenda_file, minutes_file)

        # Compare
        print("3. Comparing results...")
        comparison = self.compare_votes(manual, ai)

        # Generate report
        print("4. Generating report...")
        output_file = Path(output_dir) / f"{Path(manual_file).stem}_comparison.txt"
        report = self.generate_report(comparison, str(output_file))

        # Save JSON comparison
        json_file = Path(output_dir) / f"{Path(manual_file).stem}_comparison.json"
        with open(json_file, 'w') as f:
            json.dump(comparison, f, indent=2)
        print(f"✓ JSON comparison saved: {json_file}")

        print("\n" + "=" * 80)
        print("QUICK SUMMARY")
        print("=" * 80)
        print(f"Accuracy: {comparison['accuracy_metrics'].get('exact_match_rate', 0):.1%}")
        print(f"Votes missed: {len(comparison['missing_in_ai'])}")
        print(f"False positives: {len(comparison['extra_in_ai'])}")
        print(f"Discrepancies: {len(comparison['differences'])}")
        print()

        return comparison

def main():
    """Main entry point"""

    if len(sys.argv) < 4:
        print("Usage: python compare_extractions.py <manual_json> <agenda_txt> <minutes_txt>")
        print("\nExample:")
        print("  python compare_extractions.py \\")
        print("    manual_extractions/santa_ana/2024-01-16.json \\")
        print("    /path/to/agenda_20240116.txt \\")
        print("    /path/to/minutes_20240116.txt")
        sys.exit(1)

    manual_file = sys.argv[1]
    agenda_file = sys.argv[2]
    minutes_file = sys.argv[3]

    comparator = ExtractionComparator()
    comparison = comparator.compare_extraction(manual_file, agenda_file, minutes_file)

    print(f"\n✅ Comparison complete!")
    print(f"   Check comparison_reports/ for detailed analysis")

if __name__ == '__main__':
    main()
