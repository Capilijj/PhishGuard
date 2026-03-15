"""
URL configuration for PhishGuard project.
"""

from django.urls import path
from .views import (
    home_view, login_view, logout_view,
    register_view, forgot_password_view,
    check_codename_view, check_email_mx_view, terms_view,
    verify_email_view, verify_pending_view, resend_verification_view,
    forgot_pending_view, forgot_resend_view,
    reset_password_view,
)

urlpatterns = [
    path('',                    login_view,                name='login'),
    path('register/',           register_view,             name='register'),
    path('home/',               home_view,                 name='home'),
    path('logout/',             logout_view,               name='logout'),
    path('check-codename/',     check_codename_view,       name='check_codename'),
    path('check-email-mx/',     check_email_mx_view,       name='check_email_mx'),
    path('terms/',              terms_view,                name='terms'),

    # ── Forgot Password ────────────────────────────────────────
    path('forgot/',             forgot_password_view,      name='forgot_password'),
    path('forgot/pending/',     forgot_pending_view,       name='forgot_pending'),
    path('forgot/resend/',      forgot_resend_view,        name='forgot_resend'),

    path('reset/',              reset_password_view,       name='reset_password'),

    path('reset/',             reset_password_view,       name='reset_password'),

    # ── Email Verification ─────────────────────────────────────
    path('verify/',             verify_email_view,         name='verify_email'),
    path('verify/pending/',     verify_pending_view,       name='verify_pending'),
    path('verify/resend/',      resend_verification_view,  name='verify_resend'),
]