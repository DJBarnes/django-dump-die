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


# Simple types that do not need to be recursively inspected.
SIMPLE_TYPES = [
    str,
    bytes,
    int,
    float,
    bool,
    types.ModuleType,
    BoundField,
]


# List of additional simple types defined as strings that do not need to be recursively inspected.
ADDITIONAL_SIMPLE_TYPES = getattr(settings, 'DJANGO_DD_ADDITIONAL_SIMPLE_TYPES', [])
# Max recursion depth to go while processing the dumped variable.
MAX_RECURSION_DEPTH = getattr(settings, 'DJANGO_DD_MAX_RECURSION_DEPTH', 20)
# Max number of iterables to recursively process before just printing the unique
# instead of recursing further. EX: if set to 20, a list of 30 will recursively
# inspect and print out 20 items and then simply print the unique for the last 10.
MAX_ITERABLE_LENGTH = getattr(settings, 'DJANGO_DD_MAX_ITERABLE_LENGTH', 20)
# Whether attributes should be included in the output.
INCLUDE_ATTRIBUTES = getattr(settings, 'DJANGO_DD_INCLUDE_ATTRIBUTES', True)
# Whether functions should be included in the output.
INCLUDE_FUNCTIONS = getattr(settings, 'DJANGO_DD_INCLUDE_FUNCTIONS', False)
# Whether objects attribute types (Attribute, Function) should start expanded for viewing.
ATTR_TYPES_START_EXPANDED = getattr(settings, 'DJANGO_DD_ATTRIBUTE_TYPES_START_EXPANDED', False)
# Whether the attributes for an object should start expanded for viewing.
ATTRIBUTES_START_EXPANDED = getattr(settings, 'DJANGO_DD_ATTRIBUTES_START_EXPANDED', True)
# Whether the functions for an object should start expanded for viewing.
FUNCTIONS_START_EXPANDED = getattr(settings, 'DJANGO_DD_FUNCTIONS_START_EXPANDED', False)
# Whether the output should include private attributes and functions.
INCLUDE_PRIVATE_METHODS = getattr(settings, 'DJANGO_DD_INCLUDE_PRIVATE_MEMBERS', False)
# Whether the output should include magic methods.
INCLUDE_MAGIC_METHODS = getattr(settings, 'DJANGO_DD_INCLUDE_MAGIC_METHODS', False)


def _get_class_name(obj):
    """Get class name of an object."""
    name = None
    try:
        name = obj.__class__.__name__
    except Exception:
        pass
    return name


def _safe_repr(obj):
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


def _safe_str(obj):
    """Call str() and ignore TypeErrors if str() doesn't return a string."""
    str_obj = ''
    try:
        str_obj = str(obj)
    except (TypeError, ObjectDoesNotExist):
        str_obj = _safe_repr(obj)

    return str_obj


def _in_dir(obj, attr):
    """Simpler hasattr() function without side effects."""
    return attr in dir(obj)


def _is_iterable(obj):
    """Return True if object can be iterated."""
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def _is_indexable(obj):
    """Return True if object can be indexed."""
    if isinstance(obj, Sequence):
        return True
    else:
        return False


def _is_query(obj):
    """Return True if object is most likely a query."""
    if obj is not None:
        return _in_dir(obj, 'as_manager') and _in_dir(obj, 'all') and _in_dir(obj, 'filter')


def _is_dict(obj):
    """Return True if object is most likely a dict."""
    if obj is not None:
        return _in_dir(obj, 'items') and _in_dir(obj, 'keys') and _in_dir(obj, 'values')


def _is_const(obj):
    """Return True if object is most likely a constant."""
    if obj is not None:
        return isinstance(obj, str) and obj[0].isalpha() and obj.upper() == obj


def _is_key(obj):
    """Return True if object is most likely a key."""
    if obj is not None:
        return "'" in obj


def _is_number(obj):
    """Return True if object is most likely a number."""
    if obj is not None:
        return isinstance(obj, (int, float)) or obj.isnumeric()


