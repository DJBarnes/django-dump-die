"""Helper functions/classes, for DumpDie example views.

Exists here, so that the project only imports these on example view load.
Helps prevent package errors relating to example view load from propagating
to general package usage.
"""

# System Imports.
import copy
import os
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from importlib.util import find_spec
from pathlib import Path, PosixPath, PurePath, WindowsPath
from types import ModuleType

# Third-Party Imports.
from django.core.files import File
from django.db import models
from django.forms import ModelForm
from django.http import QueryDict
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils import timezone

# Internal Imports.
from django_dump_die.constants import PYTZ_PRESENT, ZONEINFO_PRESENT
from django_dump_die.middleware import dump

# Imports that may not be accessible, depending on local python environment setup.
if PYTZ_PRESENT:
    import pytz
if ZONEINFO_PRESENT:
    from zoneinfo import ZoneInfo


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# region Helper Functions/Classes


def sample_func():
    """Sample doc string"""
    return 42


def sample_func_param(param1, *args, some_kwarg=None, **kwargs):  # pylint: disable=unused-argument
    """Sample param doc string.

    :param param1: Doc for param1.
    """
    return f"MyReturnValue with param1 as: {param1}"


class EmptyClass:
    """Empty sample class"""

    pass  # pylint: disable=unnecessary-pass


class SimpleClass:
    """Spam sample class."""

    SAMPLE_CLASS_CONST = "Sample Class Constant Content"

    sample_class_var = 23

    def __init__(self):
        self._sample_private_module = ModuleType("django.html")
        self._sample_private_bytes = b"sample bytes"
        self._sample_private_date = datetime.now().date()
        self._sample_private_datetime = datetime.now()
        self._sample_private_time = datetime.now().time()
        self._sample_private_int = 42
        self._sample_private_float = 42.42
        self._sample_private_decimal = Decimal(42.42)
        self._sample_private_string = "Sample String Content"
        self._sample_private_none = None
        self._sample_private_bool = True

        self._sample_private_set = {"A", "B", "C"}
        self._sample_private_tuple = ("A", 12, True)
        self._sample_private_list = ["A", 12, True]
        self._sample_private_dict = {
            "first": "A",
            "second": 12,
            "third": True,
        }

        self.sample_public_module = ModuleType("django.html")
        self.sample_public_bytes = b"sample bytes"
        self.sample_public_date = datetime.now().date()
        self.sample_public_datetime = datetime.now()
        self.sample_public_time = datetime.now().time()
        self.sample_public_int = 42
        self.sample_public_float = 42.42
        self.sample_public_decimal = Decimal(42.42)
        self.sample_public_string = "Sample String Content"
        self.sample_public_none = None
        self.sample_public_bool = True

        self.sample_public_set = {"A", "B", "C"}
        self.sample_public_tuple = ("A", 12, True)
        self.sample_public_list = ["A", 12, True]
        self.sample_public_dict = {
            "first": "A",
            "second": 12,
            "third": True,
        }

    def sample_class_func(self):
        """Sample class func doc string"""
        return "Sample class result"

    def sample_class_param_func(self, arg1, *args, **kwargs):
        """Sample class param func doc string"""
        return arg1


class ComplexClass:
    """Complex class with nested instances"""

    def __init__(self):
        self._sample_private_simple_class = SimpleClass()
        self.sample_public_simple_class = SimpleClass()
        self.duplicate_sample_public_simple_class = self.sample_public_simple_class


class SampleEnum(Enum):
    """Sample Enum"""

    RED = 1
    BLUE = 2


class SampleRelation(models.Model):
    """Sample Class for foreign relation"""

    relate_name = models.TextField()


class SampleManyRelation(models.Model):
    """Sample Class for many to many relation"""

    relate_name = models.TextField()


class SampleOneRelation(models.Model):
    """Sample Class for one to one relation"""

    relate_name = models.TextField()


