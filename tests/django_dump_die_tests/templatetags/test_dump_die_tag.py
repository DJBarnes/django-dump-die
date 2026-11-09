"""
Tests for the DumpDie template tag's handling of settings, index ranges, deep copies, and members that raise.
"""

# System Imports.
import re
from datetime import date, datetime
from enum import Enum

# Third-Party Imports.
from django import forms
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings
from django.utils.functional import cached_property
from django.utils.html import format_html

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dump
from django_dump_die.app_settings import app_settings
from django_dump_die.templatetags.dump_die import _process_root_indices
from django_dump_die.utils import generate_unique_from_obj


class Leaf:
    """Innermost object of the nested sample."""

    def __init__(self):
        self.value = 3


class Branch:
    """Object with a nested object, a private attribute, and a method."""

    def __init__(self):
        self.leaf = Leaf()
        self._private_value = "hidden"

    def do_work(self):
        """Do some work."""
        return True


class HasMethodTypes:
    """Class with a static method, a class method, and a normal method."""

    @staticmethod
    def static_work():
        """Static work."""

    @classmethod
    def class_work(cls):
        """Class work."""

    def normal_work(self):
        """Normal work."""


class HasAttributeTypes:
    """Class with a property, a cached property, a class attribute, and an instance attribute."""

    shared = "shared value"

    def __init__(self):
        self.own = "own value"

    @property
    def computed(self):
        """A property."""
        return "computed value"

    @cached_property
    def cached(self):
        """A cached property."""
        return "cached value"


class RaisesOnRepr:
    """Object whose repr raises an error that isn't ObjectDoesNotExist."""

    def __repr__(self):
        raise ValueError("Repr failed.")


class SafeRepr:
    """Object whose repr is marked safe, as when built with format_html(), and has HTML in it."""

    def __repr__(self):
        return format_html("<b id={0}>key</b>", "injected")


class HasSecrets:
    """Object with sensitive attributes, a sensitive function to show the result of, and a harmless attribute."""

    dd_function_results = ("get_token",)

    def __init__(self, calls):
        self.password = "hunter2"
        self.credentials = {"user": "someone"}
        self.name = "visible"
        self.calls = calls

    def get_token(self):
        """Return a token. Must not be run while the value is hidden."""
        self.calls.append("get_token")
        return "token value"


class SampleForm(forms.Form):
    """Form with one field, for dumping a bound field."""

    name = forms.CharField()


def render_dump(obj):
    """Render the dump template tag for one object."""
    return Template("{% load dump_die %}{% dump obj %}").render(Context({"obj": obj}))


def render_dumped_objects():
    """Render everything collected by dump() calls, then clear the collected objects."""
    objects = middleware.dump_objects[:]
    middleware.dump_objects.clear()
    return Template("{% load dump_die %}{% dump_objects objects %}").render(Context({"objects": objects}))


class DumpDieRootIndicesTestCase(SimpleTestCase):
    """Verify the start and end index used for a dumped root iterable."""

    def test_process_root_indices(self):
        """Verify each start and end index gives the expected range, for a root iterable of 10 items."""
        cases = [
            ((None, None), (0, app_settings.MAX_ITERABLE_LENGTH)),
            ((2, None), (2, 2 + app_settings.MAX_ITERABLE_LENGTH)),
            ((None, 5), (0, 5)),
            ((-3, None), (7, 7 + app_settings.MAX_ITERABLE_LENGTH)),
            ((-30, None), (0, app_settings.MAX_ITERABLE_LENGTH)),
            ((0, -2), (0, 8)),
            ((0, -30), (0, 0)),
            ((5, 2), (2, 5)),
        ]
        for (start, end), expected in cases:
            with self.subTest(start=start, end=end):
                self.assertEqual(_process_root_indices(start, end, 10), expected)


