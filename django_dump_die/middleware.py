"""
Middleware for DumpAndDie.
"""

# System Imports.
import asyncio
import logging

# Third-Party Imports.
from django.conf import settings

# Imports that may not be accessible, depending on the Django version.
try:
    from asgiref.sync import sync_to_async
except ImportError:
    # Django 2.2 doesn't install asgiref, and doesn't support async middleware.
    sync_to_async = None
try:
    from asgiref.sync import iscoroutinefunction, markcoroutinefunction
except ImportError:
    # asgiref before 3.6, which Django 3.1 to 4.0 allow.
    iscoroutinefunction = asyncio.iscoroutinefunction
    markcoroutinefunction = None

# Internal Imports.
from .views import dd_view
from django_dump_die.utils import DumpBreak, get_dumped_object_info, is_valid_break_size

logger = logging.getLogger("django_dump_die")
dump_objects = []


class DumpAndDie(Exception):
    """
    DumpAndDie Exception.
    Triggers the middleware exception logic which outputs the alternate dd debug view.
    """

    def __init__(self, obj):
        super().__init__(obj)
        self.object = obj


def dd(obj, index_range=None, deepcopy=False):
    """
    Immediately return debug template with info about objects.
    Includes any objects passed in through dump().

    Does nothing if DEBUG != True.
    """

    if settings.DEBUG:

        # Get the object info
        object_info = get_dumped_object_info(obj, index_range, deepcopy)

        # Run dd core logic.
        raise DumpAndDie(object_info)


def dump(obj, index_range=None, deepcopy=False):
    """
    Show debug template whenever response finishes.
    dd() will also include objects from dump().

    Does nothing if DEBUG != True

    NOTE: Not thread safe, this will collect objects server wide,
    dumped objects can come from multiple requests.
    """

    if settings.DEBUG:

        # Get the object info
        object_info = get_dumped_object_info(obj, index_range, deepcopy)

        # Run dd core logic.
        dump_objects.append(object_info)


def dump_break(size=None):
    """
    Show a break between the objects dumped before and after it.
    Used as dump.br(), so that it doesn't need its own built-in name.

    :param size: Height of the break, as a whole number of lines. Defaults to DJANGO_DD_BREAK_SIZE.

    Does nothing if DEBUG != True
    """

    # Check the size even when DEBUG is off, so that a typo shows up at the call.
    if size is not None and not is_valid_break_size(size):
        raise ValueError("dump.br() size must be a whole number of lines, 1 or more, not {0!r}.".format(size))

    if settings.DEBUG:
        dump_objects.append((None, None, None, DumpBreak(size), None, None, None, None))


# Make dump_break available as dump.br().
dump.br = dump_break


def _set_content(response, content):
    """
    Replace the response's content, and its Content-Length header if it has one.

    Middleware below this one, such as Django's CommonMiddleware, may have set Content-Length already. Left at the old
    length, it would make the browser cut off the new content.
    """
    response.content = content
    if response.has_header("Content-Length"):
        response["Content-Length"] = str(len(response.content))


class DumpAndDieMiddleware:
    """
    DumpAndDie Middleware.

    Allows access to php/laravel-like function dd().

    Supports both sync and async requests (Django 3.1+), so that under ASGI it doesn't make Django switch between
    the event loop and a thread around the view on every request.
    """

    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        """
        Add our dd() and dump() commands to be universally accessible.
        """
        self.get_response = get_response

        # Under ASGI, Django passes an async get_response. Mark this middleware as async too, so that Django awaits it.
        self.is_async = iscoroutinefunction(get_response)
        if self.is_async:
            if markcoroutinefunction is not None:
                markcoroutinefunction(self)
            else:  # pragma: no cover
                # asgiref before 3.6, as installed on Python 3.6, which CI tests. How Django before 4.1 detects async
                # middleware.
                self._is_coroutine = asyncio.coroutines._is_coroutine  # pylint: disable=protected-access

        # Add global dd() function.
        __builtins__["dd"] = dd
        # Add global dump() function.
        __builtins__["dump"] = dump

    def __call__(self, request):
        """
        Return standard response if nothing dumped.
        Otherwise return dump view.
        """
        if self.is_async:
            return self.__acall__(request)

        # Get the response
        response = self.get_response(request)
        return self._process_response(request, response)

    async def __acall__(self, request):
        """
        Async version of __call__, used under ASGI.
        Awaits the rest of the middleware chain directly, and only switches to a thread when something was dumped.
        """
        response = await self.get_response(request)

        # Nothing was dumped, so the response is returned unchanged, without leaving the event loop.
        if not dump_objects:
            return response

        # Rendering the dump page can query the database, such as for a dumped QuerySet, which Django only allows
        # in sync code. So render it in a thread.
        return await sync_to_async(self._process_response, thread_sensitive=True)(request, response)

    def _process_response(self, request, response):
        """
        Return the dump page instead of the response if anything was dumped.
        After an unhandled exception, add the dumps to the error page instead.
        """
        # Nothing was dumped, so the response is returned unchanged.
        if not dump_objects:
            return response

        # Take the dumped objects, so that they are only shown once.
        objects = dump_objects[:]
        dump_objects.clear()

        # dump() and dump.br() only collect objects while DEBUG is on. But DEBUG can be turned off after they were
        # collected, such as by override_settings in tests. Dumps can hold anything, including secrets, so they are
        # never shown with DEBUG off.
        if not settings.DEBUG:
            return response

        # Determine if view had an unhandled non-dd exception.
        # This attribute will be set by the "process_exception" method below.
        has_non_dd_exception = getattr(request, "has_non_dd_exception", False)

        # Without an unhandled exception, assume that the user just forgot to use dd() to actually die. Return the
        # dump page with the collected objects instead of the response.
        # A "combo" view that shows the dumps above the original response is an idea for #45.
        if not has_non_dd_exception:
            return dd_view(request, objects)

        # After an unhandled exception, add the dumps from before the exception to Django's error page, so that both
        # are shown.
        # A setting to turn this on or off is an idea for #45.

        # Get the head and body content of the DD view
        head_string = dd_view(request, objects, template_name="django_dump_die/partials/_head.html", as_string=True)
        body_string = dd_view(request, objects, template_name="django_dump_die/partials/_body.html", as_string=True)
        # Fetch the content of the standard Django 500 error page.
        content = response.content.decode("utf-8")
        # Inject the head and body parts of the DD view into the correct spots of the standard Django 500 error view.
        content = content.replace("</head>", f"{head_string}</head>", 1)
        content = content.replace("<body>", f"<body>{body_string}", 1)
        _set_content(response, content.encode("utf-8"))

        return response

    def process_exception(self, request, exception):
        """
        This a a Middleware hook provided by Django.

        Check if exception is of DumpAndDie type.
        If so, return Dump Die Debug Response.
        If not, ignore and allow standard exception handling.
        """
        if isinstance(exception, DumpAndDie):
            # Create a copy of the list, and clear it.
            objects = dump_objects[:]
            objects.append(exception.object)
            dump_objects.clear()

            # Return custom DumpAndDie output view.
            return dd_view(request, objects)

        # Not a DumpDie Exception, mark request as having an exception and
        # continue with processing by returning None.
        # NOTE: Middleware will detect that the request has an exception and
        # handle correctly in the __call__ above.
        request.has_non_dd_exception = True
        return None
