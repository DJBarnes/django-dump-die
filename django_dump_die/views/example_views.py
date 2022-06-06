"""Various example views for DumpDie library."""

import os
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.files import File
from django.db import models
from django.forms import ModelForm
from django.shortcuts import render
from types import ModuleType


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# region Example Helpers

def sample_func():
    """Sample doc string"""
    return 42


def sample_func_param(param1, *args, some_kwarg=None, **kwargs):
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

        self._sample_private_set = {'A', 'B', 'C'}
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

        self.sample_public_set = {'A', 'B', 'C'}
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
    """Sample Django Model with all field types"""
    sample_big_int = models.BigIntegerField()
    sample_binary = models.BinaryField()
    sample_bool = models.BooleanField()
    sample_char = models.CharField(max_length=200)
    sample_date = models.DateField()
    sample_datetime = models.DateTimeField()
    sample_decimal = models.DecimalField(decimal_places=8, max_digits=16)
    sample_duration = models.DurationField()
    sample_email = models.EmailField()
    sample_file = models.FileField(upload_to='uploads')
    sample_file_path = models.FilePathField(path='/')
    sample_float = models.FloatField()
    sample_ip = models.GenericIPAddressField()
    sample_image = models.ImageField(upload_to='uploads')
    sample_int = models.IntegerField()
    sample_json = models.JSONField()
    sample_pos_bint = models.PositiveBigIntegerField()
    sample_pos_int = models.PositiveIntegerField()
    sample_pos_sint = models.PositiveSmallIntegerField()
    sample_slug = models.SlugField()
    sample_sint = models.SmallIntegerField()
    sample_text = models.TextField()
    sample_time = models.TimeField()
    sample_url = models.URLField()
    sample_uuid = models.UUIDField()
    sample_foreign = models.ForeignKey(SampleRelation, on_delete=models.CASCADE, related_name='sample_foreign')
    sample_many = models.ManyToManyField(SampleManyRelation, 'sample_many')
    sample_one = models.OneToOneField(SampleOneRelation, on_delete=models.CASCADE, related_name='sample_one')


class SampleModelForm(ModelForm):
    """Sample Model Form"""
    class Meta:
        """Meta info"""
        model = SampleDjangoModel
        fields = [
            'sample_big_int',
            'sample_bool',
            'sample_char',
            'sample_date',
            'sample_datetime',
            'sample_decimal',
            'sample_duration',
            'sample_email',
            'sample_file',
            'sample_file_path',
            'sample_float',
            'sample_ip',
            'sample_image',
            'sample_int',
            'sample_json',
            'sample_pos_bint',
            'sample_pos_int',
            'sample_pos_sint',
            'sample_slug',
            'sample_sint',
            'sample_text',
            'sample_time',
            'sample_url',
            'sample_uuid',
            'sample_foreign',
            'sample_many',
            'sample_one',
        ]

# endregion Example Helpers


# region Example Views

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

    sample_date = datetime.now().date()
    sample_datetime = datetime.now()
    sample_time = datetime.now().time()

    # Call dump on all generated variables.
    dump('Displaying example of "intermediate type" object output.')

    dump('')
    dump(sample_date)
    dump(sample_datetime)
    dump(sample_time)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def complex_type_example(request):
    """Example view, rendering only "complex type" object output."""

    # Generate variables to dump.
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

    # Call dump on all generated variables.
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

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def function_type_example(request):
    """Example view, rendering only function object output."""

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
            sample_json='{"key": "my_val"}',
            sample_pos_bint=345,
            sample_pos_int=34,
            sample_pos_sint=3,
            sample_sint=3,
            sample_slug='foobar',
            sample_text='All my text',
            sample_time=datetime.now().time(),
            sample_url='https://github.com',
            sample_uuid='asdfasdfas',
        )

        dump(sample_django_model_populated)

    # Force dd to prevent further view parsing.
    dump('')
    dd('done')

    # Show that any calls after dd() end up ignored.
    return render(request, 'django_dump_die/sample.html', {})


def full_example(request):
    """Example view, rendering all examples shown in all other views, all in one page."""

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
            sample_json='{"key": "my_val"}',
            sample_pos_bint=345,
            sample_pos_int=34,
            sample_pos_sint=3,
            sample_sint=3,
            sample_slug='foobar',
            sample_text='All my text',
            sample_time=datetime.now().time(),
            sample_url='https://github.com',
            sample_uuid='asdfasdfas',
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


# endregion Example Views
