"""
Vote analysis service - calculates vote summaries and statistics
"""
from typing import Dict, List, Any


class VoteAnalyzer:
    """Handles vote-related analysis and calculations"""

    @staticmethod
    def calculate_vote_summary(processed_data: Dict) -> Dict[str, Any]:
        """Calculate vote summary with member participation"""
        vote_summary = processed_data.get('vote_summary', {})
        member_analysis = processed_data.get('member_analysis', {})

        total_members = len(member_analysis)
        active_members = len([m for m in member_analysis.values() if m['total_votes'] > 0])

        # Calculate member participation
        member_participation = [
            {
                'name': name,
                'votes': stats['total_votes'],
                'aye_percentage': round(
                    (stats['vote_breakdown']['AYE'] / stats['total_votes'] * 100)
                    if stats['total_votes'] > 0 else 0, 1
                )
            }
            for name, stats in member_analysis.items()
        ]
        member_participation.sort(key=lambda x: x['votes'], reverse=True)

        return {
            'vote_summary': vote_summary,
            'member_participation': member_participation,
            'total_members': total_members,
            'active_members': active_members
        }

    @staticmethod
    def get_agenda_items_grouped(raw_data: Dict) -> Dict[str, Any]:
        """Group agenda items by meeting date"""
        votes = raw_data.get('votes', [])
        meetings = {}

        for vote in votes:
            meeting_date = vote.get('meeting_date', 'Unknown')
            meeting_type = vote.get('meeting_type', 'Regular')
            meeting_key = f"{meeting_date} ({meeting_type})"

            if meeting_key not in meetings:
                meetings[meeting_key] = {
                    'date': meeting_date,
                    'type': meeting_type,
                    'agenda_items': []
                }

            meetings[meeting_key]['agenda_items'].append({
                'agenda_item': vote.get('agenda_item_number', 'N/A'),
                'title': vote.get('agenda_item_title', 'Unknown'),
                'outcome': vote.get('outcome', 'Unknown'),
                'section': vote.get('meeting_section', 'Unknown'),
                'example_id': vote.get('example_id', '')
            })

        # Sort by date (newest first)
        sorted_meetings = dict(sorted(meetings.items(), key=lambda x: x[1]['date'], reverse=True))
        return sorted_meetings

    @staticmethod
    def get_agenda_item_detail(raw_data: Dict, item_id: str) -> Dict[str, Any]:
        """Get details for a specific agenda item"""
        votes = raw_data.get('votes', [])

        for vote in votes:
            if vote.get('example_id') == item_id:
                member_votes = [
                    {'name': member, 'vote': vote_choice}
                    for member, vote_choice in vote.get('member_votes', {}).items()
                ]
                return {
                    'item': vote,
                    'member_votes': member_votes
                }

        return None
