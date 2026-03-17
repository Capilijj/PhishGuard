# =============================================================
#  media_manager/views.py
#  Handles image uploads and admin site settings.
#  Only admins (role='Admin') can access these views.
# =============================================================

import os
import uuid

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

from .db_helpers import (
    save_image_record,
    get_image_by_purpose,
    get_all_images,
    get_all_site_settings,
    set_site_setting,
)


# ── Allowed image types ───────────────────────────────────────
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE_MB   = 5
MAX_FILE_SIZE_B    = MAX_FILE_SIZE_MB * 1024 * 1024


# ── Admin guard decorator ─────────────────────────────────────
def admin_required(view_fn):
    """Redirect non-admin users to home."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        if request.session.get('role', '').lower() != 'admin':
            return redirect('home')
        return view_fn(request, *args, **kwargs)
    return wrapper


# =============================================================
#  UPLOAD IMAGE
#  POST /media/upload/
#  Accepts: multipart/form-data with 'image' + 'purpose' fields
#  Returns: JSON {success, url, error}
# =============================================================

@admin_required
def upload_image_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    image_file = request.FILES.get('image')
    purpose    = request.POST.get('purpose', 'general').strip().lower()

    # ── Validate ───────────────────────────────────────────────
    if not image_file:
        return JsonResponse({'success': False, 'error': 'No image file provided.'})

    ext = image_file.name.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({
            'success': False,
            'error': f'File type .{ext} not allowed. Use: {", ".join(ALLOWED_EXTENSIONS)}'
        })

    if image_file.size > MAX_FILE_SIZE_B:
        return JsonResponse({
            'success': False,
            'error': f'File too large. Maximum size is {MAX_FILE_SIZE_MB}MB.'
        })

    # ── Save file ──────────────────────────────────────────────
    try:
        # Generate unique filename to avoid collisions
        unique_name = f'{purpose}_{uuid.uuid4().hex[:12]}.{ext}'
        upload_dir  = os.path.join(settings.MEDIA_ROOT, 'uploads', purpose)
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, unique_name)
        with open(file_path, 'wb+') as dest:
            for chunk in image_file.chunks():
                dest.write(chunk)

        # Relative path for DB storage and URL generation
        relative_path = f'uploads/{purpose}/{unique_name}'
        media_url     = f'{settings.MEDIA_URL}{relative_path}'

        # ── Save to DB ─────────────────────────────────────────
        uploader_id = request.session['user_id']
        save_image_record(
            uploader_id = uploader_id,
            filename    = image_file.name,
            file_path   = relative_path,
            file_size   = image_file.size,
            purpose     = purpose,
        )

        # ── If this is a logo upload, update site_settings too ─
        if purpose == 'site_logo':
            set_site_setting('site_logo_url', media_url)

        return JsonResponse({
            'success': True,
            'url':     media_url,
            'path':    relative_path,
        })

    except Exception as e:
        print(f'[upload_image_view ERROR] {e}')
        return JsonResponse({'success': False, 'error': 'Upload failed. Please try again.'})


# =============================================================
#  ADMIN SETTINGS PANEL
#  GET  /media/settings/   — show settings form
#  POST /media/settings/   — save a setting
# =============================================================

@admin_required
def admin_settings_view(request):
    message = ''
    error   = ''

    if request.method == 'POST':
        action = request.POST.get('action', '')

        # ── Update a text setting ──────────────────────────────
        if action == 'update_setting':
            key   = request.POST.get('key', '').strip()
            value = request.POST.get('value', '').strip()
            if key:
                set_site_setting(key, value)
                message = f'Setting "{key}" updated successfully.'
            else:
                error = 'Setting key cannot be empty.'

        # ── Upload logo via form (non-AJAX fallback) ───────────
        elif action == 'upload_logo':
            image_file = request.FILES.get('logo_image')
            if not image_file:
                error = 'No image selected.'
            else:
                ext = image_file.name.rsplit('.', 1)[-1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    error = f'File type .{ext} not allowed.'
                elif image_file.size > MAX_FILE_SIZE_B:
                    error = f'File too large. Max {MAX_FILE_SIZE_MB}MB.'
                else:
                    try:
                        unique_name = f'site_logo_{uuid.uuid4().hex[:12]}.{ext}'
                        upload_dir  = os.path.join(settings.MEDIA_ROOT, 'uploads', 'site_logo')
                        os.makedirs(upload_dir, exist_ok=True)

                        file_path = os.path.join(upload_dir, unique_name)
                        with open(file_path, 'wb+') as dest:
                            for chunk in image_file.chunks():
                                dest.write(chunk)

                        relative_path = f'uploads/site_logo/{unique_name}'
                        media_url     = f'{settings.MEDIA_URL}{relative_path}'

                        save_image_record(
                            uploader_id = request.session['user_id'],
                            filename    = image_file.name,
                            file_path   = relative_path,
                            file_size   = image_file.size,
                            purpose     = 'site_logo',
                        )
                        set_site_setting('site_logo_url', media_url)
                        message = 'Logo updated successfully.'

                    except Exception as e:
                        print(f'[admin_settings_view ERROR] {e}')
                        error = 'Upload failed. Please try again.'

    # ── Build context ──────────────────────────────────────────
    current_settings = get_all_site_settings()
    current_logo     = get_image_by_purpose('site_logo')
    all_images       = get_all_images()

    return render(request, 'media_manager/AdminSettings.html', {
        'settings':    current_settings,
        'logo':        current_logo,
        'all_images':  all_images,
        'message':     message,
        'error':       error,
        'username':    request.session.get('username'),
        'role':        request.session.get('role'),
    })