"""Constants for dump die"""

# System Imports.
import datetime
import types
from decimal import Decimal
from pathlib import PosixPath, PurePath, PurePosixPath, PureWindowsPath

# Third-Party Imports.
from django.conf import settings
from django.forms.boundfield import BoundField
from django.utils import timezone

# Imports that may not be accessible, depending on local python environment setup.
try:
    import pytz
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
    BoundField,
    bytes,
    Decimal,
    float,
    int,
    types.ModuleType,
    str,
]


# Intermediate types, that need some level of recursion and some level of "simple type" handling.
INTERMEDIATE_TYPES = [
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


# List of additional simple types defined as strings that do not need to be recursively inspected.
ADDITIONAL_SIMPLE_TYPES = getattr(settings, 'DJANGO_DD_ADDITIONAL_SIMPLE_TYPES', [])
# List of additional intermediate types defined as strings that do not need to be recursively inspected.
ADDITIONAL_INTERMEDIATE_TYPES = getattr(settings, 'DJANGO_DD_ADDITIONAL_INTERMEDIATE_TYPES', [])
# Max recursion depth to go while processing the dumped variable.
# Deep recursion will cause DD to take forever on complex structures.
MAX_RECURSION_DEPTH = getattr(settings, 'DJANGO_DD_MAX_RECURSION_DEPTH', 5)
# Max number of entries in an iterable to process further with recursion.
# After reaching an entry beyond this length, it will just print the unique
# instead of recursing into the entry to find further details.
# EX: if set to 20, a list of 30 will recursively inspect and print out 20
# items and then simply print the unique for the last 10.
MAX_ITERABLE_LENGTH = getattr(settings, 'DJANGO_DD_MAX_ITERABLE_LENGTH', 20)
# Whether each dump should include the filename and linenumber of the dump call.
INCLUDE_FILENAME_LINENUMBER = getattr(settings, 'DJANGO_DD_INCLUDE_FILENAME_LINENUMBER', False)
# Whether attributes should be included in the output.
INCLUDE_ATTRIBUTES = getattr(settings, 'DJANGO_DD_INCLUDE_ATTRIBUTES', True)
# Whether functions should be included in the output.
INCLUDE_FUNCTIONS = getattr(settings, 'DJANGO_DD_INCLUDE_FUNCTIONS', False)
# Whether function doc output should try to fit on one line, or output with original newlines.
MULTILINE_FUNCTION_DOCS = getattr(settings, 'DJANGO_DD_MULTILINE_FUNCTION_DOCS', False)
# Whether or not to colorize the name of the dumped object
COLORIZE_DUMPED_OBJECT_NAME = getattr(settings, 'DJANGO_DD_COLORIZE_DUMPED_OBJECT_NAME', True)
# Whether objects overarching item content (Attribute, Function) should start expanded for viewing.
CONTENT_STARTS_EXPANDED = getattr(settings, 'DJANGO_DD_CONTENT_STARTS_EXPANDED', False)
# Whether the attributes for an object should start expanded for viewing.
ATTRIBUTES_START_EXPANDED = getattr(settings, 'DJANGO_DD_ATTRIBUTES_START_EXPANDED', True)
# Whether the functions for an object should start expanded for viewing.
FUNCTIONS_START_EXPANDED = getattr(settings, 'DJANGO_DD_FUNCTIONS_START_EXPANDED', False)
# Whether the output should include private attributes and functions.
INCLUDE_PRIVATE_METHODS = getattr(settings, 'DJANGO_DD_INCLUDE_PRIVATE_MEMBERS', False)
# Whether the output should include magic methods.
INCLUDE_MAGIC_METHODS = getattr(settings, 'DJANGO_DD_INCLUDE_MAGIC_METHODS', False)
