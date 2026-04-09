# =============================================================
#  admin_panel/urls.py
# =============================================================

from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
    path('settings/', views.admin_settings_view, name='admin_settings'),
]