class SampleDjangoModel(models.Model):
    """Sample Django Model with all field types.

    To be backwards-compatible with all possible Django versions, we check for attr errors
    and skip field if error is present.

    Note: We add this logic to all fields, to account for both past-Django versions not
    having some fields, as well as hypothetical future versions of Django where one or
    more of these fields may become depreciated.
    """

    try:
        sample_big_int = models.BigIntegerField()
    except AttributeError:
        pass

    try:
        sample_binary = models.BinaryField()
    except AttributeError:
        pass

    try:
        sample_bool = models.BooleanField()
    except AttributeError:
        pass

    try:
        sample_char = models.CharField(max_length=200)
    except AttributeError:
        pass

    try:
        sample_date = models.DateField()
    except AttributeError:
        pass

    try:
        sample_datetime = models.DateTimeField()
    except AttributeError:
        pass

    try:
        sample_decimal = models.DecimalField(decimal_places=8, max_digits=16)
    except AttributeError:
        pass

    try:
        sample_duration = models.DurationField()
    except AttributeError:
        pass

    try:
        sample_email = models.EmailField()
    except AttributeError:
        pass

    try:
        sample_file = models.FileField(upload_to="uploads")
    except AttributeError:
        pass

    try:
        sample_file_path = models.FilePathField(path="/")
    except AttributeError:
        pass

    try:
        sample_float = models.FloatField()
    except AttributeError:
        pass

    try:
        sample_ip = models.GenericIPAddressField()
    except AttributeError:
        pass

    try:
        if find_spec("pillow"):
            sample_image = models.ImageField(upload_to="uploads")
    except AttributeError:
        pass

    try:
        sample_int = models.IntegerField()
    except AttributeError:
        pass

    try:
        sample_json = models.JSONField()
    except AttributeError:
        pass

    try:
        sample_pos_bint = models.PositiveBigIntegerField()
    except AttributeError:
        pass

    try:
        sample_pos_int = models.PositiveIntegerField()
    except AttributeError:
        pass

    try:
        sample_pos_sint = models.PositiveSmallIntegerField()
    except AttributeError:
        pass

    try:
        sample_sint = models.SmallIntegerField()
    except AttributeError:
        pass

    try:
        sample_slug = models.SlugField()
    except AttributeError:
        pass

    try:
        sample_text = models.TextField()
    except AttributeError:
        pass

    try:
        sample_time = models.TimeField()
    except AttributeError:
        pass

    try:
        sample_url = models.URLField()
    except AttributeError:
        pass

    try:
        sample_uuid = models.UUIDField()
    except AttributeError:
        pass

    try:
        sample_foreign = models.ForeignKey(SampleRelation, on_delete=models.CASCADE, related_name="sample_foreign")
    except AttributeError:
        pass

    try:
        sample_many = models.ManyToManyField(SampleManyRelation, "sample_many")
    except AttributeError:
        pass

    try:
        sample_one = models.OneToOneField(SampleOneRelation, on_delete=models.CASCADE, related_name="sample_one")
    except AttributeError:
        pass


class SampleModelForm(ModelForm):
    """Sample Model Form.

    To be backwards-compatible with all possible Django versions, we check for attr existence
    and include field if respective attr is present.

    Note: We add this logic to all fields, to account for both past-Django versions not
    having some fields, as well as hypothetical future versions of Django where one or
    more of these fields may become depreciated.
    """

    class Meta:
        """Meta info"""

        model = SampleDjangoModel
        fields = []

        if hasattr(SampleDjangoModel, "sample_big_int"):
            fields += ["sample_big_int"]
        if hasattr(SampleDjangoModel, "sample_bool"):
            fields += ["sample_bool"]
        if hasattr(SampleDjangoModel, "sample_char"):
            fields += ["sample_char"]
        if hasattr(SampleDjangoModel, "sample_date"):
            fields += ["sample_date"]
        if hasattr(SampleDjangoModel, "sample_datetime"):
            fields += ["sample_datetime"]
        if hasattr(SampleDjangoModel, "sample_decimal"):
            fields += ["sample_decimal"]
        if hasattr(SampleDjangoModel, "sample_duration"):
            fields += ["sample_duration"]
        if hasattr(SampleDjangoModel, "sample_email"):
            fields += ["sample_email"]
        if hasattr(SampleDjangoModel, "sample_file"):
            fields += ["sample_file"]
        if hasattr(SampleDjangoModel, "sample_file_path"):
            fields += ["sample_file_path"]
        if hasattr(SampleDjangoModel, "sample_float"):
            fields += ["sample_float"]
        if hasattr(SampleDjangoModel, "sample_ip"):
            fields += ["sample_ip"]
        if hasattr(SampleDjangoModel, "sample_image"):
            fields += ["sample_image"]
        if hasattr(SampleDjangoModel, "sample_int"):
            fields += ["sample_int"]
        if hasattr(SampleDjangoModel, "sample_json"):
            fields += ["sample_json"]
        if hasattr(SampleDjangoModel, "sample_pos_bint"):
            fields += ["sample_pos_bint"]
        if hasattr(SampleDjangoModel, "sample_pos_int"):
            fields += ["sample_pos_int"]
        if hasattr(SampleDjangoModel, "sample_pos_sint"):
            fields += ["sample_pos_sint"]
        if hasattr(SampleDjangoModel, "sample_slug"):
            fields += ["sample_slug"]
        if hasattr(SampleDjangoModel, "sample_sint"):
            fields += ["sample_sint"]
        if hasattr(SampleDjangoModel, "sample_text"):
            fields += ["sample_text"]
        if hasattr(SampleDjangoModel, "sample_time"):
            fields += ["sample_time"]
        if hasattr(SampleDjangoModel, "sample_url"):
            fields += ["sample_url"]
        if hasattr(SampleDjangoModel, "sample_uuid"):
            fields += ["sample_uuid"]
        if hasattr(SampleDjangoModel, "sample_foreign"):
            fields += ["sample_foreign"]
        if hasattr(SampleDjangoModel, "sample_many"):
            fields += ["sample_many"]
        if hasattr(SampleDjangoModel, "sample_one"):
            fields += ["sample_one"]


