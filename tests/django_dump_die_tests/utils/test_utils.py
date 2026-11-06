"""
Tests for the DumpDie utils that collect and prepare dumped object information.
"""

# System Imports.
import functools
import inspect
import json
from unittest.mock import patch

# Third-Party Imports.
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase, override_settings
from django.utils.functional import cached_property

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dd, dump
from django_dump_die.utils import (
    get_attribute_type,
    get_method_type,
    is_dict,
    is_query,
    safe_repr,
    safe_str,
    sanitize_index_range,
)


def get_dumped_info():
    """Return the information collected by the last dump() call, and remove it from the dumped objects."""
    return middleware.dump_objects.pop()


def get_dumped_name(info):
    """Return the dumped object name from collected dump information, as plain text."""
    return "".join((" " if part.get("space_before") else "") + part["value"] for part in info[2])


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


class BaseWithClassAttribute:
    """Parent class with a class attribute, which its subclasses inherit."""

    inherited = "inherited"


class HasAttributeTypes(BaseWithClassAttribute):
    """Class with each kind of attribute: properties, class attributes, and instance attributes."""

    shared = "shared"
    hidden = "class value"

    def __init__(self):
        self.own = "own"
        self.hidden = "instance value"

    @property
    def computed(self):
        """A property."""
        return "computed"

    @cached_property
    def django_cached(self):
        """A Django cached property."""
        return "django cached"


class HasSlots:
    """Class whose instances store their attributes in __slots__, without a __dict__."""

    __slots__ = ("slot",)
    shared = "shared"

    def __init__(self):
        self.slot = "slot"


class RaisesDoesNotExistOnRepr:
    """Object whose repr raises ObjectDoesNotExist, like a list of deleted database objects."""

    def __repr__(self):
        raise ObjectDoesNotExist("Deleted.")


class ReturnsNonStringOnStr:
    """Object whose str() is invalid, because __str__ doesn't return a string."""

    def __str__(self):
        return 42

    def __repr__(self):
        return "<ReturnsNonStringOnStr>"


