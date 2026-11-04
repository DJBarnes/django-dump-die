"""Views for the general DumpDie tests."""

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
from django_dump_die.middleware import dd, dump
from django_dump_die.views.example_helpers import SampleRelation


def database_error_example(request):
    """Dumps a QuerySet whose query fails.

    The sample models have no database table, so evaluating the QuerySet raises a database error.
    """
    dd(SampleRelation.objects.all())


def dump_only_example(request):
    """Dumps without calling dd, then returns a normal page."""
    dump("Dumped without dd.")
    return render(request, "django_dump_die/sample.html", {})


def dd_only_example(request):
    """Calls dd without any dump before it."""
    dd("Only dd, without dumps.")