# endregion Helper Functions/Classes


# region DD Display Classes

SAMPLE_CONST = "Sample Constant Content"


class SimpleTypesHelper:
    """Class containing methods to dump simple types"""

    def dump_simple_types(self):
        """Dump Simple Types"""
        self.dump_non_numeric_types()
        self.dump_numeric_types()

    def dump_non_numeric_types(self):
        """Dump Non-numeric Types"""
        # Generate variables to dump.
        sample_module = ModuleType("django.html")
        sample_bytes = b"sample bytes"
        sample_string = "Sample String Content"
        sample_none = None
        sample_bool = True

        # Call dump on all generated variables.
        dump("")
        dump("Non-Numeric examples:")
        dump(SAMPLE_CONST)
        dump(sample_module)
        dump(sample_bytes)
        dump(sample_string)
        dump(sample_none)
        dump(sample_bool)

    def dump_numeric_types(self):
        """Dump Simple Numeric Types"""
        # Generate variables to dump.
        sample_int = 42
        sample_float = 42.42
        sample_decimal = Decimal(42.42)

        # Call dump on all generated variables.
        dump("")
        dump("Numeric examples:")
        dump(sample_int)
        dump(sample_float)
        dump(sample_decimal)


class IntermediateTypesHelper:
    """Class containing methods to dump intermediate types"""

    def dump_intermediate_types(self):
        """Dump Intermediate Types"""
        self.dump_bytes_array_type()

        self.dump_complex_number_type()

        self.dump_datetime_types()

        self.dump_syspath_types()

    def dump_bytes_array_type(self):
        """Dump Bytes Array Type"""

        # Generate variables to dump.
        sample_bytes_array = bytearray([8, 9, 10, 11])

        # Call dump on all generated variables.
        dump("")
        dump("Python bytes array examples:")
        dump(sample_bytes_array)

    def dump_complex_number_type(self):
        """Dump Complex Number Type"""

        # Generate variables to dump.
        sample_complex = 3 - 1j

        # Call dump on all generated variables.
        dump("")
        dump("Python complex number examples:")
        dump(sample_complex)

    def dump_datetime_types(self):
        """Dump Datetime Types"""
        # Generate variables to dump.
        sample_dt_date = datetime.now().date()
        sample_tz_date = timezone.now().date()
        sample_dt_datetime = datetime.now()
        sample_tz_datetime = timezone.now()
        sample_dt_time = datetime.now().time()
        sample_tz_time = timezone.now().time()
        sample_dt_timedelta = timedelta(days=1)
        sample_tz_timedelta = timezone.timedelta(days=2)
        if PYTZ_PRESENT:
            sample_pytz_timezone = pytz.timezone("UTC")
        if ZONEINFO_PRESENT:
            sample_zoneinfo_timezone = ZoneInfo("UTC")

        # Call dump on all generated variables.
        dump("")
        dump("Date/Time examples:")
        dump(sample_dt_date)
        dump(sample_tz_date)
        dump(sample_dt_datetime)
        dump(sample_tz_datetime)
        dump(sample_dt_time)
        dump(sample_tz_time)
        dump(sample_dt_timedelta)
        dump(sample_tz_timedelta)
        if PYTZ_PRESENT:
            dump(sample_pytz_timezone)
        if ZONEINFO_PRESENT:
            dump(sample_zoneinfo_timezone)

    def dump_syspath_types(self):
        """Dump System Path Types"""
        # Generate variables to dump.
        os_path = os.path.abspath(os.getcwd())
        pure_path = PurePath(Path.cwd())
        try:
            posix_path = PosixPath(Path.cwd())
        except NotImplementedError:
            posix_path = None
        try:
            windows_path = WindowsPath(Path.cwd())
        except NotImplementedError:
            windows_path = None

        # Call dump on all generated variables.
        dump("")
        dump("Python os.path examples:")
        dump(os.path)
        dump(os_path)

        dump("")
        dump("Python pathlib examples:")
        dump(pure_path)
        if posix_path:
            dump(posix_path)
        if windows_path:
            dump(windows_path)


