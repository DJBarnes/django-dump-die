"""Views for the django-dump-die test project."""

# Third-Party Imports.
from django.shortcuts import render


def index(request):
    """Index of the test views, for opening them in a browser while debugging tests."""
    return render(request, "django_dump_die_tests/index.html", {})
