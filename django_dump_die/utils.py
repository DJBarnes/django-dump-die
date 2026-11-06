"""Utils for dump die"""

# System Imports.
import copy
import dis
import functools
import inspect
import io
import linecache
import tokenize
from collections.abc import Sequence
from decimal import Decimal
from enum import EnumMeta, Enum as OrigEnum
from tokenize import (
    generate_tokens,
    COMMENT,
    DEDENT,
    ENDMARKER,
    INDENT,
    NAME,
    NEWLINE,
    NL,
    NUMBER,
    OP,
    STRING,
)

# Third-Party Imports.
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.http import QueryDict
from django.utils.functional import Promise, cached_property as django_cached_property

# Internal Imports.
from django_dump_die.constants import COLORIZE_DUMPED_OBJECT_NAME, INCLUDE_FILENAME_LINENUMBER, PYTZ_PRESENT

# Imports that may not be accessible, depending on local python environment setup.
if PYTZ_PRESENT:
    import pytz


# Types of cached properties. functools.cached_property was added in Python 3.8.
CACHED_PROPERTY_TYPES = (django_cached_property,) + (
    (functools.cached_property,) if hasattr(functools, "cached_property") else ()
)


class DumpBreak:
    """Marker for a break between dumped objects, added with dump.br()."""

    def __init__(self, size=None):
        # Height of the break in lines, or None for the DJANGO_DD_BREAK_SIZE default.
        self.size = size


def is_valid_break_size(size):
    """Return True if size is a whole number of lines, 1 or more. True and False don't count."""
    return isinstance(size, int) and not isinstance(size, bool) and size >= 1


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

    # Get the source of the first argument of the dump() or dd() call, as the dumped object's name.
    dumped_text = get_dumped_argument_source(base_frame) or "Unknown_Object_Name"

    # If function get the callable name for each function name.
    if callable(object_needing_name) and not inspect.isclass(object_needing_name):
        dumped_text = get_callable_name(dumped_text, object_needing_name)

    return filename, linenumber, dumped_text


# region Dumped Name Functions

# Names that dump() and dd() are called by, as built-ins or imported.
DUMP_FUNCTION_NAMES = ("dump", "dd")
# Bytecode instructions that look up a name, other than as an attribute, such as json.dump.
_NAME_LOAD_OPNAMES = {
    "LOAD_CLASSDEREF",
    "LOAD_DEREF",
    "LOAD_FAST",
    "LOAD_FAST_AND_CLEAR",
    "LOAD_FAST_BORROW",
    "LOAD_FAST_CHECK",
    "LOAD_FROM_DICT_OR_GLOBALS",
    "LOAD_GLOBAL",
    "LOAD_NAME",
}
# Token types that don't affect the dumped name.
_SKIPPED_TOKEN_TYPES = (COMMENT, NL, NEWLINE, INDENT, DEDENT, ENDMARKER)


def get_dumped_argument_source(frame):
    """Return the source of the first argument of the dump() or dd() call that the frame is running.

    The bytecode shows the line where the running call's dump or dd name is, and how many calls to them come before
    it on that line. The source is then tokenized from that line, so that strings and comments can't be mistaken for
    code, and the call's brackets are followed to find its first argument.

    :return: The argument's source, with its whitespace between tokens collapsed to one space, or None if it can't be
        found, such as when the source isn't available, or dump() was called by another name.
    """
    location = _get_running_call_location(frame)
    if location is None:
        return None
    line_number, call_index = location

    # Read lines until the call's brackets are closed. A call can span several lines, and is always closed before
    # the end of its file, since the code is running.
    source = ""
    while True:
        line = linecache.getline(frame.f_code.co_filename, line_number, frame.f_globals)
        if not line:
            # The source isn't available, such as for code run with exec().
            return None
        source += line
        argument = _get_first_argument(_tokenize(source), call_index)
        if argument is not None:
            return argument
        line_number += 1


def _get_running_call_location(frame):
    """Return the line of the running dump() or dd() call, and how many calls to them come before it on that line.

    :return: (line number, index of the call on its line), or None if the frame isn't running a call to dump or dd.
    """
    code = frame.f_code
    line_starts = [(offset, line) for offset, line in dis.findlinestarts(code) if line is not None]

    def line_of(offset):
        """Line of the instruction at a bytecode offset."""
        line = None
        for start_offset, start_line in line_starts:
            if start_offset > offset:
                break
            line = start_line
        return line

    # Every lookup of dump or dd up to the running instruction. The last one is the running call's.
    loads = [
        instruction
        for instruction in dis.get_instructions(code)
        if instruction.offset <= frame.f_lasti
        and instruction.opname in _NAME_LOAD_OPNAMES
        and instruction.argval in DUMP_FUNCTION_NAMES
    ]
    if not loads:
        return None

    line = line_of(loads[-1].offset)
    call_index = sum(1 for instruction in loads[:-1] if line_of(instruction.offset) == line)
    return line, call_index


