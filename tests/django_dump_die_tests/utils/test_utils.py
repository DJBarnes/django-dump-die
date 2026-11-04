"""
Tests for the DumpDie utils that collect and prepare dumped object information.
"""

# System Imports.
import inspect
from unittest.mock import patch

# Third-Party Imports.
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase, override_settings

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dump
from django_dump_die.utils import get_method_type, is_dict, is_query, safe_repr, safe_str, sanitize_index_range


def get_dumped_info():
    """Return the information collected by the last dump() call, and remove it from the dumped objects."""
    return middleware.dump_objects.pop()


def get_dumped_name(info):
    """Return the dumped object name from collected dump information, as plain text."""
    return "".join(part["value"] for part in info[2])


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
        for obj in (HasMethodTypes, HasMethodTypes()):
            cases = [
                ("static_work", "staticmethod"),
                ("class_work", "classmethod"),
                ("normal_work", None),
                ("missing", None),
                (42, None),
            ]
            for attr, expected in cases:
                with self.subTest(obj=obj, attr=attr):
                    self.assertEqual(get_method_type(obj, attr), expected)