class ComplexTypesHelper:
    """Class containing methods to dump complex types"""

    def __init__(self):
        """Set up some class level vars"""
        self.sample_multilevel_set = {
            (
                "A",
                12,
                True,
            ),
            (
                "B",
                24,
                False,
            ),
        }

        self.sample_multilevel_tuple = (
            {
                "first": "A",
                "second": 12,
                "third": True,
            },
            {
                "fourth": "B",
                "fifth": 24,
                "sixth": False,
            },
        )

        self.sample_multilevel_list = [
            {
                "first": "A",
                "second": 12,
                "third": True,
            },
            {
                "fourth": "B",
                "fifth": 24,
                "sixth": False,
            },
        ]

        self.sample_multilevel_dict = {
            "initial": {
                "first": "A",
                "second": 12,
                "third": True,
            },
            "secondary": {
                "fourth": "B",
                "fifth": 24,
                "sixth": False,
            },
        }

    def dump_all_complex_types(self):
        """Dump All Complex Types"""

        self.dump_all_iterables()

        self.dump_class_types()

    def dump_all_iterables(self):
        """Dump all iterable sample objects"""

        self.dump_single_level_iterables()

        self.dump_multi_level_iterables()

        self.dump_multi_level_iterable_elements()

    def dump_single_level_iterables(self):
        """Dump Single Level Iterables"""
        dump("")
        dump("Minimal object examples:")
        self.dump_set()
        self.dump_frozen_set()
        self.dump_tuple()
        self.dump_list()
        self.dump_dict()
        self.dump_querydict()
        self.dump_memory_view()
        self.dump_enum()

    def dump_multi_level_iterables(self):
        """Dump Multi Level Iterables"""
        dump("")
        dump("Nested object examples:")
        self.dump_multilevel_set()
        self.dump_multilevel_tuple()
        self.dump_multilevel_list()
        self.dump_multilevel_dict()

    def dump_multi_level_iterable_elements(self):
        """Dump Multi Level Iterable Elements"""
        dump("")
        dump("Examples of pulling items/indexes/subsets from above objects:")
        self.dump_list_element()
        self.dump_tuple_element()
        self.dump_tuple_element_function()
        self.dump_dict_element()
        self.dump_enum_element()

    def dump_set(self):
        """Dump a sample set"""
        # Generate variables to dump.
        sample_set = {"A", "B", "C"}

        # Dump variable.
        dump(sample_set)

    def dump_frozen_set(self):
        """Dump a sample frozen set"""
        # Generate variables to dump.
        sample_frozen_set = frozenset({"D", "E", "F"})

        # Dump variable.
        dump(sample_frozen_set)

    def dump_tuple(self):
        """Dump a sample tuple"""
        # Generate variables to dump.
        sample_tuple = ("A", 12, True)

        # Dump variable.
        dump(sample_tuple)

    def dump_list(self):
        """Dump a sample list"""
        # Generate variables to dump.
        sample_list = ["A", 12, True]

        # Dump variable.
        dump(sample_list)

    def dump_dict(self):
        """Dump a sample dict"""
        # Generate variables to dump.
        sample_dict = {
            "first": "A",
            "second": 12,
            "third": True,
        }

        # Dump variable.
        dump(sample_dict)

    def dump_querydict(self):
        """Dump a sample querydict"""
        # Generate variables to dump.
        sample_querydict = QueryDict('first="A"&second=12&third=True&first="B"&first="C"')

        # Dump variable.
        dump(sample_querydict)

    def dump_enum(self):
        """Dump a sample enum"""
        # Dump variable.
        dump(SampleEnum)

    def dump_memory_view(self):
        """Dump a sample memoryview"""
        # Generate variables to dump.
        sample_memory_view = memoryview(bytearray([8, 9, 10, 11]))

        # Dump variable.
        dump(sample_memory_view)

    def dump_multilevel_set(self):
        """Dump a sample multi-level set"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_set)

    def dump_multilevel_tuple(self):
        """Dump a sample multi-level tuple"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_tuple)

    def dump_multilevel_list(self):
        """Dump a sample multi-level list"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable
        dump(self.sample_multilevel_list)

    def dump_multilevel_dict(self):
        """Dump a sample multi-level dict"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_dict)

    def dump_list_element(self):
        """Dump a sample list element"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_list[0])

    def dump_tuple_element(self):
        """Dump a sample tuple element"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_tuple[0])

    def dump_tuple_element_function(self):
        """Dump a sample tuple element function"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_tuple[0].items)

    def dump_dict_element(self):
        """Dump a sample dict element"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(self.sample_multilevel_dict["initial"])

    def dump_enum_element(self):
        """Dump a sample enum element"""
        # Generate variables to dump.
        # Uses class-level vars

        # Dump variable.
        dump(SampleEnum.RED)
        dump(SampleEnum.BLUE)

    def dump_class_types(self):
        """Dump Class Types"""

        # Generate variables to dump.
        sample_empty_class = EmptyClass()
        sample_simple_class = SimpleClass()
        sample_complex_class = ComplexClass()

        # Call dump on all generated variables.
        dump("")
        dump("Class object examples:")
        dump(EmptyClass)
        dump(SimpleClass)
        dump(ComplexClass)

        dump("")
        dump("Class instance examples:")
        dump(sample_empty_class)
        dump(sample_simple_class)
        dump(sample_complex_class)
        dump(sample_complex_class)

        dump("")
        dump("Examples of pulling nested items (classes/functions/data/etc) from above classes.")
        dump(sample_complex_class._sample_private_simple_class)  # pylint: disable=protected-access
        dump(sample_complex_class.sample_public_simple_class)
        dump(sample_complex_class.sample_public_simple_class.sample_public_dict)
        dump(sample_complex_class.sample_public_simple_class.sample_public_dict["first"])
        dump(sample_simple_class.sample_class_func)
        dump(sample_simple_class.sample_class_param_func)
        dump(sample_simple_class.sample_class_func())
        dump(sample_simple_class.sample_class_param_func("test"))


