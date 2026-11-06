"""DjangoDumpDie intermediate type testing URL Configuration."""

# Third-Party Imports.
from django.urls import path

# Internal Imports.
from django_dump_die_tests.intermediate_types import views

app_name = "django_dump_die__tests__intermediate"
urlpatterns = [
    path("intermediate/bytearray/", views.intermediate_type_bytearray, name="intermediate__bytearray"),
    path("intermediate/complex/", views.intermediate_type_complex, name="intermediate__complex"),
    path("intermediate/date/", views.intermediate_type_date, name="intermediate__date"),
    path("intermediate/naive-datetime/", views.intermediate_type_naive_datetime, name="intermediate__naive_datetime"),
    path("intermediate/aware-datetime/", views.intermediate_type_aware_datetime, name="intermediate__aware_datetime"),
    path("intermediate/naive-time/", views.intermediate_type_naive_time, name="intermediate__naive_time"),
    path("intermediate/aware-time/", views.intermediate_type_aware_time, name="intermediate__aware_time"),
    path("intermediate/timedelta/", views.intermediate_type_timedelta, name="intermediate__timedelta"),
    path("intermediate/pytz-timezone/", views.intermediate_type_pytz_timezone, name="intermediate__pytz_timezone"),
    path(
        "intermediate/zoneinfo-timezone/",
        views.intermediate_type_zoneinfo_timezone,
        name="intermediate__zoneinfo_timezone",
    ),
    path("intermediate/pure-path/", views.intermediate_type_pure_path, name="intermediate__pure_path"),
    path("intermediate/posix-path/", views.intermediate_type_posix_path, name="intermediate__posix_path"),
]
