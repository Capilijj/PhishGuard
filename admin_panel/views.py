# =============================================================
#  admin_panel/views.py
#  Admin-only views. Guarded by admin_required decorator.
# =============================================================

from django.shortcuts import render, redirect


def admin_required(view_fn):
    """Block non-superadmins — redirect to home."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        if request.session.get('role', '').lower() != 'superadmin':
            return redirect('home')
        return view_fn(request, *args, **kwargs)
    wrapper.__name__ = view_fn.__name__
    return wrapper


@admin_required
def admin_dashboard_view(request):
    """
    Admin overview dashboard.
    Context variables for AdminDashboard.html:
      total_users       — total registered agents
      active_users      — agents active today
      total_simulations — total simulations run
      open_inquiries    — pending inquiry tickets
      bar_labels        — JSON list of day labels for bar chart
      bar_data          — JSON list of simulation counts per day
      line_labels       — JSON list of week labels for line chart
      line_data         — JSON list of registration counts per week
      recent_activity   — list of dicts:
                          {username, action, mission, result, time}
    """

    # ── Pull from DB (replace with real queries later) ─────────
    # Example:
    #   from .db_helpers import get_admin_overview
    #   stats = get_admin_overview()

    import json

    stats = _get_placeholder_admin_stats()

    context = {
        'username':          request.session.get('username', 'ADMIN'),
        'role':              request.session.get('role', 'Admin'),

        # Overview cards
        'total_users':       stats['total_users'],
        'active_users':      stats['active_users'],
        'total_simulations': stats['total_simulations'],
        'open_inquiries':    stats['open_inquiries'],

        # Chart data — passed as JSON strings for Chart.js
        'bar_labels':        json.dumps(stats['bar_labels']),
        'bar_data':          json.dumps(stats['bar_data']),
        'line_labels':       json.dumps(stats['line_labels']),
        'line_data':         json.dumps(stats['line_data']),

        # Recent activity table
        'recent_activity':   stats['recent_activity'],
    }

    response = render(request, 'admin_panel/AdminDashboard.html', context)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma']        = 'no-cache'
    response['Expires']       = '0'
    return response


@admin_required
def admin_settings_view(request):
    """Site settings placeholder page."""
    return render(request, 'admin_panel/AdminSettings.html', {
        'username': request.session.get('username', 'ADMIN'),
        'role':     request.session.get('role', 'Admin'),
    })


def _get_placeholder_admin_stats():
    """Safe defaults — replace with real DB calls."""
    return {
        'total_users':       0,
        'active_users':      0,
        'total_simulations': 0,
        'open_inquiries':    0,

        'bar_labels': ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'],
        'bar_data':   [0, 0, 0, 0, 0, 0, 0],

        'line_labels': ['WK1', 'WK2', 'WK3', 'WK4'],
        'line_data':   [0, 0, 0, 0],

        'recent_activity': [],
    }