def _is_private(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('_')


def _is_magic(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('__')


def _get_access_modifier(obj):
    """Return the access modifier that should be used."""
    if _is_magic(obj):
        return '-'
    elif _is_private(obj):
        return '#'
    else:
        return '+'


@register.inclusion_tag('django_dump_die/_dd_object.html')
def dd_object(obj, parent_len, skip=None, curr_iteration=0, curr_depth=0, root_index_start=None, root_index_end=None):
    """
    Return info about object.
    If we have exceeded specified iteration count or depth, OR if object is of simple type, then output minimal info.
    Otherwise, output full object info, including information for any inner-children, if applicable.
    (Inner children are minimally processed here, and fully processed later in a new call to templatetag.)

    :param obj: Object to iterate over and attempt to parse information from.
    :param parent_len: Length of parent object. Used to calculate negative index values.
    :param skip: Set of already-processed objects. Used to skip re-processing identical objects.
    :param curr_iteration: Current iteration-index. Used to track current index of object we're iterating through.
    :param curr_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    :param root_index_start: Starting index for root iteratable object. If None, uses default behavior.
    :param root_index_end: Ending index for root iteratable object. If None, uses default behavior.
    """
    # Set up set to store uniques to skip if not passed in.
    # Will be used to skip objects already done to prevent infinite loops.
    skip = skip or set()

    # Validate root_index values.
    if root_index_start is not None:
        # Ensure proper typing.
        try:
            root_index_start = int(root_index_start)
        except (TypeError, ValueError):
            # Invalid type. Does not support integers. Reset to default.
            root_index_start = None

    if root_index_end is not None:
        # Ensure proper typing.
        try:
            root_index_end = int(root_index_end)
        except (TypeError, ValueError):
            # Invalid type. Does not support integers. Reset to default.
            root_index_end = None

    # Create unique via hash and fallback to id on exception.
    try:
        unique = hash(obj)
    except Exception:
        unique = id(obj)
    # Append the class name to the unique to really make unique.
    unique = f'{_get_class_name(obj)}_{unique}'
    # Default for css class to use with object.
    css_class = ''

    # Handle if obj is a simple type (Null/None, int, str, bool, and basic number types).
    if (
        obj is None
        or type(obj) in SIMPLE_TYPES
        or _get_class_name(obj) in ADDITIONAL_SIMPLE_TYPES
    ):
        return _handle_simple_type(obj)

    # Handle if object is in skip set, aka already processed.
    elif unique in skip:
        # Found in skip set. Skip further handling of if clauses and go to end of function.
        pass

    # Handle if we're at the root's element direct children (depth of 1),
    # element is iterable, AND "root_index" values are set.
    elif (
        curr_depth == 1
        and (root_index_start is not None or root_index_end is not None)
        and _is_iterable(obj)
    ):
        # Handle unique indexing logic for root element.
        # We do not do this logic for child elements (depth > 0), but allow it for the root
        # element, in case user wants to only run dd for a specific range of values.

        # Handle defaults.
        # If we got this far, at least one is set. Make sure the other is set as well.
        if root_index_start is None:
            root_index_start = 0
        if root_index_end is None:
            root_index_end = MAX_ITERABLE_LENGTH

        # Handle if provided start_index is negative.
        if root_index_start < 0:
            root_index_start = parent_len + root_index_start

            # Reset if still negative.
            if root_index_start < 0:
                root_index_start = 0

        # Handle if provided end_index is negative.
        if root_index_end < 0:
            root_index_end = parent_len + root_index_end

            # Reset if still negative.
            if root_index_end < 0:
                root_index_end = 0

        # Handle if user provided a start_index that is higher than end_index.
        if root_index_start > root_index_end:
            temp = root_index_start
            root_index_start = root_index_end
            root_index_end = temp

        # Handle if current index is between root_index values.
        # Otherwise fallback to "already processed" logic.
        if curr_iteration >= (root_index_start + 1) and curr_iteration <= (root_index_end + 1):
            # Handle for new "unique" object output.
            return _handle_unique_obj(
                obj,
                unique,
                skip=skip,
                curr_iteration=curr_iteration,
                curr_depth=curr_depth,
            )

    # Handle if not at root element and/or "root_index" values are not set.
    elif (
        # Check if the max_recursion is set to None, or we have not reached it yet.
        (
            MAX_RECURSION_DEPTH is None
            or curr_depth <= MAX_RECURSION_DEPTH
        )

        # And if the max_iterable_length is set to None, or we have not reached it yet.
        and (
            MAX_ITERABLE_LENGTH is None
            or curr_iteration <= MAX_ITERABLE_LENGTH
        )
    ):
        # Handle for new "unique" object output.
        return _handle_unique_obj(
            obj,
            unique,
            skip=skip,
            curr_iteration=curr_iteration,
            curr_depth=curr_depth,
            root_index_start=root_index_start,
            root_index_end=root_index_end,
        )

    # If we're here then the object has already been processed before,
    # or we have reached the max depth or number of iterations.
    # In any case, just return the type and unique of the object for output.
    return {
        'type': type(obj).__name__,
        'unique': unique,
    }


def _handle_simple_type(obj):
    """
    Logic for outputting information about a "simpel type".
    Includes str, numbers, bools, etc.
    """
    # Determine which css class to use.
    css_class = ''
    if obj is None:
        css_class = 'none'
    elif isinstance(obj, str):
        css_class = 'string'
    elif isinstance(obj, bool):
        css_class = 'bool'
    elif isinstance(obj, (int, float, bytes)):
        css_class = 'number'

    # Since simple type, return safe representation of simple type and
    # which css class to use.
    return {
        'simple': _safe_repr(obj),
        'css_class': css_class,
    }


def _handle_unique_obj(
    obj,
    unique,
    skip=None,
    curr_iteration=0,
    curr_depth=0,
    root_index_start=None,
    root_index_end=None,
):
    """
    Main logic for outputting information for a given "unique".

    :param obj: Object to iterate over and attempt to parse information from.
    :param skip: Set of already-processed objects. Used to skip re-processing identical objects.
    :param curr_iteration: Current iteration-index. Used to track current index of object we're iterating through.
    :param curr_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    """
    # Add unique to skip so it won't be processed a second time by additional
    # recursive calls to this template tag.
    skip.add(unique)

    # Determine which type of braces should be used.
    if isinstance(obj, list):
        braces = '[]'
    elif isinstance(obj, tuple):
        braces = '()'
    else:
        braces = '{}'

    # List to store all the attributes for this object.
    attributes = []  # (attr, value, access_modifier, css_class, title)
    # List to store all the functions for this object
    functions = []  # (attr, doc, access_modifier)

    # If the object is a query, evaluate it.
    # This prevents a crash because a lazy queryset has too many members.
    if _is_query(obj):
        obj = list(obj)

    # Try to get the members by using inspect and fallback to an empty list
    # on a raised exception.
    try:
        members = inspect.getmembers(obj)
    except Exception:
        members = []

    # Add type specific members that will not be included from the use of
    # the inspect.getmembers function.
    if _is_dict(obj):
        # Dictionary members.
        members.extend(obj.items())
    elif _is_iterable(obj):
        # Lists, sets, etc.
        if _is_indexable(obj):
            # Use indexes as left half.
            members.extend(list(enumerate(obj)))
        else:
            # Use None as left half. Most likely a set.
            members.extend([(None, x) for x in obj])

    # Now that all members have been collected, time to figure out what
    # type, access modifier, css class, and title should be used.
    # For each attribute and value in the members.
    for attr, value in members:

        # Skip private members if not including them.
        if _is_private(attr) and not INCLUDE_PRIVATE_METHODS:
            continue

        # Determine if the value is callable (function).
        # If so, Functions will just return documentation.
        is_callable = callable(value)
        if is_callable:  # Handle member functions.

            # Skip dunder (magic) methods if not including them.
            if _is_magic(attr) and not INCLUDE_MAGIC_METHODS:
                continue

            # Get the method signature and fall back to simply appending
            # parentheses to the method name on exception.
            try:
                attr += _safe_str(inspect.signature(value))
            except Exception:
                attr += '()'

            # Get the documentation for the method.
            value = inspect.getdoc(value)

            # Get the access modifier for the method.
            access_modifier = _get_access_modifier(attr)

            functions.append([attr, value, access_modifier])

        else:  # Handle member attributes.

            # Always skip dunder attributes.
            if _is_magic(attr):
                continue

            # If attr is not None (anything but set) change to safe_repr.
            if attr is not None:
                attr = _safe_repr(attr)

            # If not a dict and not None, remove the outside quotes
            # so it looks more like an attribute and not a string.
            if not _is_dict(obj) and attr is not None:
                attr = re.sub("'", "", attr)

            # Determine what type attribute is so that the access modifier,
            # css class, and title can be appropriately set.
            # Processing order is: Index, const, key, set, attribute
            if _is_number(attr):  # Index.
                access_modifier = None
                css_class = 'index'
                title = 'Index'
            elif _is_const(attr):  # Constant.
                access_modifier = _get_access_modifier(attr)
                css_class = 'constant'
                title = 'Constant'
            elif _is_key(attr):  # Key.
                access_modifier = None
                css_class = 'key'
                title = 'Key'
            elif attr is None:  # Set.
                access_modifier = None
                css_class = ''
                title = ''
            else:  # Class Attribute.
                access_modifier = _get_access_modifier(attr)
                css_class = 'attribute'
                title = 'Attribute'

            # Append the attribute information to the list of attributes.
            attributes.append([attr, value, access_modifier, css_class, title])

    # Attempt to sort the functions and just ignore any errors.
    try:
        functions = sorted(functions)
    except Exception:
        pass  # Ignore sort errors

    # Return information required to render object.
    return {
        'include_attributes': INCLUDE_ATTRIBUTES,
        'include_functions': INCLUDE_FUNCTIONS,
        'attribute_types_start_expanded': ATTR_TYPES_START_EXPANDED,
        'attributes_start_expanded': ATTRIBUTES_START_EXPANDED,
        'functions_start_expanded': FUNCTIONS_START_EXPANDED,
        'braces': braces,
        'object': obj,
        'unique': unique,
        'type': type(obj).__name__,
        'attributes': attributes,
        'functions': functions,
        'is_iterable': _is_iterable(obj),
        'skip': skip,
        'index': curr_iteration,
        'depth': curr_depth,
        'root_index_start': root_index_start,
        'root_index_end': root_index_end,
    }
