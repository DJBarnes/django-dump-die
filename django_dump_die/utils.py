"""Utils for dump die"""

import inspect
import pytz

from collections.abc import Sequence

from django.core.exceptions import ObjectDoesNotExist

# region Object Property Functions


def generate_unique_from_obj(obj):
    """Generate a unique identifier for the object passed in."""

    # Create unique via hash and fallback to id on exception.
    try:
        unique = hash(obj)
    except Exception:
        unique = id(obj)
    # Append the class name to the unique to really make unique.
    unique = f'{get_class_name(obj)}_{unique}'

    return unique


def get_members(obj):
    """Attempts to get object members. Falls back to an empty list."""

    # Get initial member set or empty list.
    try:
        members = inspect.getmembers(obj)
    except Exception:
        members = []

    # Add type specific members that will not be included from the use of the
    # inspect.getmembers function.
    if is_dict(obj):
        # Dictionary members.
        members.extend(obj.items())
    elif is_iterable(obj):
        # Lists, sets, etc.
        if _is_indexable(obj):
            # Use indexes as left half.
            members.extend(list(enumerate(obj)))
        elif is_set(obj):
            # Use None as left half. Most likely a set.
            members.extend([(None, x) for x in obj])

    return members


def get_class_name(obj):
    """Get class name of an object."""
    name = None
    try:
        name = obj.__class__.__name__
    except Exception:
        pass
    return name


def get_callable_name(obj_name, obj):
    """Get callable name of an object"""

    # Get the method signature and fall back to simply appending
    # parentheses to the method name on exception.
    try:
        obj_name += safe_str(inspect.signature(obj))
    except Exception:
        obj_name += '()'
    return obj_name


def get_obj_type(obj):
    """Determines the string representation of object's type."""

    # Get default type value.
    obj_type = type(obj).__name__

    # Special handling for certain types.
    if obj_type == 'NoneType':
        obj_type = 'null'
    elif isinstance(obj, pytz.BaseTzInfo):
        obj_type = 'pytz_timezone'

    return obj_type


def safe_repr(obj):
    """Call repr() and ignore ObjectDoesNotExist."""
    str_obj = ''
    try:
        str_obj = repr(obj)
    except ObjectDoesNotExist:
        # L8R: A list of deleted db objects will cause repr(list) to fail.
        # We should detect this and print out the __class__ of the contents of
        # the list.
        str_obj = f'<{obj.__class__} DELETED>'

    return str_obj


def safe_str(obj):
    """Call str() and ignore TypeErrors if str() doesn't return a string."""
    str_obj = ''
    try:
        str_obj = str(obj)
    except (TypeError, ObjectDoesNotExist):
        str_obj = safe_repr(obj)

    return str_obj


def is_iterable(obj):
    """Return True if object can be iterated."""
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def is_query(obj):
    """Return True if object is most likely a query."""
    if obj is not None:
        return _in_dir(obj, 'as_manager') and _in_dir(obj, 'all') and _in_dir(obj, 'filter')


def is_dict(obj):
    """Return True if object is most likely a dict."""
    if obj is not None:
        return _in_dir(obj, 'items') and _in_dir(obj, 'keys') and _in_dir(obj, 'values')


def is_set(obj):
    """Return True if object is most likely a dict."""
    return isinstance(obj, set)


def is_const(obj):
    """Return True if object is most likely a constant."""
    if obj is not None:
        return isinstance(obj, str) and obj[0].isalpha() and obj.upper() == obj


def is_key(obj):
    """Return True if object is most likely a key."""
    if obj is not None:
        return "'" in obj


def is_number(obj):
    """Return True if object is most likely a number."""
    if obj is not None:
        return isinstance(obj, (int, float)) or obj.isnumeric()


def is_private(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('_')


def is_magic(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('__') and obj.endswith('__')


def _in_dir(obj, attr):
    """Simpler hasattr() function without side effects."""
    return attr in dir(obj)


def _is_indexable(obj):
    """Return True if object can be indexed."""
    if isinstance(obj, Sequence):
        return True
    else:
        return False

# endregion Object Property Functions
