"""Utils for dump die"""

# System Imports.
import copy
import inspect
import io
import linecache
import re
import tokenize
from collections.abc import Sequence
from decimal import Decimal
from enum import EnumMeta
from tokenize import (
    generate_tokens,
    ENDMARKER,
    NAME,
    NEWLINE,
    NUMBER,
    OP,
    STRING,
)

# Third-Party Imports.
from django.core.exceptions import ObjectDoesNotExist
from django.http import QueryDict

# Internal Imports.
from django_dump_die.constants import COLORIZE_DUMPED_OBJECT_NAME, INCLUDE_FILENAME_LINENUMBER, PYTZ_PRESENT

# Imports that may not be accessible, depending on local python environment setup.
if PYTZ_PRESENT:
    import pytz


class Enum:
    """Enum faker class so an entire Enum can be dumped correctly."""
    def __init__(self, *args, **kwargs):
        """Set attrs on this class for each kwarg passed in."""
        for key, val in kwargs.items():
            setattr(self, key, val)


def get_dumped_object_info(obj, index_range=None, deepcopy=False):
    """Get all the required information to be able to dump an object"""
    # Get object filename, linenumber, and name
    filename, linenumber, obj_name = get_dumped_object_name_and_location(obj)

    # Process the object name to add coloring and/or put in correct format for the template.
    obj_name = process_object_name(obj_name)

    # Handle if function.
    function_doc = None
    if callable(obj) and not inspect.isclass(obj):
        function_doc = inspect.getdoc(obj)

    # Sanitize and validate provided index values.
    start_index, end_index = sanitize_index_range(index_range)

    # Handle if Enum by converting to a standard class.
    # NOTE: Dumping an Enum without conversion results in a blank string being dumped.
    if isinstance(obj, EnumMeta):
        obj = Enum(**obj.__members__)

    # Handle if deepcopy set.
    original_obj = None
    try:
        if deepcopy:
            original_obj = obj
            obj = copy.deepcopy(obj)
    except TypeError as type_error:
        original_obj = None
        raise TypeError(f"Object contains type that can't be deep copied. - {type_error}") from None

    return (filename, linenumber, obj_name, obj, function_doc, start_index, end_index, original_obj)


def get_dumped_object_name_and_location(object_needing_name):
    """Look at the stack frame to figure out what the dumped var is"""

    # Get the frame where the dump or dd occurred.
    base_frame = inspect.currentframe().f_back.f_back.f_back
    frame_info = inspect.getframeinfo(base_frame)

    # Default to not showing filename and lineno via setting to None
    linenumber = None
    filename = None
    # If we are to show the filename and linenumber
    if INCLUDE_FILENAME_LINENUMBER:
        # Get line number
        linenumber = frame_info.lineno
        # Get filename
        filename = frame_info.filename

    # Parse line that called, for full "name" to output.
    # Accounts for things like functions that span multiple lines.
    code_context = get_fully_qualified_dumped_line(base_frame, frame_info)

    # TODO: This work of using RegEx to get down to the dumped object name can probably be improved.
    # Establish a couple of regular expressions to fetch out what was passed to dump or dd.
    dump_pattern = r".*dump\((.*)[\)]"
    dd_pattern = r".*dd\((.*)[\)]"
    options_pattern = r"(.*)(?=,.*=.*)"
    # Find the results for both dump and dd.
    dumped_text_matches = re.findall(dump_pattern, code_context)
    dd_text_matches = re.findall(dd_pattern, code_context)
    # Determine if dumped or dd'd and put result in dumped_text
    dumped_text = 'Unknown_Object_Name'
    if dumped_text_matches:
        dumped_text = dumped_text_matches[0]
    elif dd_text_matches:
        dumped_text = dd_text_matches[0]

    while 'deepcopy' in dumped_text or 'index_range' in dumped_text:
        dumped_text_matches = re.findall(options_pattern, dumped_text)
        if dumped_text_matches:
            dumped_text = dumped_text_matches[0]
        else:
            break

    # If function get the callable name for each function name.
    if callable(object_needing_name) and not inspect.isclass(object_needing_name):
        dumped_text = get_callable_name(dumped_text, object_needing_name)

    return filename, linenumber, dumped_text


def get_fully_qualified_dumped_line(base_frame, frame_info):
    """Loop through frame info until we get full object name.

    Required for definitions of things that span multiple lines, within a given dump/dd statement.
    """

    line_num = base_frame.f_lineno - 1
    code_context = ''
    counter = None
    total_loops = 0
    # Loop through lines until counter goes back to 0, to account for newlines.
    # Counter increments for every proper ( token found, and decrements for every proper ) token found.
    # Additional checks are present so that the page does not hang forever, in event of input we did not account for.
    while counter is None or (0 < counter < 100 and total_loops < 1000):
        total_loops += 1

        # Initialize counter for first loop.
        if counter is None:
            counter = 0

        # Check line for parsing actual name info.
        line_num += 1
        line = linecache.getline(frame_info.filename, line_num, base_frame.f_globals)
        code_context += line

        # Get the tokens out of the string.
        # NOTE: generate_tokens returns an iterator and not a data structure.
        tokens = generate_tokens(io.StringIO(line).readline)

        # Iterate through all tokens from line, and adjust counter if paren tokens are found.
        try:
            for token in tokens:
                if token.exact_type == 7:
                    counter += 1
                elif token.exact_type == 8:
                    counter -= 1

        except tokenize.TokenError:
            # Seems to only come up for end of line. We can safely ignore, probably?
            pass

    # Strip out extra whitespace, if present.
    code_context = re.sub(r'\s+', ' ', code_context)

    # Return final result.
    return code_context


