"""
Plain-text output of dumps, for dd() and dump() called outside of a request, such as in a management command, the
shell, or a background task.

It uses the same code as the dump page, the dump_object template tag's function, so that the same objects are shown,
with the same limits (DJANGO_DD_MAX_RECURSION_DEPTH, DJANGO_DD_MAX_ITERABLE_LENGTH), the same hidden sensitive values,
and the same settings for attributes and function results. Only the formatting differs: an indented tree, instead of
HTML. Functions are left out, as their signatures and docs would make the tree hard to read.
"""

# Internal Imports.
from django_dump_die.app_settings import app_settings
from django_dump_die.templatetags.dump_die import dump_object, start_page_of_dumps
from django_dump_die.utils import DumpBreak, Placeholder

INDENT = "    "
# Width of the line that dump.br() prints.
BREAK_WIDTH = 60
# Types whose value already shows its type, such as 'text' or 42, so the type isn't printed before it.
SELF_EVIDENT_TYPES = ("str", "int", "float", "bool", "null")


def format_dump(object_info):
    """Return a dumped object, as collected by dd() or dump(), as text: its name, then its tree."""
    filename, linenumber, obj_name, obj, function_doc, root_index_start, root_index_end, original_obj = object_info

    if isinstance(obj, DumpBreak):
        return _format_break(obj)

    lines = []
    if filename and linenumber:
        lines.append(f"File: {filename}, Line: {linenumber}")

    name = _format_name(obj_name, "Unknown Function" if function_doc else "Unknown Object")
    if function_doc:
        # A dumped function shows its signature, in the name, and its docs.
        lines.append(f"{name}: {function_doc}")
    else:
        start_page_of_dumps()
        tree = _format_object(obj, obj, None, 0, original_obj, False, root_index_start, root_index_end)
        lines.append(f"{name}: {tree[0]}")
        lines.extend(tree[1:])

    return "\n".join(lines)


def _format_break(dump_break):
    """Return a break as a line across, in the middle of as many lines as its size."""
    size = dump_break.size or app_settings.BREAK_SIZE
    lines = [""] * size
    lines[size // 2] = "-" * BREAK_WIDTH
    return "\n".join(lines)


def _format_name(obj_name, unknown):
    """Return the dumped name, from its parts, such as a function name and its parameters, as one string."""
    if obj_name is None:
        return unknown
    return "".join((" " if part.get("space_before") else "") + part["value"] for part in obj_name)


def _format_object(obj, root_obj, skip_set, depth, original_obj, parent_is_intermediate, start=None, end=None):
    """Return the lines of an object's tree. The first line follows the object's name or key."""
    context = dump_object(obj, root_obj, skip_set, depth, original_obj, parent_is_intermediate, start, end)

    # A simple value, such as a string or a number.
    if "simple" in context:
        if context["type"] in SELF_EVIDENT_TYPES:
            return [context["simple"]]
        return [f"{context['type']} {context['simple']}"]

    # Without the count the page adds to an object dumped more than once, since each console dump stands alone, and so
    # that an object shown again, such as one that refers back to itself, shows the same unique as where it is shown.
    unique = context["unique"]
    header = context["type"]
    if context.get("length") is not None:
        header += f":{context['length']}"
    if context.get("intermediate"):
        header += f" {context['intermediate']}"

    # An object already shown, such as one that refers back to itself, or past the maximum depth. Its unique matches
    # the one where it is shown in full.
    if context.get("object") is None:
        return [f"{header} {unique}"]

    opening, closing = context["braces"]
    lines = [f"{header} {unique} {opening}"]
    children = context.get("skip")
    is_intermediate = bool(context.get("intermediate"))

    for label, value, *_ in context.get("attributes", []):
        key = f"{label}: " if label is not None else ""
        if isinstance(value, Placeholder):
            # Such as a hidden sensitive value, or the items past the limit.
            child = [value.text]
        else:
            child = _format_object(value, root_obj, children, depth + 1, original_obj, is_intermediate)
        lines.extend(_indent(key, child))

    for result in context.get("function_results", []):
        key = f"{result['name']}(): "
        if result.get("error"):
            child = [result["error"]]
        else:
            child = _format_object(result["value"], root_obj, children, depth + 1, original_obj, is_intermediate)
        lines.extend(_indent(key, child))

    lines.append(closing)
    return lines


def _indent(key, lines):
    """Return a child's lines, indented one level, with its key before the first line."""
    return [f"{INDENT}{key}{lines[0]}"] + [f"{INDENT}{line}" for line in lines[1:]]
