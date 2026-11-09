"""
Tests for the Function Results section: which functions are run, how their results and errors are shown, and the
settings that turn it on and choose the functions.
"""

# System Imports.
import re
from datetime import datetime, timedelta, timezone

# Third-Party Imports.
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dump

# An escaped single quote. Django before 3.0 escapes it as &#39;, later versions as &#x27;.
QUOTE = r"&#(?:x27|39);"


class Invoice:
    """Class that lists functions to show the results of, with each kind of entry that can't be run."""

    dd_function_results = (
        "total",
        "_tax",
        "make_greeter",
        "needs_arguments",
        "raises",
        "not_a_function",
        "broken_property",
        "missing",
    )
    not_a_function = "plain value"

    def __init__(self):
        self.calls = []

    def total(self):
        """A function whose result is shown."""
        self.calls.append("total")
        return 42

    def _tax(self):
        """A private function whose result is shown."""
        return 4

    def make_greeter(self):
        """A function whose result is itself a function."""

        def greet():
            self.calls.append("greet")

        return greet

    def needs_arguments(self, amount):
        """A function that can't be run, since it needs an argument."""
        self.calls.append("needs_arguments")
        return amount

    def raises(self):
        """A function that raises an error."""
        raise ValueError("Total is unknown.")

    @property
    def broken_property(self):
        """A property, listed by mistake, that raises an error."""
        raise KeyError("No such total.")

    def not_listed(self):
        """A function that isn't listed, so it isn't run."""
        self.calls.append("not_listed")


class ListsOneString:
    """Class whose dd_function_results is a single string instead of a tuple of names."""

    dd_function_results = "total"

    def total(self):
        """A function that isn't run, since the list is invalid."""
        return 42


class AnswersAnyName:
    """Object whose __getattr__ returns a value for any name, like a mock or a proxy."""

    def __getattr__(self, name):
        return "answer for {0}".format(name)


def render_dumped(obj):
    """Dump an object with dump(), and render the dump. Dumped with dump(), since a template would call a callable."""
    dump(obj)
    objects = middleware.dump_objects[:]
    middleware.dump_objects.clear()
    return Template("{% load dump_die %}{% dump_objects objects %}").render(Context({"objects": objects}))


def result_row(name):
    """Pattern for the start of the row of one function result."""
    return r'<span class="function" title="Function Result">{0}<span class="braces">\(\)</span></span>:\s*'.format(
        re.escape(name)
    )


