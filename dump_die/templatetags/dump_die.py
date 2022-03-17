"""Template Tags for DumpDie"""

import inspect
import re
import types

from collections.abc import Sequence
from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms.boundfield import BoundField

register = template.Library()

SIMPLE_TYPES = [
    str,
    bytes,
    int,
    float,
    bool,
    types.ModuleType,
    BoundField,
]

SIMPLE_TYPE_NAMES = [
    'Cell', # openpyxl Cell
]


def get_class_name(obj):
    """Get class name of an object"""
    name = None
    try:
        name = obj.__class__.__name__
    except Exception:
        pass
    return name


def safe_repr(obj):
    """Call repr() and ignore ObjectDoesNotExist."""
    str_obj = ''
    try:
        str_obj = repr(obj)
    except ObjectDoesNotExist:
        # L8R: A list of deleted db objects will cause repr(list) to fail.
        # We should detect this and print out the __class__ of the contents of
        # the list.
        str_obj = '<{} DELETED>'.format(obj.__class__)

    return str_obj

def safe_str(obj):
    """Call str() and ignore TypeErrors if str() doesn't return a string."""
    str_obj = ''
    try:
        str_obj = str(obj)
    except (TypeError, ObjectDoesNotExist):
        str_obj = safe_repr(obj)

    return str_obj

def _in_dir(obj, attr):
    """Simpler hasattr() function without side effects."""
    return attr in dir(obj)

def _is_iterable(obj):
    """Return True if object can be iterated"""
    try:
        iter(obj)
    except TypeError:
        return False
    return True

def _is_indexable(obj):
    """Return True if object can be indexed"""
    if isinstance(obj, Sequence):
        return True
    else:
        return False

def _is_query(obj):
    """Return True if object is most likely a query"""
    return _in_dir(obj, 'as_manager') and _in_dir(obj, 'all') and _in_dir(obj, 'filter')

def _is_dict(obj):
    """Return True if object is most likely a dict"""
    return _in_dir(obj, 'items') and _in_dir(obj, 'keys') and _in_dir(obj, 'values')

def _is_const(obj):
    """Return True if object is most likely a constant"""
    if obj is not None:
        return isinstance(obj, str) and obj[0].isalpha() and obj.upper() == obj

def _is_key(obj):
    """Return True if object is most likely a key"""
    if obj is not None:
        return "'" in obj

def _is_number(obj):
    """Return True if object is most likely a number"""
    if obj is not None:
        return isinstance(obj, (int, float)) or obj.isnumeric()

def _is_private(obj):
    """Return True if object is private"""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('_')

def _is_magic(obj):
    """Return True if object is private"""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('__')

def _get_access_modifier(obj):
    """Return the access modifier that should be used"""
    if _is_magic(obj):
        return '-'
    elif _is_private(obj):
        return '#'
    else:
        return '+'


