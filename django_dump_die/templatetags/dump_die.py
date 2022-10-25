"""Template Tags for DumpDie"""

# System Imports.
import inspect
import re
import traceback
import types
from decimal import Decimal

# Third-Party Imports.
from django import template
from django.forms.boundfield import BoundField

# Internal Imports.
from django_dump_die.constants import (
    SIMPLE_TYPES,
    INTERMEDIATE_TYPES,
    ADDITIONAL_SIMPLE_TYPES,
    ADDITIONAL_INTERMEDIATE_TYPES,
    MAX_RECURSION_DEPTH,
    MAX_ITERABLE_LENGTH,
    MULTILINE_FUNCTION_DOCS,
    CONTENT_STARTS_EXPANDED,
    ATTRIBUTES_START_EXPANDED,
    FUNCTIONS_START_EXPANDED,
    INCLUDE_PRIVATE_METHODS,
    INCLUDE_MAGIC_METHODS,
    INCLUDE_ATTRIBUTES,
    INCLUDE_FUNCTIONS,
    PYTZ_PRESENT,
)
from django_dump_die.utils import (
    get_dumped_object_info,
    generate_unique_from_obj,
    get_members,
    get_class_name,
    get_callable_params,
    get_obj_type,
    safe_repr,
    safe_str,
    is_iterable,
    is_query,
    is_dict,
    is_const,
    is_key,
    is_number,
    is_private,
    is_magic,
)

# Imports that may not be accessible, depending on local python environment setup.
if PYTZ_PRESENT:
    import pytz


register = template.Library()


# region Module Variables

# Stores the uniques for each dumped root object.
repeat_iteration_tracker = {}
deepcopy_unique_map = {}

# endregion Module Variables


@register.inclusion_tag('django_dump_die/partials/_dump.html', takes_context=True)
def dump(context, obj):
    """Template tag that can be used in templates to use dd"""
    object_info = get_dumped_object_info(obj)

    render_head = context.get('django_dd_template_tag_render_head', True)
    if render_head:
        context['django_dd_template_tag_render_head'] = False

    return {
        'objects': [object_info],
        'render_head': render_head,
    }


@register.inclusion_tag('django_dump_die/partials/_dump_objects.html')
def dump_objects(objects):
    """Template tag that can be used to dump a list of objects"""
    return {'objects': objects}


@register.inclusion_tag('django_dump_die/partials/_dump_object.html')
def dump_object(
    obj,
    root_obj,
    skip_set=None,
    current_iteration=0,
    current_depth=0,
    root_index_start=None,
    root_index_end=None,
    original_obj=None,
    parent_is_intermediate=False,
):
    """Determines template dd/dump info for provided object.

    Determines appropriate attributes/functions associated with object, for dd/dump output to template.

    There are three major object categories:
      * Simple - Basic entities that simply output minimal, direct value output.
      * Intermediate - Objects that that display only one level of attribute/function values.
      * Complex - Complex objects that recursively display attribute/function values for self and all children.

    Note:
      * If we have exceeded specified iteration count or depth, then defaults back to "simple" type output.
      * On each call, inner children are minimally processed, and fully processed later in a new call to templatetag.

    :param obj: Object to iterate over and attempt to parse information from.
    :param root_obj: Root, parent object associated with current object.
    :param skip_set: Set of already-processed objects. Used to skip re-processing identical non-objects.
    :param current_iteration: Current iteration-index. Used to track current index of object we're iterating through.
    :param current_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    :param root_index_start: Starting index for root iterable object. If None, uses default behavior.
    :param root_index_end: Ending index for root iterable object. If None, uses default behavior.
    :param original_obj: Original object, for handling uniques if dealing with deepcopy.
    :param parent_is_intermediate: Boolean indicating that parent is intermediate type. Do not recurse further.
    """
    # Set up set to store uniques to skip if not passed in.
    # Will be used to skip objects already done to prevent infinite loops.
    skip_set = skip_set or set()

    # Generate the unique
    unique, root_count = _generate_unique(obj, root_obj, original_obj)

    # Following section will determine what should get rendered out.
    intermediate_value = None

    # Handle if object is in skip set, aka already processed.
    if unique in skip_set:
        # Complex object found in skip set. Skip further handling of if clauses and go to end of function.
        # Intermediates get slightly extra handling for "simple" value output.
        if _is_intermediate_type(obj):
            intermediate_value = safe_str(obj)

    # Handle if obj is a simple type (Null/None, int, str, bool, and basic number types)
    # OR if direct parent is an intermediate (excluding pytz timezone objects).
    elif (
        _is_simple_type(obj)
        or (
            (PYTZ_PRESENT and parent_is_intermediate and not isinstance(obj, pytz.BaseTzInfo))
            or parent_is_intermediate
        )
    ):
        return _handle_simple_type(obj)

    # Handle if obj is an intermediate (date/time types).
    elif _is_intermediate_type(obj):
        return _handle_intermediate_type(
            obj,
            root_obj,
            unique,
            root_count,
            skip_set=skip_set,
            original_obj=original_obj
        )

    # Handle if element is iterable and we are at the root's element direct children (depth of 1),
    elif is_iterable(root_obj) and current_depth == 0:

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
            return _handle_complex_type(
                obj,
                root_obj,
                unique,
                root_count,
                skip_set=skip_set,
                current_iteration=current_iteration,
                current_depth=current_depth,
                original_obj=original_obj,
            )

    # Handle if not at root element and/or "root_index" values are not set.
    elif is_complex_type(current_depth, current_iteration):

        # Handle for new "unique" object output.
        return _handle_complex_type(
            obj,
            root_obj,
            unique,
            root_count,
            skip_set=skip_set,
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
        'type': get_obj_type(obj),
        'unique': unique,
        'root_count': root_count,
        'intermediate': intermediate_value,
    }


