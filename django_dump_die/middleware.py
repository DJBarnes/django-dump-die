"""
Middleware for DumpAndDie.
"""

# System Imports.
import logging

# Third-Party Imports.
from django.conf import settings

# Internal Imports.
from .views import dd_view
from django_dump_die.utils import get_dumped_object_info


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
        __builtins__["dd"] = dd
        # Add global dump() function.
        __builtins__["dump"] = dump

    def __call__(self, request):
        """
        Return standard response if nothing dumped.
        Otherwise return dump view.
        """
        # Get the response
        response = self.get_response(request)

        # Determine if view had an unhandled non-dd exception.
        # This attribute will be set by the "process_exception" method below.
        has_non_dd_exception = getattr(request, "has_non_dd_exception", False)

        # If there are un-dumped object in the dump_objects list and a
        # non-dd-exception was not raised, assume that the user
        # just forgot to use DD to actually die. Return the dd_view with those
        # collected dump_objects instead of returning the default response.
        # TODO: Consider combining this logic with the non-dd-exception logic
        # below to return a "combo" view that has dump info at the top and the
        # original response below that. The downside is that it might affect the
        # output due to a clash of CSS.
        # TODO: Consider adding a setting to turn the combo function on or off if added.
        # TODO: Make sure that this will not run when Debug is turned off.
        if dump_objects and has_non_dd_exception is False:
            objects = dump_objects[:]
            dump_objects.clear()
            return dd_view(request, objects)

        # If the request object had an unhandled non-dd exception, attempt to
        # create a "combo" view that shows both the dumped objects and the
        # original response content.
        # Attempt to collect any dumps that ran prior to the unhandled exception
        # and inject the dump info into the standard Django 500 error page.
        # TODO: Consider adding a setting to turn this on or off.
        # TODO: Make sure that this will not run when Debug is turned off.
        if has_non_dd_exception:
            objects = dump_objects[:]
            dump_objects.clear()

            # Get the head and body content of the DD view
            head_string = dd_view(request, objects, template_name="django_dump_die/partials/_head.html", as_string=True)
            body_string = dd_view(request, objects, template_name="django_dump_die/partials/_body.html", as_string=True)
            # Fetch the content of the standard Django 500 error page.
            content = response.content.decode("utf-8")
            # Inject the head and body parts of the DD view into the correct spots of the standard Django 500 error view.
            content = content.replace("</head>", f"{head_string}</head>")
            content = content.replace("<body>", f"<body>{body_string}")
            # Set the new content on the response object
            response.content = content.encode("utf-8")

        # Regardless of whether the content was altered, return the response.
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
