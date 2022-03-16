"""Middleware for DumpDie"""
import contextlib
import copy
import inspect
import logging
import threading
import warnings

from django.conf import settings
from django.template import Context

from .views import dd_view


logger = logging.getLogger('django_dump_die')
dump_objects = []
local_settings_unused_ignore = getattr(settings, 'CONTEXT_UNUSED_IGNORE', [])
UNUSED_IGNORE = [
    'sql_queries',
    'perms',
    'DEFAULT_MESSAGE_LEVELS',
    'debug',
    'False',
    'None',
    'True',
    'csrf_token',
    'view',
    'object',
    'site',
    'site_name',
    'page_obj',
    'is_paginated',
    'paginator',
    'user',
    'messages',
    # Error pages (from assertRaises)
    'lastframe',
] + local_settings_unused_ignore

lock = threading.Lock()


@contextlib.contextmanager
def warn_unused_context(request):
    """Warn if unused keys in context when using request.

    Currently ignores admin pages

    Usage:
        with warn_unused_context(request):
            response = self.get_response(request)
    """
    if request.path.startswith('/admin/'):
        yield  # Let caller get the response
        return  # Ignore admin pages

    # NOTE: Monkeypatching is not threadsafe
    lock.acquire()

    # Monkeypatch context to keep track of unused variables in context
    __orig_getitem__ = Context.__getitem__

    used_keys = set(UNUSED_IGNORE)
    all_keys = set()

    def __getitem__(self, key):
        if not all_keys:
            flattened = {}
            try:
                flattened = self.flatten()
            except Exception as err:
                # Exceptions here are usually caused because a template tag
                # returned a Context() object instead of a plain dictionary.
                logger.exception("Ignoring context error: %s", err)
                raise
            for x, y in flattened.items():
                if y:
                    all_keys.add(x)
        used_keys.add(key)
        return __orig_getitem__(self, key)

    try:
        Context.__getitem__ = __getitem__

        # Let caller get the response
        yield
    finally:
        # Un-patch it
        Context.__getitem__ = __orig_getitem__
        lock.release()

    # Check for unused keys
    unused = all_keys.difference(used_keys)

    if unused:
        msg = "Request Context %s had unused keys: %s"
        warnings.warn(msg % (request, unused))
        logger.warning(msg, request, unused)


class DumpAndDie(Exception):
    """Dump And Die Exception"""

    def __init__(self, obj):
        super().__init__(obj)
        self.object = obj


def dd(obj, deepcopy=False):
    """Immediately return debug template with info about objects.

    Includes any objects passed in through dump().

    Does nothing if DEBUG != True
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

        raise DumpAndDie(
            (obj_name, obj,)
        )


def dump(obj, deepcopy=False):
    """Show debug template whenever response finishes.

    dd() will also include objects from dump().

    Does nothing if DEBUG != True

    NOTE: Not thread safe, this will collect objects server wide,
    dumped objects can come from multiple requests.
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
    """Dump And Die Middleware

    Allows access to php/laravel-like function dd().
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Add global dd() function
        __builtins__['dd'] = dd
        # Add global dump() function
        __builtins__['dump'] = dump

    def __call__(self, request):
        """Simply return the response if nothing dumped"""
        with warn_unused_context(request):
            response = self.get_response(request)

        if not dump_objects or getattr(request, '_has_exception', False):
            return response
        else:
            # Create a copy of the list, and clear it
            objects = dump_objects[:]
            dump_objects.clear()

            return dd_view(request, objects)

    def process_exception(self, request, exception):
        """Check if exception is from dd(). If not, ignore.

        If so, return Debug Response.
        """
        if not isinstance(exception, DumpAndDie):
            request._has_exception = True
            return None

        # Create a copy of the list, and clear it
        objects = dump_objects[:]
        objects.append(exception.object)
        dump_objects.clear()

        return dd_view(request, objects)
