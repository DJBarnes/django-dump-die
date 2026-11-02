"""
Testing URL configuration for django-dump-die project.

Mocks being the "project settings root" urls.py file.
"""

# System Imports.
from django.urls import include, path

app_name = "django_dump_die__tests"
urlpatterns = [
    path("tests/complex/", include("django_dump_die_tests.complex_types.urls")),
    # path("tests/django/", include("django_dump_die_tests.django_types.urls")),
    # path("tests/function/", include("django_dump_die_tests.function_types.urls")),
    # path("tests/intermediate/", include("django_dump_die_tests.intermediate_types.urls")),
    path("tests/simple/", include("django_dump_die_tests.simple_types.urls")),
    # path("tests/", include("django_dump_die_tests.general.urls")),
    path("", include("django_dump_die.urls")),
]
