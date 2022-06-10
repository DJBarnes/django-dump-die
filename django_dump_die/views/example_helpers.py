"""Helper functions/classes, for DumpDie example views.

Exists here, so that the project only imports these on example view load.
Helps prevent package errors relating to example view load from propagating
to general package usage.
"""

import os
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.files import File
from django.db import models
from django.forms import ModelForm
from types import ModuleType


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
    # sample_json = models.JSONField() #  Commented out until support for Django 3.0 is dropped.
    # sample_pos_bint = models.PositiveBigIntegerField() #  Commented out until support for Django 3.0 is dropped.
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
            # 'sample_json', #  Commented out until support for Django 3.0 is dropped.
            # 'sample_pos_bint', #  Commented out until support for Django 3.0 is dropped.
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
