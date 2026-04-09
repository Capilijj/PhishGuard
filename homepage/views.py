# =============================================================
#  homepage/views.py
#  Dashboard view — requires login session.
# =============================================================

from django.shortcuts import render, redirect
from django.templatetags.static import static


def home_view(request):
    """
    Agent dashboard. Requires an active session.
    """
    if not request.session.get('user_id'):
        return redirect('login')

    username = request.session.get('username', 'AGENT')
    role     = request.session.get('role', 'Player')

    stats = _get_placeholder_stats()

    xp_current = stats['xp_current']
    xp_next    = stats['xp_next']
    xp_percent = round((xp_current / xp_next) * 100, 1) if xp_next else 0

    site_logo_url = static('images/Logo.png')

    context = {
        'username':           username,
        'role':               role,
        'profile_image':      'images/default_profile.png',
        'site_logo_url':      site_logo_url,

        # Level / XP
        'agent_level':        stats['agent_level'],
        'xp_current':         xp_current,
        'xp_next':            xp_next,
        'xp_percent':         xp_percent,

        # Performance stats
        'accuracy':           stats['accuracy'],
        'safe_count':         stats['safe_count'],
        'fail_count':         stats['fail_count'],
        'avg_time':           stats['avg_time'],

        # Agent status panel
        'missions_completed': stats['missions_completed'],
        'total_score':        stats['total_score'],
        'detection_skill':    stats['detection_skill'],
        'speed_rating':       stats['speed_rating'],

        # Activity feed
        'recent_activity':    stats['recent_activity'],
    }

    response = render(request, 'homepage/Home.html', context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma']        = 'no-cache'
    response['Expires']       = '0'
    return response


def _get_placeholder_stats():
    """
    Safe defaults for a brand-new agent.
    Replace with real DB calls once game tables exist.
    """
    return {
        'agent_level':        1,
        'xp_current':         0,
        'xp_next':            1000,
        'accuracy':           0,
        'safe_count':         0,
        'fail_count':         0,
        'avg_time':           '—',
        'missions_completed': 0,
        'total_score':        0,
        'detection_skill':    0,
        'speed_rating':       0,
        'recent_activity': [
            {
                'message': 'Agent account activated. Welcome to PhishGuard.',
                'time':    'NOW',
                'color':   'green',
            },
            {
                'message': 'No missions completed yet. Start with EMAIL DETECTOR.',
                'time':    '—',
                'color':   'cyan',
            },
        ],
    }