"""Template Tags for DumpDie"""

# System Imports.
import inspect
import re
import traceback
import types
from decimal import Decimal

# Third-Party Imports.
from django import template
from django.conf import settings
from django.db import DatabaseError
from django.forms.boundfield import BoundField
from django.utils.functional import Promise

# Internal Imports.
from django_dump_die.app_settings import app_settings
from django_dump_die.constants import (
    BREAK_STYLES,
    DEFAULT_FUNCTION_RESULTS,
    FUNCTION_RESULTS_ATTRIBUTE,
    SIMPLE_TYPES,
    INTERMEDIATE_TYPES,
    PYTZ_PRESENT,
)
from django_dump_die.utils import (
    DumpBreak,
    HiddenValue,
    ItemRange,
    Placeholder,
    get_dumped_object_info,
    is_valid_break_size,
    is_sensitive_name,
    generate_unique_from_obj,
    get_members,
    get_class_name,
    get_attribute_type,
    get_callable_params,
    get_method_type,
    get_obj_type,
    safe_repr,
    safe_str,
    is_iterable,
    is_query,
    is_dict,
    is_const,
    is_enum_member,
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

# Uniques of the dumped root objects on the page being rendered, to count objects dumped more than once, and the
# uniques of the original objects of deep copies. Cleared for each page of dumps by the dump_objects tag.
repeat_iteration_tracker = {}
deepcopy_unique_map = {}

# endregion Module Variables


# region Callable Handling


class NotCalledInTemplates:
    """Holds a dumped callable, such as a function or a class, so that the templates pass it on without calling it.

    Why this is needed:
    When a Django template looks up a variable whose value is callable, it calls it with no arguments and uses the
    return value. That is what lets templates write {{ user.get_full_name }} without parentheses. The only way to
    stop it is a do_not_call_in_templates = True attribute on the value. If the call raises a TypeError because
    arguments are needed, the template uses an empty string instead.

    The dumped object has to pass through template variables: _dump_objects.html gives it to the dump_object tag,
    and the templates that dump_object renders give the root object and the deepcopy original on to the dump_object
    calls for its children. Without this holder, every one of those lookups would call a dumped callable. A dumped
    function would run, possibly several times, and its return value would be dumped instead of the function.
    A dumped class would be dumped as a new instance of itself, or as an empty string if its constructor needs
    arguments.

    The do_not_call_in_templates attribute can't be set on the dumped object itself: it is the user's own object,
    and functions, classes, and builtins may not accept new attributes, or would keep them after the dump.

    How it is used:

    * Python code wraps a callable with _hold_if_callable() right before handing it to a template: the dump_objects
      tag for the dumped objects, and the type handlers for the context that the dump_object tag renders.
    * The dump_object tag unwraps it with _release() as soon as it receives it, so all other Python code works with
      the real object.
    * So templates only ever see the holder. They must not use the dumped object's own value, such as with
      {{ object|length }}, since they would get the holder's. Anything a template shows about the object is worked
      out in Python and put in the context instead, such as the iterable length.

    Only callables are wrapped, so that templates can still use other objects directly, such as a DumpBreak's size.

    Attribute values don't need this: a callable member is listed in the Functions section, as text, and is never
    passed to dump_object. Function results can be callable, so they are wrapped too.

    This can't help the {% dump %} template tag: the template that uses it resolves (and so calls) the variable
    before the tag receives it.
    """

    do_not_call_in_templates = True

    def __init__(self, obj):
        self.obj = obj


def _hold_if_callable(obj):
    """Wrap a callable in NotCalledInTemplates before a template gets it, so that the template doesn't call it.

    See NotCalledInTemplates for why.
    """
    return NotCalledInTemplates(obj) if callable(obj) else obj


def _release(obj):
    """Return the object held in NotCalledInTemplates, or the object itself if it wasn't wrapped.

    See NotCalledInTemplates for why.
    """
    return obj.obj if isinstance(obj, NotCalledInTemplates) else obj


# endregion Callable Handling


@register.inclusion_tag("django_dump_die/partials/_dump.html", takes_context=True)
def dump(context, obj):
    """Template tag that can be used in templates to use dd

    Note: if obj is callable, the calling template has already called it, and obj is its return value.
    Django resolves the tag's argument before the tag runs, so this tag can't prevent that. See NotCalledInTemplates.
    """
    # Like dump() and dd() in Python code, does nothing unless DEBUG is on.
    if not settings.DEBUG:
        return {"dump_enabled": False}

    object_info = get_dumped_object_info(obj)

    new_context = context.flatten()

    # Only the first dump tag on a page loads the css and js.
    # The flag is set on the page's context, so that later dump tags see it.
    render_head = context.get("django_dd_template_tag_render_head", True)
    if render_head:
        context["django_dd_template_tag_render_head"] = False

    new_context.update(
        {
            "objects": [object_info],
            "render_head": render_head,
            "dump_enabled": True,
        }
    )

    return new_context


@register.inclusion_tag("django_dump_die/partials/_dump_objects.html")
def dump_objects(objects):
    """Template tag that can be used to dump a list of objects"""
    if app_settings.BREAK_STYLE not in BREAK_STYLES:
        raise ValueError(
            'DJANGO_DD_BREAK_STYLE must be one of {0}, not "{1}".'.format(
                ", ".join(BREAK_STYLES), app_settings.BREAK_STYLE
            )
        )
    if not is_valid_break_size(app_settings.BREAK_SIZE):
        raise ValueError(
            "DJANGO_DD_BREAK_SIZE must be a whole number of lines, 1 or more, not {0!r}.".format(
                app_settings.BREAK_SIZE
            )
        )
    if app_settings.INCLUDE_FUNCTION_RESULTS:
        _check_function_results_setting()

    # The trackers of repeated objects only last for one page of dumps. Kept longer, they would grow for as long as
    # the server runs. And since a unique comes from id(), which Python reuses once an object is gone, an object on a
    # later page could be taken for one dumped earlier, and get its count or deep copy uniques.
    repeat_iteration_tracker.clear()
    deepcopy_unique_map.clear()

    # _dump_objects.html passes each dumped object, and its deepcopy original, to the dump_object tag through
    # template variables, which would call them if they are callable. So hold callables until dump_object gets them.
    # See NotCalledInTemplates.
    objects = [
        (filename, linenumber, obj_name, _hold_if_callable(obj), function_doc, start, end, _hold_if_callable(original))
        for filename, linenumber, obj_name, obj, function_doc, start, end, original in objects
    ]
    return {"objects": objects, "break_style": app_settings.BREAK_STYLE, "break_size": app_settings.BREAK_SIZE}


@register.filter
def is_dump_break(obj):
    """Return True if the dumped object is a break added with dump.br()."""
    return isinstance(obj, DumpBreak)


@register.filter
def is_placeholder(obj):
    """Return True if the value is shown in place of values that aren't dumped, such as a hidden sensitive value."""
    return isinstance(obj, Placeholder)


@register.inclusion_tag("django_dump_die/partials/_dump_object.html")
def dump_object(
    obj,
    root_obj,
    skip_set=None,
    current_depth=0,
    original_obj=None,
    parent_is_intermediate=False,
    root_index_start=None,
    root_index_end=None,
):
    """Determines template dd/dump info for provided object.

    Determines appropriate attributes/functions associated with object, for dd/dump output to template.

    There are three major object categories:
      * Simple - Basic entities that simply output minimal, direct value output.
      * Intermediate - Objects that that display only one level of attribute/function values.
      * Complex - Complex objects that recursively display attribute/function values for self and all children.

    Note:
      * If we have exceeded the specified depth, then defaults back to "simple" type output.
      * On each call, inner children are minimally processed, and fully processed later in a new call to templatetag.
      * Only the items of an iterable that are dumped are listed: the first MAX_ITERABLE_LENGTH, or for the root
        object the items in its index range. See _get_item_range().

    :param obj: Object to iterate over and attempt to parse information from.
    :param root_obj: Root, parent object associated with current object.
    :param skip_set: Set of already-processed objects. Used to skip re-processing identical non-objects.
    :param current_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    :param original_obj: Original object, for handling uniques if dealing with deepcopy.
    :param parent_is_intermediate: Boolean indicating that parent is intermediate type. Do not recurse further.
    :param root_index_start: Starting index of the root iterable's items to dump. Only given for the root object.
    :param root_index_end: Ending index of the root iterable's items to dump. Only given for the root object.
    """
    # A callable object, root object, or original object reaches this tag wrapped, so that the template passing it
    # here didn't call it. Unwrap them, so that the rest of the code works with the real objects.
    # See NotCalledInTemplates.
    obj, root_obj, original_obj = _release(obj), _release(root_obj), _release(original_obj)

    # Set up set to store uniques to skip if not passed in.
    # Will be used to skip objects already done to prevent infinite loops.
    skip_set = skip_set or set()

    # Generate the unique
    unique, root_count = _generate_unique(obj, root_obj, original_obj)

    # Following section will determine what should get rendered out.
    intermediate_value = None

    # Determine if pytz timezone object for use in below decisions.
    is_pytz_timezone = PYTZ_PRESENT and isinstance(obj, pytz.BaseTzInfo)

    # Handle if object is in skip set, aka already processed.
    intermediate_css_class = None
    if unique in skip_set:
        # Complex object found in skip set. Skip further handling of if clauses and go to end of function.
        # Intermediates get slightly extra handling for "simple" value output.
        if _is_intermediate_type(obj):
            intermediate_value = safe_str(obj)
            intermediate_css_class = _get_intermediate_css_class(obj)

    # Handle if obj is a simple type (Null/None, int, str, bool, and basic number types)
    # OR if direct parent is an intermediate (excluding pytz timezone objects).
    elif _is_simple_type(obj) or (parent_is_intermediate and not is_pytz_timezone):
        return _handle_simple_type(obj)

    # Handle if obj is an intermediate (date/time types).
    elif _is_intermediate_type(obj):
        return _handle_intermediate_type(
            obj,
            root_obj,
            unique,
            root_count,
            skip_set=skip_set,
            original_obj=original_obj,
        )

    # Handle if at the root object, or not past the maximum depth yet.
    elif is_complex_type(current_depth):

        # Handle for new "unique" object output.
        return _handle_complex_type(
            obj,
            root_obj,
            unique,
            root_count,
            skip_set=skip_set,
            current_depth=current_depth,
            root_index_start=root_index_start,
            root_index_end=root_index_end,
            original_obj=original_obj,
        )

    # If we're here then the object has already been processed before,
    # or we have reached the max depth.
    # In any case, just return the type and unique of the object for output.
    return {
        "type": get_obj_type(obj),
        "unique": unique,
        "root_count": root_count,
        "intermediate": intermediate_value,
        "intermediate_css_class": intermediate_css_class,
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
    root_count_string = ""

    # If there is an original_obj, we may need to create the unique map so that
    # we can restore the original uniques to the deepcopied object.
    # Compared with None, since the truth of some objects runs code, such as a QuerySet, which loads every row.
    if original_obj is not None:
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
            root_count_string = f"_{root_count}"
        else:
            root_count_string = ""

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

    # Map each object once. Objects that refer back to an object already mapped, such as a form's bound fields
    # referring to their form, would otherwise recurse forever.
    if obj_unique in deepcopy_unique_map[root_unique]:
        return

    # Add the new unique to the root unique map.
    deepcopy_unique_map[root_unique][obj_unique] = original_obj_unique

    # Attempt to get member values of object and original object.
    members = get_members(obj)
    original_members = get_members(original_obj)

    # Loop through members and recursively determine unique mappings.
    # We do this because the state of an object might change over time, so child values (and mappings) might be
    # different. Parent might also be of complex type with children that are also complex types.
    for attr, value in members:
        # Skip simple types and children of intermediate types, in the copy or in the original, which may have
        # changed since it was copied.
        if _is_simple_type(value) or _is_intermediate_type(obj) or _is_intermediate_type(original_obj):
            continue
        # Skip private members if not including them and functions.
        if (is_private(attr) and not app_settings.INCLUDE_PRIVATE_MEMBERS) or callable(value):
            continue

        # Loop through orig members looking for a match.
        for orig_attr, orig_value in original_members:
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
        or get_class_name(obj) in app_settings.ADDITIONAL_SIMPLE_TYPES
        # Subclasses of str, such as Django's SafeString, and lazy strings, such as from gettext_lazy(), are shown as
        # their text, like a str. Enum members that are also strings stay enums.
        or (isinstance(obj, (str, Promise)) and not is_enum_member(obj))
    )


def _is_intermediate_type(obj):
    """Return if the obj is an intermediate type."""

    # Special handling for pytz timezone objects.
    if PYTZ_PRESENT and isinstance(obj, pytz.BaseTzInfo):
        return True

    # Handling for all other objects.
    return type(obj) in INTERMEDIATE_TYPES or get_class_name(obj) in app_settings.ADDITIONAL_INTERMEDIATE_TYPES


def is_complex_type(current_depth):
    """Return if we should render the full object.

    The items of an iterable past MAX_ITERABLE_LENGTH aren't checked here, since they aren't listed. See get_members().
    """
    return (
        # Ensure all dump calls are processed.
        current_depth == 0
        # Check if the max_recursion is set to None or we have not reached it yet.
        or app_settings.MAX_RECURSION_DEPTH is None
        or current_depth < app_settings.MAX_RECURSION_DEPTH
    )


def _handle_simple_type(obj):
    """
    Logic for outputting information about a "simple type".
    Includes str, numbers, bools, etc.
    """
    # Determine which css class to use.
    css_class = ""
    if obj is None:
        css_class = "none"
    elif isinstance(obj, (str, Promise)):
        css_class = "string"
    elif isinstance(obj, bool):
        css_class = "bool"
    elif isinstance(obj, (int, Decimal, float, bytes)):
        css_class = "number"
    elif _is_intermediate_type(obj):
        css_class = _get_intermediate_css_class(obj)
    elif isinstance(obj, types.ModuleType):
        css_class = "module"
    else:
        css_class = "default"

    # Determine which output to use.
    if isinstance(obj, Promise):
        # A lazy string's text, quoted like a str.
        output_value = safe_repr(safe_str(obj))
    elif _is_intermediate_type(obj) or isinstance(obj, Decimal):
        output_value = safe_str(obj)
    else:
        output_value = safe_repr(obj)

    # Since simple type, return safe representation of simple type and
    # which css class to use.
    return {
        "simple": output_value,
        "type": get_obj_type(obj),
        "css_class": css_class,
    }


def _get_intermediate_css_class(obj):
    """Return the CSS class of an intermediate object's value. Bound form fields have a color of their own."""
    return "bound" if isinstance(obj, BoundField) else "intermediate"


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
    function_results = get_function_results(obj) if app_settings.INCLUDE_FUNCTION_RESULTS else []

    # Return information required to render object.
    # The object, root object, and original object go through template variables again, to the dump_object calls
    # for the children, so callables stay wrapped. See NotCalledInTemplates.
    context = {
        "include_attributes": app_settings.INCLUDE_ATTRIBUTES,
        # Only objects with functions listed have a Function Results section. Most objects have none, and an
        # empty section on each of them would only be noise.
        "include_function_results": bool(function_results),
        "include_functions": app_settings.INCLUDE_FUNCTIONS,
        "collapsable": _get_collapsable_values(has_function_results=bool(function_results)),
        "braces": "{}",
        "object": _hold_if_callable(obj),
        "intermediate": safe_str(obj),
        "intermediate_css_class": _get_intermediate_css_class(obj),
        "unique": unique,
        "root_count": root_count,
        "type": get_obj_type(obj),
        "is_iterable": False,
        "depth": 0,
        "original_obj": _hold_if_callable(original_obj),
    }
    if app_settings.INCLUDE_ATTRIBUTES or function_results:
        # Used by both sections to dump their values.
        context["root_obj"] = _hold_if_callable(root_obj)
        context["skip"] = set()
    if app_settings.INCLUDE_ATTRIBUTES:
        context["attributes"] = attributes
    if function_results:
        context["function_results"] = function_results
    if app_settings.INCLUDE_FUNCTIONS:
        context["functions"] = functions
        context["multiline_function_docs"] = app_settings.MULTILINE_FUNCTION_DOCS

    return context


def _handle_complex_type(
    obj,
    root_obj,
    unique,
    root_count,
    skip_set=None,
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
    :param current_depth: Current depth-index. Used to track how deep of child-members we're iterating through.
    :param root_index_start: Starting index of the root iterable's items to dump. Only given for the root object.
    :param root_index_end: Ending index of the root iterable's items to dump. Only given for the root object.
    """
    # Add unique to skip so it won't be processed a second time by additional
    # recursive calls to this template tag.
    skip_set.add(unique)

    # Get a QuerySet's length with count(), which doesn't load its rows if it isn't evaluated yet, unlike len().
    # Only the rows dumped are fetched. See get_members().
    length = None
    query_exception = None
    if is_query(obj):
        try:
            length = obj.count()
        except DatabaseError as exception:
            # The query failed, such as when its table doesn't exist. Show the error instead of the results.
            query_exception = exception

    is_dict_obj = is_dict(obj)
    is_iterable_obj = (
        query_exception is None and is_iterable(obj) and not is_dict_obj and not isinstance(obj, memoryview)
    )
    if length is None and (is_iterable_obj or is_dict_obj):
        length = _get_length(obj)

    # Determine which type of braces should be used.
    if isinstance(obj, list) or (is_iterable_obj and is_query(obj)):
        braces = "[]"
    elif isinstance(obj, tuple):
        braces = "()"
    else:
        braces = "{}"

    # Attempt to get corresponding attribute/function values of object.
    if query_exception is not None:
        attributes, functions = [_get_exception_attribute(query_exception)], []
    else:
        item_range = None
        if is_iterable_obj:
            item_range = _get_item_range(length, root_index_start, root_index_end)
        attributes, functions = get_obj_values(obj, item_range)

    # A query that failed has no results to show, only its error.
    function_results = []
    if app_settings.INCLUDE_FUNCTION_RESULTS and query_exception is None:
        function_results = get_function_results(obj)

    # Return information required to render object.
    # The object, root object, and original object go through template variables again, to the dump_object calls
    # for the children, so callables stay wrapped. See NotCalledInTemplates.
    context = {
        "include_attributes": app_settings.INCLUDE_ATTRIBUTES,
        # Only objects with functions listed have a Function Results section. Most objects have none, and an
        # empty section on each of them would only be noise.
        "include_function_results": bool(function_results),
        "include_functions": app_settings.INCLUDE_FUNCTIONS,
        "collapsable": _get_collapsable_values(has_function_results=bool(function_results)),
        "braces": braces,
        "object": _hold_if_callable(obj),
        # Worked out here, since the template can't use the length filter on an object that may be wrapped.
        "length": length,
        "unique": unique,
        "root_count": root_count,
        "type": get_obj_type(obj),
        "is_iterable": is_iterable_obj,
        "is_dict": is_dict_obj,
        "depth": current_depth,
        "original_obj": _hold_if_callable(original_obj),
    }
    if app_settings.INCLUDE_ATTRIBUTES or function_results:
        # Used by both sections to dump their values.
        context["root_obj"] = _hold_if_callable(root_obj)
        context["skip"] = skip_set
    if app_settings.INCLUDE_ATTRIBUTES:
        context["attributes"] = attributes
    if function_results:
        context["function_results"] = function_results
    if app_settings.INCLUDE_FUNCTIONS:
        context["functions"] = functions
        context["multiline_function_docs"] = app_settings.MULTILINE_FUNCTION_DOCS

    return context


# endregion Type Handling Functions


# region Object Property Functions


def _get_exception_attribute(exception):
    """Attribute entry that shows an exception raised while inspecting an object, with its traceback."""
    tb = exception.__traceback__
    title = "Exception Occurred\n\n"
    title += f"Exception Type: {type(exception).__name__}\n"
    title += f"Exception Value: {str(exception)}\n\n"
    title += "Traceback (most recent call last):\n\n"
    for entry in traceback.format_tb(tb):
        title += f"{entry}\n"
    title += "End of traceback"

    return ["EXCEPTION", str(exception), None, "empty", title, None]


def get_obj_values(obj, item_range=None):
    """Determines full corresponding member values (attributes/functions) of object.

    :param item_range: ItemRange of the items to list, for an iterable. See get_members().
    """

    # Initialize attribute/function lists. This is what we ultimately return.
    attributes = []  # (attr, value, access_modifier, css_class, title, decorator)
    functions = []  # (attr, params, doc, access_modifier, method_type)

    try:
        # Attempt to get member values of object. Falls back to empty list on failure.
        members = get_members(obj, item_range)

    except Exception as exception:
        # On exception, add exception to attributes and return the attributes.
        attributes.append(_get_exception_attribute(exception))
        return (attributes, functions)

    # Once all members have been collected, attempt to figure out what type, access modifier, css class, and title
    # should be used for each attribute/function/value in the members.
    for attr, value in members:

        try:

            # Skip private members if not including them.
            # Magic members also start with an underscore, but follow their own setting below.
            if is_private(attr) and not is_magic(attr) and not app_settings.INCLUDE_PRIVATE_MEMBERS:
                continue

            # Determine if the value is callable (function).
            # If so, Functions will just return documentation.
            is_callable = callable(value)
            if is_callable:  # Handle member functions.

                # Skip dunder (magic) methods if not including them.
                if is_magic(attr) and not app_settings.INCLUDE_MAGIC_METHODS:
                    continue

                # Get the method signature for attr.
                params = get_callable_params(value)

                # Get the documentation for the method.
                doc = inspect.getdoc(value)

                # Get the access modifier for the method.
                access_modifier = _get_access_modifier(attr)

                # Get whether the method is a static or class method.
                method_type = get_method_type(obj, attr)

                # Append function to list of functions
                functions.append([attr, params, doc, access_modifier, method_type])

            else:  # Handle member attributes.

                # Always skip dunder attributes.
                if is_magic(attr):
                    continue

                # Get whether the attribute is a property, or comes from the object's class.
                attribute_type = get_attribute_type(obj, attr)
                decorator = attribute_type if attribute_type in ("property", "cached_property") else None

                # Hide the value if its name looks sensitive, such as a password, secret key, or session cookie.
                shown_value = HiddenValue() if is_sensitive_name(attr) else value

                # The name shown. If attr is not None (anything but set) change to safe_repr.
                label = attr
                if label is not None:
                    label = safe_repr(label)

                # If not a dict and not None, remove the outside quotes so
                # it looks more like an attribute and not a string.
                if not is_dict(obj) and label is not None:
                    label = re.sub("'", "", label)

                # Determine what type attribute is so that the access modifier,
                # css class, and title can be appropriately set.
                # Processing order is: Index, const, key, set, attribute
                if is_number(label):  # Index.
                    access_modifier = None
                    css_class = "index"
                    title = "Index"
                elif is_const(label):  # Constant.
                    access_modifier = _get_access_modifier(label)
                    css_class = "constant"
                    title = "Constant"
                elif is_key(label):  # Key.
                    access_modifier = None
                    css_class = "key"
                    title = "Key"
                    decorator = None
                elif label is None:  # Set.
                    access_modifier = None
                    css_class = ""
                    title = ""
                elif attribute_type == "class_attribute":  # Attribute from the object's class.
                    access_modifier = _get_access_modifier(label)
                    css_class = "class_attribute"
                    title = "Class Attribute"
                else:  # Instance Attribute.
                    access_modifier = _get_access_modifier(label)
                    css_class = "attribute"
                    title = "Attribute"

                # Append the attribute information to the list of attributes.
                attributes.append([label, shown_value, access_modifier, css_class, title, decorator])

        except Exception as inner_exception:
            # First get exception data.
            tb = inner_exception.__traceback__
            title = "Exception:\n"
            while tb is not None:
                line_num = tb.tb_lineno
                name = tb.tb_frame.f_code.co_name
                filename = tb.tb_frame.f_code.co_filename
                tb = tb.tb_next
                title += f"\n[ {line_num} : {name} ] {filename}\n"

            # Add exception data to attributes and return.
            attributes.append(["EXCEPTION", str(inner_exception), None, "empty", title, None])

    # Attempt to sort the functions and just ignore any errors.
    try:
        functions = sorted(functions)
    except Exception:
        pass  # Ignore sort errors.

    return (attributes, functions)


# region Function Results


def _is_list_of_names(names):
    """Return True if names is a list, tuple, or set of strings. A single string is not, so that it isn't split up."""
    return isinstance(names, (list, tuple, set, frozenset)) and all(isinstance(name, str) for name in names)


def _check_function_results_setting():
    """Raise a ValueError if DJANGO_DD_FUNCTION_RESULTS isn't a dict of class names to lists of function names."""
    if not isinstance(app_settings.FUNCTION_RESULTS, dict):
        raise ValueError(
            "DJANGO_DD_FUNCTION_RESULTS must be a dict of class names to lists of function names, not {0!r}.".format(
                app_settings.FUNCTION_RESULTS
            )
        )
    for class_name, names in app_settings.FUNCTION_RESULTS.items():
        if not _is_list_of_names(names):
            raise ValueError(
                "DJANGO_DD_FUNCTION_RESULTS[{0!r}] must be a list of function names, not {1!r}.".format(
                    class_name, names
                )
            )


def _get_function_result_row(name, value=None, error=None, error_title=None):
    """Return one row of the Function Results section. A row with an error shows the error instead of a value."""
    return {
        "name": name,
        # The value goes through a template variable to dump_object, which would call it. See NotCalledInTemplates.
        "value": _hold_if_callable(value),
        "access_modifier": _get_access_modifier(name),
        "error": error,
        "error_title": error_title,
    }


def _get_function_result_error_row(name, exception):
    """Return the row of a function result that raised an error, with the error in place of the result."""
    _, message, _, _, title, _ = _get_exception_attribute(exception)
    return _get_function_result_row(name, error="{0}: {1}".format(type(exception).__name__, message), error_title=title)


def _get_function_result(obj, name):
    """Run one listed function of the object, and return its row, with the result or the reason it has none."""
    # A function whose name looks sensitive isn't run, and its result is hidden like a sensitive attribute.
    if is_sensitive_name(name):
        return _get_function_result_row(name, error=HiddenValue.text, error_title=HiddenValue.title)

    try:
        function = getattr(obj, name)
    except AttributeError:
        return _get_function_result_row(
            name,
            error="Not Found",
            error_title="Listed in {0} or DJANGO_DD_FUNCTION_RESULTS, but the object has no such function.".format(
                FUNCTION_RESULTS_ATTRIBUTE
            ),
        )
    except Exception as exception:
        # Such as a listed property that raises an error.
        return _get_function_result_error_row(name, exception)
    if not callable(function):
        return _get_function_result_row(
            name,
            error="Not A Function",
            error_title="Listed in {0} or DJANGO_DD_FUNCTION_RESULTS, but it isn't a function.".format(
                FUNCTION_RESULTS_ATTRIBUTE
            ),
        )

    # Only run functions that need no arguments. Some built-in functions, such as datetime's, have no signature to
    # check. They are run anyway, and if they need arguments, the TypeError is shown below like any other error.
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        signature = None
    if signature is not None:
        try:
            signature.bind()
        except TypeError:
            return _get_function_result_row(
                name,
                error="Needs Arguments",
                error_title="Only functions that can be called without arguments are run.",
            )

    try:
        value = function()
    except Exception as exception:
        # Show the error in place of the result, so that the rest of the dump still shows.
        return _get_function_result_error_row(name, exception)

    return _get_function_result_row(name, value=value)


def get_function_results(obj):
    """Run the functions listed for the object, and return a row for each, sorted by name.

    Only called when DJANGO_DD_INCLUDE_FUNCTION_RESULTS is on. The functions come from:
      * DJANGO_DD_FUNCTION_RESULTS, for the object's class name. If the class isn't in it, DEFAULT_FUNCTION_RESULTS.
      * The dd_function_results attribute of the object's class.
    """
    # A dumped class's methods aren't bound to an object, so nothing is run.
    if inspect.isclass(obj):
        return []

    class_name = get_class_name(obj)
    names = set(app_settings.FUNCTION_RESULTS.get(class_name, DEFAULT_FUNCTION_RESULTS.get(class_name, ())))
    rows = []

    # Read the class attribute without running anything. getattr() would also call a __getattr__ method, which can
    # return something for any name, such as on a mock object.
    attribute_names = inspect.getattr_static(obj, FUNCTION_RESULTS_ATTRIBUTE, ())
    if _is_list_of_names(attribute_names):
        names.update(attribute_names)
    else:
        rows.append(
            _get_function_result_row(
                FUNCTION_RESULTS_ATTRIBUTE,
                error="Not A List Of Function Names",
                error_title="{0} must be a list or tuple of function names, not {1!r}.".format(
                    FUNCTION_RESULTS_ATTRIBUTE, attribute_names
                ),
            )
        )

    rows.extend(_get_function_result(obj, name) for name in sorted(names))
    return rows


# endregion Function Results


def _get_length(obj):
    """Return the length shown after an iterable's type. 0 if it has none, like Django's length filter.

    Used instead of the template's length filter, which would measure the NotCalledInTemplates holder of a callable.
    """
    try:
        return len(obj)
    except (TypeError, ValueError):
        # Such as a Django SessionStore, which is dict-like without a length.
        return 0


def _get_access_modifier(obj):
    """Return the access modifier that should be used."""
    if is_magic(obj):
        return "-"
    elif is_private(obj):
        return "#"
    else:
        return "+"


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
    # MAX_ITERABLE_LENGTH None means no limit.
    limit = app_settings.MAX_ITERABLE_LENGTH
    if limit is None:
        limit = parent_length
    if end is None:
        end = limit

    # Handle if provided start_index is negative.
    if start < 0:
        start = parent_length + start

        # Reset if still negative.
        start = max(start, 0)

    # If the original value of end is None, there is no specified end and
    # it makes sense to then run from the start, now that it is calculated,
    # to the max iterable length.
    if orig_end is None:
        end = start + limit

    # Handle if provided end_index is negative.
    if end < 0:
        end = parent_length + end

        # Reset if still negative.
        end = max(end, 0)

    # Handle if user provided a start_index that is higher than end_index.
    if start > end:
        temp = start
        start = end
        end = temp

    # Return the processed indices.
    return start, end


def _get_item_range(length, root_index_start=None, root_index_end=None):
    """Return the ItemRange of an iterable's items to dump.

    The root object's items are those in the index_range of dump() and dd(), and otherwise, like the items of other
    iterables, the first MAX_ITERABLE_LENGTH.
    """
    start, stop = _process_root_indices(root_index_start, root_index_end, length)
    return ItemRange(min(start, length), min(stop, length), length)


def _get_collapsable_values(has_function_results=False):
    """Get the arrow and collapsable values

    :param has_function_results: Whether the object has a Function Results section.
    """

    # Determine default sets.
    content_set = {
        "arrow": "▼" if app_settings.CONTENT_STARTS_EXPANDED else "▶",
        "show": "show" if app_settings.CONTENT_STARTS_EXPANDED else "",
        "always_show": "false",
        "class": "" if app_settings.CONTENT_STARTS_EXPANDED else "collapsed",
        "aria": "true" if app_settings.CONTENT_STARTS_EXPANDED else "false",
    }
    attr_set = {
        "arrow": "▼" if app_settings.ATTRIBUTES_START_EXPANDED else "▶",
        "show": "show" if app_settings.ATTRIBUTES_START_EXPANDED else "",
        "always_show": "false",
        "class": "" if app_settings.ATTRIBUTES_START_EXPANDED else "collapsed",
        "aria": "true" if app_settings.ATTRIBUTES_START_EXPANDED else "false",
    }
    result_set = {
        "arrow": "▼" if app_settings.FUNCTION_RESULTS_START_EXPANDED else "▶",
        "show": "show" if app_settings.FUNCTION_RESULTS_START_EXPANDED else "",
        "always_show": "false",
        "class": "" if app_settings.FUNCTION_RESULTS_START_EXPANDED else "collapsed",
        "aria": "true" if app_settings.FUNCTION_RESULTS_START_EXPANDED else "false",
    }
    func_set = {
        "arrow": "▼" if app_settings.FUNCTIONS_START_EXPANDED else "▶",
        "show": "show" if app_settings.FUNCTIONS_START_EXPANDED else "",
        "always_show": "false",
        "class": "" if app_settings.FUNCTIONS_START_EXPANDED else "collapsed",
        "aria": "true" if app_settings.FUNCTIONS_START_EXPANDED else "false",
    }

    # If only one section is shown, it doesn't make sense for it to have an expandable arrow, so it's always shown.
    sections = [
        (app_settings.INCLUDE_ATTRIBUTES, attr_set),
        (has_function_results, result_set),
        (app_settings.INCLUDE_FUNCTIONS, func_set),
    ]
    shown_sets = [section_set for included, section_set in sections if included]
    if len(shown_sets) == 1:
        shown_sets[0].update(
            {
                "arrow": "",
                "show": "show",
                "always_show": "true",
                "class": "show always-show",
                "aria": "",
            }
        )

    return {
        "content": content_set,
        "attribute": attr_set,
        "function_result": result_set,
        "function": func_set,
    }


# endregion Misc Functions
