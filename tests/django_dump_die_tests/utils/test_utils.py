"""
Tests for the DumpDie utils that collect and prepare dumped object information.
"""

# System Imports.
import functools
import inspect
import json

# Third-Party Imports.
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.safestring import SafeData

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dd, dump
from django_dump_die.views.example_helpers import SampleRelation
from django_dump_die.utils import (
    get_attribute_type,
    get_callable_name,
    get_method_type,
    is_sensitive_name,
    is_dict,
    is_iterable,
    is_query,
    safe_repr,
    safe_str,
    sanitize_index_range,
)


def get_dumped_info():
    """Return the information collected by the last dump() call, and remove it from the dumped objects."""
    return middleware.get_dump_objects().pop()


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


class ReturnsSafeStringOnReprAndStr:
    """Object whose repr and str are marked safe, as when built with format_html()."""

    def __repr__(self):
        return format_html("<b>{0}</b>", "repr")

    def __str__(self):
        return format_html("<b>{0}</b>", "str")


class ReturnsNonStringOnStr:
    """Object whose str() is invalid, because __str__ doesn't return a string."""

    def __str__(self):
        return 42  # noqa: PLE0307 - Not a string, on purpose.

    def __repr__(self):
        return "<ReturnsNonStringOnStr>"


@override_settings(DEBUG=True)
class DumpDieDumpedObjectInfoTestCase(SimpleTestCase):
    """Verify the information collected about dumped objects."""

    def tearDown(self):
        middleware.get_dump_objects().clear()
        super().tearDown()

    def test_deepcopy_of_object_that_cannot_be_copied_raises_an_error(self):
        """Verify dumping with deepcopy=True an object that can't be deep copied raises a clear TypeError."""
        generator = (value for value in [1, 2])

        with self.assertRaisesMessage(TypeError, "Object contains type that can't be deep copied."):
            dump(generator, deepcopy=True)

    def test_deepcopy_is_off_by_default(self):
        """Verify an object is dumped as itself, not a copy, by default, so later changes show in the dump."""
        values = [1, 2]
        dump(values)

        info = get_dumped_info()
        self.assertIs(info[3], values)
        self.assertIsNone(info[7])

    @override_settings(DJANGO_DD_DEEPCOPY=True)
    def test_deepcopy_setting_dumps_a_copy(self):
        """Verify the setting dumps a copy of the object as it was, and keeps the original for its uniques."""
        values = [1, [2]]
        dump(values)
        values[1].append(3)

        info = get_dumped_info()
        self.assertEqual(info[3], [1, [2]])
        self.assertIsNot(info[3], values)
        self.assertIs(info[7], values)
        self.assertEqual(get_dumped_name(info), "values")

    @override_settings(DJANGO_DD_DEEPCOPY=True)
    def test_deepcopy_argument_overrides_the_setting(self):
        """Verify deepcopy=False in a call dumps the object itself, even with the setting on."""
        values = [1, 2]
        dump(values, deepcopy=False)

        info = get_dumped_info()
        self.assertIs(info[3], values)
        self.assertIsNone(info[7])

    @override_settings(DJANGO_DD_DEEPCOPY=True)
    def test_deepcopy_setting_dumps_an_object_that_cannot_be_copied_as_it_is(self):
        """Verify the setting dumps an object that can't be deep copied as itself, with a note, without an error."""
        generator = (value for value in [1, 2])
        dump(generator)

        info = get_dumped_info()
        self.assertIs(info[3], generator)
        self.assertIsNone(info[7])
        note = info[2][-1]
        self.assertEqual(note["value"], "(not copied)")
        self.assertTrue(note["space_before"])
        self.assertIn("DJANGO_DD_DEEPCOPY is on, but this object couldn't be deep copied", note["title"])
        self.assertIn("TypeError: ", note["title"])
        self.assertEqual(get_dumped_name(info), "generator (not copied)")

    @override_settings(DJANGO_DD_INCLUDE_FILENAME_LINENUMBER=True)
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

        self.assertEqual(get_dumped_name(middleware.get_dump_objects()[0]), "first")
        self.assertEqual(get_dumped_name(middleware.get_dump_objects()[1]), "second")

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
        exec("dump(42)", {"dump": dump})

        self.assertEqual(get_dumped_name(get_dumped_info()), "Unknown_Object_Name")

    def test_name_is_unknown_when_dump_has_another_name(self):
        """Verify a dump called by another name has an unknown name, rather than another call's argument."""
        show = dump
        value = 42
        show(value)

        self.assertEqual(get_dumped_name(get_dumped_info()), "Unknown_Object_Name")

    @override_settings(DJANGO_DD_COLORIZE_DUMPED_OBJECT_NAME=False)
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

    def test_safe_repr_and_safe_str_return_plain_strings(self):
        """Verify a repr or str marked safe comes back as a plain str, so that templates escape it."""
        obj = ReturnsSafeStringOnReprAndStr()
        for label, function, expected in (("repr", safe_repr, "<b>repr</b>"), ("str", safe_str, "<b>str</b>")):
            with self.subTest(function=label):
                text = function(obj)

                self.assertEqual(text, expected)
                self.assertIs(type(text), str)
                self.assertNotIsInstance(text, SafeData)

    def test_type_checks_of_none(self):
        """Verify the query and dict checks treat None as neither."""
        self.assertFalse(is_query(None))
        self.assertFalse(is_dict(None))