class DjangoTypesHelper:
    """Class containing methods to dump various django types"""

    def dump_all_django_types(self, request):
        """Dump All Django Types"""

        self.dump_model_types()

        self.dump_django_request_response_cycle_types(request)

    def dump_model_types(self):
        """Dump Model Types"""

        # Generate variables to dump.
        sample_django_model_empty = SampleDjangoModel(id=1)  # Must provide id so many to many field can be dumped.
        sample_model_form = SampleModelForm()

        # Call dump on all generated variables.
        dump("")
        dump("Model and ModelForm class examples:")
        # TODO: See if there is a better way to "fix" this.
        # Need to remove the Many-To-Many relationship when dumping the class
        # definition (non-instance) because python's get_members can't handle a
        # m2m when the "object" does not have an id. Which it can't due to it being
        # a class definition and not an instance. Problem is solved when an instance
        # is created. See below dump of instance.
        SampleDjangoModelNoManyRelation = copy.deepcopy(SampleDjangoModel)  # pylint: disable=invalid-name
        delattr(SampleDjangoModelNoManyRelation, "sample_many")
        dump(SampleDjangoModelNoManyRelation)

        dump(SampleModelForm)

        dump("")
        dump("Model and ModelForm instance examples:")
        dump(sample_django_model_empty)
        dump(sample_model_form)

        # Populate model with values and re-check.
        dump("")
        dump("Example of model with all values populated/updated from above.")
        path = os.path.join(BASE_DIR, "../../media/uploads/test_img.png")
        with open(path, "rb") as local_file:
            django_file = File(local_file, name=os.path.basename(local_file.name))

            sample_django_model_populated = SampleDjangoModel(
                pk=1,
                sample_big_int=1,
                sample_binary=b"",
                sample_bool=True,
                sample_char="A",
                sample_date=datetime.now().date(),
                sample_datetime=datetime.now(),
                sample_decimal=Decimal(42.42),
                sample_duration=None,
                sample_email="someone@example.com",
                sample_file=django_file,
                sample_file_path="../media",
                sample_float=42.42,
                sample_image=django_file,
                sample_int=5,
                sample_ip="127.0.0.1",
                # sample_json='{"key": "my_val"}',
                # sample_pos_bint=345,
                sample_pos_int=34,
                sample_pos_sint=3,
                sample_sint=3,
                sample_slug="foobar",
                sample_text="All my text",
                sample_time=datetime.now().time(),
                sample_url="https://github.com",
                sample_uuid="asdfasdf",
            )

            dump(sample_django_model_populated)

    def dump_django_request_response_cycle_types(self, request):
        """Dump Django request-response cycle Types."""

        # Generate variables to dump.
        sample_query_dict = QueryDict("one_val=test&two_vals=one&two_vals=2")
        sample_query_dict = copy.deepcopy(sample_query_dict)
        sample_query_dict.appendlist("example_field_list", "username")
        sample_query_dict.appendlist("example_field_list", "first_name")
        sample_query_dict.appendlist("example_field_list", "last_name")
        sample_query_dict.appendlist("example_types", None)
        sample_query_dict.appendlist("example_types", True)
        sample_query_dict.appendlist("example_types", 5)
        sample_query_dict.appendlist("example_types", 3.0)

        sample_request = request
        sample_http_response = render(request, "django_dump_die/sample.html", {})
        sample_template_response = TemplateResponse(request, "django_dump_die/sample.html", {})
        sample_template_response.render()

        # Call dump on generated variables.
        dump("")
        dump("QueryDict object (GET and POST are instances of this):")
        dump(sample_query_dict)

        dump("")
        dump("Request object:")
        dump(sample_request)

        dump("")
        dump("HttpResponse object:")
        dump(sample_http_response)

        dump("")
        dump("TemplateResponse object:")
        dump(sample_template_response)


