# =============================================================
#  tokens.py
#  Token generation for both email verification and reset.
#  Both stored in email_verifications with different type values.
# =============================================================

import secrets
from datetime import timedelta

from django.utils import timezone

from .db_helpers import create_token


TOKEN_EXPIRY_HOURS = 24


def generate_and_store_token(user_id):
    """
    Generate a verification token (type='verify').
    Stored in email_verifications.
    Returns: token string (~64 URL-safe chars)
    """
    token      = secrets.token_urlsafe(48)
    expires_at = timezone.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    create_token(user_id, token, expires_at, token_type='verify')
    return token


def generate_and_store_reset_token(user_id):
    """
    Generate a password reset token (type='reset').
    Stored in email_verifications.
    Returns: token string (~64 URL-safe chars)
    """
    token      = secrets.token_urlsafe(48)
    expires_at = timezone.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
    create_token(user_id, token, expires_at, token_type='reset')
    return token