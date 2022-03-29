"""
django_dump_die URL Configuration.
Used exclusively to show example output.
"""

from django.urls import path

from . import views


urlpatterns = [
    path('simple', views.simple_example, name='simple_example'),
]
