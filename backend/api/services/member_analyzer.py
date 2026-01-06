"""
Member analysis service - calculates member statistics and alignments
"""
from typing import Dict, List, Any, Tuple


class MemberAnalyzer:
    """Handles member-related analysis and calculations"""

    @staticmethod
    def calculate_alignment_matrix(member_analysis: Dict, raw_votes: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Calculate alignment scores between all member pairs"""
        member_names = list(member_analysis.keys())
        alignment_data = {}

        for i, member1 in enumerate(member_names):
            alignment_data[member1] = {}
            for j, member2 in enumerate(member_names):
                if i == j:
                    alignment_data[member1][member2] = 100  # Perfect self-alignment
                else:
                    agreements = 0
                    total_comparisons = 0

                    for vote in raw_votes:
                        member_votes = vote.get('member_votes', {})
                        if member1 in member_votes and member2 in member_votes:
                            vote1 = member_votes[member1]
                            vote2 = member_votes[member2]
                            if vote1 in ['AYE', 'NAY'] and vote2 in ['AYE', 'NAY']:
                                total_comparisons += 1
                                if vote1 == vote2:
                                    agreements += 1

                    alignment_score = round(
                        (agreements / total_comparisons * 100) if total_comparisons > 0 else 0, 1
                    )
                    alignment_data[member1][member2] = alignment_score

        return alignment_data

    @staticmethod
    def get_aligned_pairs(alignment_data: Dict[str, Dict[str, float]]) -> Tuple[List[Dict], List[Dict]]:
        """Get most and least aligned pairs from alignment matrix"""
        member_names = list(alignment_data.keys())
        alignment_pairs = []

        for member1 in member_names:
            for member2 in member_names:
                if member1 < member2:  # Avoid duplicates
                    score = alignment_data[member1][member2]
                    alignment_pairs.append({
                        'member1': member1,
                        'member2': member2,
                        'score': score
                    })

        alignment_pairs.sort(key=lambda x: x['score'], reverse=True)
        most_aligned = alignment_pairs[:3]
        least_aligned = alignment_pairs[-3:] if len(alignment_pairs) >= 3 else []

        return most_aligned, least_aligned

    @staticmethod
    def get_member_profile(member_name: str, member_analysis: Dict, raw_votes: List[Dict]) -> Dict[str, Any]:
        """Get detailed profile for a specific member"""
        if member_name not in member_analysis:
            return None

        member_stats = member_analysis[member_name]

        # Build voting history
        vote_history = []
        for vote in raw_votes:
            member_votes = vote.get('member_votes', {})
            if member_name in member_votes:
                vote_history.append({
                    'agenda_item': vote.get('agenda_item_number', 'N/A'),
                    'title': vote.get('agenda_item_title', 'Unknown'),
                    'outcome': vote.get('outcome', 'Unknown'),
                    'member_vote': member_votes[member_name],
                    'meeting_date': vote.get('meeting_date', 'Unknown'),
                    'meeting_section': vote.get('meeting_section', 'Unknown')
                })

        # Calculate agreements with other members
        member_names = list(member_analysis.keys())
        agreements = {}
        for other_member in member_names:
            if other_member != member_name:
                agree_count = 0
                total_compare = 0
                for vote in raw_votes:
                    mv = vote.get('member_votes', {})
                    if member_name in mv and other_member in mv:
                        v1, v2 = mv[member_name], mv[other_member]
                        if v1 in ['AYE', 'NAY'] and v2 in ['AYE', 'NAY']:
                            total_compare += 1
                            if v1 == v2:
                                agree_count += 1
                if total_compare > 0:
                    agreements[other_member] = round(agree_count / total_compare * 100, 1)

        # Sort by agreement percentage
        sorted_agreements = sorted(agreements.items(), key=lambda x: x[1], reverse=True)

        return {
            'member_stats': member_stats,
            'vote_history': vote_history,
            'agreements': sorted_agreements
        }
