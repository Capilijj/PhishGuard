# =============================================================
#  views.py
#  Request → Response logic ONLY.
#  No raw SQL, no send_mail, no token secrets here.
#
#  Imports:
#    db_helpers.py  — all database queries
#    tokens.py      — token generation
#    emails.py      — all outgoing email
# =============================================================

import random

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password

import dns.resolver

from .db_helpers import (
    get_user_by_username,
    get_user_by_email,
    activate_user,
    update_user_password,
    call_sp_register_agent,
    call_sp_check_email,
    get_valid_token_row,
    mark_token_used,
)
from .tokens import generate_and_store_token, generate_and_store_reset_token
from .emails import send_verification_email, send_password_reset_email


# =============================================================
#  EMAIL MX VALIDATOR
# =============================================================

_KNOWN_VALID_DOMAINS = frozenset([
    'gmail.com', 'yahoo.com', 'yahoo.com.ph', 'ymail.com',
    'outlook.com', 'hotmail.com', 'hotmail.com.ph',
    'live.com', 'msn.com', 'icloud.com', 'me.com',
    'protonmail.com', 'proton.me', 'zoho.com',
])


def is_valid_email_domain(email):
    try:
        domain = email.split('@')[1].strip().lower()
    except IndexError:
        return False

    if domain in _KNOWN_VALID_DOMAINS:
        return True

    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        resolver.timeout     = 3
        resolver.lifetime    = 5
        resolver.resolve(domain, 'MX')
        return True
    except (dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
            Exception):
        return False


# =============================================================
#  HOME
# =============================================================

def home_view(request):
    if not request.session.get('user_id'):
        return redirect('login')

    response = render(request, 'homepage/Home.html', {
        'username': request.session.get('username'),
        'role':     request.session.get('role'),
    })
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma']        = 'no-cache'
    response['Expires']       = '0'
    return response


# =============================================================
#  LOGIN
# =============================================================

def login_view(request):
    if request.session.get('user_id'):
        return redirect('home')

    error   = ''
    message = request.GET.get('message', '')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username:
            error = 'FIELD ERROR: Agent codename cannot be empty.'
        elif not password:
            error = 'FIELD ERROR: Security code cannot be empty.'
        else:
            user = get_user_by_username(username)

            if user is None:
                error = (
                    'ACCESS DENIED: Agent codename not recognised. '
                    'Check your codename or create an account.'
                )
            elif not user['is_active']:
                error = (
                    'ACCESS DENIED: Account not yet verified. '
                    'Check your email for the verification link.'
                )
            else:
                if check_password(password, user['password']):
                    request.session['user_id']  = user['id']
                    request.session['username'] = user['username']
                    request.session['role']     = user['role']
                    return redirect('home')
                else:
                    error = 'ACCESS DENIED: Incorrect security code.'

    return render(request, 'Login/Login.html', {
        'error':   error,
        'message': message,
    })


# =============================================================
#  REGISTER
# =============================================================

def register_view(request):
    if request.session.get('user_id'):
        return redirect('home')

    if request.method == 'POST':
        username         = request.POST.get('new_agent', '').strip()
        email            = request.POST.get('new_email', '').strip()
        password         = request.POST.get('new_code', '')
        confirm_password = request.POST.get('confirm_code', '')

        form_data = {'new_agent': username, 'new_email': email}

        if not username:
            return render(request, 'Login/Register.html', {
                'error': 'SECURITY ERROR: Codename is required.',
                'form_data': form_data,
            })

        if len(username) < 3:
            return render(request, 'Login/Register.html', {
                'error': 'SECURITY ERROR: Codename must be at least 3 characters.',
                'form_data': form_data,
            })

        if not email or '@' not in email:
            return render(request, 'Login/Register.html', {
                'error': 'SECURITY ERROR: A valid email address is required.',
                'form_data': form_data,
            })

        if not password or len(password) < 8:
            return render(request, 'Login/Register.html', {
                'error': 'SECURITY ERROR: Security code must be at least 8 characters.',
                'form_data': form_data,
            })

        if password != confirm_password:
            return render(request, 'Login/Register.html', {
                'error': 'SECURITY ERROR: Security codes do not match.',
                'form_data': form_data,
            })

        if get_user_by_username(username):
            return render(request, 'Login/Register.html', {
                'error': 'CREATE ACCOUNT FAILED: Codename already active in the system.',
                'form_data': form_data,
            })

        if call_sp_check_email(email):
            return render(request, 'Login/Register.html', {
                'error': 'CREATE ACCOUNT FAILED: Email already registered to another agent.',
                'form_data': form_data,
            })

        try:
            call_sp_register_agent(username, email, make_password(password))
            user  = get_user_by_username(username)
            token = generate_and_store_token(user['id'])
            send_verification_email(request, email, username, token)
            return redirect(f'/verify/pending/?email={email}')

        except Exception as e:
            print(f'[register_view ERROR] {e}')
            err_msg = str(e)

            if 'already active' in err_msg:
                error = 'CREATE ACCOUNT FAILED: Codename already active in the system.'
            elif 'already registered' in err_msg:
                error = 'CREATE ACCOUNT FAILED: Email already registered to another agent.'
            else:
                error = 'SYSTEM ERROR: CREATE ACCOUNT protocol failed. Please try again.'

            return render(request, 'Login/Register.html', {
                'error': error,
                'form_data': form_data,
            })

    return render(request, 'Login/Register.html', {})


