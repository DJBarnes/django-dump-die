"""Test views for "intermediate" types, one object per view, with fixed values."""

# System Imports.
from datetime import date, datetime, time, timedelta, timezone
from pathlib import PosixPath, PurePosixPath

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
from django_dump_die.constants import PYTZ_PRESENT, ZONEINFO_PRESENT
from django_dump_die.middleware import dd, dump

# Imports that may not be accessible, depending on local python environment setup.
if PYTZ_PRESENT:
    import pytz
if ZONEINFO_PRESENT:
    from zoneinfo import ZoneInfo


def _done(request):
    """End the view with dd(), so that the dump page is shown. The page after it is never rendered."""
    dd("done")
    return render(request, "django_dump_die/sample.html", {})


def intermediate_type_bytearray(request):
    """Test view dumping a bytearray."""
    sample_bytearray = bytearray([8, 9, 10, 11])
    dump(sample_bytearray)
    return _done(request)


def intermediate_type_complex(request):
    """Test view dumping a complex number."""
    sample_complex = 3 - 1j
    dump(sample_complex)
    return _done(request)


def intermediate_type_date(request):
    """Test view dumping a date."""
    sample_date = date(2026, 1, 2)
    dump(sample_date)
    return _done(request)


def intermediate_type_naive_datetime(request):
    """Test view dumping a datetime without a timezone."""
    sample_naive_datetime = datetime(2026, 1, 2, 3, 4, 5, 678901)
    dump(sample_naive_datetime)
    return _done(request)


def intermediate_type_aware_datetime(request):
    """Test view dumping a datetime with a timezone."""
    sample_aware_datetime = datetime(2026, 1, 2, 3, 4, 5, 678901, tzinfo=timezone.utc)
    dump(sample_aware_datetime)
    return _done(request)


def intermediate_type_naive_time(request):
    """Test view dumping a time without a timezone."""
    sample_naive_time = time(3, 4, 5, 678901)
    dump(sample_naive_time)
    return _done(request)


def intermediate_type_aware_time(request):
    """Test view dumping a time with a timezone."""
    sample_aware_time = time(3, 4, 5, 678901, tzinfo=timezone.utc)
    dump(sample_aware_time)
    return _done(request)


def intermediate_type_timedelta(request):
    """Test view dumping a timedelta."""
    sample_timedelta = timedelta(days=1, hours=2, minutes=3, seconds=4, microseconds=5)
    dump(sample_timedelta)
    return _done(request)


def intermediate_type_pytz_timezone(request):
    """Test view dumping a pytz timezone."""
    sample_pytz_timezone = pytz.timezone("UTC")
    dump(sample_pytz_timezone)
    return _done(request)


def intermediate_type_zoneinfo_timezone(request):
    """Test view dumping a zoneinfo timezone."""
    sample_zoneinfo_timezone = ZoneInfo("UTC")
    dump(sample_zoneinfo_timezone)
    return _done(request)


def intermediate_type_pure_path(request):
    """Test view dumping a pure path, which doesn't depend on the machine running the tests."""
    sample_pure_path = PurePosixPath("/srv/app/data.txt")
    dump(sample_pure_path)
    return _done(request)


def intermediate_type_posix_path(request):
    """Test view dumping a path on a POSIX system, such as Linux or macOS. It doesn't need to exist."""
    sample_posix_path = PosixPath("/srv/app/data.txt")
    dump(sample_posix_path)
    return _done(request)