def process_object_name(object_name):
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
            if token_number == OP and token.exact_type == 7:
                # Append previous token to the function list
                functions.append(previous_token)
                # Flip flag to indicate that we are now processing the parameter list.
                in_param_list = True

            # If we are inside the param list and not at the ending paren
            if in_param_list and token.exact_type != 8:
                # Append the token to the list of params
                params.append(token_value)
            else:
                in_param_list = False

            # Update the previous token to the current one.
            previous_token = token_value

        # Iterate over tokens classifying them with a CSS class.
        for token_number, token_value, _, _, _ in all_tokens:

            # Ignore newlines and endmarkers
            if token_number == NEWLINE or token_number == ENDMARKER:
                continue

            if token_number == NAME and token_value == 'Unknown_Object_Name':
                # Use empty color as object name can't be determined
                css_class = 'empty'
            elif token_number == NAME and is_const(token_value):
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


def sanitize_index_range(index_range):
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


# region Object Property Functions


def generate_unique_from_obj(obj):
    """Generate a unique identifier for the object passed in."""

    # Create unique via hash and fallback to id on exception.
    try:
        unique = hash(obj)
    except Exception:
        unique = id(obj)
    # Append the class name to the unique to really make unique.
    unique = f'{get_class_name(obj)}_{unique}'

    return unique


def get_members(obj):
    """Attempts to get object members. Falls back to an empty list."""

    # Get initial member set or empty list.
    members = inspect.getmembers(obj)

    # Add type specific members that will not be included from the use of the inspect.getmembers function.
    if is_dict(obj):
        if isinstance(obj, QueryDict):
            # Django QueryDict members. Has handling for multiple unique values referencing the same key.
            # https://docs.djangoproject.com/en/dev/ref/request-response/#querydict-objects
            obj_copy = copy.deepcopy(obj)
            for key in obj.keys():
                item = obj_copy.pop(key)
                members.append((key, item))
        else:
            # Standard dictionary members.
            members.extend(obj.items())

    elif is_iterable(obj):
        # Lists, sets, etc.
        if _is_indexable(obj):
            # Use indexes as left half.
            members.extend(list(enumerate(obj)))
        elif is_set(obj):
            # Use None as left half. Most likely a set.
            members.extend([(None, x) for x in obj])

    return members


def get_class_name(obj):
    """Get class name of an object."""
    name = None
    try:
        name = obj.__class__.__name__
    except Exception:
        pass
    return name


def get_callable_name(obj_name, obj):
    """Get callable name of an object"""

    # Get the method signature and fall back to simply appending
    # parentheses to the method name on exception.
    try:
        obj_name += safe_str(inspect.signature(obj))
    except Exception:
        obj_name += '()'
    return obj_name


def get_callable_params(obj):
    """Get callable params of an object"""

    # Get the method signature and fall back to simply returning
    # parentheses on exception.
    try:
        signature = safe_str(inspect.signature(obj))
    except Exception:
        signature = '()'

    signature_minus_parentheses = signature[1:-1]

    return signature_minus_parentheses


def get_obj_type(obj):
    """Determines the string representation of object's type."""

    # Get default type value.
    obj_type = type(obj).__name__

    # Special handling for certain types.
    if obj_type == 'NoneType':
        obj_type = 'null'
    elif PYTZ_PRESENT and isinstance(obj, pytz.BaseTzInfo):
        obj_type = 'pytz_timezone'

    return obj_type


def safe_repr(obj):
    """Call repr() and ignore ObjectDoesNotExist."""
    str_obj = ''
    try:
        str_obj = repr(obj)
    except ObjectDoesNotExist:
        # NOTE: A list of deleted db objects will cause repr(list) to fail.
        # So, we detect this and print out the __class__ of the contents of
        # the list.
        str_obj = f'<{obj.__class__} DELETED>'

    return str_obj


def safe_str(obj):
    """Call str() and ignore TypeErrors if str() doesn't return a string."""
    str_obj = ''
    try:
        str_obj = str(obj)
    except (TypeError, ObjectDoesNotExist):
        str_obj = safe_repr(obj)

    return str_obj


def is_iterable(obj):
    """Return True if object can be iterated."""
    try:
        iter(obj) and len(obj)
    except NotImplementedError:
        return False
    except TypeError:
        return False
    except ValueError:
        return False
    return True


def is_query(obj):
    """Return True if object is most likely a query."""
    if obj is not None:
        return _in_dir(obj, 'as_manager') and _in_dir(obj, 'all') and _in_dir(obj, 'filter')


def is_dict(obj):
    """Return True if object is most likely a dict."""
    if obj is not None:
        return _in_dir(obj, 'items') and _in_dir(obj, 'keys') and _in_dir(obj, 'values')


def is_set(obj):
    """Return True if object is most likely a dict."""
    return isinstance(obj, set) or isinstance(obj, frozenset)


def is_const(obj):
    """Return True if object is most likely a constant."""
    if obj is not None:
        return isinstance(obj, str) and obj[0].isalpha() and obj.upper() == obj


def is_key(obj):
    """Return True if object is most likely a key."""
    if obj is not None and isinstance(obj, str):
        return "'" in obj


def is_number(obj):
    """Return True if object is most likely a number."""
    if obj is not None:
        return (
            isinstance(obj, (int, float, Decimal))
            or (getattr(obj, 'isnumeric', None) and obj.isnumeric())
        )


def is_private(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('_')


def is_magic(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith('__') and obj.endswith('__')


def _in_dir(obj, attr):
    """Simpler hasattr() function without side effects."""
    return attr in dir(obj)


def _is_indexable(obj):
    """Return True if object can be indexed."""
    if isinstance(obj, Sequence):
        return True
    else:
        return False

# endregion Object Property Functions
