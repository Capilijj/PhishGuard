# =============================================================
#  db_helpers.py
#  All raw SQL / stored procedure calls in one place.
#  views.py should never call connection.cursor() directly.
#
#  email_verifications table handles both:
#    type = 'verify' — email verification tokens
#    type = 'reset'  — password reset tokens
# =============================================================

from django.db import connection
from django.utils import timezone


# ── auth_user queries ─────────────────────────────────────────

def get_user_by_username(username):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, password, role, is_active "
            "FROM auth_user WHERE username = %s",
            [username]
        )
        row = cursor.fetchone()

    if row:
        return {
            'id':        row[0],
            'username':  row[1],
            'email':     row[2],
            'password':  row[3],
            'role':      row[4],
            'is_active': row[5],
        }
    return None


def get_user_by_id(user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, email, password, role, is_active "
            "FROM auth_user WHERE id = %s",
            [user_id]
        )
        row = cursor.fetchone()

    if row:
        return {
            'id':        row[0],
            'username':  row[1],
            'email':     row[2],
            'password':  row[3],
            'role':      row[4],
            'is_active': row[5],
        }
    return None


def get_user_by_email(email):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, is_active "
            "FROM auth_user WHERE email = %s",
            [email]
        )
        row = cursor.fetchone()

    if row:
        return {
            'id':        row[0],
            'username':  row[1],
            'is_active': row[2],
        }
    return None


def activate_user(user_id):
    """Set is_active = 1 for the given user."""
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE auth_user SET is_active = 1 WHERE id = %s",
            [user_id]
        )


def update_user_password(user_id, hashed_password):
    """Directly update auth_user.password — no SP needed."""
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE auth_user SET password = %s WHERE id = %s",
            [hashed_password, user_id]
        )


# ── Stored procedures ─────────────────────────────────────────

def call_sp_register_agent(username, email, hashed_password, role='Player'):
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC sp_RegisterAgent "
            "@p_username=%s, @p_email=%s, @p_password=%s, @p_role=%s",
            [username, email, hashed_password, role]
        )


def call_sp_reregister_agent(username, email, hashed_password):
    """
    Calls sp_ReRegisterAgent.
    Used when email exists but account is unverified (is_active=0).
    Updates credentials and resets for re-verification.
    Raises on error (e.g. account already active, username taken).
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC sp_ReRegisterAgent "
            "@p_username=%s, @p_email=%s, @p_password=%s",
            [username, email, hashed_password]
        )


def get_unverified_user_by_email(email):
    """
    Returns user dict if email exists and is_active = 0.
    Returns None if email doesn't exist or account is already active.
    Used to detect expired-unverified accounts during registration.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, username, is_active "
            "FROM auth_user WHERE email = %s AND is_active = 0",
            [email]
        )
        row = cursor.fetchone()

    if row:
        return {
            'id':        row[0],
            'username':  row[1],
            'is_active': row[2],
        }
    return None


def call_sp_check_email(email):
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC sp_CheckEmailExists @p_email=%s",
            [email]
        )
        row = cursor.fetchone()

    return bool(row and row[0] == 1)


# ── email_verifications queries ───────────────────────────────
#  type = 'verify' → email verification
#  type = 'reset'  → password reset

def create_token(user_id, token, expires_at, token_type):
    """
    Invalidate old unused tokens of the same type,
    then insert the new one.
    token_type: 'verify' or 'reset'
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE email_verifications SET is_used = 1 "
            "WHERE user_id = %s AND type = %s AND is_used = 0",
            [user_id, token_type]
        )
        cursor.execute(
            "INSERT INTO email_verifications "
            "(user_id, token, expires_at, is_used, type) "
            "VALUES (%s, %s, %s, 0, %s)",
            [user_id, token, expires_at, token_type]
        )


def get_valid_token_row(token, token_type):
    """
    Look up a token of a given type in email_verifications.
    Returns {'id', 'user_id'} if valid, unused, not expired.
    Returns None otherwise.
    token_type: 'verify' or 'reset'
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, user_id, expires_at, is_used "
            "FROM email_verifications "
            "WHERE token = %s AND type = %s",
            [token, token_type]
        )
        row = cursor.fetchone()

    if not row:
        return None

    token_id, user_id, expires_at, is_used = row

    if is_used:
        return None

    now = timezone.now()
    exp = timezone.make_aware(expires_at) if expires_at.tzinfo is None else expires_at
    if now > exp:
        return None

    return {'id': token_id, 'user_id': user_id}


def mark_token_used(token_id):
    """Mark a token as consumed."""
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE email_verifications SET is_used = 1 WHERE id = %s",
            [token_id]
        )