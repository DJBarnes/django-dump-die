"""Template Tags for DumpDie"""

import datetime
import inspect
import pytz
import re
import types

from collections.abc import Sequence
from decimal import Decimal

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms.boundfield import BoundField
from django.utils import timezone

register = template.Library()


# Simple types that do not need to be recursively inspected.
SIMPLE_TYPES = [
    bool,
    BoundField,
    bytes,
    Decimal,
    float,
    int,
    types.ModuleType,
    str,
]


# Intermediate types, that need some level of recursion and some level of "simple type" handling.
INTERMEDIATE_TYPES = [
    datetime.datetime,
    datetime.date,
    datetime.time,
    timezone.timezone,
    # pytz.BaseTzInfo,  # pytz timezone object. Has to be handled separately. Noted here just as a reminder.
]


# List of additional simple types defined as strings that do not need to be recursively inspected.
ADDITIONAL_SIMPLE_TYPES = getattr(settings, 'DJANGO_DD_ADDITIONAL_SIMPLE_TYPES', [])
# List of additional intermediate types defined as strings that do not need to be recursively inspected.
ADDITIONAL_INTERMEDIATE_TYPES = getattr(settings, 'DJANGO_DD_ADDITIONAL_INTERMEDIATE_TYPES', [])
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
# Whether function doc output should try to fit on one line, or output with original newlines.
MULTILINE_FUNCTION_DOCS = getattr(settings, 'DJANGO_DD_MULTILINE_FUNCTION_DOCS', False)
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

# Stores the uniques for each dumped root object.
root_skip = {}
root_unique_map = {}


def _generate_unique_from_obj(obj):
    """Generate a unique identifier for the object passed in."""

    # Create unique via hash and fallback to id on exception.
    try:
        unique = hash(obj)
    except Exception:
        unique = id(obj)
    # Append the class name to the unique to really make unique.
    unique = f'{_get_class_name(obj)}_{unique}'

    return unique


def _generate_unique(obj, root_obj, original_obj):
    """Generate the current and root unique"""

    # Get a unique for the object
    unique = _generate_unique_from_obj(obj)

    # Get a unique for the object
    root_unique = _generate_unique_from_obj(root_obj)

    # If there is an original_obj, we may need to create the unique map so that
    # we can restore the original uniques to the deepcopied object.
    if original_obj:
        # Ensure root unique in root_unique_map
        root_unique = _generate_unique_from_obj(root_obj)
        if root_unique not in root_unique_map:
            # Create the unique map
            _create_unique_map(obj, root_obj, original_obj)

        # Skip simple types and intermediate types
        if unique in root_unique_map[root_unique]:
            # Do unique swap so that both unique and root unique are the
            # same value as the original value before deep copying.
            unique = root_unique_map[root_unique][unique]
            root_unique = root_unique_map[root_unique][root_unique]

    # If the root unique is already in root_skip.
    if root_unique in root_skip:

        # If obj and root_obj are the same, increment the count
        if obj == root_obj:
            # Get the current count out.
            root_count = root_skip[root_unique]
            # Increment the count.
            root_skip[root_unique] += 1
        # Else set the root count to the value - 1 as it is a child of the
        # root unique and would otherwise have the wrong value.
        else:
            # Get the current count out.
            root_count = root_skip[root_unique] - 1

        # If the root count is greater than zero, use it.
        if root_count > 0:
            # Append the current iteration.
            unique = f'{unique}_{root_count}'
    else:
        # Else add the unique to the root_skip.
        root_skip[root_unique] = 1

    return unique


def _create_unique_map(obj, root_obj, original_obj):
    """Create an entry in the root_unique_map for this object"""

    # Calculate the root unique
    root_unique = _generate_unique_from_obj(root_obj)
    # Create a dict for that unique map
    root_unique_map[root_unique] = {}
    # Begin recursively adding entries to the unique map
    _add_unique_map_entry(obj, original_obj, root_unique)