class FunctionTypesHelper:
    """Class containing methods to dump functions"""

    def dump_function_types(self):
        """Dump Function Types"""

        # Generate variables to dump.
        # None for this view.

        # Call dump on all generated variables.
        dump("")
        dump("Function examples:")
        # Minimal function with no args.
        dump(sample_func)
        # Function with args & kwargs.
        dump(sample_func_param)

        dump("")
        dump("Function call examples:")
        # Calling above "minimal function with no args".
        dump(sample_func())
        # Calling function with one arg.
        dump(sample_func_param(32))
        # Calling function with both args & kwargs.
        dump(sample_func_param("test_param", some_kwarg=True))
        # Calling function with multiple args.
        dump(sample_func_param("test_param", "extra_arg_1", 2, True))


class EdgeCasesHelper:
    """Class containing methods to dump various types as strange edge-cases"""

    def dump_edgecase_types(self):
        """Dump Edge Case Types"""
        # Call dump on problem children.
        dump("Displaying example of various edge-case output.")
        dump("")

        dump("")
        dump("Output of parens as string within dd parameters:")
        dump(")")
        dump("(")
        dump(")()))(")
        dump(")((()(")
        dump(sample_func_param("("))
        dump(sample_func_param(")"))

        dump("")
        dump(
            "Function call examples (when also passing DumpDie-specific kwargs. Those should be excluded from output):"
        )
        dump(sample_func_param(32), deepcopy=True)
        dump(sample_func_param(32), index_range=(0, 1))
        dump(sample_func_param(32), deepcopy=True, index_range=(0, 1))
        dump(sample_func_param(32, foo=12), deepcopy=True)

        dump("")
        dump("Function call examples (spanning multiple lines, in code):")
        dump("")
        dump(
            sample_func_param(
                "test_param",
                some_kwarg=False,
                extra_kwarg_1="extra_kwarg",
                extra_kwarg_2=2,
                extra_kwarg_3=3,
            )
        )
        dump(
            sample_func_param(
                "test_param",
                "extra_arg_1",
                2,
                True,
                extra_kwarg_1="extra_kwarg",
                extra_kwarg_2=2,
                extra_kwarg_3=3,
            )
        )


# endregion DD Display Classes
