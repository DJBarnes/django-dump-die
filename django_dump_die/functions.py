"""
The dd() and dump() functions, and where they collect the objects dumped in a request.

Inside a request, the DumpAndDieMiddleware shows the dumped objects as a page, or above the page's own content.
Outside of a request, such as in a management command, the shell, or a background task, there is no page to show
them on, so they are printed to the console instead. See console.py.

This module doesn't import the middleware or the views, so that importing dd() and dump() in a management command stays
light.
"""

# System Imports.
import builtins
import sys
from contextlib import contextmanager
from contextvars import ContextVar

# Third-Party Imports.
from django.conf import settings

# Internal Imports.
from django_dump_die.utils import DumpBreak, get_dumped_object_info, is_valid_break_size

# The objects dumped in the current request. The middleware sets a new list for each request, with collect_dumps(), so
# that a request only shows its own dumps, even when requests run at the same time, in threads or in async tasks.
# Django runs sync code of an async request in a thread with a copy of the request's context, which holds the same
# list, so its dumps are kept too. So the list is only ever appended to and cleared, never replaced, inside a request.
# Outside of a request, it isn't set, and dumps are printed to the console.
_dump_objects = ContextVar("django_dump_die_dump_objects")


class DumpAndDie(Exception):  # noqa: N818 - Public name, raised by dd().
    """
    DumpAndDie Exception.

    Raised by dd(). Inside a request, the middleware catches it and shows the dump page instead of the response.
    Outside of a request, it stops the code after the object is printed to the console.
    """

    def __init__(self, obj, message=None):
        super().__init__(message if message is not None else obj)
        self.object = obj


@contextmanager
def collect_dumps():
    """Collect the objects dumped in the block, such as during a request, instead of printing them to the console.

    The middleware wraps each request in it. Yields the list the objects are collected in.
    """
    token = _dump_objects.set([])
    try:
        yield _dump_objects.get()
    finally:
        _dump_objects.reset(token)


def get_dump_objects():
    """Return the list of objects dumped in the current request, or an empty list outside of a request."""
    return _dump_objects.get([])


def _is_collecting():
    """Return True if dumps are collected, such as during a request, or False if they are printed to the console."""
    return _dump_objects.get(None) is not None


def dd(obj, index_range=None, deepcopy=None):
    """
    Immediately return debug template with info about objects.
    Includes any objects passed in through dump().

    Outside of a request, prints the object to the console, then stops by raising DumpAndDie.

    Does nothing if DEBUG != True.
    """

    if settings.DEBUG:
        # Get the object info
        object_info = get_dumped_object_info(obj, index_range, deepcopy)

        # Inside a request, the middleware catches the exception and shows the dump page.
        if _is_collecting():
            raise DumpAndDie(object_info)

        # Outside of a request, there is no page to show, so print it, and stop with a message that says why.
        _print_to_console(object_info)
        raise DumpAndDie(
            object_info,
            "dd() stopped here, after printing the object above. Outside of a request, dd() and dump() print to the "
            "console.",
        )


def dump(obj, index_range=None, deepcopy=None):
    """
    Show debug template whenever response finishes.
    dd() will also include objects from dump().

    Objects are collected for the current request only, so requests that run at the same time each show their own.
    Outside of a request, the object is printed to the console right away.

    Does nothing if DEBUG != True
    """

    if settings.DEBUG:
        # Get the object info
        object_info = get_dumped_object_info(obj, index_range, deepcopy)

        if _is_collecting():
            _dump_objects.get().append(object_info)
        else:
            _print_to_console(object_info)


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
        object_info = (None, None, None, DumpBreak(size), None, None, None, None)
        if _is_collecting():
            _dump_objects.get().append(object_info)
        else:
            _print_to_console(object_info)


# Make dump_break available as dump.br().
dump.br = dump_break


def _print_to_console(object_info):
    """Print a dumped object, or a break, to the console (stderr), so that it doesn't mix with a command's output."""
    # Imported here, since the console output uses the template tag's code, which isn't needed until something is
    # printed.
    from django_dump_die.console import format_dump, get_console_colors  # noqa: PLC0415

    sys.stderr.write(format_dump(object_info, get_console_colors(sys.stderr)) + "\n")


def install_builtins():
    """Make dd() and dump() built-ins, so that code can call them without importing them."""
    builtins.dd = dd
    builtins.dump = dump