@register.inclusion_tag('dump_die/_dd_object.html')
def dd_object(obj, skip=None, index=0, depth=0):
    """Return info about object"""

    max_recursion_depth = getattr(settings, 'DJANGO_DD_MAX_RECURSION_DEPTH', 20)
    max_iterable_length = getattr(settings, 'DJANGO_DD_MAX_ITERABLE_LENGTH', 20)
    include_attributes = getattr(settings, 'DJANGO_DD_INCLUDE_ATTRIBUTES', True)
    include_functions = getattr(settings, 'DJANGO_DD_INCLUDE_FUNCTIONS', False)
    attribute_types_start_expanded = getattr(settings, 'DJANGO_DD_ATTRIBUTE_TYPES_START_EXPANDED', False)
    attributes_start_expanded = getattr(settings, 'DJANGO_DD_ATTRIBUTES_START_EXPANDED', False)
    functions_start_expanded = getattr(settings, 'DJANGO_DD_FUNCTIONS_START_EXPANDED', False)
    include_private_methods = getattr(settings, 'DJANGO_DD_INCLUDE_PRIVATE_MEMBERS', False)
    include_magic_methods = getattr(settings, 'DJANGO_DD_INCLUDE_MAGIC_METHODS', False)

    skip = skip or set()
    # Skip objects already done to prevent infinite loops

    try:
        unique = hash(obj)
    except Exception:
        unique = id(obj)
    unique = f'{get_class_name(obj)}_{unique}'
    css_class = ''

    if (
        obj is None
        or type(obj) in SIMPLE_TYPES
        or get_class_name(obj) in SIMPLE_TYPE_NAMES
    ):
        if obj is None:
            css_class = 'none'
        elif isinstance(obj, str):
            css_class = 'string'
        elif isinstance(obj, bool):
            css_class = 'bool'
        elif isinstance(obj, (int, float, bytes)):
            css_class = 'number'

        return {
            'simple': safe_repr(obj),
            'css_class': css_class,
        }

    elif (
        # unique has not been done before
        unique not in skip
        # And either the max_recursion is set to None, or we have not reached it yet.
        and (
            max_recursion_depth is None
            or depth <= max_recursion_depth
        # And either the max_iterable_length is set to None, or we have not reached it yet.
        ) and (
            max_iterable_length is None
            or index <= max_iterable_length
        )
    ):
        # New object not parsed yet
        skip.add(unique)

        is_list = isinstance(obj, list)
        is_tuple = isinstance(obj, tuple)

        if is_list:
            braces = '[]'
        elif is_tuple:
            braces = '()'
        else:
            braces = '{}'

        attributes = [] # (attr, value, access_modifier, css_class, title)
        functions = [] # (attr, doc, access_modifier)

        if _is_query(obj):
            # Probably a query, so evaluate it
            # This prevents a crash because a lazy queryset has too many members.
            obj = list(obj)

        try:
            members = inspect.getmembers(obj)
        except Exception:
            members = []

        if _is_dict(obj):
            # Dictionary members
            members.extend(obj.items())
        elif _is_iterable(obj):
            # Lists, sets, etc.
            if _is_indexable(obj):
                # Use indexes as left half
                # members.extend([(idx, x) for idx, x in enumerate(obj)])
                members.extend(list(enumerate(obj)))
            else:
                # Use None as left half. Most likely a set.
                members.extend([(None, x) for x in obj])

        for attr, value in members:

            # Skip private members if not including them
            if _is_private(attr) and not include_private_methods:
                continue # Skip private attributes and methods

            is_callable = callable(value)
            if is_callable:
                # Skip dunder (magic) methods if not including them
                if _is_magic(attr) and not include_magic_methods:
                    continue #  Skip magic attributes and methods

                # Functions will just return documentation
                try:
                    attr += safe_str(inspect.signature(value))
                except Exception:
                    attr += '()'

                value = inspect.getdoc(value)

                if attr.startswith('_'):
                    access_modifier = '#'
                elif attr.startswith('__'):
                    access_modifier = '-'
                else:
                    access_modifier = '+'

                functions.append([attr, value, access_modifier])
            else:
                # Attributes logic

                # Always skip dunder attributes
                if _is_magic(attr):
                    continue #  Skip all dunder attributes

                # If attr is not None (anything but set) change to safe_repr
                if attr is not None:
                    attr = safe_repr(attr)

                if not _is_dict(obj) and attr is not None:
                    attr = re.sub("'", "", attr)

                # Index, const, key, set, attribute
                if _is_number(attr):
                    access_modifier = None
                    css_class = 'index'
                    title = 'Index'
                elif _is_const(attr):
                    access_modifier = _get_access_modifier(attr)
                    css_class = 'constant'
                    title = 'Constant'
                elif _is_key(attr):
                    access_modifier = None
                    css_class = 'key'
                    title = 'Key'
                elif attr is None:
                    access_modifier = None
                    css_class = ''
                    title = ''
                else:
                    access_modifier = _get_access_modifier(attr)
                    css_class = 'attribute'
                    title = 'Attribute'

                attributes.append([attr, value, access_modifier, css_class, title])

        try:
            functions = sorted(functions)
        except Exception:
            pass # Ignore sort errors

        return {
            'include_attributes': include_attributes,
            'include_functions': include_functions,
            'attribute_types_start_expanded': attribute_types_start_expanded,
            'attributes_start_expanded': attributes_start_expanded,
            'functions_start_expanded': functions_start_expanded,
            'braces': braces,
            'object': obj,
            'unique': unique,
            'type': type(obj).__name__,
            'attributes': attributes,
            'functions': functions,
            'is_iterable': _is_iterable(obj),
            'skip': skip,
            'index': index,
            'depth': depth,
        }

    # If we're here then the object has already been processed before,
    # so just return a repr() of it.

    return {
        'type': type(obj).__name__,
        'unique': unique,
    }
