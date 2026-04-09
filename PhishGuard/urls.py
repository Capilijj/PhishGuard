"""
URL configuration for PhishGuard project.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    login_view, logout_view,
    register_view, forgot_password_view,
    check_codename_view, check_email_mx_view, terms_view,
    verify_email_view, verify_pending_view, resend_verification_view,
    forgot_pending_view, forgot_resend_view,
    reset_password_view,
)

urlpatterns = [

    # ── Auth ───────────────────────────────────────────────────
    path('',                login_view,               name='login'),
    path('register/',       register_view,             name='register'),
    path('logout/',         logout_view,               name='logout'),
    path('check-codename/', check_codename_view,       name='check_codename'),
    path('check-email-mx/', check_email_mx_view,       name='check_email_mx'),
    path('terms/',          terms_view,                name='terms'),

    # ── Forgot / Reset Password ────────────────────────────────
    path('forgot/',         forgot_password_view,      name='forgot_password'),
    path('forgot/pending/', forgot_pending_view,       name='forgot_pending'),
    path('forgot/resend/',  forgot_resend_view,        name='forgot_resend'),
    path('reset/',          reset_password_view,       name='reset_password'),

    # ── Email Verification ─────────────────────────────────────
    path('verify/',         verify_email_view,         name='verify_email'),
    path('verify/pending/', verify_pending_view,       name='verify_pending'),
    path('verify/resend/',  resend_verification_view,  name='verify_resend'),

    # ── Apps ───────────────────────────────────────────────────
    path('',            include('homepage.urls')),
    path('admin/',      include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)