# region Unique Mapping Functions

def _generate_unique(obj, root_obj, original_obj):
    """Generates object "unique" identifier.

    If using dump/dd on multiple instances of a root object, tracks such and appends iteration counters appropriately.

    If dealing with deepcopy, creates mapping to track the original values, so end user can track evolution of a single
    variable over time.

    :param obj: Current object to determine unique for.
    :param root_obj: Root object associated with current obj. Used for deepcopy mapping logic.
    :param original_obj: Original instance of object corresponding to current obj. Used for deepcopy mapping logic.
    """
    # Get a unique for the object.
    unique = generate_unique_from_obj(obj)

    # Get a unique for the object.
    root_unique = generate_unique_from_obj(root_obj)

    # Default root_count to blank string
    root_count_string = ''

    # If there is an original_obj, we may need to create the unique map so that
    # we can restore the original uniques to the deepcopied object.
    if original_obj:
        # Ensure root unique in root_unique_map.
        if root_unique not in deepcopy_unique_map:
            # Create the unique mapping of current deepcopy to original object.
            _create_unique_map(obj, root_unique, original_obj)

        # Skip simple types and intermediate types
        if unique in deepcopy_unique_map[root_unique]:
            # Do unique swap so that both unique and root unique are the
            # same value as the original value before deep copying.
            unique = deepcopy_unique_map[root_unique][unique]
            root_unique = deepcopy_unique_map[root_unique][root_unique]

    # If the root unique is already in repeat_iteration_tracker.
    if root_unique in repeat_iteration_tracker:
        # Unique found in tracker.
        # Determine appended "iteration tracker" value for root unique and all associated children.

        # If obj and root_obj are the same, increment the count.
        if obj == root_obj:
            # Get the current count out.
            root_count = repeat_iteration_tracker[root_unique]
            # Increment the count.
            repeat_iteration_tracker[root_unique] += 1

        # Else set the root count to the value - 1 as it is a child of the
        # root unique and would otherwise have the wrong value.
        else:
            # Get the current count out.
            root_count = repeat_iteration_tracker[root_unique] - 1

        # If the root count is greater than zero, use it.
        if root_count > 0:
            # Update root_count_string.
            root_count_string = f'_{root_count}'
        else:
            root_count_string = ''

    else:
        # Unique not found in tracker. Add the unique to the repeat_iteration_tracker.
        repeat_iteration_tracker[root_unique] = 1

    return unique, root_count_string


def _create_unique_map(obj, root_unique, original_obj):
    """Create an entry in the root_unique_map for this object."""

    # Create a dict for that unique map.
    deepcopy_unique_map[root_unique] = {}

    # Begin recursively adding entries to the unique map.
    _add_unique_map_entry(obj, original_obj, root_unique)