@override_settings(DEBUG=True)
class DumpDieDumpedObjectInfoTestCase(SimpleTestCase):
    """Verify the information collected about dumped objects."""

    def tearDown(self):
        middleware.dump_objects.clear()
        super().tearDown()

    def test_deepcopy_of_object_that_cannot_be_copied_raises_an_error(self):
        """Verify dumping with deepcopy=True an object that can't be deep copied raises a clear TypeError."""
        generator = (value for value in [1, 2])

        with self.assertRaisesMessage(TypeError, "Object contains type that can't be deep copied."):
            dump(generator, deepcopy=True)

    @patch("django_dump_die.utils.INCLUDE_FILENAME_LINENUMBER", True)
    def test_filename_and_line_number_are_included_when_enabled(self):
        """Verify the dumped object's file and line number are collected when the setting is on."""
        value = 42
        line_number = inspect.currentframe().f_lineno + 1
        dump(value)

        info = get_dumped_info()
        self.assertEqual(info[0], __file__)
        self.assertEqual(info[1], line_number)

    def test_filename_and_line_number_are_left_out_by_default(self):
        """Verify the dumped object's file and line number are not collected by default."""
        value = 42
        dump(value)

        info = get_dumped_info()
        self.assertIsNone(info[0])
        self.assertIsNone(info[1])

    def test_name_leaves_out_dump_options(self):
        """Verify the dumped object's name doesn't include the deepcopy and index_range options."""
        value = [1, 2, 3]
        dump(value, deepcopy=True, index_range=(0, 1))

        self.assertEqual(get_dumped_name(get_dumped_info()), "value")

    def test_name_containing_an_option_name_is_kept(self):
        """Verify a dumped name that contains an option's name, but no options, is kept whole."""
        my_deepcopy_value = 42
        dump(my_deepcopy_value)

        self.assertEqual(get_dumped_name(get_dumped_info()), "my_deepcopy_value")

    def test_names_of_two_dumps_on_one_line(self):
        """Verify two dumps on one line each get their own name."""
        first, second = 1, 2
        # fmt: off
        dump(first); dump(second)  # noqa: E702
        # fmt: on

        self.assertEqual(get_dumped_name(middleware.dump_objects[0]), "first")
        self.assertEqual(get_dumped_name(middleware.dump_objects[1]), "second")

    def test_name_after_another_use_of_dump_on_the_line(self):
        """Verify a dump after dump.br(), or after an attribute named dump, on the same line gets its own name."""
        value = 42
        # fmt: off
        dump.br(); json.dumps(value); dump(value)  # noqa: E702
        # fmt: on

        self.assertEqual(get_dumped_name(get_dumped_info()), "value")

    def test_name_ignores_a_comment(self):
        """Verify a comment after the dump, even one that mentions a dump, isn't part of the name."""
        value = 42
        dump(value)  # Not dump(other).

        self.assertEqual(get_dumped_name(get_dumped_info()), "value")

    def test_name_with_a_string_containing_a_comma_and_an_equals_sign(self):
        """Verify an expression with a string that looks like options is kept whole, with its spaces."""
        value = 42
        dump(value if value else "x, y=1")

        self.assertEqual(get_dumped_name(get_dumped_info()), 'value if value else "x, y=1"')

    def test_name_of_a_call_over_several_lines(self):
        """Verify a dump call over several lines gets its argument as the name, without the line breaks."""
        values = [1, 2]
        # fmt: off
        dump(
            values[0]
            + values[1],
            deepcopy=True,
        )
        # fmt: on

        self.assertEqual(get_dumped_name(get_dumped_info()), "values[0] + values[1]")

    def test_name_of_an_argument_given_by_keyword(self):
        """Verify an object given as dump(obj=...) is named without the keyword."""
        value = 42
        dump(obj=value)

        self.assertEqual(get_dumped_name(get_dumped_info()), "value")

    def test_name_of_a_dd_after_a_dump_on_the_same_line(self):
        """Verify dd() gets its own name after a dump() on the same line."""
        first, second = 1, 2
        with self.assertRaises(middleware.DumpAndDie) as raised:
            # fmt: off
            dump(first); dd(second)  # noqa: E702
            # fmt: on

        self.assertEqual(get_dumped_name(raised.exception.object), "second")
        self.assertEqual(get_dumped_name(get_dumped_info()), "first")

    def test_name_is_unknown_without_the_source(self):
        """Verify a dump in code that has no source file, such as code run with exec(), has an unknown name."""
        exec("dump(42)", {"dump": dump})  # pylint: disable=exec-used

        self.assertEqual(get_dumped_name(get_dumped_info()), "Unknown_Object_Name")

    def test_name_is_unknown_when_dump_has_another_name(self):
        """Verify a dump called by another name has an unknown name, rather than another call's argument."""
        show = dump
        value = 42
        show(value)

        self.assertEqual(get_dumped_name(get_dumped_info()), "Unknown_Object_Name")

    @patch("django_dump_die.utils.COLORIZE_DUMPED_OBJECT_NAME", False)
    def test_name_is_one_uncolored_part_when_colorizing_is_off(self):
        """Verify the dumped object's name isn't split into colorized parts when the setting is off."""
        value = 42
        dump(value)

        self.assertEqual(get_dumped_info()[2], [{"css_class": "", "value": "value"}])


class DumpDieIndexRangeTestCase(SimpleTestCase):
    """Verify sanitizing of the index_range dump option."""

    def test_sanitize_index_range(self):
        """Verify each kind of index_range value gives the expected start and end index."""
        cases = [
            (None, (None, None)),
            ((), (None, None)),
            (3, (3, None)),
            ((2,), (2, None)),
            ((1, 4), (1, 4)),
            ((1, 4, 9), (1, 4)),
            (("1", "4"), (1, 4)),
            ((0, 3), (0, 3)),
            (("a", 3), (None, 3)),
            (([1], 3), (None, 3)),
            ((1, "b"), (1, None)),
        ]
        for index_range, expected in cases:
            with self.subTest(index_range=index_range):
                self.assertEqual(sanitize_index_range(index_range), expected)