def _tokenize(source):
    """Return the source's tokens, without comments and line structure. An unfinished statement is fine."""
    tokens = []
    try:
        for token in generate_tokens(io.StringIO(source).readline):
            if token.type not in _SKIPPED_TOKEN_TYPES:
                tokens.append(token)
    except (tokenize.TokenError, IndentationError):
        # The source ends inside the call's brackets, or a string, because the rest of it isn't read yet.
        pass
    return tokens


def _get_first_argument(tokens, call_index):
    """Return the source of the first argument of a dump() or dd() call that starts on the first line.

    :param tokens: The tokens of the source, starting with the line of the call.
    :param call_index: Which of the calls that start on the first line, counting from 0.
    :return: The argument's source, or None if the call's brackets aren't closed yet.
    """
    # Every use of the dump or dd name on the first line, in the order the bytecode looks them up. That includes uses
    # that aren't calls, such as dump.br(), but not attributes with the same name, such as json.dump().
    names = [
        index
        for index, token in enumerate(tokens[:-1])
        if token.type == NAME
        and token.string in DUMP_FUNCTION_NAMES
        and token.start[0] == 1
        and (index == 0 or tokens[index - 1].string != ".")
    ]
    if call_index >= len(names) or tokens[names[call_index] + 1].string != "(":
        return None

    # Collect the tokens of the first argument: up to the first comma, or the call's closing bracket.
    argument = []
    depth = 0
    for token in tokens[names[call_index] + 2 :]:
        if token.string in "([{" and token.type == OP:
            depth += 1
        elif token.string in ")]}" and token.type == OP:
            if depth == 0:
                return _join_tokens(_without_keyword(argument))
            depth -= 1
        elif token.string == "," and depth == 0:
            return _join_tokens(_without_keyword(argument))
        argument.append(token)
    return None


def _without_keyword(tokens):
    """Leave out the "obj=" of an argument given by keyword, as in dump(obj=user)."""
    if len(tokens) > 2 and tokens[0].string == "obj" and tokens[1].string == "=":
        return tokens[2:]
    return tokens


def _join_tokens(tokens):
    """Join tokens back into source, with one space where the source had any whitespace between them."""
    text = ""
    previous_end = None
    for token in tokens:
        if previous_end is not None and token.start != previous_end:
            text += " "
        text += token.string
        previous_end = token.end
    return text


# endregion Dumped Name Functions


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
        previous_token = ""
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
        previous_end = None
        for token_number, token_value, start, end, _ in all_tokens:

            # Ignore newlines and endmarkers
            if token_number == NEWLINE or token_number == ENDMARKER:
                continue

            # Keep a space where the name had whitespace, such as in "a if b else c", since each part is shown in its
            # own element.
            space_before = previous_end is not None and start != previous_end
            previous_end = end

            if token_number == NAME and token_value == "Unknown_Object_Name":
                # Use empty color as object name can't be determined
                css_class = "empty"
            elif token_number == NAME and is_const(token_value):
                # Use constant color.
                css_class = "constant"
            elif token_number == STRING:
                # Use string color.
                css_class = "string"
            elif token_number == NUMBER:
                # Use number color.
                css_class = "number"
            elif token_number == OP and token_value in "(){}[]":
                # Use braces color.
                css_class = "braces"
            elif token_value in functions:
                # Use function color
                css_class = "function"
            elif token_value in params:
                # User param color
                css_class = "params"
            else:
                # Use default color.
                css_class = "dumped_name"

            # Append the info on to the name list
            name.append(
                {
                    "css_class": css_class,
                    "value": token_value,
                    "space_before": space_before,
                }
            )

    else:
        # Convert object name to the format expected by the template.
        name.append(
            {
                "css_class": "",
                "value": object_name,
            }
        )

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
        except (TypeError, ValueError):
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
    unique = f"{get_class_name(obj)}_{unique}"

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
    elif is_enum_member(obj):
        # Prevent enum entry from recursively showing up in entries members.
        members = [m for m in members if not is_enum_member(m[1])]

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
        obj_name += "()"
    return obj_name


