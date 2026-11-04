"""DjangoDumpDie general testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from django_dump_die_tests.general.views import database_error_example

app_name = "django_dump_die__tests__general"
urlpatterns = [
    path("general/database-error/", database_error_example, name="database_error"),
]
