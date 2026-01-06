"""
Dashboard routes for CityVotes POC
Handles the three main dashboard views: Vote Summary, Member Analysis, City Comparison
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash, current_app, request

dashboard_bp = Blueprint('dashboard', __name__)

def get_session_data_or_redirect(city_name=None):
    """Helper function to get session data or redirect if not available"""
    session_id = session.get('session_id')
    if not session_id:
        flash('No active session. Please upload data first.', 'error')
        return None, redirect(url_for('main.home'))

    if city_name:
        session_data = current_app.file_processor.get_session_data(session_id, city_name)
        if not session_data:
            flash(f'No data found for {city_name}. Please upload data first.', 'error')
            return None, redirect(url_for('main.home'))
        return session_data, None

    return session_id, None

@dashboard_bp.route('/')
def dashboard_home():
    """Dashboard landing page - redirect to appropriate dashboard"""
    current_city = session.get('current_city')

    if current_city:
        return redirect(url_for('dashboard.vote_summary'))

    # Check if user has any data
    session_id = session.get('session_id')
    if session_id:
        cities = current_app.file_processor.get_session_cities(session_id)
        if cities:
            session['current_city'] = cities[0]
            return redirect(url_for('dashboard.vote_summary'))

    flash('Please upload voting data to view dashboards', 'info')
    return redirect(url_for('main.home'))

@dashboard_bp.route('/vote-summary')
def vote_summary():
    """Vote Summary Dashboard - Core functionality showcase"""
    current_city = session.get('current_city')
    if not current_city:
        return redirect(url_for('dashboard.dashboard_home'))

    session_data, error_response = get_session_data_or_redirect(current_city)
    if error_response:
        return error_response

    # Extract processed data
    processed_data = session_data['processed_data']
    vote_summary = processed_data['vote_summary']
    city_info = processed_data['city_info']
    member_analysis = processed_data['member_analysis']

    # Calculate additional metrics for display
    total_members = len(member_analysis)
    active_members = len([m for m in member_analysis.values() if m['total_votes'] > 0])

    # Most/least active members
    member_participation = [
        {
            'name': name,
            'votes': stats['total_votes'],
            'aye_percentage': round((stats['vote_breakdown']['AYE'] / stats['total_votes'] * 100) if stats['total_votes'] > 0 else 0, 1)
        }
        for name, stats in member_analysis.items()
    ]
    member_participation.sort(key=lambda x: x['votes'], reverse=True)

    # Get available cities for navigation
    session_cities = current_app.file_processor.get_session_cities(session.get('session_id'))
    available_cities = {}
    for city_key in session_cities:
        config = current_app.city_config.get_city_config(city_key)
        available_cities[city_key] = config['display_name'] if config else city_key.title()

    return render_template('dashboards/vote_summary.html',
                         vote_summary=vote_summary,
                         city_info=city_info,
                         current_city=current_city,
                         member_participation=member_participation,
                         total_members=total_members,
                         active_members=active_members,
                         upload_info=session_data,
                         available_cities=available_cities)

@dashboard_bp.route('/member-analysis')
def member_analysis():
    """Council Member Analysis Dashboard - Detailed member insights"""
    current_city = session.get('current_city')
    if not current_city:
        return redirect(url_for('dashboard.dashboard_home'))

    session_data, error_response = get_session_data_or_redirect(current_city)
    if error_response:
        return error_response

    # Extract processed data
    processed_data = session_data['processed_data']
    member_analysis = processed_data['member_analysis']
    city_info = processed_data['city_info']

    # Calculate member alignment matrix (simplified)
    alignment_data = {}
    member_names = list(member_analysis.keys())

    # Get voting records from raw data for alignment calculation
    raw_votes = session_data['raw_data']['votes']

    # Calculate alignment scores (percentage of votes where members agreed)
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

                alignment_score = round((agreements / total_comparisons * 100) if total_comparisons > 0 else 0, 1)
                alignment_data[member1][member2] = alignment_score

    # Find most/least aligned pairs
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
    least_aligned = alignment_pairs[-3:]

    # Get available cities for navigation
    session_cities = current_app.file_processor.get_session_cities(session.get('session_id'))
    available_cities = {}
    for city_key in session_cities:
        config = current_app.city_config.get_city_config(city_key)
        available_cities[city_key] = config['display_name'] if config else city_key.title()

    return render_template('dashboards/member_analysis.html',
                         member_analysis=member_analysis,
                         city_info=city_info,
                         current_city=current_city,
                         alignment_data=alignment_data,
                         most_aligned=most_aligned,
                         least_aligned=least_aligned,
                         available_cities=available_cities)

@dashboard_bp.route('/city-comparison')
def city_comparison():
    """City Comparison Dashboard - Multi-city analysis"""
    session_id, error_response = get_session_data_or_redirect()
    if error_response:
        return error_response

    # Get all cities with data in session
    session_cities = current_app.file_processor.get_session_cities(session_id)

    if len(session_cities) < 2:
        flash('Upload data for at least 2 cities to view comparison', 'warning')
        return redirect(url_for('main.home'))

    # Collect data for all cities
    comparison_data = {}

    for city_key in session_cities:
        session_data = current_app.file_processor.get_session_data(session_id, city_key)
        city_config = current_app.city_config.get_city_config(city_key)

        if session_data and city_config:
            processed = session_data['processed_data']

            comparison_data[city_key] = {
                'display_name': city_config['display_name'],
                'colors': city_config['colors'],
                'council_size': city_config['total_seats'],
                'vote_summary': processed['vote_summary'],
                'member_count': len(processed['member_analysis']),
                'upload_filename': session_data['original_filename'],
                'upload_time': session_data['upload_timestamp']
            }

    # Calculate comparative metrics
    comparison_metrics = {}
    for city_key, data in comparison_data.items():
        vs = data['vote_summary']
        total_votes = vs['total_votes']
        pass_count = vs['outcomes']['PASS']['count'] if 'PASS' in vs['outcomes'] else 0

        comparison_metrics[city_key] = {
            'pass_rate': round((pass_count / total_votes * 100) if total_votes > 0 else 0, 1),
            'votes_per_member': round(total_votes / data['member_count'] if data['member_count'] > 0 else 0, 1),
            'council_efficiency': round(data['member_count'] / data['council_size'] * 100, 1)
        }

    return render_template('dashboards/city_comparison.html',
                         comparison_data=comparison_data,
                         comparison_metrics=comparison_metrics,
                         cities_count=len(comparison_data))

@dashboard_bp.route('/member/<member_name>')
def member_profile(member_name):
    """Individual member profile page"""
    current_city = session.get('current_city')
    if not current_city:
        return redirect(url_for('dashboard.dashboard_home'))

    session_data, error_response = get_session_data_or_redirect(current_city)
    if error_response:
        return error_response

    # Extract processed data
    processed_data = session_data['processed_data']
    member_analysis = processed_data['member_analysis']
    city_info = processed_data['city_info']

    # Check if member exists
    if member_name not in member_analysis:
        flash(f'Member "{member_name}" not found', 'error')
        return redirect(url_for('dashboard.member_analysis'))

    member_stats = member_analysis[member_name]

    # Get voting history from raw data
    raw_votes = session_data['raw_data']['votes']
    member_vote_history = []
    for vote in raw_votes:
        member_votes = vote.get('member_votes', {})
        if member_name in member_votes:
            member_vote_history.append({
                'agenda_item': vote.get('agenda_item_number', 'N/A'),
                'title': vote.get('agenda_item_title', 'Unknown'),
                'outcome': vote.get('outcome', 'Unknown'),
                'member_vote': member_votes[member_name],
                'meeting_date': vote.get('meeting_date', 'Unknown'),
                'meeting_section': vote.get('meeting_section', 'Unknown')
            })

    # Calculate agreement with other members
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

    return render_template('dashboards/member_profile.html',
                         member_name=member_name,
                         member_stats=member_stats,
                         city_info=city_info,
                         current_city=current_city,
                         vote_history=member_vote_history,
                         agreements=sorted_agreements)

@dashboard_bp.route('/agenda-items')
def agenda_items():
    """Agenda Items Summary page - list of all agenda items"""
    current_city = session.get('current_city')
    if not current_city:
        return redirect(url_for('dashboard.dashboard_home'))

    session_data, error_response = get_session_data_or_redirect(current_city)
    if error_response:
        return error_response

    city_info = session_data['processed_data']['city_info']
    raw_votes = session_data['raw_data']['votes']

    # Group votes by meeting date
    meetings = {}
    for vote in raw_votes:
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

    # Sort meetings by date (newest first)
    sorted_meetings = dict(sorted(meetings.items(), key=lambda x: x[1]['date'], reverse=True))

    return render_template('dashboards/agenda_items.html',
                         meetings=sorted_meetings,
                         city_info=city_info,
                         current_city=current_city,
                         total_items=len(raw_votes))

@dashboard_bp.route('/agenda-item/<item_id>')
def agenda_item_detail(item_id):
    """Individual Agenda Item page with vote details"""
    current_city = session.get('current_city')
    if not current_city:
        return redirect(url_for('dashboard.dashboard_home'))

    session_data, error_response = get_session_data_or_redirect(current_city)
    if error_response:
        return error_response

    city_info = session_data['processed_data']['city_info']
    raw_votes = session_data['raw_data']['votes']

    # Find the specific agenda item
    item_data = None
    for vote in raw_votes:
        if vote.get('example_id') == item_id:
            item_data = vote
            break

    if not item_data:
        flash(f'Agenda item "{item_id}" not found', 'error')
        return redirect(url_for('dashboard.agenda_items'))

    # Process member votes for display
    member_votes_list = []
    for member, vote_choice in item_data.get('member_votes', {}).items():
        member_votes_list.append({
            'name': member,
            'vote': vote_choice
        })

    return render_template('dashboards/agenda_item_detail.html',
                         item=item_data,
                         member_votes=member_votes_list,
                         city_info=city_info,
                         current_city=current_city)

@dashboard_bp.route('/switch-city/<city_name>')
def switch_city(city_name):
    """Switch to a different city's dashboard"""
    # Validate city exists in session
    session_id = session.get('session_id')
    if session_id:
        session_data = current_app.file_processor.get_session_data(session_id, city_name)
        if session_data:
            session['current_city'] = city_name
            flash(f'Switched to {city_name}', 'success')

            # Redirect to the same dashboard type they were viewing
            referrer = request.referrer
            if referrer:
                if 'member-analysis' in referrer:
                    return redirect(url_for('dashboard.member_analysis'))
                elif 'city-comparison' in referrer:
                    return redirect(url_for('dashboard.city_comparison'))

            return redirect(url_for('dashboard.vote_summary'))

    flash(f'No data found for {city_name}', 'error')
    return redirect(url_for('dashboard.dashboard_home'))