def _add_unique_map_entry(obj, original_obj, root_unique):
    """Add a unique entry to the unique entry map."""

    # Calculate the obj unique and the original obj unique.
    obj_unique = generate_unique_from_obj(obj)
    original_obj_unique = generate_unique_from_obj(original_obj)

    # Add the new unique to the root unique map.
    deepcopy_unique_map[root_unique][obj_unique] = original_obj_unique

    # Attempt to get member values of object and original object.
    members = get_members(obj)
    original_members = get_members(original_obj)

    # Loop through members and recursively determine unique mappings.
    # We do this because the state of an object might change over time, so child values (and mappings) might be
    # different. Parent might also be of complex type with children that are also complex types.
    for attr, value in members:
        # Skip simple types and children of intermediate types.
        if _is_simple_type(value) or _is_intermediate_type(obj):
            continue
        # Skip private members if not including them and functions.
        if (is_private(attr) and not INCLUDE_PRIVATE_METHODS) or callable(value):
            continue

        # Loop through orig members looking for a match.
        for orig_attr, orig_value in original_members:
            # Skip simple types and children of intermediate types.
            if _is_simple_type(value) or _is_intermediate_type(original_obj):
                continue
            # Skip private members if not including them and functions.
            if (is_private(attr) and not INCLUDE_PRIVATE_METHODS) or callable(value):
                continue

            # If the attrs match, make recursive call to add more entries to the unique map.
            if orig_attr == attr:
                _add_unique_map_entry(value, orig_value, root_unique)

# endregion Unique Mapping Functions


# region Type Handling Functions

def _is_simple_type(obj):
    """Return if the obj is a simple type."""
    return (
        obj is None
        or type(obj) in SIMPLE_TYPES
        or get_class_name(obj) in ADDITIONAL_SIMPLE_TYPES
    )


def _is_intermediate_type(obj):
    """Return if the obj is an intermediate type."""

    # Special handling for pytz timezone objects.
    if PYTZ_PRESENT and isinstance(obj, pytz.BaseTzInfo):
        return True

    # Handling for all other objects.
    return (
        type(obj) in INTERMEDIATE_TYPES
        or get_class_name(obj) in ADDITIONAL_INTERMEDIATE_TYPES
    )


def is_complex_type(current_depth, current_iteration):
    """Return if we should render the full object"""
    return (
        # Ensure all dump calls are processed.
        current_depth == 0
        # Check for any nested objects
        or (
            # Check if the max_recursion is set to None or we have not reached it yet.
            (
                MAX_RECURSION_DEPTH is None
                or current_depth < MAX_RECURSION_DEPTH
            )

            # And if the max_iterable_length is set to None,
            # or we have not reached it yet or we are at the root level.
            and (
                MAX_ITERABLE_LENGTH is None
                or current_iteration < MAX_ITERABLE_LENGTH
            )
        )
    )


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
        css_class = 'intermediate'
    elif isinstance(obj, types.ModuleType):
        css_class = 'module'
    elif isinstance(obj, BoundField):
        css_class = 'bound'
    else:
        css_class = 'default'

    # Determine which output to use.
    if _is_intermediate_type(obj) or isinstance(obj, Decimal):
        output_value = safe_str(obj)
    else:
        output_value = safe_repr(obj)

    # Since simple type, return safe representation of simple type and
    # which css class to use.
    return {
        'simple': output_value,
        'type': get_obj_type(obj),
        'css_class': css_class,
    }


def _handle_intermediate_type(obj, root_obj, unique, root_count, skip_set=None, original_obj=None):
    """Handling for a intermediate object.

    Effectively, it's an object that's complex enough to have associated attributes and functions that we want to
    display in dd output. But for basic cases, treating it more almost as a "simple type" is generally enough
    information. Thus, it ends up being a combination of the two output formats.

    Similar to "simple type" in that we display base value output without needing to expand.

    Similar to "complex type" in that we display associated attributes, but do not fully recursively expand all.

    :param obj: Object to iterate over and attempt to parse information from.
    :param root_obj: Root, parent object associated with current object.
    :param unique: Unique identifier associated with current object.
    :param root_count: Count of how many times the root object has been dumped as a string prefixed with '_'.
    :param original_obj: Original object, for handling uniques if dealing with deepcopy.
    """
    # Add unique to skip so it won't be processed a second time by additional
    # recursive calls to this template tag.
    skip_set.add(unique)

    # Attempt to get corresponding attribute/function values of object.
    attributes, functions = get_obj_values(obj)

    # Return information required to render object.
    context = {
        'include_attributes': INCLUDE_ATTRIBUTES,
        'include_functions': INCLUDE_FUNCTIONS,
        'collapsable': _get_collapsable_values(),
        'braces': '{}',
        'object': obj,
        'intermediate': safe_str(obj),
        'unique': unique,
        'root_count': root_count,
        'type': get_obj_type(obj),
        'is_iterable': False,
        'depth': 0,
        'root_index_start': None,
        'root_index_end': None,
        'original_obj': original_obj,
    }
    if INCLUDE_ATTRIBUTES:
        context['attributes'] = attributes
        context['index'] = 0
        context['root_obj'] = root_obj
        context['skip'] = set()
    if INCLUDE_FUNCTIONS:
        context['functions'] = functions
        context['multiline_function_docs'] = MULTILINE_FUNCTION_DOCS

    return context