def _add_unique_map_entry(obj, original_obj, root_unique):
    """Add a unique entry to the unique entry map"""

    # Calculate the obj unique and the original obj unique.
    obj_unique = _generate_unique_from_obj(obj)
    original_obj_unique = _generate_unique_from_obj(original_obj)

    # Add the new unique to the root unique map.
    root_unique_map[root_unique][obj_unique] = original_obj_unique

    # Attempt to get member values of object and original object.
    members = _get_members(obj)
    original_members = _get_members(original_obj)

    # Loop through members
    for attr, value in members:
        # Skip simple types and childrent of intermediate types
        if _is_simple_type(value) or _is_intermediate_type(obj):
            continue
        # Skip private members if not including them and functions.
        if (_is_private(attr) and not INCLUDE_PRIVATE_METHODS) or callable(value):
            continue

        # Loop through orig members looking for a match
        for orig_attr, orig_value in original_members:
            # Skip simple types and children of intermediate types
            if _is_simple_type(value) or _is_intermediate_type(original_obj):
                continue
            # Skip private members if not including them and functions.
            if (_is_private(attr) and not INCLUDE_PRIVATE_METHODS) or callable(value):
                continue

            # If the attrs match, make recursive call to add more entries to the unique map
            if orig_attr == attr:
                _add_unique_map_entry(value, orig_value, root_unique)


def _get_class_name(obj):
    """Get class name of an object."""
    name = None
    try:
        name = obj.__class__.__name__
    except Exception:
        pass
    return name


def _get_access_modifier(obj):
    """Return the access modifier that should be used."""
    if _is_magic(obj):
        return '-'
    elif _is_private(obj):
        return '#'
    else:
        return '+'


def _get_obj_type(obj):
    """Determines the string representation of object's type."""

    # Get default type value.
    obj_type = type(obj).__name__

    # Special handling for certain types.
    if obj_type == 'NoneType':
        obj_type = 'null'
    elif isinstance(obj, pytz.BaseTzInfo):
        obj_type = 'pytz_timezone'

    return obj_type


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
        return isinstance(obj, str) and obj.startswith('__') and obj.endswith('__')


def _is_simple_type(obj):
    """Return if the obj is a simple type."""
    return (
        obj is None
        or type(obj) in SIMPLE_TYPES
        or _get_class_name(obj) in ADDITIONAL_SIMPLE_TYPES
    )


def _is_intermediate_type(obj):
    """Return if the obj is an intermediate type."""

    # Special handling for pytz timezone objects.
    if isinstance(obj, pytz.BaseTzInfo):
        return True

    # Handling for all other objects.
    return (
        type(obj) in INTERMEDIATE_TYPES
        or _get_class_name(obj) in ADDITIONAL_INTERMEDIATE_TYPES
    )


def _should_render_full_object(current_depth, current_iteration):
    """Return if we should render the full object"""
    return (
        # Ensure all dump calls are processed.
        current_depth == 0
        # Check for any nested objects
        or (
            # Check if the max_recursion is set to None or we have not reached it yet.
            (
                MAX_RECURSION_DEPTH is None
                or current_depth <= MAX_RECURSION_DEPTH
            )

            # And if the max_iterable_length is set to None,
            # or we have not reached it yet or we are at the root level.
            and (
                MAX_ITERABLE_LENGTH is None
                or current_iteration <= MAX_ITERABLE_LENGTH
            )
        )
    )


def _process_root_indices(start, end, parent_length):
    """Process the passed in start and end indices into proper format"""
    # Handle unique indexing logic for root element.
    # We do not do this logic for child elements (depth > 0), but allow it for the root
    # element, in case user wants to only run dd for a specific range of values.

    # Save for later processing
    orig_end = end

    # Handle defaults.
    # If we got this far, at least one is set. Make sure the other is set as well.
    if start is None:
        start = 0
    if end is None:
        end = MAX_ITERABLE_LENGTH

    # Handle if provided start_index is negative.
    if start < 0:
        start = parent_length + start

        # Reset if still negative.
        if start < 0:
            start = 0

    # If the original value of end is None, there is no specified end and
    # it makes sense to then run from the start, now that it is calculated,
    # to the max iterable length.
    if orig_end is None:
        end = start + MAX_ITERABLE_LENGTH

    # Handle if provided end_index is negative.
    if end < 0:
        end = parent_length + end

        # Reset if still negative.
        if end < 0:
            end = 0

    # Handle if user provided a start_index that is higher than end_index.
    if start > end:
        temp = start
        start = end
        end = temp

    # Return the processed indices.
    return start, end


def _get_collapsable_values():
    """Get the arrow and collapsable values"""

    return {
        'attribute_type' : {
            'arrow': '▼' if ATTR_TYPES_START_EXPANDED else '▶',
            'show': 'show' if ATTR_TYPES_START_EXPANDED else '',
        },
        'attribute' : {
            'arrow': '▼' if ATTRIBUTES_START_EXPANDED else '▶',
            'show': 'show' if ATTRIBUTES_START_EXPANDED else '',
        },
        'function' : {
            'arrow': '▼' if FUNCTIONS_START_EXPANDED else '▶',
            'show': 'show' if FUNCTIONS_START_EXPANDED else '',
        },
    }


