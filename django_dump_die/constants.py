"""Constants for dump die"""

# System Imports.
import datetime
import types
from decimal import Decimal
from pathlib import PosixPath, PurePath, PurePosixPath, PureWindowsPath

# Third-Party Imports.
from django.forms.boundfield import BoundField
from django.utils import timezone

# Imports that may not be accessible, depending on local python environment setup.
try:
    import pytz  # noqa: F401 - Imported to check that it is installed.

    PYTZ_PRESENT = True
except ImportError:
    PYTZ_PRESENT = False
try:
    from zoneinfo import ZoneInfo

    ZONEINFO_PRESENT = True
except ImportError:
    ZONEINFO_PRESENT = False


# Simple types that do not need to be recursively inspected.
SIMPLE_TYPES = [
    bool,
    bytes,
    Decimal,
    float,
    int,
    types.ModuleType,
    str,
]


# Intermediate types, that need some level of recursion and some level of "simple type" handling.
INTERMEDIATE_TYPES = [
    # Shown as its rendered widget, what it outputs in a template.
    BoundField,
    bytearray,
    complex,
    datetime.datetime,
    datetime.date,
    datetime.time,
    datetime.timedelta,
    timezone.timezone,
    PosixPath,
    PurePath,
    PurePosixPath,
    PureWindowsPath,
]

if ZONEINFO_PRESENT:
    INTERMEDIATE_TYPES.append(ZoneInfo)


# Functions whose results are shown by default, by class name. Only functions that are cheap, have no side effects,
# and don't touch the filesystem or network.
DEFAULT_FUNCTION_RESULTS = {
    "date": ("weekday",),
    "datetime": ("weekday", "timestamp", "utcoffset", "tzname"),
    "time": ("utcoffset", "tzname"),
    "timedelta": ("total_seconds",),
}
# Name of the class attribute that lists the methods whose results are shown for that class's objects.
FUNCTION_RESULTS_ATTRIBUTE = "dd_function_results"
# Lines a break added with dump.br() can have, for the BREAK_STYLE setting. "blank" has no line.
BREAK_STYLES = ("dashed", "solid", "dotted", "blank")
