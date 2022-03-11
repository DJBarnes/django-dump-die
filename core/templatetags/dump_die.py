"""Template Tags for DumpDie"""
import inspect
import types

from django import template
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


def in_dir(obj, attr):
    """Simpler hasattr() function without side effects."""
    return attr in dir(obj)

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

def isiterable(obj):
    """Return True if object can be iterated"""
    try:
        iter(obj)
    except TypeError:
        return False
    return True

def get_class_name(obj):
    name = None
    try:
        name = obj.__class__.__name__
    except:
        pass
    return name


@register.simple_tag
def is_upper(value):
    return value.upper()


@register.inclusion_tag('dump_die/_dd_object.html')
def dd_object(obj, skip=None, index=0):
    skip = skip or set()
    # Skip objects already done to prevent infinite loops

    try:
        unique = hash(obj)
    except:
        unique = id(obj)
    unique = '{0}_{1}'.format(safe_str(obj.__class__.__name__), unique)

    if (
        obj is None
        or type(obj) in SIMPLE_TYPES
        or get_class_name(obj) in SIMPLE_TYPE_NAMES
    ):
        is_none = obj is None
        is_string = type(obj) is str
        is_bool = type(obj) is bool
        is_number = type(obj) is int or type(obj) is float or type(obj) is bytes

        # Simple types will just be returned
        return {
            'is_none': is_none,
            'is_string': is_string,
            'is_bool': is_bool,
            'is_number': is_number,
            'object': None,
            'type': type(obj),
            'text': safe_str(obj),
            'repr': safe_repr(obj),
            'index': index,
        }
    elif unique not in skip or index < 20:
        # New object not parsed yet
        skip.add(unique)

        attributes = [] # (attr, value)
        functions = [] # (attr, doc)

        if in_dir(obj, 'as_manager') and in_dir(obj, 'all') and in_dir(obj, 'filter'):
            # Probably a query, so evaluate it
            # This prevents a crash because a lazy queryset has too many members.
            obj = list(obj)

        try:
            members = inspect.getmembers(obj)
        except:
            members = []

        if in_dir(obj, 'items') and in_dir(obj, 'keys') and in_dir(obj, 'values'):
            # Dictionary members
            members.extend(obj.items())
        elif isiterable(obj):
            # Lists, sets, etc.
            members.extend([(safe_str(x), x) for x in obj])

        for attr, value in members:
            if type(attr) is str and attr.startswith('_'):
                continue # Skip special attributes

            is_callable = callable(value)

            if is_callable:
                # Functions will just return documentation
                try:
                    attr += safe_str(inspect.signature(value))
                except:
                    attr += '()'
                value = inspect.getdoc(value)
                functions.append([attr, value])
            else:
                attributes.append([safe_repr(attr), value])

        try:
            functions = sorted(functions)
        except:
            pass # Ignore sort errors

        return {
            'is_string': False,
            'object': obj,
            'unique': unique,
            'type': type(obj).__name__,
            'text': safe_str(obj),
            'repr': safe_repr(obj),
            'attributes': attributes,
            'functions': functions,
            'skip': skip,
            'index': index,
        }

    # If we're here then the object has already been processed before,
    # so just return a repr() of it.

    return {
        'is_string': False,
        'object': None,
        'unique': unique,
        'type': type(obj),
        'text': safe_str(obj),
        'repr': safe_repr(obj),
    }
