"""Various simple type test views for testing."""

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
from django_dump_die.middleware import dd
from django_dump_die.views.example_helpers import SimpleTypesHelper


def simple_type_bool(request):
    """Test view rendering a bool"""

    # Output desired dump values
    SimpleTypesHelper().dump_bool()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_bytes(request):
    """Test view rendering a bytes"""

    # Output desired dump values
    SimpleTypesHelper().dump_bytes()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_const(request):
    """Test view rendering a constant"""

    # Output desired dump values
    SimpleTypesHelper().dump_const()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_decimal(request):
    """Test view rendering a decimal"""

    # Output desired dump values
    SimpleTypesHelper().dump_decimal()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_float(request):
    """Test view rendering a float"""

    # Output desired dump values
    SimpleTypesHelper().dump_float()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_int(request):
    """Test view rendering a integer"""

    # Output desired dump values
    SimpleTypesHelper().dump_int()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_module(request):
    """Test view rendering a module"""

    # Output desired dump values
    SimpleTypesHelper().dump_module()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_none(request):
    """Test view rendering a None"""

    # Output desired dump values
    SimpleTypesHelper().dump_none()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})


def simple_type_string(request):
    """Test view rendering a string"""

    # Output desired dump values
    SimpleTypesHelper().dump_string()
    # Force dd to prevent further view parsing
    dd("done")
    # Show that any calls after dd() end up ignored
    return render(request, "django_dump_die/sample.html", {})
