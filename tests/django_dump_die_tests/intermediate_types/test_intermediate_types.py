"""
Tests for "intermediate" type DD output, each with its own view and a fixed value.

Intermediate types show their value next to their type, and their attributes one level deep.
"""

# System Imports.
import os
from unittest import skipIf, skipUnless
from unittest.mock import patch

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase

# Internal Imports.
from django_dump_die.constants import PYTZ_PRESENT

UNIQUE = "data_9001"


def opening(dumped_name, type_name, value):
    """Expected start of a dumped intermediate object: its name, type, value, and the start of its Attributes."""
    return """
        <div class="dump-wrapper">
            <span class="dumped_object" title="Dumped Object">
                <span class="dumped_name">{name}</span>
            </span>:
            <span class="type" title="{type}">{type}</span>
            <code class="intermediate">{value}</code>
            <span class="braces">{{</span>
            <a
                class="arrow-toggle collapsed"
                title="[Ctrl+click] Expand all children"
                data-dd-toggle="collapse"
                data-target=".{unique}"
                data-dd-type="type"
                data-object-depth="1"
                aria-label="Close"
                aria-expanded="false"
            >
                <span class="unique" data-highlight-unique="{unique}">{unique}</span>
                <span id="arrow-{unique}" class="arrow arrow-{unique}">▶</span>
            </a>
            <div class="dd-wrapper collapse {unique} " data-unique="{unique}">
                <ul class="attribute-list">
                    <a
                        class="arrow-toggle show always-show"
                        title="[Ctrl+click] Expand all children"
                        data-target=".{unique}-attributes"
                        data-dd-type="attr"
                        aria-label="Open/Close"
                        aria-expanded=""
                    >
                        <span class="section_name">Attributes</span>
                        <span id="arrow-{unique}-attributes" class="arrow"></span>
                    </a>
                    <div
                        class="li-wrapper collapse {unique}-attributes show"
                        data-unique-attributes="{unique}-attributes"
                    >
    """.format(name=dumped_name, type=type_name, value=value, unique=UNIQUE)


def row(name, type_name, value, css_class="number", kind="attribute", decorator=None):
    """Expected row of an attribute: its name, and its value's type and value.

    :param kind: "attribute", "class_attribute", or "index".
    :param decorator: "property" to expect the @property marker.
    """
    titles = {"attribute": "Attribute", "class_attribute": "Class Attribute", "index": "Index"}
    access_modifier = "" if kind == "index" else '<span class="access-modifier">+</span>'
    marker = '<span class="decorator" title="Property">@{0}</span>'.format(decorator) if decorator else ""
    return """
        <li>
            {access_modifier}
            {marker}
            <span class="{kind}" title="{title}">{name}</span>:
            <span class="type" title="{type}">{type}</span>
            <code class="{css_class}">{value}</code>
        </li>
    """.format(
        access_modifier=access_modifier,
        marker=marker,
        kind=kind,
        title=titles[kind],
        name=name,
        type=type_name,
        css_class=css_class,
        value=value,
    )


