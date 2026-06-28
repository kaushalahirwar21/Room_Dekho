"""
TEMPORARY VIEW: One-time migration endpoint.

This view allows running `python manage.py migrate` via HTTP.
It is intended ONLY for initial deployment on platforms like Vercel
where CLI access is not available.

SECURITY:
- Requires MIGRATION_SECRET token via ?token= query parameter
- Disables itself after first successful run by creating a flag file
- DELETE THIS ENDPOINT AFTER USE

Usage: GET /__/migrate/?token=your_secret_token
"""

import os
import sys
import io
from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from pathlib import Path


# Flag file to mark that migrations have been run
MIGRATION_FLAG_FILE = Path(settings.BASE_DIR) / '.migration_complete'


@method_decorator(csrf_exempt, name='dispatch')
class RunMigrationsView(View):
    """
    One-time endpoint to run database migrations.
    """
    
    def get(self, request, *args, **kwargs):
        # Verify token
        token = request.GET.get('token')
        expected_token = os.getenv('MIGRATION_SECRET')
        
        if not expected_token:
            return HttpResponseServerError(
                "MIGRATION_SECRET environment variable not set.",
                content_type='text/plain'
            )
        
        if token != expected_token:
            return HttpResponseForbidden(
                "Invalid token.",
                content_type='text/plain'
            )
        
        # Check if already run
        if MIGRATION_FLAG_FILE.exists():
            return HttpResponse(
                "Migrations already executed. This is a one-time endpoint.\n"
                "Delete the .migration_complete file to re-run (not recommended).",
                content_type='text/plain',
                status=410  # Gone
            )
        
        # Run migrations
        try:
            # Capture output
            out = io.StringIO()
            sys.stdout = out
            
            call_command('migrate', '--noinput')
            
            sys.stdout = sys.__stdout__
            output = out.getvalue()
            
            # Create flag file to prevent re-use
            MIGRATION_FLAG_FILE.touch(exist_ok=True)
            
            # Also create .env entry reminder
            response_text = (
                "✅ Migrations completed successfully!\n\n"
                "=== Migration Output ===\n"
                f"{output}\n"
                "=== Important ===\n"
                "This endpoint has now disabled itself. "
                "For security, DELETE the 'maintenance' app from your project "
                "and remove the URL pattern after confirming migrations work.\n"
                "The MIGRATION_SECRET should also be removed from your environment."
            )
            
            return HttpResponse(response_text, content_type='text/plain')
            
        except Exception as e:
            sys.stdout = sys.__stdout__
            return HttpResponseServerError(
                f"Migration failed: {str(e)}",
                content_type='text/plain'
            )
