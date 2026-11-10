"""
Tests for dd() and dump() outside of a request, such as in a management command, which print to the console.
"""

# System Imports.
import builtins
import io
import re
from contextlib import contextmanager, redirect_stderr
from datetime import date
from decimal import Decimal

# Third-Party Imports.
from django.contrib.auth.models import User
from django.db import connection
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext

# Internal Imports.
import django_dump_die
from django_dump_die import functions
from django_dump_die.console import format_dump
from django_dump_die.functions import DumpAndDie, dd, dump, get_dump_objects
from django_dump_die.utils import DumpBreak, generate_unique_from_obj


class Account:
    """Object with a nested list, a sensitive attribute, and a reference back to itself."""

    def __init__(self):
        self.name = "example"
        self.password = "hunter2"
        self.items = list(range(25))
        self.owner = self


class HasResults:
    """Object with a function to show the result of, and a sensitive function that must not be run."""

    dd_function_results = ("get_total", "get_token")

    def get_total(self):
        """Return a total."""
        return 42

    def get_token(self):
        """Return a token."""
        raise AssertionError("A function with a sensitive name must not be run.")


def sample_function(first, second=2):
    """Add two numbers."""
    return first + second


@contextmanager
def console():
    """Capture what is printed to the console (stderr) in the block.

    The dumps are called in the block itself, since dd() and dump() read the dumped name from the line that calls them.
    """
    output = io.StringIO()
    with redirect_stderr(output):
        yield output


@override_settings(DEBUG=True)
class DumpDieConsoleTestCase(SimpleTestCase):
    """Verify dumps outside of a request are printed to the console, as a text tree, instead of collected."""

    def test_dump_prints_instead_of_collecting(self):
        """Verify dump() outside of a request prints the object right away, and collects nothing to show later."""
        value = 42
        with console() as output:
            dump(value)

        self.assertEqual(output.getvalue(), "value: 42\n")
        self.assertEqual(get_dump_objects(), [])

    def test_object_is_printed_as_a_tree(self):
        """Verify an object's attributes are indented under it, with the page's limits and hidden values."""
        account = Account()
        with console() as printed:
            dump(account)
        output = printed.getvalue()
        unique = generate_unique_from_obj(account)

        self.assertTrue(output.startswith(f"account: Account {unique} {{\n"))
        self.assertIn("\n    name: 'example'\n", output)
        self.assertIn("\n    password: ********************\n", output)
        self.assertIn("\n    items: list:25 ", output)
        self.assertIn("\n        19: 19\n        … 5 more\n    ]\n", output)
        # The reference back to the object shows the same unique as the object.
        self.assertIn(f"\n    owner: Account {unique}\n", output)
        self.assertNotIn("hunter2", output)
        self.assertTrue(output.endswith("\n}\n"))

    def test_values_show_their_type_unless_it_is_clear(self):
        """Verify strings, numbers, and None are printed as they are, and other values with their type."""
        for value, expected in (
            ("text", "'text'"),
            (1.5, "1.5"),
            (None, "None"),
            (True, "True"),
            (Decimal("1.5"), "Decimal 1.5"),
        ):
            with self.subTest(expected=expected), console() as output:
                dump(value)
                self.assertEqual(output.getvalue(), f"value: {expected}\n")

    def test_intermediate_value_shows_its_value_and_attributes(self):
        """Verify a value such as a date shows its value after its type, and its attributes under it."""
        day = date(2026, 11, 9)
        with console() as printed:
            dump(day)
        output = printed.getvalue()

        self.assertTrue(output.startswith("day: date 2026-11-09 "))
        self.assertIn("\n    year: 2026\n", output)

    def test_dd_prints_then_stops(self):
        """Verify dd() outside of a request prints the object, then stops with a message that says why."""
        value = 42
        with console() as output, self.assertRaises(DumpAndDie) as raised:
            dd(value)

        self.assertEqual(output.getvalue(), "value: 42\n")
        self.assertIn("dd() stopped here", str(raised.exception))
        self.assertEqual(raised.exception.object[3], 42)

    @override_settings(DEBUG=False)
    def test_nothing_is_printed_with_debug_off(self):
        """Verify dd() and dump() print nothing, and dd() doesn't stop, with DEBUG off."""
        value = 42

        with console() as output:
            dump(value)
            dd(value)
            dump.br()

        self.assertEqual(output.getvalue(), "")

    def test_break_prints_a_line(self):
        """Verify dump.br() prints a line across, in the middle of as many lines as its size."""
        with console() as output:
            dump.br()
        with console() as tall_output:
            dump.br(3)

        self.assertEqual(output.getvalue(), "-" * 60 + "\n")
        self.assertEqual(tall_output.getvalue(), "\n" + "-" * 60 + "\n\n")

    @override_settings(DJANGO_DD_BREAK_SIZE=2)
    def test_break_uses_the_break_size_setting(self):
        """Verify dump.br() without a size uses DJANGO_DD_BREAK_SIZE."""
        with console() as output:
            dump.br()

        self.assertEqual(output.getvalue(), "\n" + "-" * 60 + "\n")

    def test_function_prints_its_signature_and_docs(self):
        """Verify a dumped function shows its signature and docs, as on the page."""
        with console() as output:
            dump(sample_function)

        self.assertEqual(output.getvalue(), "sample_function(first, second=2): Add two numbers.\n")

    @override_settings(DJANGO_DD_INCLUDE_FILENAME_LINENUMBER=True)
    def test_location_is_printed_when_turned_on(self):
        """Verify the file and line of the dump come first, with DJANGO_DD_INCLUDE_FILENAME_LINENUMBER on."""
        value = 42
        with console() as output:
            dump(value)

        self.assertRegex(output.getvalue(), r"^File: .*test_console\.py, Line: \d+\nvalue: 42\n$")

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_function_results_are_printed(self):
        """Verify function results follow the attributes, and a function with a sensitive name isn't run."""
        results = HasResults()
        with console() as output:
            dump(results)

        self.assertIn("\n    get_total(): 42\n", output.getvalue())
        self.assertIn("\n    get_token(): ********************\n", output.getvalue())

    def test_object_without_a_name(self):
        """Verify an object or function whose name couldn't be read is printed as unknown."""
        for obj, function_doc, expected in (
            (42, None, "Unknown Object: 42"),
            (sample_function, "Add two numbers.", "Unknown Function: Add two numbers."),
        ):
            with self.subTest(expected=expected):
                self.assertEqual(format_dump((None, None, None, obj, function_doc, None, None, None)), expected)

    def test_break_object(self):
        """Verify a break is formatted as a line, without a name."""
        self.assertEqual(format_dump((None, None, None, DumpBreak(1), None, None, None, None)), "-" * 60)


