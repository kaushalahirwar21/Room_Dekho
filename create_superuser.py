#!/usr/bin/env python
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')

import django
django.setup()

from accounts.models import User

# Delete existing superuser if any
User.objects.filter(email='admin@gmail.com').delete()

# Create new superuser
user = User.objects.create_superuser(
    email='admin@gmail.com',
    password='1234'
)
print(f'Superuser created! Email: {user.email}, is_superuser: {user.is_superuser}')