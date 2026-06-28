import os
import sys
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

# Configure Django
import django
django.setup()

if os.getenv('VERCEL'):
    migrate_flag = '/tmp/room-dekho.migrated'
    if not os.path.exists(migrate_flag):
        try:
            call_command('migrate', '--noinput')
            with open(migrate_flag, 'w', encoding='utf-8') as flag_file:
                flag_file.write('ok')
        except Exception as e:
            print(f"Auto-migration failed: {str(e)}")

# Export the WSGI application
application = WSGIHandler()