def get_callable_params(obj):
    """Get callable params of an object"""

    # Get the method signature and fall back to simply returning
    # parentheses on exception.
    try:
        signature = safe_str(inspect.signature(obj))
    except Exception:
        signature = "()"

    signature_minus_parentheses = signature[1:-1]

    return signature_minus_parentheses


def get_method_type(obj, attr):
    """Return "staticmethod" or "classmethod" if an object's member is one, otherwise None."""
    try:
        # The raw class attribute still shows the decorator, which getattr() resolves away.
        raw_value = inspect.getattr_static(obj, attr)
    except (AttributeError, TypeError):
        # Not a named attribute, such as a dict key that isn't a string.
        return None
    if isinstance(raw_value, staticmethod):
        return "staticmethod"
    if isinstance(raw_value, classmethod):
        return "classmethod"
    return None


def get_attribute_type(obj, attr):
    """Return how an object's attribute is defined, without running anything.

    :return: "property" or "cached_property" if the attribute is one, "class_attribute" if the value comes from the
        object's class instead of the object itself, otherwise None, such as for an instance attribute.
    """
    if not isinstance(attr, str):
        # Not a named attribute, such as a list index.
        return None

    # Find the attribute where its class defines it, if it does. A computed cached_property is stored on the
    # instance, so the class shows that it is one, while inspect.getattr_static() would find the stored value.
    is_class = inspect.isclass(obj)
    class_value = None
    is_on_class = False
    for klass in inspect.getmro(obj if is_class else type(obj)):
        if attr in klass.__dict__:
            class_value = klass.__dict__[attr]
            is_on_class = True
            break

    if isinstance(class_value, property):
        return "property"
    if isinstance(class_value, CACHED_PROPERTY_TYPES):
        return "cached_property"

    # When a class itself is dumped, all of its attributes are class attributes, so none are marked.
    # Descriptors, such as __slots__ members and Django's model field and related object descriptors, give each
    # instance its own value.
    if is_class or not is_on_class or hasattr(type(class_value), "__get__"):
        return None

    # An instance attribute that hides a class attribute is the instance's own.
    try:
        instance_dict = object.__getattribute__(obj, "__dict__")
    except AttributeError:
        # Objects with __slots__ and no __dict__.
        instance_dict = {}
    if attr in instance_dict:
        return None

    return "class_attribute"


def get_obj_type(obj):
    """Determines the string representation of object's type."""

    # Get default type value.
    obj_type = type(obj).__name__

    # Special handling for certain types.
    if obj_type == "NoneType":
        obj_type = "null"
    elif PYTZ_PRESENT and isinstance(obj, pytz.BaseTzInfo):  # pylint: disable=E0606
        obj_type = "pytz_timezone"
    elif isinstance(obj, Promise):
        # A lazy string, such as from gettext_lazy(), whose class is a "__proxy__".
        obj_type = "lazy str"

    return obj_type


def safe_repr(obj):
    """Call repr() and ignore ObjectDoesNotExist."""
    str_obj = ""
    try:
        str_obj = repr(obj)
    except ObjectDoesNotExist:
        # NOTE: A list of deleted db objects will cause repr(list) to fail.
        # So, we detect this and print out the __class__ of the contents of
        # the list.
        str_obj = f"<{obj.__class__} DELETED>"

    return str_obj


def safe_str(obj):
    """Call str() and ignore TypeErrors if str() doesn't return a string."""
    str_obj = ""
    try:
        str_obj = str(obj)
    except (TypeError, ObjectDoesNotExist):
        str_obj = safe_repr(obj)

    return str_obj


def is_iterable(obj):
    """Return True if object can be iterated."""
    try:
        iter(obj) and len(obj)
    except DatabaseError:
        # Such as a QuerySet whose query fails. Dump it as an object instead of failing the whole dump.
        return False
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
        return _in_dir(obj, "as_manager") and _in_dir(obj, "all") and _in_dir(obj, "filter")


def is_dict(obj):
    """Return True if object is most likely a dict."""
    if obj is not None:
        return _in_dir(obj, "items") and _in_dir(obj, "keys") and _in_dir(obj, "values")


def is_set(obj):
    """Return True if object is most likely a dict."""
    return isinstance(obj, set) or isinstance(obj, frozenset)


def is_enum_member(obj):
    """Return True if object is most likely a enum"""
    return issubclass(type(obj), OrigEnum)


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
        return isinstance(obj, (int, float, Decimal)) or (getattr(obj, "isnumeric", None) and obj.isnumeric())


def is_private(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith("_")


def is_magic(obj):
    """Return True if object is private."""
    if obj is not None:
        return isinstance(obj, str) and obj.startswith("__") and obj.endswith("__")


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
