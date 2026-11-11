"""Views for the browser tests of the DumpDie page's JavaScript."""

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
from django_dump_die.middleware import dd, dump
from django_dump_die_tests.django_test_project.models import Book


class BrowserTestClass:
    """Class with attributes and functions, for checking the Attributes, Function Results, and Functions sections."""

    dd_function_results = ("do_work",)

    def __init__(self):
        self.number = 42
        self.items = ["first", "second"]

    def do_work(self):
        """Do some work."""
        return True


def nested_example(request):
    """Dumps nested objects, with one object referenced twice, so its unique appears twice."""
    shared = {"shared": True}
    nested_example = [
        {"name": "first", "inner": {"value": 1, "shared": shared}},
        {"name": "second", "inner": {"value": 2, "shared": shared}},
        BrowserTestClass(),
    ]
    dd(nested_example)


def relations_example(request):
    """Dumps a model instance, which has a Relations section. It isn't saved, so the page runs no queries."""
    sample_book = Book(title="Draft")
    dd(sample_book)


def template_dump_example(request):
    """Dumps from a template, into a normal page without the DumpDie toolbar."""
    return render(request, "django_dump_die/template_dump.html", {"sample_simple_class": BrowserTestClass()})


def above_page_example(request):
    """Dumps nested objects without dd(), then returns a page that has its own template dump."""
    shared = {"shared": True}
    dump([{"inner": shared}, {"inner": shared}])
    return render(request, "django_dump_die_tests/browser/above_page.html", {"sample": BrowserTestClass()})
