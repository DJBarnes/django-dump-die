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
        sample_file = models.FileField(upload_to='uploads')
    except AttributeError:
        pass

    try:
        sample_file_path = models.FilePathField(path='/')
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
        sample_image = models.ImageField(upload_to='uploads')
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
        sample_foreign = models.ForeignKey(SampleRelation, on_delete=models.CASCADE, related_name='sample_foreign')
    except AttributeError:
        pass

    try:
        sample_many = models.ManyToManyField(SampleManyRelation, 'sample_many')
    except AttributeError:
        pass

    try:
        sample_one = models.OneToOneField(SampleOneRelation, on_delete=models.CASCADE, related_name='sample_one')
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

        if hasattr(SampleDjangoModel, 'sample_big_int'):
            fields += ['sample_big_int']
        if hasattr(SampleDjangoModel, 'sample_bool'):
            fields += ['sample_bool']
        if hasattr(SampleDjangoModel, 'sample_char'):
            fields += ['sample_char']
        if hasattr(SampleDjangoModel, 'sample_date'):
            fields += ['sample_date']
        if hasattr(SampleDjangoModel, 'sample_datetime'):
            fields += ['sample_datetime']
        if hasattr(SampleDjangoModel, 'sample_decimal'):
            fields += ['sample_decimal']
        if hasattr(SampleDjangoModel, 'sample_duration'):
            fields += ['sample_duration']
        if hasattr(SampleDjangoModel, 'sample_email'):
            fields += ['sample_email']
        if hasattr(SampleDjangoModel, 'sample_file'):
            fields += ['sample_file']
        if hasattr(SampleDjangoModel, 'sample_file_path'):
            fields += ['sample_file_path']
        if hasattr(SampleDjangoModel, 'sample_float'):
            fields += ['sample_float']
        if hasattr(SampleDjangoModel, 'sample_ip'):
            fields += ['sample_ip']
        if hasattr(SampleDjangoModel, 'sample_image'):
            fields += ['sample_image']
        if hasattr(SampleDjangoModel, 'sample_int'):
            fields += ['sample_int']
        if hasattr(SampleDjangoModel, 'sample_json'):
            fields += ['sample_json']
        if hasattr(SampleDjangoModel, 'sample_pos_bint'):
            fields += ['sample_pos_bint']
        if hasattr(SampleDjangoModel, 'sample_pos_int'):
            fields += ['sample_pos_int']
        if hasattr(SampleDjangoModel, 'sample_pos_sint'):
            fields += ['sample_pos_sint']
        if hasattr(SampleDjangoModel, 'sample_slug'):
            fields += ['sample_slug']
        if hasattr(SampleDjangoModel, 'sample_sint'):
            fields += ['sample_sint']
        if hasattr(SampleDjangoModel, 'sample_text'):
            fields += ['sample_text']
        if hasattr(SampleDjangoModel, 'sample_time'):
            fields += ['sample_time']
        if hasattr(SampleDjangoModel, 'sample_url'):
            fields += ['sample_url']
        if hasattr(SampleDjangoModel, 'sample_uuid'):
            fields += ['sample_uuid']
        if hasattr(SampleDjangoModel, 'sample_foreign'):
            fields += ['sample_foreign']
        if hasattr(SampleDjangoModel, 'sample_many'):
            fields += ['sample_many']
        if hasattr(SampleDjangoModel, 'sample_one'):
            fields += ['sample_one']
