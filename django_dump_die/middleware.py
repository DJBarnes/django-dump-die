"""
Middleware for DumpAndDie.
"""

import copy
import inspect
import io
import logging
import re
from tokenize import (
    generate_tokens,
    ENDMARKER,
    NAME,
    NEWLINE,
    NUMBER,
    OP,
    STRING,
)

from collections.abc import Sequence
from django.conf import settings

from .views import dd_view
from django_dump_die.constants import INCLUDE_FILENAME_LINENUMBER, COLORIZE_DUMPED_OBJECT_NAME
from django_dump_die.utils import get_callable_name, is_const


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


def _get_dumped_object_info(object_needing_name):
    """Look at the stack frame to figure out what the dumped var is"""

    # Get the frame where the dump or dd occurred.
    frame = inspect.getframeinfo(inspect.currentframe().f_back.f_back)

    # Default to not showing filename and lineno via setting to None
    linenumber = None
    filename = None
    # If we are to show the filename and linenumber
    if INCLUDE_FILENAME_LINENUMBER:
        # Get line number
        linenumber = frame.lineno
        # Get filename
        filename = frame.filename

    # Establish a couple of regular expressions to fetch out what was passed to dump or dd.
    dump_pattern = r".*dump\((.*?)[,\)].*"
    dd_pattern = r".*dd\((.*?)[,\)].*"
    # Find the results for both dump and dd.
    dumped_text_matches = re.findall(dump_pattern, frame.code_context[0])
    dd_text_matches = re.findall(dd_pattern, frame.code_context[0])
    # Determine if dumped or dd'd and put result in dumped_text
    dumped_text = ''
    if dumped_text_matches:
        dumped_text = dumped_text_matches[0]
    elif dd_text_matches:
        dumped_text = dd_text_matches[0]

    # If function get the callable name for each function name.
    if callable(object_needing_name) and not inspect.isclass(object_needing_name):
        dumped_text = get_callable_name(dumped_text, object_needing_name)

    return filename, linenumber, dumped_text


def _process_object_name(object_name):
    """Process the object name into a dictionary of parts that can be colorized in output"""

    # List to return for the name
    name = []

    # If the dumped object name should be colorized
    if COLORIZE_DUMPED_OBJECT_NAME:

        # List of function names
        functions = []

        # List of params
        params = []

        # Get the tokens out of the string
        # NOTE: generate_tokens returns an iterator and not a data structure.
        tokens = generate_tokens(io.StringIO(object_name).readline)

        # Stores all tokens extracted from the iterator.
        all_tokens = []
        # Stores the previous token as we iterate.
        previous_token = ''
        # Whether we are inside a param list. Default to False
        in_param_list = False

        # Convert the tokens from the iterator to a list of tokens.
        # Also, store the tokens that are function names or params for later color processing.
        for token in tokens:
            # Store token for later processing.
            all_tokens.append(token)
            # Convert for readability
            token_number = token[0]
            token_value = token[1]

            # If token is a opening paren
            if token_number == OP and token_value == '(':
                # Append previous token to the function list
                functions.append(previous_token)
                # Flip flag to indicate that we are now processing the parameter list.
                in_param_list = True

            # If we are inside the param list and not at the ending paren
            if in_param_list and token_value != ')':
                # Append the token to the list of params
                params.append(token_value)

            # Update the previous token to the current one.
            previous_token = token_value


        # Iterate over tokens classifying them with a CSS class.
        for token_number, token_value, _, _, _ in all_tokens:

            # Ignore newlines and endmarkers
            if token_number == NEWLINE or token_number == ENDMARKER:
                continue

            if token_number == NAME and is_const(token_value):
                # Use constant color.
                css_class = 'constant'
            elif token_number == STRING:
                # Use string color.
                css_class = 'string'
            elif token_number == NUMBER:
                # Use number color.
                css_class = 'number'
            elif token_number == OP and token_value in '(){}[]':
                # Use braces color.
                css_class = 'braces'
            elif token_value in functions:
                # Use function color
                css_class = 'function'
            elif token_value in params:
                # User param color
                css_class = 'params'
            else:
                # Use default color.
                css_class = 'dumped_name'

            # Append the info on to the name list
            name.append({
                'css_class': css_class,
                'value': token_value,
            })

    else:
        # Convert object name to the format expected by the template.
        name.append({
            'css_class': '',
            'value': object_name,
        })

    return name


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
        # Get object filename, linenumber, and name
        filename, linenumber, obj_name = _get_dumped_object_info(obj)

        # Process the object name to add coloring and/or put in correct format for the template.
        obj_name = _process_object_name(obj_name)

        # Handle if function.
        function_doc = None
        if callable(obj) and not inspect.isclass(obj):
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
            (filename, linenumber, obj_name, obj, function_doc, start_index, end_index, original_obj),
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
        # Get object filename, linenumber, and name
        filename, linenumber, obj_name = _get_dumped_object_info(obj)

        # Process the object name to add coloring and/or put in correct format for the template.
        obj_name = _process_object_name(obj_name)

        # Handle if function.
        function_doc = None
        if callable(obj) and not inspect.isclass(obj):
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
            (filename, linenumber, obj_name, obj, function_doc, start_index, end_index, original_obj),
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
