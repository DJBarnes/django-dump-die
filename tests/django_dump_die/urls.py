"""
Testing URL configuration for django-dump-die project.

Mocks being the "project settings root" urls.py file.
"""

# System Imports.
from django.urls import include, path

app_name = "django_dump_die__tests"
urlpatterns = [
    path("tests/complex/", include("tests.django_dump_die.complex_types.urls")),
    # path("tests/django/", include("tests.django_dump_die.django_types.urls")),
    # path("tests/function/", include("tests.django_dump_die.function_types.urls")),
    # path("tests/intermediate/", include("tests.django_dump_die.intermediate_types.urls")),
    path("tests/simple/", include("tests.django_dump_die.simple_types.urls")),
    # path("tests/", include("tests.django_dump_die.general.urls")),
    path("", include("django_dump_die.urls")),
]