@override_settings(DEBUG=True)
class DumpDieTagSettingsTestCase(SimpleTestCase):
    """Verify the dump output follows the attribute, function, private, and magic member settings."""

    @override_settings(DJANGO_DD_INCLUDE_ATTRIBUTES=False)
    def test_attributes_left_out(self):
        """Verify complex and intermediate objects have no Attributes section when attributes are off."""
        for obj in (Branch(), datetime(2026, 1, 2)):
            with self.subTest(obj=type(obj).__name__):
                content = render_dump(obj)

                self.assertNotIn('<span class="section_name">Attributes</span>', content)
                self.assertNotIn('<span class="attribute"', content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTIONS=True)
    def test_functions_included(self):
        """Verify complex and intermediate objects have a Functions section when functions are on."""
        for obj, function_name in ((Branch(), "do_work"), (datetime(2026, 1, 2), "isoformat")):
            with self.subTest(obj=type(obj).__name__):
                content = render_dump(obj)

                self.assertIn('<span class="section_name">Functions</span>', content)
                self.assertIn(function_name, content)
                # Magic methods stay out unless they are turned on too.
                self.assertNotIn("__init__", content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTIONS=True)
    def test_static_and_class_methods_are_marked(self):
        """Verify static and class methods are marked in the Functions section, and normal methods aren't."""
        for label, obj in (("class", HasMethodTypes), ("instance", HasMethodTypes())):
            with self.subTest(dumped=label):
                # Dumped with dump(), since a template would call the class and dump an instance.
                dump(obj)
                content = render_dumped_objects()

                self.assertIn('<span class="type" title="{0}">'.format(type(obj).__name__), content)
                self.assertIn('<span class="decorator" title="Static Method">@staticmethod</span>', content)
                self.assertIn('<span class="decorator" title="Class Method">@classmethod</span>', content)
                self.assertEqual(content.count('class="decorator"'), 2)
                self.assertIn("normal_work", content)

    def test_properties_and_class_attributes_are_marked(self):
        """Verify properties are marked, class attributes have their own color and title, and other attributes don't."""
        content = render_dump(HasAttributeTypes())

        self.assertRegex(
            content,
            r'<span class="decorator" title="Property">@property</span>\s*'
            r'<span class="attribute" title="Attribute">computed</span>:',
        )
        self.assertRegex(
            content,
            r'<span class="decorator" title="Cached Property">@cached_property</span>\s*'
            r'<span class="attribute" title="Attribute">cached</span>:',
        )
        self.assertIn('<span class="class_attribute" title="Class Attribute">shared</span>:', content)
        self.assertIn('<span class="attribute" title="Attribute">own</span>:', content)
        self.assertEqual(content.count('class="decorator"'), 2)
        self.assertEqual(content.count('class="class_attribute"'), 1)

    def test_dumped_class_does_not_mark_class_attributes(self):
        """Verify a dumped class shows its attributes as plain attributes, and still marks its properties."""
        # Dumped with dump(), since a template would call the class and dump an instance.
        dump(HasAttributeTypes)
        content = render_dumped_objects()

        self.assertIn('<span class="attribute" title="Attribute">shared</span>:', content)
        self.assertNotIn('class="class_attribute"', content)
        self.assertIn('<span class="decorator" title="Property">@property</span>', content)
        self.assertIn('<span class="decorator" title="Cached Property">@cached_property</span>', content)

    def test_dumped_callables_are_not_called(self):
        """Verify dumping a function, a callable object, or a class shows it without calling it."""
        calls = []

        def no_docstring():  # pylint: disable=missing-function-docstring
            calls.append("function")

        class CallableObject:
            """Object that can be called."""

            def __call__(self):
                calls.append("object")

        class NeedsArguments:
            """Class that can't be created without an argument."""

            def __init__(self, value):
                calls.append("class")
                self.value = value

        for label, obj in (
            ("function", no_docstring),
            ("callable object", CallableObject()),
            ("class", NeedsArguments),
        ):
            with self.subTest(dumped=label):
                dump(obj)
                render_dumped_objects()

                self.assertEqual(calls, [])

        # The class is dumped as the class itself, not an instance or an empty string.
        dump(NeedsArguments)
        self.assertIn('<span class="type" title="type">type</span>', render_dumped_objects())

    @override_settings(DJANGO_DD_INCLUDE_FUNCTIONS=True)
    @override_settings(DJANGO_DD_INCLUDE_ATTRIBUTES=False)
    def test_only_functions_section_is_not_collapsible(self):
        """Verify the Functions section, when it is the only section, is always shown and can't be collapsed."""
        content = render_dump(Branch())

        functions_toggle = re.search(r'<a\s+class="arrow-toggle[^>]*data-dd-type="func"', content).group(0)
        self.assertIn("always-show", functions_toggle)
        self.assertNotIn("data-dd-toggle", functions_toggle)

    def test_string_enum_member_stays_an_enum(self):
        """Verify an enum member that is also a str is dumped as an enum, with its name and value."""

        class Color(str, Enum):
            """Enum whose members are strings."""

            RED = "red"

        dump(Color.RED)
        content = render_dumped_objects()

        self.assertIn('<span class="type" title="Color">Color', content)
        self.assertIn('<span class="attribute" title="Attribute">value</span>', content)

    def test_repeated_intermediate_value_keeps_its_color(self):
        """Verify an intermediate object shown again, as already output, keeps the intermediate color."""
        sample_date = date(2026, 1, 2)
        content = render_dump([sample_date, sample_date])

        self.assertEqual(content.count('<code class="intermediate">2026-01-02</code>'), 2)
        self.assertNotIn('class="datetime"', content)

    @override_settings(DJANGO_DD_INCLUDE_PRIVATE_MEMBERS=True)
    def test_private_members_included(self):
        """Verify private attributes are shown, with the private access modifier, when they are on."""
        content = render_dump(Branch())

        self.assertIn('<span class="access-modifier">#</span>', content)
        self.assertIn("_private_value", content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTIONS=True)
    @override_settings(DJANGO_DD_INCLUDE_MAGIC_METHODS=True)
    def test_magic_methods_included(self):
        """Verify magic methods are shown, with the magic access modifier, when they and functions are on."""
        content = render_dump(Branch())

        self.assertIn('<span class="access-modifier">-</span>', content)
        self.assertIn("__init__", content)


