# =============================================================
#  media_manager/db_helpers.py
#  All DB queries for site_settings and image uploads.
#  Never call connection.cursor() outside this file.
# =============================================================

from django.db import connection


# ── site_settings queries ─────────────────────────────────────
#
#  Table schema (create this in SQL Server):
#
#  CREATE TABLE site_settings (
#      id          INT IDENTITY(1,1) PRIMARY KEY,
#      setting_key NVARCHAR(100) NOT NULL UNIQUE,
#      value       NVARCHAR(MAX) NULL,
#      updated_at  DATETIME DEFAULT GETDATE()
#  );
#
#  Default rows:
#  INSERT INTO site_settings (setting_key, value)
#  VALUES ('site_logo_url', ''), ('site_name', 'PhishGuard');


def get_site_setting(key):
    """
    Fetch a single setting value by key.
    Returns the value string or None if not found.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT value FROM site_settings WHERE setting_key = %s",
            [key]
        )
        row = cursor.fetchone()
    return row[0] if row else None


def get_all_site_settings():
    """
    Fetch all settings as a dict {key: value}.
    Useful for the admin settings panel.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT setting_key, value FROM site_settings")
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}


def set_site_setting(key, value):
    """
    Upsert a setting (insert if not exists, update if exists).
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM site_settings WHERE setting_key = %s",
            [key]
        )
        exists = cursor.fetchone()[0]

        if exists:
            cursor.execute(
                "UPDATE site_settings "
                "SET value = %s, updated_at = GETDATE() "
                "WHERE setting_key = %s",
                [value, key]
            )
        else:
            cursor.execute(
                "INSERT INTO site_settings (setting_key, value) "
                "VALUES (%s, %s)",
                [key, value]
            )


# ── image_uploads queries ─────────────────────────────────────
#
#  Table schema (create this in SQL Server):
#
#  CREATE TABLE image_uploads (
#      id           INT IDENTITY(1,1) PRIMARY KEY,
#      uploader_id  INT NOT NULL,             -- auth_user.id
#      filename     NVARCHAR(255) NOT NULL,
#      file_path    NVARCHAR(500) NOT NULL,   -- relative path under MEDIA_ROOT
#      file_size    INT NULL,                 -- bytes
#      uploaded_at  DATETIME DEFAULT GETDATE(),
#      purpose      NVARCHAR(100) NULL        -- e.g. 'site_logo', 'profile_pic'
#  );


def save_image_record(uploader_id, filename, file_path, file_size, purpose):
    """
    Insert an image upload record and return its new ID.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO image_uploads "
            "(uploader_id, filename, file_path, file_size, purpose) "
            "VALUES (%s, %s, %s, %s, %s)",
            [uploader_id, filename, file_path, file_size, purpose]
        )
        cursor.execute("SELECT SCOPE_IDENTITY()")
        row = cursor.fetchone()
    return int(row[0]) if row else None


def get_image_by_purpose(purpose):
    """
    Get the most recent image record for a given purpose.
    Returns a dict or None.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT TOP 1 id, filename, file_path, uploaded_at "
            "FROM image_uploads "
            "WHERE purpose = %s "
            "ORDER BY uploaded_at DESC",
            [purpose]
        )
        row = cursor.fetchone()

    if row:
        return {
            'id':          row[0],
            'filename':    row[1],
            'file_path':   row[2],
            'uploaded_at': row[3],
        }
    return None


def get_all_images(purpose=None):
    """
    Get all image records, optionally filtered by purpose.
    Returns a list of dicts.
    """
    with connection.cursor() as cursor:
        if purpose:
            cursor.execute(
                "SELECT id, uploader_id, filename, file_path, "
                "file_size, uploaded_at, purpose "
                "FROM image_uploads WHERE purpose = %s "
                "ORDER BY uploaded_at DESC",
                [purpose]
            )
        else:
            cursor.execute(
                "SELECT id, uploader_id, filename, file_path, "
                "file_size, uploaded_at, purpose "
                "FROM image_uploads ORDER BY uploaded_at DESC"
            )
        rows = cursor.fetchall()

    return [
        {
            'id':          r[0],
            'uploader_id': r[1],
            'filename':    r[2],
            'file_path':   r[3],
            'file_size':   r[4],
            'uploaded_at': r[5],
            'purpose':     r[6],
        }
        for r in rows
    ]