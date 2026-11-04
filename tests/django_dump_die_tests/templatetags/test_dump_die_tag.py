"""
Tests for the DumpDie template tag's handling of settings, index ranges, deep copies, and members that raise.
"""

# System Imports.
from datetime import datetime
from unittest.mock import patch

# Third-Party Imports.
from django import forms
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dump
from django_dump_die.templatetags.dump_die import MAX_ITERABLE_LENGTH, _process_root_indices
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


class RaisesOnRepr:
    """Object whose repr raises an error that isn't ObjectDoesNotExist."""

    def __repr__(self):
        raise ValueError("Repr failed.")


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
            ((None, None), (0, MAX_ITERABLE_LENGTH)),
            ((2, None), (2, 2 + MAX_ITERABLE_LENGTH)),
            ((None, 5), (0, 5)),
            ((-3, None), (7, 7 + MAX_ITERABLE_LENGTH)),
            ((-30, None), (0, MAX_ITERABLE_LENGTH)),
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

    @patch("django_dump_die.templatetags.dump_die.INCLUDE_ATTRIBUTES", False)
    def test_attributes_left_out(self):
        """Verify complex and intermediate objects have no Attributes section when attributes are off."""
        for obj in (Branch(), datetime(2026, 1, 2)):
            with self.subTest(obj=type(obj).__name__):
                content = render_dump(obj)

                self.assertNotIn('<span class="section_name">Attributes</span>', content)
                self.assertNotIn('<span class="attribute"', content)

    @patch("django_dump_die.templatetags.dump_die.INCLUDE_FUNCTIONS", True)
    def test_functions_included(self):
        """Verify complex and intermediate objects have a Functions section when functions are on."""
        for obj, function_name in ((Branch(), "do_work"), (datetime(2026, 1, 2), "isoformat")):
            with self.subTest(obj=type(obj).__name__):
                content = render_dump(obj)

                self.assertIn('<span class="section_name">Functions</span>', content)
                self.assertIn(function_name, content)
                # Magic methods stay out unless they are turned on too.
                self.assertNotIn("__init__", content)

    @patch("django_dump_die.templatetags.dump_die.INCLUDE_PRIVATE_METHODS", True)
    def test_private_members_included(self):
        """Verify private attributes are shown, with the private access modifier, when they are on."""
        content = render_dump(Branch())

        self.assertIn('<span class="access-modifier">#</span>', content)
        self.assertIn("_private_value", content)

    @patch("django_dump_die.templatetags.dump_die.INCLUDE_FUNCTIONS", True)
    @patch("django_dump_die.templatetags.dump_die.INCLUDE_MAGIC_METHODS", True)
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
