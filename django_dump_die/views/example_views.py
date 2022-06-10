"""Various example views for DumpDie library."""

import os
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.files import File
from django.shortcuts import render
from pathlib import Path, PosixPath, PurePath, WindowsPath
from types import ModuleType


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def index(request):
    """Index view, to easily navigate to example views."""
    return render(request, 'django_dump_die/index.html')


def simple_type_example(request):
    """Example view, rendering only "simple type" object output."""

    # Generate variables to dump.
    SAMPLE_CONST = 'Sample Constant Content'
    sample_module = ModuleType('django.html')
    sample_bytes = b'sample bytes'
    sample_int = 42
    sample_float = 42.42
    sample_decimal = Decimal(42.42)
    sample_string = 'Sample String Content'
    sample_none = None
    sample_bool = True

    # Call dump on all generated variables.
    dump('Displaying example of "simple type" object output.')

    dump('')
    dump(SAMPLE_CONST)
    dump(sample_module)
    dump(sample_bytes)
    dump(sample_int)
    dump(sample_float)
    dump(sample_decimal)
    dump(sample_string)
    dump(sample_none)
    dump(sample_bool)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def intermediate_type_example(request):
    """Example view, rendering only "intermediate type" object output."""

    # Generate variables to dump.
    sample_bytes_array = bytearray([8, 9, 10, 11])
    sample_memory_view = memoryview(sample_bytes_array)
    sample_complex = 3-1j

    sample_date = datetime.now().date()
    sample_datetime = datetime.now()
    sample_time = datetime.now().time()
    sample_timedelta = timedelta(days=1)

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
    dump('Displaying example of "intermediate type" object output.')

    dump('')
    dump('Python type examples:')
    dump(sample_bytes_array)
    dump(sample_complex)

    dump('')
    dump('Date/Time examples:')
    dump(sample_date)
    dump(sample_datetime)
    dump(sample_time)
    dump(sample_timedelta)

    dump('')
    dump('Python os.path examples:')
    dump(os.path)
    dump(os_path)

    dump('')
    dump('Python pathlib examples:')
    dump(PurePath)
    dump(pure_path)
    if posix_path:
        dump(PosixPath)
        dump(posix_path)
    if windows_path:
        dump(WindowsPath)
        dump(windows_path)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example(request):
    """Example view, rendering only "complex type" object output."""

    # Generate variables to dump.
    sample_set = {'A', 'B', 'C'}
    sample_frozen_set = frozenset({'D', 'E', 'F'})
    sample_tuple = ('A', 12, True)
    sample_list = ['A', 12, True]
    sample_dict = {
        'first': 'A',
        'second': 12,
        'third': True,
    }
    sample_memory_view = memoryview(bytearray([8, 9, 10, 11]))

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

    # Call dump on all generated variables.
    dump('Displaying example of "complex type" object output.')

    dump('')
    dump('Basic object examples:')
    dump(sample_set)
    dump(sample_frozen_set)
    dump(sample_tuple)
    dump(sample_list)
    dump(sample_dict)
    dump(sample_memory_view)

    dump('')
    dump('Elaborate object examples:')
    dump(sample_complex_set)
    dump(sample_complex_tuple)
    dump(sample_complex_list)
    dump(sample_complex_dict)

    dump('')
    dump('Examples of pulling items/indexes/subsets from above objects:')
    dump(sample_complex_list[0])
    dump(sample_complex_tuple[0])
    dump(sample_complex_tuple[0].items)
    dump(sample_complex_dict['initial'])

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def function_type_example(request):
    """Example view, rendering only function object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import sample_func, sample_func_param

    # Generate variables to dump.
    # None for this view. All defined above, at module level.

    # Call dump on all generated variables.
    dump('Displaying example of function object output.')

    dump('')
    dump('Function examples:')
    dump(sample_func)
    dump(sample_func_param)

    dump('')
    dump('Function call examples:')
    dump(sample_func())
    dump(sample_func_param(32))
    dump(sample_func_param('test_param', some_kwarg=True))
    dump(sample_func_param('test_param', 'extra_arg_1', 2, True))

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def class_type_example(request):
    """Example view, rendering only class object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import ComplexClass, EmptyClass, SimpleClass

    # Generate variables to dump.
    sample_empty_class = EmptyClass()
    sample_simple_class = SimpleClass()
    sample_complex_class = ComplexClass()

    # Call dump on all generated variables.
    dump('Displaying example of class object output.')

    dump('')
    dump('Class object examples:')
    dump(EmptyClass)
    dump(SimpleClass)
    dump(ComplexClass)

    dump('')
    dump('Class instance examples:')
    dump(sample_empty_class)
    dump(sample_simple_class)
    dump(sample_complex_class)
    dump(sample_complex_class)

    dump('')
    dump('Examples of pulling nested items (classes/functions/data/etc) from above classes.')
    dump(sample_complex_class._sample_private_simple_class)
    dump(sample_complex_class.sample_public_simple_class)
    dump(sample_complex_class.sample_public_simple_class.sample_public_dict)
    dump(sample_complex_class.sample_public_simple_class.sample_public_dict['first'])
    dump(sample_simple_class.sample_class_func)
    dump(sample_simple_class.sample_class_param_func)
    dump(sample_simple_class.sample_class_func())
    dump(sample_simple_class.sample_class_param_func('test'))

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def django_model_type_example(request):
    """Example view, rendering only Django model object output."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import SampleDjangoModel, SampleModelForm

    # Generate variables to dump.
    sample_django_model_empty = SampleDjangoModel(id=1)  # Must provide id so many to many field can be dumped.
    sample_model_form = SampleModelForm()

    # Call dump on all generated variables.
    dump('Displaying example of Django model object output.')

    dump('')
    dump('Model and ModelForm class example:')
    dump(SampleDjangoModel)
    dump(SampleModelForm)

    dump('')
    dump('Model and ModelForm instance example:')
    dump(sample_django_model_empty)
    dump(sample_model_form)

    # Populate model with values and re-check.
    dump('')
    dump('Example of model with all values populated/updated from above.')
    path = os.path.join(BASE_DIR, '../../media/uploads/test_img.png')
    with open(path, 'rb') as local_file:
        django_file = File(local_file, name=os.path.basename(local_file.name))

        sample_django_model_populated = SampleDjangoModel(
            pk=1,
            sample_big_int=1,
            sample_binary=b'',
            sample_bool=True,
            sample_char='A',
            sample_date=datetime.now().date(),
            sample_datetime=datetime.now(),
            sample_decimal=Decimal(42.42),
            sample_duration=None,
            sample_email='someone@example.com',
            sample_file=django_file,
            sample_file_path='../media',
            sample_float=42.42,
            sample_image=django_file,
            sample_int=5,
            sample_ip='127.0.0.1',
            # sample_json='{"key": "my_val"}',
            # sample_pos_bint=345,
            sample_pos_int=34,
            sample_pos_sint=3,
            sample_sint=3,
            sample_slug='foobar',
            sample_text='All my text',
            sample_time=datetime.now().time(),
            sample_url='https://github.com',
            sample_uuid='asdfasdf',
        )

        dump(sample_django_model_populated)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def system_path_example(request):
    """Example view, rendering only "system path" object output."""

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
    dump('Displaying example of "system path" object output.')

    dump('')
    dump('Python os.path examples:')
    dump(os.path)
    dump(os_path)

    dump('')
    dump('Python pathlib examples:')
    dump(PurePath)
    dump(pure_path)
    if posix_path:
        dump(PosixPath)
        dump(posix_path)
    if windows_path:
        dump(WindowsPath)
        dump(windows_path)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def full_example(request):
    """Example view, rendering all examples shown in all other views, all in one page."""

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import sample_func, sample_func_param
    from .example_helpers import ComplexClass, EmptyClass, SimpleClass
    from .example_helpers import SampleDjangoModel, SampleModelForm

    # Generate variables to dump.
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

    sample_set = {'A', 'B', 'C'}
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

    sample_empty_class = EmptyClass()
    sample_simple_class = SimpleClass()
    sample_complex_class = ComplexClass()

    sample_django_model_empty = SampleDjangoModel(id=1)  # Must provide id so many to many field can be dumped.
    sample_model_form = SampleModelForm()

    # Call dump on all generated variables.
    dump('Displaying example of "simple type" object output.')
    dump('')
    dump(SAMPLE_CONST)
    dump(sample_module)
    dump(sample_bytes)
    dump(sample_int)
    dump(sample_float)
    dump(sample_decimal)
    dump(sample_string)
    dump(sample_none)
    dump(sample_bool)

    dump('')
    dump('')
    dump('')
    dump('')
    dump('Displaying example of "intermediate type" object output.')
    dump('')
    dump(sample_date)
    dump(sample_datetime)
    dump(sample_time)

    dump('')
    dump('')
    dump('')
    dump('')
    dump('Displaying example of "complex type" object output.')
    dump('')
    dump('Basic object examples:')
    dump(sample_set)
    dump(sample_tuple)
    dump(sample_list)
    dump(sample_dict)
    dump('')
    dump('Elaborate object examples:')
    dump(sample_complex_set)
    dump(sample_complex_tuple)
    dump(sample_complex_list)
    dump(sample_complex_dict)
    dump('')
    dump('Examples of pulling items/indexes/subsets from above objects:')
    dump(sample_complex_list[0])
    dump(sample_complex_tuple[0])
    dump(sample_complex_tuple[0].items)
    dump(sample_complex_dict['initial'])

    dump('')
    dump('')
    dump('')
    dump('')
    dump('Displaying example of function object output.')
    dump('')
    dump('Function examples:')
    dump(sample_func)
    dump(sample_func_param)
    dump('')
    dump('Function call examples:')
    dump(sample_func())
    dump(sample_func_param(32))
    dump(sample_func_param('test_param', some_kwarg=True))
    dump(sample_func_param('test_param', 'extra_arg_1', 2, True))

    dump('')
    dump('')
    dump('')
    dump('')
    dump('Displaying example of class object output.')
    dump('')
    dump('Class object examples:')
    dump(EmptyClass)
    dump(SimpleClass)
    dump(ComplexClass)
    dump('')
    dump('Class instance examples:')
    dump(sample_empty_class)
    dump(sample_simple_class)
    dump(sample_complex_class)
    dump(sample_complex_class)
    dump('')
    dump('Examples of pulling nested items (classes/functions/data/etc) from above classes.')
    dump(sample_complex_class._sample_private_simple_class)
    dump(sample_complex_class.sample_public_simple_class)
    dump(sample_complex_class.sample_public_simple_class.sample_public_dict)
    dump(sample_complex_class.sample_public_simple_class.sample_public_dict['first'])
    dump(sample_simple_class.sample_class_func)
    dump(sample_simple_class.sample_class_param_func)
    dump(sample_simple_class.sample_class_func())
    dump(sample_simple_class.sample_class_param_func('test'))

    dump('')
    dump('')
    dump('')
    dump('')
    dump('Displaying example of Django model object output.')
    dump('')
    dump('Model and ModelForm class example:')
    dump(SampleDjangoModel)
    dump(SampleModelForm)
    dump('')
    dump('Model and ModelForm instance example:')
    dump(sample_django_model_empty)
    dump(sample_model_form)
    # Populate model with values and re-check.
    dump('')
    dump('Example of model with all values populated/updated from above.')
    path = os.path.join(BASE_DIR, '../../media/uploads/test_img.png')
    with open(path, 'rb') as local_file:
        django_file = File(local_file, name=os.path.basename(local_file.name))

        sample_django_model_populated = SampleDjangoModel(
            pk=1,
            sample_big_int=1,
            sample_binary=b'',
            sample_bool=True,
            sample_char='A',
            sample_date=datetime.now().date(),
            sample_datetime=datetime.now(),
            sample_decimal=Decimal(42.42),
            sample_duration=None,
            sample_email='someone@example.com',
            sample_file=django_file,
            sample_file_path='../media',
            sample_float = 42.42,
            sample_image=django_file,
            sample_int=5,
            sample_ip='127.0.0.1',
            # sample_json='{"key": "my_val"}',
            # sample_pos_bint=345,
            sample_pos_int=34,
            sample_pos_sint=3,
            sample_sint=3,
            sample_slug='foobar',
            sample_text='All my text',
            sample_time=datetime.now().time(),
            sample_url='https://github.com',
            sample_uuid='asdfasdf',
        )

        dump(sample_django_model_populated)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {'sample_simple_class': sample_simple_class})


def edge_case_example(request):
    """Example view, rendering various edge-case output.

    These are output types that don't necessarily belong in the other example views, but have
    resulted in errors/bad output, in the past.

    This view allows easily checking them to make sure they are still handled correctly.
    """

    # Import applicable helper functions/classes.
    # Imported here so that these are only loaded on view access, and not package initialization.
    from .example_helpers import sample_func_param

    # Call dump on problem children.
    dump('Displaying example of various edge-case output.')

    dump('')
    dump('Output of parens as string within dd parameters:')
    dump(')')
    dump('(')
    dump(')()))(')
    dump(')((()(')
    dump(sample_func_param('('))
    dump(sample_func_param(')'))

    dump('')
    dump('Function call examples (when also passing DumpDie-specific kwargs. Those should be excluded from output):')
    dump(sample_func_param(32), deepcopy=True)
    dump(sample_func_param(32), index_range=(0, 1))
    dump(sample_func_param(32), deepcopy=True, index_range=(0, 1))
    dump(sample_func_param(32, foo=12), deepcopy=True)

    dump('')
    dump('Function call examples (spanning multiple lines, in code):')
    dump(sample_func_param(
        'test_param',
        some_kwarg=False,
        extra_kwarg_1='extra_kwarg',
        extra_kwarg_2=2,
        extra_kwarg_3=3,
    ))
    dump(sample_func_param(
        'test_param',
        'extra_arg_1',
        2,
        True,
        extra_kwarg_1='extra_kwarg',
        extra_kwarg_2=2,
        extra_kwarg_3=3,
    ))

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})
