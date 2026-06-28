"""
Maintenance URLs - One-time migration endpoint.
DELETE this file after migrations are complete.
"""

from django.urls import path
from .views import RunMigrationsView

urlpatterns = [
    path('migrate/', RunMigrationsView.as_view(), name='run-migrations'),
]
