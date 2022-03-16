"""
django_dump_die URL Configuration.
"""

from django.urls import path, include


urlpatterns = [
    path('', include('dump_die.urls')),
]
