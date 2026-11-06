"""
Testing URL configuration for django-dump-die project.

Mocks being the "project settings root" urls.py file.
"""

# System Imports.
from django.urls import include, path

# Internal Imports.
from django_dump_die_tests.django_test_project.views import index

urlpatterns = [
    path("tests/", index, name="tests-index"),
    path("tests/", include("django_dump_die_tests.complex_types.urls")),
    path("tests/", include("django_dump_die_tests.simple_types.urls")),
    path("tests/", include("django_dump_die_tests.intermediate_types.urls")),
    path("tests/", include("django_dump_die_tests.function_types.urls")),
    path("tests/", include("django_dump_die_tests.django_types.urls")),
    path("tests/", include("django_dump_die_tests.browser.urls")),
    path("tests/", include("django_dump_die_tests.general.urls")),
    path("", include("django_dump_die.urls")),
]