@override_settings(DEBUG=True)
class DumpDieTagObjectsTestCase(SimpleTestCase):
    """Verify the dump output of bound fields, members that raise, deep copies, and index ranges."""

    def tearDown(self):
        middleware.dump_objects.clear()
        super().tearDown()

    def test_dict_key_with_a_safe_repr_is_escaped(self):
        """Verify a dict key whose repr is marked safe is shown as text, not added to the page as HTML."""
        content = render_dump({SafeRepr(): 1})

        self.assertNotIn("<b id=injected>", content)
        self.assertIn("&lt;b id=injected&gt;key&lt;/b&gt;", content)

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    def test_sensitive_values_are_hidden(self):
        """Verify attributes, dict keys, and function results with sensitive names are hidden, and others aren't."""
        calls = []
        content = render_dump({"api_key": "abc123", "secrets": HasSecrets(calls)})

        for value in ("abc123", "hunter2", "someone", "token value"):
            with self.subTest(value=value):
                self.assertNotIn(value, content)
        self.assertEqual(content.count("********************"), 4)
        self.assertIn('title="Hidden, because its name looks sensitive.', content)
        self.assertIn("visible", content)
        # The sensitive function wasn't run.
        self.assertEqual(calls, [])

    @override_settings(DJANGO_DD_INCLUDE_FUNCTION_RESULTS=True)
    @override_settings(DJANGO_DD_SHOW_SENSITIVE_VALUES=True)
    def test_sensitive_values_are_shown_when_turned_on(self):
        """Verify sensitive values are shown, and sensitive functions are run, when the setting is on."""
        calls = []
        content = render_dump({"api_key": "abc123", "secrets": HasSecrets(calls)})

        for value in ("abc123", "hunter2", "someone", "token value"):
            with self.subTest(value=value):
                self.assertIn(value, content)
        self.assertNotIn("********************", content)
        self.assertEqual(calls, ["get_token"])

    def test_bound_field(self):
        """Verify a form's bound field is shown as a "bound" value."""
        content = render_dump(SampleForm()["name"])

        self.assertIn('class="bound"', content)

    def test_member_whose_repr_raises(self):
        """Verify a dict key whose repr raises is shown as an exception, without stopping the dump."""
        content = render_dump({RaisesOnRepr(): 1, "other": 2})

        self.assertIn('<span class="empty" title="Exception:', content)
        self.assertIn("Repr failed.", content)

    def test_deepcopy_of_nested_objects(self):
        """Verify a deep-copied object shows the uniques of the original objects, not of the copies."""
        branch = Branch()
        dump(branch, deepcopy=True)
        content = render_dumped_objects()

        self.assertIn("leaf", content)
        self.assertIn("value", content)
        self.assertIn('data-highlight-unique="{0}"'.format(generate_unique_from_obj(branch.leaf)), content)

    def test_index_range_of_root_iterable(self):
        """Verify only the root iterable's items inside index_range are expanded."""
        branches = [Branch(), Branch(), Branch()]
        dump(branches, index_range=(0, 1))
        content = render_dumped_objects()

        # Only the first item is expanded. The other two only show their unique.
        expanded = [content.count('data-unique="{0}"'.format(generate_unique_from_obj(b))) for b in branches]
        self.assertEqual(expanded, [1, 0, 0])
        for branch in branches[1:]:
            self.assertIn('data-highlight-unique="{0}"'.format(generate_unique_from_obj(branch)), content)