class HasInvalidSignature:
    """Callable whose signature can't be read, because its __signature__ isn't a Signature."""

    __signature__ = "not a signature"

    def __call__(self):
        """Do nothing."""


class DumpDieCallableNameTestCase(SimpleTestCase):
    """Verify the name shown for a dumped callable."""

    def test_callable_name_has_its_signature(self):
        """Verify the signature follows the callable's name."""
        self.assertEqual(get_callable_name("sample", lambda first, second=2: None), "sample(first, second=2)")

    def test_callable_without_a_signature_gets_empty_parentheses(self):
        """Verify a callable whose signature can't be read gets empty parentheses, instead of failing the dump."""
        self.assertEqual(get_callable_name("sample", HasInvalidSignature()), "sample()")


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


class DumpDieSensitiveNameTestCase(SimpleTestCase):
    """Verify which attribute, key, and function names have their values hidden."""

    def test_is_sensitive_name(self):
        """Verify sensitive words, keys, and request headers are hidden, and similar harmless names aren't."""
        cases = [
            # Settings and request.META entries that Django's debug page hides.
            ("SECRET_KEY", True),
            ("SECRET_KEY_FALLBACKS", True),
            ("PASSWORD", True),
            ("EMAIL_HOST_PASSWORD", True),
            ("HTTP_COOKIE", True),
            ("HTTP_AUTHORIZATION", True),
            ("HTTP_X_API_KEY", True),
            # Attribute and key names.
            ("password", True),
            ("db_pass", True),
            ("access_token", True),
            ("csrfmiddlewaretoken", True),
            ("csrftoken", True),
            ("myApiKey", True),
            ("privateKey", True),
            ("session_key", True),
            ("sessionid", True),
            ("Cookie", True),
            ("get_secret", True),
            # Names that only look similar.
            ("key", False),
            ("primary_key", False),
            ("cache_key", False),
            ("KEY_PREFIX", False),
            ("author", False),
            ("is_authenticated", False),
            ("passenger", False),
            ("tokenize", False),
            ("COOKIES", False),
            ("CSRF_COOKIE_NAME", False),
            ("SESSION_COOKIE_AGE", False),
            ("DATABASES", False),
            # Names that aren't strings, such as list indexes and dict keys of other types.
            (3, False),
            (None, False),
        ]
        for name, expected in cases:
            with self.subTest(name=name):
                self.assertEqual(is_sensitive_name(name), expected)

    @override_settings(SESSION_COOKIE_NAME="my_session")
    def test_session_cookie_name_setting_is_sensitive(self):
        """Verify the session cookie is hidden by the name it is given in the SESSION_COOKIE_NAME setting."""
        self.assertTrue(is_sensitive_name("my_session"))

    @override_settings(DJANGO_DD_SHOW_SENSITIVE_VALUES=True)
    def test_nothing_is_sensitive_when_shown(self):
        """Verify no name is hidden when the setting to show sensitive values is on."""
        for name in ("SECRET_KEY", "password", "sessionid", "HTTP_COOKIE"):
            with self.subTest(name=name):
                self.assertFalse(is_sensitive_name(name))


class DumpDieIterableQueryTestCase(TestCase):
    """Verify which queries count as iterable, without running them where possible."""

    def test_queryset_is_iterable_without_a_query(self):
        """Verify a QuerySet is iterable without running its query, which would load every row."""
        with self.assertNumQueries(0):
            self.assertTrue(is_iterable(SampleRelation.objects.all()))

    def test_raw_queryset_whose_query_fails_is_not_iterable(self):
        """Verify a raw QuerySet, which runs its query to be iterated, isn't iterable if the query fails."""
        # The sample models have no database table.
        self.assertFalse(is_iterable(SampleRelation.objects.raw("SELECT * FROM django_dump_die_samplerelation")))
