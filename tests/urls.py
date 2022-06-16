"""
Testing URL configuration for django-dump-die project.

Mocks being the "project settings root" urls.py file.
"""

# System Imports.
from django.urls import include, path


urlpatterns = [
    path('', (include('django_dump_die.urls', namespace='django_dump_die'))),
]