class DumpDieSafeStringTestCase(SimpleTestCase):
    """Verify the string helpers handle objects whose str() or repr() fail."""

    def test_safe_repr_of_deleted_database_object(self):
        """Verify safe_repr shows the class when repr raises ObjectDoesNotExist."""
        self.assertEqual(safe_repr(RaisesDoesNotExistOnRepr()), f"<{RaisesDoesNotExistOnRepr} DELETED>")

    def test_safe_str_of_object_whose_str_is_invalid(self):
        """Verify safe_str falls back to repr when str() raises a TypeError."""
        self.assertEqual(safe_str(ReturnsNonStringOnStr()), "<ReturnsNonStringOnStr>")

    def test_type_checks_of_none(self):
        """Verify the query and dict checks treat None as neither."""
        self.assertFalse(is_query(None))
        self.assertFalse(is_dict(None))


class DumpDieMethodTypeTestCase(SimpleTestCase):
    """Verify detecting static and class methods."""

    def test_get_method_type(self):
        """Verify static and class methods are detected on a class and on an instance, and nothing else is."""
        for label, obj in (("class", HasMethodTypes), ("instance", HasMethodTypes())):
            cases = [
                ("static_work", "staticmethod"),
                ("class_work", "classmethod"),
                ("normal_work", None),
                ("missing", None),
                (42, None),
            ]
            for attr, expected in cases:
                with self.subTest(obj=label, attr=attr):
                    self.assertEqual(get_method_type(obj, attr), expected)


class DumpDieAttributeTypeTestCase(SimpleTestCase):
    """Verify detecting properties and class attributes."""

    def test_get_attribute_type_of_an_instance(self):
        """Verify each kind of instance member is detected, and that nothing is run to detect it."""
        obj = HasAttributeTypes()
        cases = [
            ("computed", "property"),
            ("django_cached", "cached_property"),
            ("shared", "class_attribute"),
            ("inherited", "class_attribute"),
            ("own", None),
            ("hidden", None),
            ("missing", None),
            (42, None),
        ]
        for attr, expected in cases:
            with self.subTest(attr=attr):
                self.assertEqual(get_attribute_type(obj, attr), expected)
        # The cached property wasn't computed while detecting it.
        self.assertNotIn("django_cached", vars(obj))

    def test_get_attribute_type_of_a_computed_cached_property(self):
        """Verify a cached property is still detected once its value is stored on the instance."""
        obj = HasAttributeTypes()
        self.assertEqual(obj.django_cached, "django cached")
        self.assertIn("django_cached", vars(obj))
        self.assertEqual(get_attribute_type(obj, "django_cached"), "cached_property")

    def test_get_attribute_type_of_a_functools_cached_property(self):
        """Verify functools.cached_property is detected, before and after it is computed."""
        if not hasattr(functools, "cached_property"):
            self.skipTest("functools.cached_property was added in Python 3.8.")

        class HasFunctoolsCachedProperty:
            """Class with a functools cached property."""

            @functools.cached_property
            def cached(self):
                """A functools cached property."""
                return "cached"

        obj = HasFunctoolsCachedProperty()
        self.assertEqual(get_attribute_type(obj, "cached"), "cached_property")
        self.assertEqual(obj.cached, "cached")
        self.assertEqual(get_attribute_type(obj, "cached"), "cached_property")

    def test_get_attribute_type_of_slots(self):
        """Verify __slots__ members are the instance's own, while other class attributes are still detected."""
        obj = HasSlots()
        self.assertIsNone(get_attribute_type(obj, "slot"))
        self.assertEqual(get_attribute_type(obj, "shared"), "class_attribute")

    def test_get_attribute_type_of_a_class(self):
        """Verify a dumped class marks its properties, but doesn't mark its attributes as class attributes."""
        cases = [
            ("computed", "property"),
            ("django_cached", "cached_property"),
            ("shared", None),
            ("inherited", None),
        ]
        for attr, expected in cases:
            with self.subTest(attr=attr):
                self.assertEqual(get_attribute_type(HasAttributeTypes, attr), expected)