@register.inclusion_tag('django_dump_die/_dd_object.html')
def dd_object(
    obj,
    root_obj,
    skip=None,
    current_iteration=0,
    current_depth=0,
    root_index_start=None,
    root_index_end=None,
    original_obj=None,
    parent_is_intermediate=False,
):
    """
    Return info about object.
    If we have exceeded specified iteration count or depth, OR if object is of simple type, then output minimal info.
    Otherwise, output full object info, including information for any inner-children, if applicable.
    (Inner children are minimally processed here, and fully processed later in a new call to templatetag.)

    :param obj: Object to iterate over and attempt to parse information from.
    :param root_obj: Root object. Used to calculate negative index values.
    :param skip: Set of already-processed objects. Used to skip re-processing identical objects.
    :param current_iteration: Current iteration-index. Used to track current index of object we're iterating through.
    :param current_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    :param root_index_start: Starting index for root iterable object. If None, uses default behavior.
    :param root_index_end: Ending index for root iterable object. If None, uses default behavior.
    :param parent_is_intermediate: Boolean indicating that parent is intermediate type. Do not recurse further.
    """

    # Set up set to store uniques to skip if not passed in.
    # Will be used to skip objects already done to prevent infinite loops.
    skip = skip or set()

    # Generate the unique
    unique = _generate_unique(obj, root_obj, original_obj)

    # Following section will determine what should get rendered out.

    # Handle if object is in skip set, aka already processed.
    if unique in skip:
        # Complex object found in skip set. Skip further handling of if clauses and go to end of function.
        pass

    # Handle if obj is a simple type (Null/None, int, str, bool, and basic number types)
    # OR if direct parent is a intermediate (excluding pytz timezone objects).
    elif (
        _is_simple_type(obj)
        or (parent_is_intermediate and not isinstance(obj, pytz.BaseTzInfo))
    ):
        return _handle_simple_type(obj)

    # Handle if obj is an intermediate (date/time types).
    elif _is_intermediate_type(obj):
        return _handle_intermediate_type(obj, root_obj, unique, original_obj=original_obj)

    # Handle if element is iterable and we are at the root's element direct children (depth of 1),
    elif _is_iterable(root_obj) and current_depth == 1:

        # Handle unique indexing logic for root element.
        root_index_start, root_index_end = _process_root_indices(
            root_index_start,
            root_index_end,
            len(root_obj)
        )

        # Handle if current index is between root_index values.
        # Otherwise fallback to "already processed" logic.
        if current_iteration >= root_index_start and current_iteration < root_index_end:

            # Handle for new "unique" object output.
            return _handle_unique_obj(
                obj,
                root_obj,
                unique,
                skip=skip,
                current_iteration=current_iteration,
                current_depth=current_depth,
                original_obj=original_obj,
            )

    # Handle if not at root element and/or "root_index" values are not set.
    elif _should_render_full_object(current_depth, current_iteration):

        # Handle for new "unique" object output.
        return _handle_unique_obj(
            obj,
            root_obj,
            unique,
            skip=skip,
            current_iteration=current_iteration,
            current_depth=current_depth,
            root_index_start=root_index_start,
            root_index_end=root_index_end,
            original_obj=original_obj,
        )

    # If we're here then the object has already been processed before,
    # or we have reached the max depth or number of iterations
    # or outside the bounds of the root indexes to process.
    # In any case, just return the type and unique of the object for output.
    return {
        'type': _get_obj_type(obj),
        'unique': unique,
    }


