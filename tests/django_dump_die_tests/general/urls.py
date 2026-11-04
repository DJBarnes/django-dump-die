"""DjangoDumpDie general testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from django_dump_die_tests.general.views import (
    async_dd_example,
    async_dump_example,
    async_queryset_example,
    break_example,
    break_sizes_example,
    database_error_example,
    dd_only_example,
    dump_only_example,
)

app_name = "django_dump_die__tests__general"
urlpatterns = [
    path("general/database-error/", database_error_example, name="database_error"),
    path("general/dump-only/", dump_only_example, name="dump_only"),
    path("general/dd-only/", dd_only_example, name="dd_only"),
    path("general/break/", break_example, name="break"),
    path("general/break-sizes/", break_sizes_example, name="break_sizes"),
    path("general/async-dump/", async_dump_example, name="async_dump"),
    path("general/async-dd/", async_dd_example, name="async_dd"),
    path("general/async-queryset/", async_queryset_example, name="async_queryset"),
]