def _handle_complex_type(
    obj,
    root_obj,
    unique,
    root_count,
    skip_set=None,
    current_iteration=0,
    current_depth=0,
    root_index_start=None,
    root_index_end=None,
    original_obj=None,
):
    """
    Main logic for outputting information for a given "unique".

    :param obj: Object to iterate over and attempt to parse information from.
    :param root_obj: Root, parent object associated with current object.
    :param unique: Unique identifier associated with current object.
    :param root_count: Count of how many times the root object has been dumped as a string prefixed with '_'.
    :param original_obj: Original object, for handling uniques if dealing with deepcopy.
    :param skip_set: Set of already-processed objects. Used to skip re-processing identical objects.
    :param current_iteration: Current iteration-index. Used to track current index of object we're iterating through.
    :param current_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    :param root_index_start:
    :param root_index_end:
    """
    # Add unique to skip so it won't be processed a second time by additional
    # recursive calls to this template tag.
    skip_set.add(unique)

    # If the object is a query, evaluate it.
    # This prevents a crash because a lazy queryset has too many members.
    if is_query(obj):
        obj = list(obj)

    # Determine which type of braces should be used.
    if isinstance(obj, list):
        braces = '[]'
    elif isinstance(obj, tuple):
        braces = '()'
    else:
        braces = '{}'

    # Attempt to get corresponding attribute/function values of object.
    attributes, functions = get_obj_values(obj)

    is_iterable_obj = is_iterable(obj) and not is_dict(obj) and not isinstance(obj, memoryview)
    is_dict_obj = is_dict(obj)

    # Return information required to render object.
    context = {
        'include_attributes': INCLUDE_ATTRIBUTES,
        'include_functions': INCLUDE_FUNCTIONS,
        'collapsable': _get_collapsable_values(),
        'braces': braces,
        'object': obj,
        'unique': unique,
        'root_count': root_count,
        'type': get_obj_type(obj),
        'is_iterable': is_iterable_obj,
        'is_dict': is_dict_obj,
        'depth': current_depth,
        'root_index_start': root_index_start,
        'root_index_end': root_index_end,
        'original_obj': original_obj,
    }
    if INCLUDE_ATTRIBUTES:
        context['attributes'] = attributes
        context['index'] = current_iteration
        context['root_obj'] = root_obj
        context['skip'] = skip_set
    if INCLUDE_FUNCTIONS:
        context['functions'] = functions
        context['multiline_function_docs'] = MULTILINE_FUNCTION_DOCS

    return context

# endregion Type Handling Functions


# region Object Property Functions

