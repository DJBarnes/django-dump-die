"""
Middleware for DumpAndDie.
"""

import copy
import inspect
import logging

from collections.abc import Sequence
from django.conf import settings

from .views import dd_view


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


def _get_callable_name(var, results):
    """
    Do extra processing for a function to get it's information.
    """
    new_results = []
    for result in results:
        # Get the method signature and fall back to simply appending
        # parentheses to the method name on exception.
        try:
            result += str(inspect.signature(var))
        except Exception:
            result += '()'
        new_results.append(result)

    return new_results


def _retrieve_name(var):
    """
    Inspects call stack in an attempt to grab names of variables to display in dd output.
    Names are determined by value. On multiple names matching given value, all corresponding names are returned.
    """

    # Get dumped variable name.
    callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
    results = [var_name for var_name, var_val in callers_local_vars if var_val is var]

    # If no results, it might be that they dumped a function on an object.
    # rather than a direct function. We can search the members of each var
    # looking for a possible match.
    # NOTE: This increases the chance of returning a function name that isn't exactly right.
    if not results:
        # Search through each var from the stack frame where dd was called from.
        for local_var_name, local_var_val in callers_local_vars:
            # Get the members of the current var.
            members = inspect.getmembers(local_var_val)
            # Look for a match. Can include callable as a requirement as we know we are looking for a function.
            inner_results = [inner_var_name for inner_var_name, inner_var_val in members if callable(inner_var_val) and inner_var_val == var]
            # If there is a match, set the inner results to the main results.
            if inner_results:
                results = inner_results

    # If function(s) get the callable name.
    if callable(var):
        results = _get_callable_name(var, results)

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
        if deepcopy:
            obj = copy.deepcopy(obj)

        # Run dd core logic.
        raise DumpAndDie(
            (obj_name, obj, function_doc, start_index, end_index),
        )


def dump(obj, index_range=None, deepcopy=False):
    """
    Show debug template whenever response finishes.
    dd() will also include objects from dump().

    Does nothing if DEBUG != True

    NOTE: Not thread safe, this will collect objects server wide, dumped objects can come from multiple requests.
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
        if deepcopy:
            obj = copy.deepcopy(obj)

        # Run dd core logic.
        dump_objects.append(
            (obj_name, obj, function_doc, start_index, end_index),
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
