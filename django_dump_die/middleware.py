"""
Middleware for DumpAndDie.
"""

import copy
import inspect
import logging

from collections.abc import Sequence
from django.conf import settings

from .views import dd_view
from django_dump_die.constants import MAX_RECURSION_DEPTH
from django_dump_die.utils import (
    generate_unique_from_obj,
    get_callable_name,
    get_members,
)
from django_dump_die.templatetags.dump_die import _is_simple_type


logger = logging.getLogger('django_dump_die')
dump_objects = []


class DumpAndDie(Exception):
    """
    DumpAndDie Exception.
    Triggers the middleware exception logic which outputs the alternate dd debug view.
    """
    def __init__(self, obj):
        super().__init__(obj)
        self.object = obj


def _find_nested_name(all_objects, object_needing_name, unique_set, depth=0):
    """
    Look through all the members of local vars trying to find a match.
    If one can not be found, recurse deeper to continue looking.
    """

    # Increment the depth
    depth += 1

    # If we are past the MAX_RECURSION_DEPTH, just give up and return.
    if depth > MAX_RECURSION_DEPTH:
        return []

    # Default to no results in case the local_objs is empty and thus does not loop.
    results = []

    # Look through the local_objs for a match.
    for object_name, object_val in all_objects:

        # Skip objs that are simple and functions.
        if _is_simple_type(object_val) or callable(object_val):
            continue

        # Generate a unique to aid in ensuring we don't recurse indefinitely.
        unique = generate_unique_from_obj(object_val)

        # Get the members of the current obj.
        members = get_members(object_val)

        # Look for a match in the members.
        member_results = [attr for attr, value in members if value == object_needing_name]

        # If there is a match, set the inner results to the main results.
        if member_results:
            results = member_results

        # Else if a new unique, search deeper using recursion.
        elif unique not in unique_set:
            # Add unique to unique set so we don't recurse indefinitely.
            unique_set.add(unique)
            # Recurse deeper looking for a match
            results = _find_nested_name(members, object_needing_name, unique_set, depth=depth)

        # Else, already processed unique and clearly not part of that project.
        else:
            results = []

        # If there are results, no need to keep checking other vars.
        if results:
            break

    return results


def _retrieve_name(object_needing_name):
    """
    Inspects call stack in an attempt to grab names of variables to display in dd output.

    Names are determined by value. On multiple names matching a given value,
    all corresponding names are returned.
    """

    # Attempt to get dumped variable name.
    callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
    results = [var_name for var_name, var_val in callers_local_vars if var_val is object_needing_name]

    # If no results, it might be that they dumped a function on an object
    # rather than a direct function. We can recursively search the members of
    # each var looking for a possible match keeping track of ones we have
    # already considered so that we don't recurse indefinitely.
    if not results:
        # Unique tracker
        unique_set = set()
        # Search through each var from the stack frame where dd was called from.
        results = _find_nested_name(callers_local_vars, object_needing_name, unique_set)

    # If function(s) get the callable name for each function name.
    if callable(object_needing_name):
        new_results = []
        for attr in results:
            new_results.append(get_callable_name(attr, object_needing_name))
        results = new_results

    # Assume no result and if there is, comma join results as return result.
    result = None
    if len(results) > 0:
        result = ", ".join(results)

    return result


def _sanitize_index_range(index_range):
    """
    Validates and sanitizes passed index values.
    """
    # Set index defaults.
    start_index = None
    end_index = None

    # First check if index_range is an iterable.
    if isinstance(index_range, Sequence):
        # Handle for length 2 or more (we ignore values past second index).
        if len(index_range) > 1:
            # Assume is index range. Split values onto indexes.
            start_index = index_range[0]
            end_index = index_range[1]

        # Handle for length exactly 1.
        elif len(index_range) == 1:
            # Assume user typo'd somehow and meant literal start index.
            start_index = index_range[0]

    else:
        # Non-iterable. Assume user passed single start-index value.
        start_index = index_range

    # Sanitize if start_index set.
    if start_index:
        try:
            start_index = int(start_index)
        except TypeError:
            start_index = None

    # Sanitize if end_index set.
    if end_index:
        try:
            end_index = int(end_index)
        except Exception:
            end_index = None

    return start_index, end_index


def dd(obj, index_range=None, deepcopy=False):
    """
    Immediately return debug template with info about objects.
    Includes any objects passed in through dump().

    Does nothing if DEBUG != True.
    """

    if settings.DEBUG:
        # Get object name
        obj_name = _retrieve_name(obj)

        # Handle if function.
        function_doc = None
        if callable(obj):
            function_doc = inspect.getdoc(obj)

        # Sanitize and validate provided index values.
        start_index, end_index = _sanitize_index_range(index_range)

        # Handle if deepcopy set.
        original_obj = None
        try:
            if deepcopy:
                original_obj = obj
                obj = copy.deepcopy(obj)
        except TypeError as type_error:
            original_obj = None
            raise TypeError(f"Object contains type that can't be deep copied. - {type_error}") from None

        # Run dd core logic.
        raise DumpAndDie(
            (obj_name, obj, function_doc, start_index, end_index, original_obj),
        )


def dump(obj, index_range=None, deepcopy=False):
    """
    Show debug template whenever response finishes.
    dd() will also include objects from dump().

    Does nothing if DEBUG != True

    NOTE: Not thread safe, this will collect objects server wide,
    dumped objects can come from multiple requests.
    """

    if settings.DEBUG:
        # Get object name
        obj_name = _retrieve_name(obj)

        # Handle if function.
        function_doc = None
        if callable(obj):
            function_doc = inspect.getdoc(obj)

        # Sanitize and validate provided index values.
        start_index, end_index = _sanitize_index_range(index_range)

        # Handle if deepcopy set.
        original_obj = None
        try:
            if deepcopy:
                original_obj = obj
                obj = copy.deepcopy(obj)
        except TypeError as type_error:
            original_obj = None
            raise TypeError(f"Object contains type that can't be deep copied. - {type_error}") from None

        # Run dd core logic.
        dump_objects.append(
            (obj_name, obj, function_doc, start_index, end_index, original_obj),
        )


class DumpAndDieMiddleware:
    """
    DumpAndDie Middleware.

    Allows access to php/laravel-like function dd().
    """
    def __init__(self, get_response):
        """
        Add our dd() and dump() commands to be universally accessible.
        """
        self.get_response = get_response

        # Add global dd() function.
        __builtins__['dd'] = dd
        # Add global dump() function.
        __builtins__['dump'] = dump

    def __call__(self, request):
        """
        Return standard response if nothing dumped.
        Otherwise return dump view.
        """
        # Get the response
        response = self.get_response(request)

        # If there are no items in the dump_objects list or there is no exception raised
        if not dump_objects or getattr(request, '_has_exception', False):
            return response
        else:
            # Create a copy of the list, and clear it.
            objects = dump_objects[:]
            dump_objects.clear()

            # Return the dd view to dump the items in the dump_objects list.
            return dd_view(request, objects)

    def process_exception(self, request, exception):
        """
        Check if exception is of DumpAndDie type.
        If so, return Debug Response.
        If not, ignore and allow standard exception handling.
        """
        if not isinstance(exception, DumpAndDie):
            request._has_exception = True
            return None

        # Create a copy of the list, and clear it.
        objects = dump_objects[:]
        objects.append(exception.object)
        dump_objects.clear()

        # Return custom DumpAndDie output view.
        return dd_view(request, objects)
