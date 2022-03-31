"""
django_dump_die URL Configuration.
Used exclusively to show example output.
"""

from django.urls import path

from . import views


urlpatterns = [
    path('function', views.function_example, name='function_example'),
    path('simple', views.simple_example, name='simple_example'),
    path('data_structure', views.data_structure_example, name='data_structure_example'),
]
