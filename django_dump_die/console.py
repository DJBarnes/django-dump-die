"""
Plain-text output of dumps, for dd() and dump() called outside of a request, such as in a management command, the
shell, or a background task.

It uses the same code as the dump page, the dump_object template tag's function, so that the same objects are shown,
with the same limits (DJANGO_DD_MAX_RECURSION_DEPTH, DJANGO_DD_MAX_ITERABLE_LENGTH), the same hidden sensitive values,
and the same settings for attributes and function results. Only the formatting differs: an indented tree, instead of
HTML. Functions are left out, as their signatures and docs would make the tree hard to read.

In a terminal, the text has the page's colors (see ConsoleColors).
"""

# System Imports.
import os
import sys

# Third-Party Imports.
from django.core.management.color import supports_color
from django.utils.termcolors import parse_color_setting

# Internal Imports.
from django_dump_die.app_settings import app_settings
from django_dump_die.templatetags.dump_die import dump_object, start_page_of_dumps
from django_dump_die.utils import DumpBreak, Placeholder

INDENT = "    "
# Width of the line that dump.br() prints.
BREAK_WIDTH = 60
# Types whose value already shows its type, such as 'text' or 42, so the type isn't printed before it.
SELF_EVIDENT_TYPES = ("str", "int", "float", "bool", "null")

# The page's default colors (Solarized), by the CSS class of each part of a dump. Braces have the text's own color.
DEFAULT_COLORS = {
    # Meta.
    "empty": "#dc322f",
    "location": "#586e75",
    "type": "#859900",
    "unique": "#6c71c4",
    # Identifiers.
    "attribute": "#93a1a1",
    "class_attribute": "#586e75",
    "constant": "#cb4b16",
    "dumped_name": "#93a1a1",
    "function": "#268bd2",
    "index": "#d33682",
    "key": "#2aa198",
    "params": "#93a1a1",
    # Types.
    "bool": "#b58900",
    "bound": "#268bd2",
    "default": "#586e75",
    "docs": "#586e75",
    "intermediate": "#d33682",
    "module": "#268bd2",
    "none": "#b58900",
    "number": "#d33682",
    "string": "#2aa198",
}
# Sections of DJANGO_DD_COLOR_SCHEME whose colors are by CSS class. The others are the page's text and backgrounds.
COLOR_SCHEME_SECTIONS = ("meta", "identifiers", "types")
# Levels of each of red, green, and blue in the 6x6x6 color cube of 256-color terminals (colors 16 to 231).
CUBE_LEVELS = (0, 95, 135, 175, 215, 255)


class ConsoleColors:
    """Colors parts of a dump by their CSS class, as the page does, with ANSI escape codes.

    Uses the page's colors, with any changed by DJANGO_DD_COLOR_SCHEME. A terminal that supports 24-bit color, by
    setting COLORTERM, gets them exactly. Other terminals get the nearest of the 256 standard terminal colors.
    """

    def __init__(self, truecolor=False):
        self.truecolor = truecolor
        self.colors = dict(DEFAULT_COLORS)
        scheme = app_settings.COLOR_SCHEME or {}
        for section in COLOR_SCHEME_SECTIONS:
            self.colors.update(scheme.get(section) or {})

    def __call__(self, text, css_class):
        """Return text in the color of css_class, or unchanged if the class has no color."""
        color = self.colors.get(css_class)
        if not text or not color:
            return text
        red, green, blue = (int(color.lstrip("#")[index : index + 2], 16) for index in (0, 2, 4))
        if self.truecolor:
            code = f"38;2;{red};{green};{blue}"
        else:
            code = f"38;5;{_nearest_256_color(red, green, blue)}"
        return f"\033[{code}m{text}\033[0m"


def plain(text, css_class):
    """Return text unchanged, for output without colors."""
    return text


def printable(text, keep_line_breaks=False):
    """Return text with its non-printable characters escaped, as repr() does, such as \x1b for an escape character.

    Values printed with str(), such as a path, or an exception's message, can hold escape sequences that control the
    terminal, such as one that sets its title or clears the screen, or invisible characters that change how the text
    reads, such as a right-to-left override. They often come from a site's users, such as a file name.

    :param keep_line_breaks: Whether line breaks and tabs are kept, such as in a function's docs.
    """
    return "".join(
        character if character.isprintable() or (keep_line_breaks and character in "\n\t") else repr(character)[1:-1]
        for character in text
    )


def get_console_colors(stream):
    """Return the colors for a dump printed to stream, or None for plain text.

    Colored only in a terminal, unless the FORCE_COLOR environment variable is set. Never colored with NO_COLOR
    (https://no-color.org) or Django's DJANGO_COLORS=nocolor set.
    """
    if os.environ.get("NO_COLOR") or parse_color_setting(os.environ.get("DJANGO_COLORS", "")) is None:
        return None
    if not os.environ.get("FORCE_COLOR"):
        if not (hasattr(stream, "isatty") and stream.isatty()):
            return None
        # Older Windows consoles show the escape codes as text. Django checks for one that shows colors.
        if sys.platform == "win32" and not supports_color():  # pragma: no cover - Only on Windows.
            return None
    return ConsoleColors(truecolor=os.environ.get("COLORTERM") in ("truecolor", "24bit"))