@override_settings(DEBUG=True)
class DumpDieConsoleQuerySetTestCase(TestCase):
    """Verify a QuerySet dumped outside of a request only fetches the rows that are printed."""

    @classmethod
    def setUpTestData(cls):
        User.objects.bulk_create([User(username=f"user{number:02}") for number in range(25)])

    def test_queryset_fetches_only_the_printed_rows(self):
        """Verify a QuerySet is counted, and only its first rows fetched, as on the page."""
        users = User.objects.order_by("username")
        with CaptureQueriesContext(connection) as queries, console() as printed:
            dump(users)
        output = printed.getvalue()

        self.assertEqual(len(queries), 2)
        self.assertTrue(output.startswith("users: QuerySet:25 "))
        self.assertIn("user19", output)
        self.assertNotIn("user20", output)
        self.assertIn("… 5 more", output)


class DumpDieBuiltinsTestCase(SimpleTestCase):
    """Verify dd() and dump() are available without the middleware, such as in management commands."""

    def test_app_makes_dd_and_dump_builtins(self):
        """Verify the app makes dd() and dump() built-ins when Django starts, not only when the middleware does."""
        self.assertIs(builtins.dd, functions.dd)
        self.assertIs(builtins.dump, functions.dump)

    def test_dd_and_dump_can_be_imported_from_the_package(self):
        """Verify `from django_dump_die import dd, dump` works, and other names still raise AttributeError."""
        self.assertIs(django_dump_die.dd, functions.dd)
        self.assertIs(django_dump_die.dump, functions.dump)
        with self.assertRaisesRegex(AttributeError, re.escape("has no attribute 'missing'")):
            django_dump_die.missing  # noqa: B018 - The attribute lookup is what is tested.