@override_settings(DEBUG=True)
@patch("django_dump_die.templatetags.dump_die._generate_unique", side_effect=[(UNIQUE, "")] * 5000)
class DumpDieIntermediateTypeTestCase(IntegrationTestCase):
    """Verify handling of dumped "intermediate" types."""

    def assertDump(self, url_name, expected):
        """Assert that a view's dump page shows the expected parts, in order."""
        self.assertGetResponse(
            "django_dump_die__tests__intermediate:" + url_name,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=expected,
            content_ends_before="<!--End Main Content-->",
        )

    def test_bytearray_display(self, _mocked_unique):
        """Verify a bytearray shows its value, and its items by index."""
        self.assertDump(
            "intermediate__bytearray",
            [
                opening("sample_bytearray", "bytearray", r"bytearray(b'\x08\t\n\x0b')"),
                row("0", "int", "8", kind="index"),
                row("1", "int", "9", kind="index"),
                row("2", "int", "10", kind="index"),
                row("3", "int", "11", kind="index"),
            ],
        )

    def test_complex_display(self, _mocked_unique):
        """Verify a complex number shows its value, and its real and imaginary parts."""
        self.assertDump(
            "intermediate__complex",
            [
                opening("sample_complex", "complex", "(3-1j)"),
                row("imag", "float", "-1.0"),
                row("real", "float", "3.0"),
            ],
        )

    def test_date_display(self, _mocked_unique):
        """Verify a date shows its value, its parts, and its class's limits."""
        self.assertDump(
            "intermediate__date",
            [
                opening("sample_date", "date", "2026-01-02"),
                row("day", "int", "2"),
                row("max", "date", "9999-12-31", "intermediate", "class_attribute"),
                row("min", "date", "0001-01-01", "intermediate", "class_attribute"),
                row("month", "int", "1"),
                row("resolution", "timedelta", "1 day, 0:00:00", "intermediate", "class_attribute"),
                row("year", "int", "2026"),
            ],
        )

    def test_naive_datetime_display(self, _mocked_unique):
        """Verify a datetime without a timezone shows its value, its parts, and no timezone."""
        self.assertDump(
            "intermediate__naive_datetime",
            [
                opening("sample_naive_datetime", "datetime", "2026-01-02 03:04:05.678901"),
                row("day", "int", "2"),
                row("fold", "int", "0"),
                row("hour", "int", "3"),
                row("max", "datetime", "9999-12-31 23:59:59.999999", "intermediate", "class_attribute"),
                row("microsecond", "int", "678901"),
                row("min", "datetime", "0001-01-01 00:00:00", "intermediate", "class_attribute"),
                row("minute", "int", "4"),
                row("month", "int", "1"),
                row("resolution", "timedelta", "0:00:00.000001", "intermediate", "class_attribute"),
                row("second", "int", "5"),
                row("tzinfo", "null", "None", "none"),
                row("year", "int", "2026"),
            ],
        )

    def test_aware_datetime_display(self, _mocked_unique):
        """Verify a datetime with a timezone shows its value with its offset, and its timezone."""
        self.assertDump(
            "intermediate__aware_datetime",
            [
                opening("sample_aware_datetime", "datetime", "2026-01-02 03:04:05.678901+00:00"),
                row("day", "int", "2"),
                row("hour", "int", "3"),
                row("tzinfo", "timezone", "UTC", "intermediate"),
                row("year", "int", "2026"),
            ],
        )

    def test_naive_time_display(self, _mocked_unique):
        """Verify a time without a timezone shows its value, its parts, and no timezone."""
        self.assertDump(
            "intermediate__naive_time",
            [
                opening("sample_naive_time", "time", "03:04:05.678901"),
                row("fold", "int", "0"),
                row("hour", "int", "3"),
                row("max", "time", "23:59:59.999999", "intermediate", "class_attribute"),
                row("microsecond", "int", "678901"),
                row("min", "time", "00:00:00", "intermediate", "class_attribute"),
                row("minute", "int", "4"),
                row("resolution", "timedelta", "0:00:00.000001", "intermediate", "class_attribute"),
                row("second", "int", "5"),
                row("tzinfo", "null", "None", "none"),
            ],
        )

    def test_aware_time_display(self, _mocked_unique):
        """Verify a time with a timezone shows its value with its offset, and its timezone."""
        self.assertDump(
            "intermediate__aware_time",
            [
                opening("sample_aware_time", "time", "03:04:05.678901+00:00"),
                row("hour", "int", "3"),
                row("tzinfo", "timezone", "UTC", "intermediate"),
            ],
        )

    def test_timedelta_display(self, _mocked_unique):
        """Verify a timedelta shows its value, its days, seconds, and microseconds, and its class's limits."""
        self.assertDump(
            "intermediate__timedelta",
            [
                opening("sample_timedelta", "timedelta", "1 day, 2:03:04.000005"),
                row("days", "int", "1"),
                row("max", "timedelta", "999999999 days, 23:59:59.999999", "intermediate", "class_attribute"),
                row("microseconds", "int", "5"),
                row("min", "timedelta", "-999999999 days, 0:00:00", "intermediate", "class_attribute"),
                row("resolution", "timedelta", "0:00:00.000001", "intermediate", "class_attribute"),
                row("seconds", "int", "7384"),
            ],
        )

    @skipUnless(PYTZ_PRESENT, "pytz is not installed.")
    def test_pytz_timezone_display(self, _mocked_unique):
        """Verify a pytz timezone shows its name."""
        self.assertDump(
            "intermediate__pytz_timezone",
            [
                opening("sample_pytz_timezone", "pytz_timezone", "UTC"),
                row("zone", "str", "'UTC'", "string", "class_attribute"),
            ],
        )

    def test_zoneinfo_timezone_display(self, _mocked_unique):
        """Verify a zoneinfo timezone shows its key."""
        self.assertDump(
            "intermediate__zoneinfo_timezone",
            [
                opening("sample_zoneinfo_timezone", "ZoneInfo", "UTC"),
                row("key", "str", "'UTC'", "string"),
            ],
        )

    def test_pure_path_display(self, _mocked_unique):
        """Verify a pure path shows its value, and its parts as properties."""
        self.assertDump(
            "intermediate__pure_path",
            [
                opening("sample_pure_path", "PurePosixPath", "/srv/app/data.txt"),
                row("anchor", "str", "'/'", "string", decorator="property"),
                row("drive", "str", "''", "string", decorator="property"),
                row("name", "str", "'data.txt'", "string", decorator="property"),
                row("parent", "PurePosixPath", "/srv/app", "intermediate", decorator="property"),
                row("parts", "tuple", "('/', 'srv', 'app', 'data.txt')", "default", decorator="property"),
                row("root", "str", "'/'", "string", decorator="property"),
                row("stem", "str", "'data'", "string", decorator="property"),
                row("suffix", "str", "'.txt'", "string", decorator="property"),
                row("suffixes", "list", "['.txt']", "default", decorator="property"),
            ],
        )

    @skipIf(os.name == "nt", "PosixPath can't be created on Windows.")
    def test_posix_path_display(self, _mocked_unique):
        """Verify a path on a POSIX system shows its value, and its parts as properties."""
        self.assertDump(
            "intermediate__posix_path",
            [
                opening("sample_posix_path", "PosixPath", "/srv/app/data.txt"),
                row("name", "str", "'data.txt'", "string", decorator="property"),
                row("parent", "PosixPath", "/srv/app", "intermediate", decorator="property"),
                row("suffix", "str", "'.txt'", "string", decorator="property"),
            ],
        )