# =============================================================
#  EMAIL VERIFICATION
#  GET /verify/?token=<token>
# =============================================================

def verify_email_view(request):
    token = request.GET.get('token', '').strip()

    if not token:
        return render(request, 'Login/VerifyEmail.html', {
            'status':  'invalid',
            'message': 'VERIFICATION FAILED: No token provided.',
        })

    row = get_valid_token_row(token, 'verify')

    if row is None:
        return render(request, 'Login/VerifyEmail.html', {
            'status':  'invalid',
            'message': (
                'VERIFICATION FAILED: This link is invalid, already used, or has expired. '
                'Please register again or request a new verification link.'
            ),
        })

    activate_user(row['user_id'])
    mark_token_used(row['id'])

    return render(request, 'Login/VerifyEmail.html', {
        'status':  'success',
        'message': 'ACCOUNT VERIFIED. You may now log in, Agent.',
    })


# =============================================================
#  VERIFY PENDING
#  GET /verify/pending/
# =============================================================

def verify_pending_view(request):
    email  = request.GET.get('email', '')
    masked = _mask_email(email)
    return render(request, 'Login/VerifyPending.html', {
        'masked_email': masked,
    })


# =============================================================
#  RESEND VERIFICATION
#  POST /verify/resend/
# =============================================================

def resend_verification_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            return render(request, 'Login/VerifyPending.html', {
                'error':        'FIELD ERROR: Email address is required.',
                'masked_email': '',
            })

        user = get_user_by_email(email)

        generic_msg = (
            'TRANSMISSION SENT. If that email is registered and unverified, '
            'a new link is on its way.'
        )

        if not user:
            return render(request, 'Login/VerifyPending.html', {
                'message':      generic_msg,
                'masked_email': '',
            })

        if user['is_active']:
            return redirect('/?message=ACCOUNT+ALREADY+VERIFIED.+Please+log+in.')

        token = generate_and_store_token(user['id'])
        send_verification_email(request, email, user['username'], token)

        masked = _mask_email(email)
        return render(request, 'Login/VerifyPending.html', {
            'message':      f'NEW LINK TRANSMITTED TO: {masked}',
            'masked_email':  masked,
        })

    return render(request, 'Login/VerifyPending.html', {'masked_email': ''})


# =============================================================
#  FORGOT PASSWORD
#  POST /forgot/
# =============================================================

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('forgot_email', '').strip()

        if not email:
            return render(request, 'Login/ForgotPassword.html', {
                'error': 'FIELD ERROR: Email address is required.',
            })

        if '@' not in email or '.' not in email.split('@')[-1]:
            return render(request, 'Login/ForgotPassword.html', {
                'error': 'FIELD ERROR: Enter a valid email address.',
            })

        if not is_valid_email_domain(email):
            return render(request, 'Login/ForgotPassword.html', {
                'error': 'FIELD ERROR: Email domain does not exist. Use a real email address.',
            })

        user = get_user_by_email(email)

        if not user or not user['is_active']:
            return render(request, 'Login/ForgotPassword.html', {
                'error': 'RESET FAILED: No active agent account found with that email address.',
            })

        token = generate_and_store_reset_token(user['id'])
        send_password_reset_email(request, email, user['username'], token)

        return redirect(f'/forgot/pending/?email={email}')

    return render(request, 'Login/ForgotPassword.html', {})


# =============================================================
#  FORGOT PENDING
#  GET /forgot/pending/
# =============================================================

def forgot_pending_view(request):
    email  = request.GET.get('email', '')
    masked = _mask_email(email)
    return render(request, 'Login/ForgotPending.html', {
        'masked_email': masked,
        'message': f'RESET LINK TRANSMITTED TO: {masked}' if masked else '',
    })


# =============================================================
#  FORGOT RESEND
#  POST /forgot/resend/
# =============================================================

def forgot_resend_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        if not email:
            return render(request, 'Login/ForgotPending.html', {
                'error':        'FIELD ERROR: Email address is required.',
                'masked_email': '',
            })

        user = get_user_by_email(email)

        generic_msg = (
            'TRANSMISSION SENT. If that email is registered and active, '
            'a new reset link is on its way.'
        )

        if not user or not user['is_active']:
            return render(request, 'Login/ForgotPending.html', {
                'message':      generic_msg,
                'masked_email': '',
            })

        token = generate_and_store_reset_token(user['id'])
        send_password_reset_email(request, email, user['username'], token)

        masked = _mask_email(email)
        return render(request, 'Login/ForgotPending.html', {
            'message':      f'NEW LINK TRANSMITTED TO: {masked}',
            'masked_email':  masked,
        })

    return render(request, 'Login/ForgotPending.html', {'masked_email': ''})


