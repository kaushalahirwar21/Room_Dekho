"""
TEMPORARY MAINTENANCE APP

This app provides a one-time endpoint for running database migrations
on platforms like Vercel that don't support manage.py commands directly.

⚠️  DELETE THIS APP AFTER USE - It is only needed for initial setup.
"""

from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'
