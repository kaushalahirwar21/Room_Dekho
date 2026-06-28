import os
import sys
from django.core.wsgi import get_wsgi_application

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

import django
django.setup()

from django.core.management import call_command
from django.http import JsonResponse

def handler(event, context):
    """Handle migration requests via Vercel Edge Functions"""
    # Only allow in development or with secret token
    secret = os.environ.get('MIGRATION_SECRET')
    if not secret or event.get('query', {}).get('secret') != secret:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        # Run migrations
        call_command('migrate', '--noinput')
        return JsonResponse({'status': 'success', 'message': 'Migrations completed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
