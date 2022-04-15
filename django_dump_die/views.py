"""Views for DumpDie"""
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from types import ModuleType


def dd_view(request, objects):
    """
    Return dump die view.
    :param request: Request object.
    :param objects: Set of objects to dump.
    """
    # Get user theme choices.
    force_light_theme = getattr(settings, 'DJANGO_DD_FORCE_LIGHT_THEME', False)
    force_dark_theme = getattr(settings, 'DJANGO_DD_FORCE_DARK_THEME', False)
    custom_color_theme = getattr(settings, 'DJANGO_DD_COLOR_SCHEME', None)
    multiline_function_docs = getattr(settings, 'DJANGO_DD_MULTILINE_FUNCTION_DOCS', False)

    # Validate chosen themes.
    if force_light_theme and force_dark_theme:
        raise ValueError("You can't force both light and dark themes.")

    # Render template.
    return render(request, 'django_dump_die/dd.html', {
        'objects': objects,
        'force_light_theme': force_light_theme,
        'force_dark_theme': force_dark_theme,
        'custom_color_theme': custom_color_theme,
        'multiline_function_docs': multiline_function_docs,
    })


def example(request):
    """Example Test"""

    SAMPLE_CONST = 'Sample Constant Content'
    sample_module = ModuleType('django.html')
    sample_bytes = b'sample bytes'
    sample_date = datetime.now().date()
    sample_datetime = datetime.now()
    sample_time = datetime.now().time()
    sample_int = 42
    sample_float = 42.42
    sample_decimal = Decimal(42.42)
    sample_string = 'Sample String Content'
    sample_none = None
    sample_bool = True

    sample_set = {'A', 'B', 'C',}
    sample_tuple = ('A', 12, True)
    sample_list = ['A', 12, True]
    sample_dict = {
        'first': 'A',
        'second': 12,
        'third': True,
    }

    sample_complex_set = {
        (
            'A',
            12,
            True,
        ),
        (
            'B',
            24,
            False,
        ),
    }

    sample_complex_tuple = (
        {
            'first': 'A',
            'second': 12,
            'third': True,
        },
        {
            'fourth': 'B',
            'fifth': 24,
            'sixth': False,
        },
    )

    sample_complex_list = [
        {
            'first': 'A',
            'second': 12,
            'third': True,
        },
        {
            'fourth': 'B',
            'fifth': 24,
            'sixth': False,
        },
    ]

    sample_complex_dict = {
        'initial': {
            'first': 'A',
            'second': 12,
            'third': True,
        },
        'secondary': {
            'fourth': 'B',
            'fifth': 24,
            'sixth': False,
        },
    }

    def sample_func():
        """Sample doc string"""
        return 42

    def sample_func_param(param1, *args, **kwargs):
        """Sample param doc string"""
        return param1

    class EmptyClass:
        """Empty sample class"""
        pass


    class SimpleClass:
        """Spam sample class."""

        SAMPLE_CLASS_CONST = 'Sample Class Constant Content'

        sample_class_var = 23

        def __init__(self):
            self._sample_private_module = ModuleType('django.html')
            self._sample_private_bytes = b'sample bytes'
            self._sample_private_date = datetime.now().date()
            self._sample_private_datetime = datetime.now()
            self._sample_private_time = datetime.now().time()
            self._sample_private_int = 42
            self._sample_private_float = 42.42
            self._sample_private_decimal = Decimal(42.42)
            self._sample_private_string = 'Sample String Content'
            self._sample_private_none = None
            self._sample_private_bool = True

            self._sample_private_set = {'A', 'B', 'C',}
            self._sample_private_tuple = ('A', 12, True)
            self._sample_private_list = ['A', 12, True]
            self._sample_private_dict = {
                'first': 'A',
                'second': 12,
                'third': True,
            }

            self.sample_public_module = ModuleType('django.html')
            self.sample_public_bytes = b'sample bytes'
            self.sample_public_date = datetime.now().date()
            self.sample_public_datetime = datetime.now()
            self.sample_public_time = datetime.now().time()
            self.sample_public_int = 42
            self.sample_public_float = 42.42
            self.sample_public_decimal = Decimal(42.42)
            self.sample_public_string = 'Sample String Content'
            self.sample_public_none = None
            self.sample_public_bool = True

            self.sample_public_set = {'A', 'B', 'C',}
            self.sample_public_tuple = ('A', 12, True)
            self.sample_public_list = ['A', 12, True]
            self.sample_public_dict = {
                'first': 'A',
                'second': 12,
                'third': True,
            }

        def sample_class_func(self):
            """Sample class func doc string"""
            return 'Sample class result'

        def sample_class_param_func(self, arg1, *args, **kwargs):
            """Sample class param func doc string"""
            return arg1


    class ComplexClass:
        """Complex class with nested instances"""

        def __init__(self):
            self._sample_private_simple_class = SimpleClass()
            self.sample_public_simple_class = SimpleClass()
            self.duplicate_sample_public_simple_class = self.sample_public_simple_class


    sample_empty_class = EmptyClass()
    sample_simple_class = SimpleClass()
    sample_complex_class = ComplexClass()


    dump(SAMPLE_CONST)
    dump(sample_module)
    dump(sample_bytes)
    dump(sample_date)
    dump(sample_datetime)
    dump(sample_time)
    dump(sample_int)
    dump(sample_float)
    dump(sample_decimal)
    dump(sample_string)
    dump(sample_none)
    dump(sample_bool)

    dump(sample_set)
    dump(sample_tuple)
    dump(sample_list)
    dump(sample_dict)

    dump(sample_complex_set)
    dump(sample_complex_tuple)
    dump(sample_complex_list)
    dump(sample_complex_dict)

    dump(sample_func)
    dump(sample_func_param)

    dump(sample_empty_class)
    dump(sample_simple_class)
    dump(sample_complex_class)
    dump(sample_complex_class)

    dump(sample_complex_list[0])
    dump(sample_complex_tuple[0])
    dump(sample_complex_dict['initial'])

    dump(sample_complex_class._sample_private_simple_class)
    dump(sample_complex_class.sample_public_simple_class)
    dump(sample_complex_class.sample_public_simple_class.sample_public_dict)
    dump(sample_complex_class.sample_public_simple_class.sample_public_dict['first'])

    dump(EmptyClass)
    dump(SimpleClass)
    dump(ComplexClass)

    dd('done')

    return HttpResponse("Example")
