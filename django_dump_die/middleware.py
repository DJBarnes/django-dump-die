"""
Middleware for DumpAndDie.
"""

import copy
import inspect
import logging
import warnings

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


def dd(obj, deepcopy=False):
    """
    Immediately return debug template with info about objects.
    Includes any objects passed in through dump().

    Does nothing if DEBUG != True.
    """
    def retrieve_name(var):
        """
        Inspects call stack in an attempt to grab names of variables to display in dd output.
        Names are determined by value. On multiple names matching given value, all corresponding names are returned.
        """
        callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
        results = [var_name for var_name, var_val in callers_local_vars if var_val is var]
        result = None
        if len(results) > 0:
            result = ", ".join(results)
        return result

    obj_name = retrieve_name(obj)

    if settings.DEBUG:
        if deepcopy:
            obj = copy.deepcopy(obj)

        raise DumpAndDie(
            (obj_name, obj,)
        )


def dump(obj, deepcopy=False):
    """
    Show debug template whenever response finishes.
    dd() will also include objects from dump().

    Does nothing if DEBUG != True

    NOTE: Not thread safe, this will collect objects server wide, dumped objects can come from multiple requests.
    """
    def retrieve_name(var):
        callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
        results = [var_name for var_name, var_val in callers_local_vars if var_val is var]
        result = None
        if len(results) > 0:
            result = ", ".join(results)
        return result

    obj_name = retrieve_name(obj)

    if settings.DEBUG:
        if deepcopy:
            obj = copy.deepcopy(obj)
        dump_objects.append(
            (obj_name, obj,)
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
