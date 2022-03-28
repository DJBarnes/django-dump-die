"""
django_dump_die URL Configuration.
Used exclusively to show example output.
"""

from django.urls import path

from . import views


urlpatterns = [
    path('string/', views.string_example, name='string_example'),
]
