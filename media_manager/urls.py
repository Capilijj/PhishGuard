# =============================================================
#  media_manager/urls.py
# =============================================================

from django.urls import path
from . import views

urlpatterns = [
    path('upload/',   views.upload_image_view,   name='media_upload'),
    path('settings/', views.admin_settings_view, name='admin_settings'),
]