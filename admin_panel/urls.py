# =============================================================
#  admin_panel/urls.py
# =============================================================

from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard_view, name='admin_dashboard'),
]