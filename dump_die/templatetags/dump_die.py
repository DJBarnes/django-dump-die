"""Template Tags for DumpDie"""
import inspect
import re
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


def get_class_name(obj):
    name = None
    try:
        name = obj.__class__.__name__
    except:
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
    try:
        obj[0]
    except TypeError:
        return False
    except KeyError:
        return False
    return True

def _is_query(obj):
    """Return True if object is most likely a query"""
    return _in_dir(obj, 'as_manager') and _in_dir(obj, 'all') and _in_dir(obj, 'filter')

def _is_dict(obj):
    """Return True if object is most likely a dict"""
    return _in_dir(obj, 'items') and _in_dir(obj, 'keys') and _in_dir(obj, 'values')


@register.simple_tag
def is_const(value):
    """Return True if attr is most likely a constant"""
    return value.upper() == value and len(value) > 1


@register.simple_tag
def is_number(value):
    """Return True if attr is numeric"""
    return value.isnumeric()


@register.simple_tag
def is_key(value):
    """Return True if attr is most likely a dict key"""
    return "'" in value


@register.inclusion_tag('dump_die/_dd_object.html')
def dd_object(obj, skip=None, index=0):
    """Return info about object"""
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
        is_indexable = _is_indexable(obj)

        # Simple types will just be returned
        return {
            'is_none': is_none,
            'is_string': is_string,
            'is_bool': is_bool,
            'is_number': is_number,
            'is_indexable': is_indexable,
            'object': None,
            'type': type(obj),
            'text': safe_str(obj),
            'repr': safe_repr(obj),
            'index': index,
        }
    elif unique not in skip and index < 20:
        # New object not parsed yet
        skip.add(unique)

        attributes = [] # (attr, value)
        functions = [] # (attr, doc)

        if _is_query(obj):
            # Probably a query, so evaluate it
            # This prevents a crash because a lazy queryset has too many members.
            obj = list(obj)

        try:
            members = inspect.getmembers(obj)
        except:
            members = []

        if _is_dict(obj):
            # Dictionary members
            members.extend(obj.items())
        elif _is_iterable(obj):
            # Lists, sets, etc.
            if _is_indexable(obj):
                # Use indexes as left half
                members.extend([(idx, x) for idx, x in enumerate(obj)])
            else:
                # Use safe_str as left half
                members.extend([(safe_str(x), x) for x in obj])

        for attr, value in members:
            # TODO: Consider allowing a setting to also output these if desired.
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
                if _is_dict(obj):
                    attributes.append([safe_repr(attr), value])
                else:
                    safe_repr_minus_quotes = safe_repr(attr)
                    safe_repr_minus_quotes = re.sub("'", "", safe_repr_minus_quotes)
                    attributes.append([safe_repr_minus_quotes, value])

        try:
            functions = sorted(functions)
        except:
            pass # Ignore sort errors

        return {
            'is_none': False,
            'is_string': False,
            'is_bool': False,
            'is_number': False,
            'is_indexable': False,
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
        'is_none': False,
        'is_string': False,
        'is_bool': False,
        'is_number': False,
        'is_indexable': False,
        'object': None,
        'unique': unique,
        'type': type(obj).__name__,
        'text': safe_str(obj),
        'repr': safe_repr(obj),
    }