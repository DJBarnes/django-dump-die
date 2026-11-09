"""
Middleware for DumpAndDie.
"""

# System Imports.
import asyncio
import logging
import re

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
from django_dump_die.app_settings import app_settings
from .views import dd_view
from django_dump_die.utils import DumpBreak, get_dumped_object_info, is_valid_break_size

logger = logging.getLogger("django_dump_die")
dump_objects = []


class DumpAndDie(Exception):  # noqa: N818 - Public name, raised by dd().
    """
    DumpAndDie Exception.
    Triggers the middleware exception logic which outputs the alternate dd debug view.
    """

    def __init__(self, obj):
        super().__init__(obj)
        self.object = obj


def dd(obj, index_range=None, deepcopy=None):
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


def dump(obj, index_range=None, deepcopy=None):
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


# Tags of an HTML page that dumps are added around. Matched without regard to case, and <body> with any attributes.
_HEAD_END_TAG = re.compile(r"</head\s*>", flags=re.IGNORECASE)
_BODY_START_TAG = re.compile(r"<body\b[^>]*>", flags=re.IGNORECASE)


def _add_dumps_above_page(request, response, objects):
    """
    Add the dumps to the top of an HTML page's body, with the dump page's CSS and JS in its head.
    Used for Django's error page after an unhandled exception, and for any page when DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE
    is on.

    Returns False, and leaves the response unchanged, if it isn't an HTML page that the dumps can be added to: a
    streaming or file response, a redirect, a compressed response, or a response that isn't HTML or has no <body>.
    """
    if response.streaming or 300 <= response.status_code < 400:
        return False
    # Such as a response compressed by GZipMiddleware, whose content can't be changed as text.
    if response.get("Content-Encoding", "identity") != "identity":
        return False
    if not response.get("Content-Type", "").startswith("text/html"):
        return False

    try:
        content = response.content.decode(response.charset)
    except (UnicodeDecodeError, LookupError):
        return False
    body_tag = _BODY_START_TAG.search(content)
    if body_tag is None:
        return False

    head_string = dd_view(request, objects, template_name="django_dump_die/partials/_head.html", as_string=True)
    body_string = dd_view(request, objects, template_name="django_dump_die/partials/_above_page.html", as_string=True)

    # The CSS and JS go at the end of the head, before the body. A page without a head gets them at the start of the
    # body, where browsers load them too.
    head_end_tag = _HEAD_END_TAG.search(content, 0, body_tag.start())
    if head_end_tag is not None:
        content = "".join(
            (
                content[: head_end_tag.start()],
                head_string,
                content[head_end_tag.start() : body_tag.end()],
                body_string,
                content[body_tag.end() :],
            )
        )
    else:
        content = "".join((content[: body_tag.end()], head_string, body_string, content[body_tag.end() :]))

    _set_content(response, content.encode(response.charset))
    return True


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
                self._is_coroutine = asyncio.coroutines._is_coroutine

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

        # After an unhandled exception, add the dumps from before the exception to Django's error page, so that both
        # are shown. Without an HTML error page to add them to, such as for a request that doesn't accept HTML, the
        # error is returned as it is, since it matters more than the dumps.
        if has_non_dd_exception:
            if app_settings.SHOW_DUMPS_ON_ERROR_PAGE:
                _add_dumps_above_page(request, response, objects)
            return response

        # Without an exception, dump() was used without dd(). Show the dumps above the page's own content if that's
        # turned on and the response is an HTML page.
        if app_settings.SHOW_DUMPS_ABOVE_PAGE and _add_dumps_above_page(request, response, objects):
            return response

        # Otherwise, return the dump page instead of the response.
        return dd_view(request, objects)

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