def _nearest_256_color(red, green, blue):
    """Return the number of the 256-color terminal color nearest to a color: from its color cube, or its greys."""

    def nearest_level(value):
        return min(range(len(CUBE_LEVELS)), key=lambda index: abs(CUBE_LEVELS[index] - value))

    levels = [nearest_level(value) for value in (red, green, blue)]
    cube_color = tuple(CUBE_LEVELS[level] for level in levels)
    cube_number = 16 + 36 * levels[0] + 6 * levels[1] + levels[2]

    # The 24 greys (colors 232 to 255) run from 8 to 238, in steps of 10.
    grey_step = min(23, max(0, round(((red + green + blue) / 3 - 8) / 10)))
    grey = 8 + 10 * grey_step

    def distance(color):
        return sum((part - target) ** 2 for part, target in zip(color, (red, green, blue), strict=True))

    return cube_number if distance(cube_color) <= distance((grey, grey, grey)) else 232 + grey_step


def format_dump(object_info, colors=None):
    """Return a dumped object, as collected by dd() or dump(), as text: its name, then its tree.

    :param colors: ConsoleColors to color the text with, or None for plain text.
    """
    color = colors or plain

    def paint(text, css_class):
        """Return text escaped for the terminal, in the color of css_class."""
        return color(printable(text, keep_line_breaks=css_class == "docs"), css_class)

    filename, linenumber, obj_name, obj, function_doc, root_index_start, root_index_end, original_obj = object_info

    if isinstance(obj, DumpBreak):
        return _format_break(obj, paint)

    lines = []
    if filename and linenumber:
        lines.append(paint(f"File: {filename}, Line: {linenumber}", "location"))

    name = _format_name(obj_name, "Unknown Function" if function_doc else "Unknown Object", paint)
    if function_doc:
        # A dumped function shows its signature, in the name, and its docs.
        lines.append(f"{name}: {paint(function_doc, 'docs')}")
    else:
        start_page_of_dumps()
        tree = _format_object(obj, obj, None, 0, original_obj, False, paint, root_index_start, root_index_end)
        lines.append(f"{name}: {tree[0]}")
        lines.extend(tree[1:])

    return "\n".join(lines)


def _format_break(dump_break, paint):
    """Return a break as a line across, in the middle of as many lines as its size."""
    size = dump_break.size or app_settings.BREAK_SIZE
    lines = [""] * size
    lines[size // 2] = paint("-" * BREAK_WIDTH, "location")
    return "\n".join(lines)


def _format_name(obj_name, unknown, paint):
    """Return the dumped name, from its parts, such as a function name and its parameters, as one string."""
    if obj_name is None:
        return paint(unknown, "empty")
    return "".join(
        (" " if part.get("space_before") else "") + paint(part["value"], part["css_class"]) for part in obj_name
    )


def _format_object(
    obj, root_obj, skip_set, depth, original_obj, parent_is_intermediate, paint, start=None, end=None, relation_steps=0
):
    """Return the lines of an object's tree. The first line follows the object's name or key."""
    context = dump_object(
        obj, root_obj, skip_set, depth, original_obj, parent_is_intermediate, start, end, relation_steps=relation_steps
    )

    # A simple value, such as a string or a number.
    if "simple" in context:
        value = paint(context["simple"], context["css_class"])
        if context["type"] in SELF_EVIDENT_TYPES:
            return [value]
        return [f"{paint(context['type'], 'type')} {value}"]

    # Without the count the page adds to an object dumped more than once, since each console dump stands alone, and so
    # that an object shown again, such as one that refers back to itself, shows the same unique as where it is shown.
    unique = paint(context["unique"], "unique")
    header = context["type"]
    if context.get("length") is not None:
        header += f":{context['length']}"
    header = paint(header, "type")
    if context.get("intermediate"):
        header += " " + paint(context["intermediate"], context.get("intermediate_css_class") or "intermediate")

    # An object already shown, such as one that refers back to itself, or past the maximum depth. Its unique matches
    # the one where it is shown in full.
    if context.get("object") is None:
        return [f"{header} {unique}"]

    opening, closing = context["braces"]
    lines = [f"{header} {unique} {opening}"]
    children = context.get("skip")
    is_intermediate = bool(context.get("intermediate"))
    steps = context.get("relation_steps", 0)

    for label, value, _access_modifier, css_class, *_ in context.get("attributes", []):
        key = f"{paint(str(label), css_class)}: " if label is not None else ""
        if isinstance(value, Placeholder):
            # Such as a hidden sensitive value, or the items past the limit.
            child = [paint(value.text, "empty")]
        else:
            child = _format_object(
                value, root_obj, children, depth + 1, original_obj, is_intermediate, paint, relation_steps=steps
            )
        lines.extend(_indent(key, child))

    # A model instance's relations follow its attributes, as on the page.
    for relation in context.get("relations", []):
        key = f"{paint(relation['name'], 'attribute')}: "
        if isinstance(relation["value"], Placeholder):
            # Such as a relation that isn't loaded, with how to load it on the page.
            child = [paint(relation["value"].text, "empty")]
        else:
            child = _format_object(
                relation["value"],
                root_obj,
                children,
                depth + 1,
                original_obj,
                False,
                paint,
                relation_steps=context["next_relation_steps"],
            )
        lines.extend(_indent(key, child))

    for result in context.get("function_results", []):
        key = f"{paint(result['name'], 'function')}(): "
        if result.get("error"):
            child = [paint(result["error"], "empty")]
        else:
            child = _format_object(
                result["value"],
                root_obj,
                children,
                depth + 1,
                original_obj,
                is_intermediate,
                paint,
                relation_steps=steps,
            )
        lines.extend(_indent(key, child))

    lines.append(closing)
    return lines


def _indent(key, lines):
    """Return a child's lines, indented one level, with its key before the first line."""
    return [f"{INDENT}{key}{lines[0]}"] + [f"{INDENT}{line}" for line in lines[1:]]
