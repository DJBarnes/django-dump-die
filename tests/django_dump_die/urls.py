"""
Testing URL configuration for django-dump-die project.

Mocks being the "project settings root" urls.py file.
"""

# System Imports.
from django.urls import include, path


urlpatterns = [
    path(
        "tests/complex/",
        (include("tests.django_dump_die.complex_types.urls", namespace="django_dump_die__tests__complex")),
    ),
    path("", (include("django_dump_die.urls", namespace="django_dump_die"))),
]
