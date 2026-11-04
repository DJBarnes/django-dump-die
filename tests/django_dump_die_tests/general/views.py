"""Views for the general DumpDie tests."""

# Internal Imports.
from django_dump_die.middleware import dd
from django_dump_die.views.example_helpers import SampleRelation


def database_error_example(request):
    """Dumps a QuerySet whose query fails.

    The sample models have no database table, so evaluating the QuerySet raises a database error.
    """
    dd(SampleRelation.objects.all())