def get_obj_values(obj):
    """Determines full corresponding member values (attributes/functions) of object."""

    # Initialize attribute/function lists. This is what we ultimately return.
    attributes = []     # (attr, value, access_modifier, css_class, title)
    functions = []      # (attr, doc, access_modifier)

    try:
        # Attempt to get member values of object. Falls back to empty list on failure.
        members = get_members(obj)

    except Exception as exception:
        # On exception, add exception to attributes and return the attributes.

        # First get exception data.
        tb = exception.__traceback__
        title = 'Exception Occurred\n\n'
        title += f'Exception Type: {type(exception).__name__}\n'
        title += f'Exception Value: {str(exception)}\n\n'
        title += 'Traceback (most recent call last):\n\n'
        for entry in traceback.format_tb(tb):
            title += f'{entry}\n'
        title += 'End of traceback'

        # Add exception data to attributes and return.
        attributes.append(['EXCEPTION', str(exception), None, 'empty', title])
        return (attributes, functions)

    # Once all members have been collected, attempt to figure out what type, access modifier, css class, and title
    # should be used for each attribute/function/value in the members.
    for attr, value in members:

        try:

            # Skip private members if not including them.
            if is_private(attr) and not INCLUDE_PRIVATE_METHODS:
                continue

            # Determine if the value is callable (function).
            # If so, Functions will just return documentation.
            is_callable = callable(value)
            if is_callable:  # Handle member functions.

                # Skip dunder (magic) methods if not including them.
                if is_magic(attr) and not INCLUDE_MAGIC_METHODS:
                    continue

                # Get the method signature for attr.
                params = get_callable_params(value)

                # Get the documentation for the method.
                value = inspect.getdoc(value)

                # Get the access modifier for the method.
                access_modifier = _get_access_modifier(attr)

                # Append function to list of functions
                functions.append([attr, params, value, access_modifier])

            else:  # Handle member attributes.

                # Always skip dunder attributes.
                if is_magic(attr):
                    continue

                # If attr is not None (anything but set) change to safe_repr.
                if attr is not None:
                    attr = safe_repr(attr)

                # If not a dict and not None, remove the outside quotes so
                # it looks more like an attribute and not a string.
                if not is_dict(obj) and attr is not None:
                    attr = re.sub("'", "", attr)

                # Determine what type attribute is so that the access modifier,
                # css class, and title can be appropriately set.
                # Processing order is: Index, const, key, set, attribute
                if is_number(attr):  # Index.
                    access_modifier = None
                    css_class = 'index'
                    title = 'Index'
                elif is_const(attr):  # Constant.
                    access_modifier = _get_access_modifier(attr)
                    css_class = 'constant'
                    title = 'Constant'
                elif is_key(attr):  # Key.
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

        except Exception as inner_exception:
            # First get exception data.
            tb = inner_exception.__traceback__
            title = 'Exception:\n'
            while tb is not None:
                line_num = tb.tb_lineno
                name = tb.tb_frame.f_code.co_name
                filename = tb.tb_frame.f_code.co_filename
                tb = tb.tb_next
                title += '\n[ {0} : {1} ] {2}\n'.format(line_num, name, filename)

            # Add exception data to attributes and return.
            attributes.append(['EXCEPTION', str(inner_exception), None, 'empty', title])

    # Attempt to sort the functions and just ignore any errors.
    try:
        functions = sorted(functions)
    except Exception:
        pass  # Ignore sort errors.

    return (attributes, functions)


def _get_access_modifier(obj):
    """Return the access modifier that should be used."""
    if is_magic(obj):
        return '-'
    elif is_private(obj):
        return '#'
    else:
        return '+'

# endregion Object Property Functions


# region Misc Functions

def _process_root_indices(start, end, parent_length):
    """Parse and validate indexes into expected format. Allows use of user-specified index ranges on root element."""

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

    # Determine default sets.
    content_set = {
        'arrow': '▼' if CONTENT_STARTS_EXPANDED else '▶',
        'show': 'show' if CONTENT_STARTS_EXPANDED else '',
        'always_show': 'false',
        'class': '' if CONTENT_STARTS_EXPANDED else 'collapsed',
        'aria': 'true' if CONTENT_STARTS_EXPANDED else 'false',
    }
    attr_set = {
        'arrow': '▼' if ATTRIBUTES_START_EXPANDED else '▶',
        'show': 'show' if ATTRIBUTES_START_EXPANDED else '',
        'always_show': 'false',
        'class': '' if ATTRIBUTES_START_EXPANDED else 'collapsed',
        'aria': 'true' if ATTRIBUTES_START_EXPANDED else 'false',
    }
    func_set = {
        'arrow': '▼' if FUNCTIONS_START_EXPANDED else '▶',
        'show': 'show' if FUNCTIONS_START_EXPANDED else '',
        'always_show': 'false',
        'class': '' if FUNCTIONS_START_EXPANDED else 'collapsed',
        'aria': 'true' if FUNCTIONS_START_EXPANDED else 'false',
    }

    # Extra handling if either attr or func output is disabled.
    # In such a case, it doesn't make sense to have expandable arrows for the remaining one.
    if INCLUDE_FUNCTIONS is False:
        attr_set['arrow'] = ''
        attr_set['show'] = 'show'
        attr_set['always_show'] = 'true'
        attr_set['class'] = 'show always-show'
        attr_set['aria'] = ''
    if INCLUDE_ATTRIBUTES is False:
        func_set['arrow'] = ''
        func_set['show'] = 'show'
        func_set['always_show'] = 'true'
        func_set['class'] = 'show always-show'
        func_set['aria'] = ''

    return {
        'content': content_set,
        'attribute': attr_set,
        'function': func_set,
    }

# endregion Misc Functions