def _handle_simple_type(obj):
    """
    Logic for outputting information about a "simple type".
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
    elif isinstance(obj, (int, Decimal, float, bytes)):
        css_class = 'number'
    elif _is_intermediate_type(obj):
        css_class = 'datetime'
    elif isinstance(obj, types.ModuleType):
        css_class = 'module'
    elif isinstance(obj, BoundField):
        css_class = 'bound'
    else:
        css_class = 'default'

    # Determine which output to use.
    if _is_intermediate_type(obj) or isinstance(obj, Decimal):
        output_value = _safe_str(obj)
    else:
        output_value = _safe_repr(obj)

    # Since simple type, return safe representation of simple type and
    # which css class to use.
    return {
        'simple': output_value,
        'type': _get_obj_type(obj),
        'css_class': css_class,
    }


def _handle_intermediate_type(obj, root_obj, unique, original_obj=None):
    """Handling for a intermediate object.

    Effectively, it's an object that's complex enough to have associated attributes and functions that we want to
    display in dd output. But for basic cases, treating it more almost as a "simple type" is generally enough
    information. Thus, it ends up being a combination of the two output formats.

    Similar to "simple type" in that we display base value output without needing to expand.

    Similar to "complex type" in that we display associated attributes, but do not fully recursively expand all.
    """
    # Attempt to get corresponding attribute/function values of object.
    attributes, functions = _get_obj_values(obj)

    # Return information required to render object.
    return {
        'include_attributes': INCLUDE_ATTRIBUTES,
        'include_functions': INCLUDE_FUNCTIONS,
        'multiline_function_docs': MULTILINE_FUNCTION_DOCS,
        'collapsable': _get_collapsable_values(),
        'braces': '{}',
        'object': obj,
        'root_obj': root_obj,
        'intermediate': _safe_str(obj),
        'unique': unique,
        'type': _get_obj_type(obj),
        'attributes': attributes,
        'functions': functions,
        'is_iterable': False,
        'skip': set(),
        'index': 0,
        'depth': 0,
        'root_index_start': None,
        'root_index_end': None,
        'original_obj': original_obj,
    }


def _handle_unique_obj(
    obj,
    root_obj,
    unique,
    skip=None,
    current_iteration=0,
    current_depth=0,
    root_index_start=None,
    root_index_end=None,
    original_obj=None,
):
    """
    Main logic for outputting information for a given "unique".

    :param obj: Object to iterate over and attempt to parse information from.
    :param skip: Set of already-processed objects. Used to skip re-processing identical objects.
    :param current_iteration: Current iteration-index. Used to track current index of object we're iterating through.
    :param current_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    """
    # Add unique to skip so it won't be processed a second time by additional
    # recursive calls to this template tag.
    skip.add(unique)

    # If the object is a query, evaluate it.
    # This prevents a crash because a lazy queryset has too many members.
    if _is_query(obj):
        obj = list(obj)

    # Determine which type of braces should be used.
    if isinstance(obj, list):
        braces = '[]'
    elif isinstance(obj, tuple):
        braces = '()'
    else:
        braces = '{}'

    # Attempt to get corresponding attribute/function values of object.
    attributes, functions = _get_obj_values(obj)

    # Return information required to render object.
    return {
        'include_attributes': INCLUDE_ATTRIBUTES,
        'include_functions': INCLUDE_FUNCTIONS,
        'multiline_function_docs': MULTILINE_FUNCTION_DOCS,
        'collapsable': _get_collapsable_values(),
        'braces': braces,
        'object': obj,
        'root_obj': root_obj,
        'unique': unique,
        'type': _get_obj_type(obj),
        'attributes': attributes,
        'functions': functions,
        'is_iterable': _is_iterable(obj),
        'skip': skip,
        'index': current_iteration,
        'depth': current_depth,
        'root_index_start': root_index_start,
        'root_index_end': root_index_end,
        'original_obj': original_obj,
    }


def _get_members(obj):
    """Attempts to get object members. Falls back to an empty list."""

    # Get initial member set or empty list.
    try:
        members = inspect.getmembers(obj)
    except Exception:
        members = []

    # Add type specific members that will not be included from the use of the inspect.getmembers function.
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

    return members


def _get_obj_values(obj):
    """Determines full corresponding member values (attributes/functions) of object."""

    # Initialize attribute/function lists. This is what we ultimately return.
    attributes = []     # (attr, value, access_modifier, css_class, title)
    functions = []      # (attr, doc, access_modifier)

    # Attempt to get member values of object. Falls back to empty list on failure.
    members = _get_members(obj)

    # Once all members have been collected, attempt to figure out what type, access modifier, css class, and title
    # should be used for each attribute/function/value in the members.
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

            # Get the method signature and fall back to simply appending parentheses to the method name on exception.
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

            # If not a dict and not None, remove the outside quotes so it looks more like an attribute and not a string.
            if not _is_dict(obj) and attr is not None:
                attr = re.sub("'", "", attr)

            # Determine what type attribute is so that the access modifier, css class, and title can be appropriately
            # set. Processing order is: Index, const, key, set, attribute
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
        pass  # Ignore sort errors.

    return (attributes, functions)
