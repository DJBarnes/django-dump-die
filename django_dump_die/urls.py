"""
django_dump_die URL Configuration.
Used exclusively to show example output.
"""

from django.urls import path

from .views import example


urlpatterns = [
    path('', example, name='example'),
]
