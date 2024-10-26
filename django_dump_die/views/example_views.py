"""Various example views for DumpDie library. To showcase how various outputs look in practice."""

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
try:
    from django_dump_die.middleware import dd, dump
except Exception:
    pass

from .example_helpers import (
    ComplexTypesHelper,
    DjangoTypesHelper,
    EdgeCasesHelper,
    FunctionTypesHelper,
    IntermediateTypesHelper,
    SimpleTypesHelper,
    SimpleClass,
)

# region Main views showcasing functionality.


def index(request):
    """Index view, to easily navigate to example views."""
    return render(request, "django_dump_die/index.html")


def simple_types_example(request):
    """Example view, rendering only "simple type" object output."""

    # Output desired dump values.
    dump('Displaying example of "simple type" object output.')
    dump("")
    SimpleTypesHelper().dump_simple_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def intermediate_types_example(request):
    """Example view, rendering only "intermediate type" object output."""

    # Output desired dump values.
    dump('Displaying example of "intermediate type" object output.')
    dump("")
    IntermediateTypesHelper().dump_intermediate_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def complex_types_example(request):
    """Example view, rendering only "complex type" object output."""

    # Output desired dump values.
    dump('Displaying example of "complex type" object output.')
    dump("")
    ComplexTypesHelper().dump_all_complex_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def iterable_types_example(request):
    """Example view, rendering only iterable object output."""
    dump('Displaying example of "iterable" object output.')
    dump("")
    ComplexTypesHelper().dump_all_iterables()
    dump("")
    dump("")

    # Force dd to prevent further view parsing
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die.sample.html", {})


def class_types_example(request):
    """Example view, rendering only class object output."""

    # Output desired dump values.
    dump("Displaying example of class object output.")
    dump("")
    ComplexTypesHelper().dump_class_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def django_types_example(request):
    """Example view, rendering only Django specific object output."""

    # Output desired dump values.
    dump("Displaying example of Django specific object output.")
    dump("")
    DjangoTypesHelper().dump_all_django_types(request)
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def django_model_types_example(request):
    """Example view, rendering only Django model object output."""

    # Output desired dump values.
    dump("Displaying example of Django model object output.")
    dump("")
    DjangoTypesHelper().dump_model_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def django_request_response_cycle_types_example(request):
    """Example view, rendering a request object."""

    # Output desired dump values.
    dump('Displaying Django "request-response-cycle" example output.')
    dump("")
    DjangoTypesHelper().dump_django_request_response_cycle_types(request)
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def function_types_example(request):
    """Example view, rendering only function object output."""

    # Output desired dump values.
    dump('Displaying example of "function" object output.')
    dump("")
    FunctionTypesHelper().dump_function_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def full_category_example(request):
    """Example view, rendering all examples shown in all other views, all in one page."""

    # Output desired dump values.
    dump("")
    SimpleTypesHelper().dump_simple_types()
    dump("")
    dump("")
    IntermediateTypesHelper().dump_intermediate_types()
    dump("")
    dump("")
    ComplexTypesHelper().dump_all_complex_types()
    dump("")
    dump("")
    DjangoTypesHelper().dump_all_django_types(request)
    dump("")
    dump("")
    FunctionTypesHelper().dump_function_types()
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


# endregion Main views showcasing functionality.

# region Specialized views showcasing specialized functionality.


def numeric_example(request):
    """Example view, rendering only "numeric" object output."""

    # Output desired dump values.
    dump('Displaying example of "numeric type" object output.')
    dump("")
    SimpleTypesHelper().dump_numeric_types()
    IntermediateTypesHelper().dump_complex_number_type()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def datetime_example(request):
    """Example view, rendering only "datetime" object output."""

    # Output desired dump values.
    dump('Displaying example of "datetime" object output.')
    dump("")
    IntermediateTypesHelper().dump_datetime_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def system_path_example(request):
    """Example view, rendering only "system path" object output."""

    # Output desired dump values.
    dump('Displaying example of "syspath" object output.')
    dump("")
    IntermediateTypesHelper().dump_syspath_types()
    dump("")
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def full_specialized_example(request):
    """Example view, rendering all examples shown in all other specialized views, all in one page."""

    # Output desired dump values.
    dump("")
    SimpleTypesHelper().dump_numeric_types()
    dump("")
    dump("")
    IntermediateTypesHelper().dump_datetime_types()
    dump("")
    dump("")
    IntermediateTypesHelper().dump_syspath_types()
    dump("")
    dump("")
    ComplexTypesHelper().dump_all_iterables()
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


# endregion Specialized views showcasing specialized functionality.

# region Edge case views showcasing potential edge cases.


def edge_case_example(request):
    """Example view, rendering various edge-case output.

    These are output types that don't necessarily belong in the other example views, but have
    resulted in errors/bad output, in the past.

    This view allows easily checking them to make sure they are still handled correctly.
    """

    # Output desired dump values.
    dump("")
    EdgeCasesHelper().dump_edgecase_types()
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


def exception_case_example(request):
    """Example view, rendering an object that raises an exception when being dumped.

    This view allows easily checking them to make sure they are still handled correctly.
    """

    # Output desired dump values.
    dump("")
    EdgeCasesHelper().dump_exception_causing_object()
    dump("")

    # Force dd to prevent further view parsing.
    dd("done")

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/sample.html", {})


# endregion Edge case views showcasing potential edge cases.

# region Template dumping.


def template_dump_example(request):
    """Example view, rendering dumps done from the template using the template tag."""

    # Make instance of simple class for context.
    sample_simple_class = SimpleClass()

    # Show that any calls after dd() end up ignored.
    return render(request, "django_dump_die/template_dump.html", {"sample_simple_class": sample_simple_class})


# endregion Template dumping.