# =============================================================
#  RESET PASSWORD
#  GET  /reset/?token=<token>  — show form
#  POST /reset/?token=<token>  — save new password
# =============================================================

def reset_password_view(request):
    token = request.GET.get('token', '').strip()

    if not token:
        return render(request, 'Login/ResetPassword.html', {
            'status':  'invalid',
            'message': 'RESET FAILED: No token provided.',
        })

    row = get_valid_token_row(token, 'reset')

    if row is None:
        return render(request, 'Login/ResetPassword.html', {
            'status':  'invalid',
            'message': (
                'RESET FAILED: This link is invalid, already used, or has expired. '
                'Please request a new reset link.'
            ),
        })

    if request.method == 'POST':
        password         = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not password or len(password) < 8:
            return render(request, 'Login/ResetPassword.html', {
                'status': 'form',
                'token':  token,
                'error':  'SECURITY ERROR: Password must be at least 8 characters.',
            })

        if password != confirm_password:
            return render(request, 'Login/ResetPassword.html', {
                'status': 'form',
                'token':  token,
                'error':  'SECURITY ERROR: Passwords do not match.',
            })

        update_user_password(row['user_id'], make_password(password))
        mark_token_used(row['id'])

        return render(request, 'Login/ResetPassword.html', {
            'status':  'success',
            'message': 'PASSWORD UPDATED. You may now log in with your new security code.',
        })

    return render(request, 'Login/ResetPassword.html', {
        'status': 'form',
        'token':  token,
    })


# =============================================================
#  LOGOUT
# =============================================================

def logout_view(request):
    request.session.flush()
    return redirect('login')


# =============================================================
#  CHECK CODENAME — AJAX
#  GET /check-codename/?codename=GHOST_ACE
# =============================================================

_PREFIXES = [
    'ALPHA', 'BETA', 'DELTA', 'ECHO', 'FOXTROT', 'GHOST',
    'HAWK', 'IRON', 'JADE', 'KILO', 'LUNA', 'MAVERICK',
    'NOVA', 'OMEGA', 'PHANTOM', 'RAVEN', 'SHADOW', 'STORM',
    'TITAN', 'ULTRA', 'VIPER', 'WOLF', 'ZERO', 'CIPHER',
    'NEXUS', 'PIXEL', 'QUANTUM', 'RECON', 'SPECTRE', 'VECTOR',
]

_SUFFIXES = [
    'ONE', 'TWO', 'SIX', 'NINE', 'ACE', 'REX',
    'MAX', 'PRO', 'X', 'PRIME', 'ELITE', 'FORCE',
    'STRIKE', 'BLADE', 'CORE', 'SURGE', 'FLUX', 'PULSE',
]


def _generate_codename():
    style = random.randint(1, 3)
    if style == 1:
        return random.choice(_PREFIXES) + '_' + random.choice(_SUFFIXES)
    elif style == 2:
        return random.choice(_PREFIXES) + str(random.randint(1, 99))
    else:
        return random.choice(_PREFIXES) + '_' + str(random.randint(10, 99))


def check_codename_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET only'}, status=405)

    codename = request.GET.get('codename', '').strip()
    if not codename:
        return JsonResponse({'error': 'Codename is required'}, status=400)

    is_available = get_user_by_username(codename) is None

    suggestions = []
    attempts    = 0
    while len(suggestions) < 3 and attempts < 30:
        candidate = _generate_codename()
        if get_user_by_username(candidate) is None and candidate not in suggestions:
            suggestions.append(candidate)
        attempts += 1

    return JsonResponse({'available': is_available, 'suggestions': suggestions})


# =============================================================
#  CHECK EMAIL MX — AJAX
#  GET /check-email-mx/?email=agent@gmail.com
# =============================================================

def check_email_mx_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET only'}, status=405)

    email = request.GET.get('email', '').strip()
    if not email or '@' not in email:
        return JsonResponse({'valid': False, 'message': 'Invalid email format.'})

    domain   = email.split('@')[1].strip().lower()
    is_valid = is_valid_email_domain(email)

    return JsonResponse({
        'valid':   is_valid,
        'domain':  domain,
        'message': (
            f'✔ {domain} is a valid email domain.'
            if is_valid else
            f'✗ {domain} does not appear to be a real email domain.'
        ),
    })


# =============================================================
#  TERMS OF SERVICE
# =============================================================

def terms_view(request):
    return render(request, 'Login/TermsOfService.html')


# =============================================================
#  PRIVATE HELPERS
# =============================================================

def _mask_email(email):
    """agent@gmail.com  →  A****@GMAIL.COM"""
    if not email or '@' not in email:
        return ''
    at = email.index('@')
    return (email[0] + '*' * (at - 1) + email[at:]).upper()