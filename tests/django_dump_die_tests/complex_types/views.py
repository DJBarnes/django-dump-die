"""Various test views for the DumpDie library.

Needed because having too many mocked "unique" values on a single response will lead to either:
* StopIteration - Due to giving an insufficient mock range.
* RecursionError - Due to too many mock calls, so Python seems to think we're recursing infinitely.

The solution was to divide objects out, displaying only one object per view, which lowers the total amount of
"uniques" being rendered on a given page.
"""

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
from django_dump_die.middleware import dd, dump
from django_dump_die.views.example_helpers import ComplexTypesHelper


def index(request):
    """Exclusively used for easy access to visual examine test views while debugging tests."""
    return render(request, "django_dump_die/test_index.html", {})


def complex_type__set(request):
    """Example view, rendering only "complex type" Set output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Set output.')
    dump("")
    ComplexTypesHelper().dump_set()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__frozen_set(request):
    """Example view, rendering only "complex type" FrozenSet output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" FrozenSet output.')
    dump("")
    ComplexTypesHelper().dump_frozen_set()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__tuple(request):
    """Example view, rendering only "complex type" Tuple output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Tuple output.')
    dump("")
    ComplexTypesHelper().dump_tuple()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__list(request):
    """Example view, rendering only "complex type" List output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" List output.')
    dump("")
    ComplexTypesHelper().dump_list()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__dict(request):
    """Example view, rendering only "complex type" Dict output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Dict output.')
    dump("")
    ComplexTypesHelper().dump_dict()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__querydict(request):
    """Example view, rendering only "complex type" QueryDict output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" QueryDict output.')
    dump("")
    ComplexTypesHelper().dump_querydict()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__memory_view(request):
    """Example view, rendering only "complex type" MemoryView output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" MemoryView output.')
    dump("")
    ComplexTypesHelper().dump_memory_view()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__enum(request):
    """Example view, rendering only "complex type" Enum output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Enum output.')
    dump("")
    ComplexTypesHelper().dump_enum()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__set(request):
    """Example view, rendering only "complex type" Multi-Level Set output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level Set output.')
    dump("")
    ComplexTypesHelper().dump_multilevel_set()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__tuple(request):
    """Example view, rendering only "complex type" Multi-Level Tuple output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level Tuple output.')
    dump("")
    ComplexTypesHelper().dump_multilevel_tuple()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__list(request):
    """Example view, rendering only "complex type" Multi-Level List output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level List output.')
    dump("")
    ComplexTypesHelper().dump_multilevel_list()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__dict(request):
    """Example view, rendering only "complex type" Multi-Level Dict output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Multi-Level Dict output.')
    dump("")
    ComplexTypesHelper().dump_multilevel_dict()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__list__element(request):
    """Example view, rendering only "complex type" List element output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" List element output.')
    dump("")
    ComplexTypesHelper().dump_list_element()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__tuple__element(request):
    """Example view, rendering only "complex type" Tuple element output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Tuple element output.')
    dump("")
    ComplexTypesHelper().dump_tuple_element()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__dict__element(request):
    """Example view, rendering only "complex type" Dict element output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Dict element output.')
    dump("")
    ComplexTypesHelper().dump_dict_element()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__enum__element(request):
    """Example view, rendering only "complex type" Enum element output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Enum element output.')
    dump("")
    ComplexTypesHelper().dump_enum_element()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_type__multilevel__tuple__element__function(request):
    """Example view, rendering only "complex type" Tuple element function output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" Tuple element function output.')
    dump("")
    ComplexTypesHelper().dump_tuple_element_function()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})