@override_settings(DEBUG=True)
class DumpDieFunctionResultsTestCase(SimpleTestCase):
    """Verify which function results are shown, and how."""

    def test_off_by_default(self):
        """Verify no function is run and there's no Function Results section unless it is turned on."""
        invoice = Invoice()
        content = render_dumped(invoice)

        self.assertNotIn("Function Results", content)
        self.assertEqual(invoice.calls, [])

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_listed_functions_are_run_and_shown(self):
        """Verify each function in dd_function_results is run once, and its result shown, sorted by name."""
        invoice = Invoice()
        content = render_dumped(invoice)

        self.assertIn('<span class="section_name">Function Results</span>', content)
        self.assertRegex(
            content, result_row("total") + r'<span class="type" title="int">int</span> <code class="number">42</code>'
        )
        self.assertRegex(content, r'<span class="access-modifier">#</span>\s*' + result_row("_tax"))
        self.assertEqual(invoice.calls.count("total"), 1)
        self.assertNotIn("not_listed", invoice.calls)
        names = re.findall(r'title="Function Result">(\w+)<', content)
        self.assertEqual(names, sorted(names))

    def test_object_without_listed_functions_is_unchanged(self):
        """Verify an object with no functions listed has no section, and looks the same as with the feature off."""

        def render_without_uniques(obj):
            # Each dump of an object gets its own unique, so leave them out of the comparison. A unique comes from
            # hash(), which can be negative.
            return re.sub(r"\w+_-?\d+(_\d+)?", "UNIQUE", render_dumped(obj))

        values = {"name": "first", "items": [1, 2]}
        expected = render_without_uniques(values)
        with override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True):
            content = render_without_uniques(values)

        self.assertEqual(content, expected)
        self.assertNotIn("Function Results", content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_functions_that_cannot_be_run_show_why(self):
        """Verify a function that needs arguments isn't run, and errors and invalid names are shown in their rows."""
        invoice = Invoice()
        content = render_dumped(invoice)

        self.assertRegex(content, result_row("needs_arguments") + r'<span class="empty" title="[^"]*">Needs Arguments<')
        self.assertNotIn("needs_arguments", invoice.calls)
        self.assertRegex(content, result_row("raises") + r'<span class="empty" title="Exception Occurred')
        self.assertIn("ValueError: Total is unknown.", content)
        self.assertRegex(content, result_row("not_a_function") + r'<span class="empty" title="[^"]*">Not A Function<')
        self.assertRegex(content, result_row("missing") + r'<span class="empty" title="[^"]*">Not Found<')
        self.assertRegex(content, result_row("broken_property") + r'<span class="empty" title="Exception Occurred')
        self.assertRegex(content, "KeyError: {0}No such total.{0}".format(QUOTE))

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_callable_result_is_not_called(self):
        """Verify a result that is itself a function is dumped without being called."""
        invoice = Invoice()
        content = render_dumped(invoice)

        self.assertRegex(content, result_row("make_greeter") + r'<span class="type" title="function">function</span>')
        self.assertNotIn("greet", invoice.calls)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_invalid_class_attribute_shows_an_error(self):
        """Verify a dd_function_results that isn't a list of names shows an error, and runs nothing."""
        content = render_dumped(ListsOneString())

        self.assertRegex(content, result_row("dd_function_results") + r'<span class="empty" title="dd_function_results')
        self.assertIn("Not A List Of Function Names", content)
        self.assertNotRegex(content, result_row("total"))

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_object_with_getattr_has_no_error(self):
        """Verify an object whose __getattr__ returns something for any name isn't taken to have the class attribute."""
        content = render_dumped(AnswersAnyName())

        self.assertNotIn("Function Results", content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_dumped_class_runs_nothing(self):
        """Verify a dumped class shows no results, since its methods aren't bound to an object."""
        content = render_dumped(Invoice)

        self.assertNotIn("Function Results", content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_built_in_functions_for_dates_and_times(self):
        """Verify the built-in functions are run for datetime and timedelta objects."""
        moment = datetime(2026, 11, 5, 12, 30, tzinfo=timezone.utc)
        content = render_dumped(moment)
        for name in ("weekday", "timestamp", "utcoffset", "tzname"):
            with self.subTest(name=name):
                self.assertRegex(content, result_row(name))
        self.assertRegex(
            content, result_row("weekday") + r'<span class="type" title="int">int</span> <code class="number">3</code>'
        )
        self.assertRegex(
            content,
            result_row("tzname")
            + r'<span class="type" title="str">str</span> <code class="string">{0}UTC{0}</code>'.format(QUOTE),
        )

        content = render_dumped(timedelta(minutes=2))
        self.assertRegex(
            content,
            result_row("total_seconds")
            + r'<span class="type" title="float">float</span> <code class="number">120.0</code>',
        )

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    @override_settings(
        DJANGO_DD_FUNCTION_RESULTS={"datetime": ["isoformat"], "timedelta": [], "Invoice": ["not_listed"]}
    )
    def test_setting_replaces_the_list_of_a_class(self):
        """Verify the setting's entry for a class replaces the built-in list, and is added to dd_function_results."""
        content = render_dumped(datetime(2026, 11, 5, 12, 30))
        self.assertRegex(content, result_row("isoformat") + r"<span class=\"type\" title=\"str\">str</span>")
        self.assertNotRegex(content, result_row("weekday"))

        content = render_dumped(timedelta(minutes=2))
        self.assertNotIn("Function Results", content)

        invoice = Invoice()
        content = render_dumped(invoice)
        self.assertRegex(content, result_row("not_listed"))
        self.assertRegex(content, result_row("total"))
        self.assertIn("not_listed", invoice.calls)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_invalid_setting_raises_an_error(self):
        """Verify a setting that isn't a dict of class names to lists of function names raises a clear error."""
        cases = [
            (["isoformat"], "DJANGO_DD_FUNCTION_RESULTS must be a dict"),
            ({"datetime": "isoformat"}, "DJANGO_DD_FUNCTION_RESULTS['datetime'] must be a list of function names"),
            ({"datetime": [42]}, "DJANGO_DD_FUNCTION_RESULTS['datetime'] must be a list of function names"),
        ]
        for value, message in cases:
            with self.subTest(value=value), override_settings(DJANGO_DD_FUNCTION_RESULTS=value):
                with self.assertRaisesMessage(ValueError, message):
                    render_dumped("anything")
        middleware.dump_objects.clear()

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    @override_settings(DJANGO_DD_INCLUDE_ATTRIBUTES=False)
    def test_only_section_is_always_shown(self):
        """Verify the Function Results section is always shown, without an arrow, when it is the only section."""
        content = render_dumped(Invoice())

        self.assertNotIn('<span class="section_name">Attributes</span>', content)
        self.assertRegex(content, result_row("total") + r'<span class="type" title="int">int</span>')
        results_toggle = re.search(r'<a\s+class="arrow-toggle[^>]*data-dd-type="result"', content).group(0)
        self.assertIn("always-show", results_toggle)
        self.assertNotIn("data-dd-toggle", results_toggle)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_section_starts_expanded_with_an_arrow(self):
        """Verify the section has its own arrow, starts open by default, and can start closed instead."""
        content = render_dumped(Invoice())
        # A unique comes from hash(), which can be negative, so it can contain a "-".
        self.assertRegex(content, r'class="li-wrapper collapse [\w-]+-function-results show"')
        self.assertRegex(content, r'data-dd-type="result"')

        with override_settings(DJANGO_DD_FUNCTION_RESULTS_START_EXPANDED=False):
            content = render_dumped(Invoice())
        self.assertRegex(content, r'class="li-wrapper collapse [\w-]+-function-results "')


@override_settings(DEBUG=True)
class DumpDieFunctionResultsPageTestCase(TestCase):
    """Verify the Function Results toolbar buttons, and results for a failing QuerySet, on the dump page."""

    def test_toolbar_buttons_follow_the_enabled_sections(self):
        """Verify the toolbar has buttons for each shown section, when there is more than one section."""
        url = reverse("django_dump_die__tests__general:dd_only")
        cases = [
            ({}, []),
            ({"DJANGO_DD_INCLUDE_FUNCTION_RESULTS": True}, ["types", "attrs", "results"]),
            ({"DJANGO_DD_INCLUDE_FUNCTIONS": True}, ["types", "attrs", "funcs"]),
            (
                {"DJANGO_DD_INCLUDE_FUNCTION_RESULTS": True, "DJANGO_DD_INCLUDE_ATTRIBUTES": False},
                [],
            ),
        ]
        for settings, buttons in cases:
            with self.subTest(settings=settings):
                with override_settings(**settings):
                    content = self.client.get(url).content.decode("utf-8")

                shown = sorted(set(re.findall(r'id="(?:expand|collapse)-(types|attrs|results|funcs)"', content)))
                self.assertEqual(shown, sorted(buttons))
                for name in buttons:
                    self.assertIn(f'id="expand-{name}"', content)
                    self.assertIn(f'id="collapse-{name}"', content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_queryset_whose_query_fails_has_no_results(self):
        """Verify a QuerySet whose query fails shows its error, and no function results."""
        response = self.client.get(reverse("django_dump_die__tests__general:database_error"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("no such table: django_dump_die_samplerelation", content)
        self.assertNotIn('<span class="section_name">Function Results</span>', content)
