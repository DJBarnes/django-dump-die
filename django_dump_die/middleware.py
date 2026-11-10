"""
Middleware for DumpAndDie.
"""

# System Imports.
import logging
import re

# Third-Party Imports.
from asgiref.sync import iscoroutinefunction, markcoroutinefunction, sync_to_async
from django.conf import settings

# Internal Imports.
from django_dump_die.app_settings import app_settings
from django_dump_die.functions import (
    DumpAndDie,
    collect_dumps,
    dd,
    dump,
    dump_break,
    get_dump_objects,
    install_builtins,
)
from .views import dd_view

# dd(), dump(), and DumpAndDie live in functions.py, and can still be imported from here, as before.
__all__ = ["DumpAndDie", "DumpAndDieMiddleware", "dd", "dump", "dump_break", "get_dump_objects"]

logger = logging.getLogger("django_dump_die")


def _take_dump_objects():
    """Return the objects dumped in the current request, and empty its list, so that they are only shown once."""
    dump_objects = get_dump_objects()
    objects = dump_objects[:]
    dump_objects.clear()
    return objects


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

    Supports both sync and async requests, so that under ASGI it doesn't make Django switch between
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
            markcoroutinefunction(self)

        # Make dd() and dump() built-ins. The app's ready() does too, for code that runs outside of requests.
        install_builtins()

    def __call__(self, request):
        """
        Return standard response if nothing dumped.
        Otherwise return dump view.
        """
        if self.is_async:
            return self.__acall__(request)

        # Each request starts without dumps, so that it never shows those of another request, or those left by a
        # request that failed before its response was handled.
        with collect_dumps():
            # Get the response
            response = self.get_response(request)
            return self._process_response(request, response)

    async def __acall__(self, request):
        """
        Async version of __call__, used under ASGI.
        Awaits the rest of the middleware chain directly, and only switches to a thread when something was dumped.
        """
        # Each request starts without dumps, as in __call__. The request's task keeps this context for all of the
        # request, and sync code run in a thread gets a copy of it, which holds the same list.
        with collect_dumps():
            response = await self.get_response(request)

            # Nothing was dumped, so the response is returned unchanged, without leaving the event loop.
            if not get_dump_objects():
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
        if not get_dump_objects():
            return response

        # Take the dumped objects, so that they are only shown once.
        objects = _take_dump_objects()

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
            # Take the objects dumped before dd(), and add the one passed to dd().
            objects = _take_dump_objects()
            objects.append(exception.object)

            # Return custom DumpAndDie output view.
            return dd_view(request, objects)

        # Not a DumpDie Exception, mark request as having an exception and
        # continue with processing by returning None.
        # NOTE: Middleware will detect that the request has an exception and
        # handle correctly in the __call__ above.
        request.has_non_dd_exception = True
        return None
