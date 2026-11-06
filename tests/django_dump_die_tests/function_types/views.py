"""Test views for dumped functions and function results, one dump per view."""

# Third-Party Imports.
from django.shortcuts import render

# Internal Imports.
from django_dump_die.middleware import dd, dump
from django_dump_die.views.example_helpers import SimpleClass, sample_func, sample_func_param


def _done(request):
    """End the view with dd(), so that the dump page is shown. The page after it is never rendered."""
    dd("done")
    return render(request, "django_dump_die/sample.html", {})


def no_docstring():
    return 7


def function_type_basic(request):
    """Test view dumping a function without parameters."""
    dump(sample_func)
    return _done(request)


def function_type_with_params(request):
    """Test view dumping a function with positional, variable, and keyword parameters."""
    dump(sample_func_param)
    return _done(request)


def function_type_no_docstring(request):
    """Test view dumping a function without a docstring, which is dumped as an object."""
    dump(no_docstring)
    return _done(request)


def function_type_lambda(request):
    """Test view dumping a lambda."""
    sample_lambda = lambda value: value * 2  # noqa: E731 pylint: disable=unnecessary-lambda-assignment
    dump(sample_lambda)
    return _done(request)


def function_type_bound_method(request):
    """Test view dumping a method of an object."""
    sample_object = SimpleClass()
    dump(sample_object.sample_class_func)
    return _done(request)


def function_type_builtin(request):
    """Test view dumping a built-in function."""
    dump(len)
    return _done(request)


def function_type_call(request):
    """Test view dumping the result of calling a function without parameters."""
    dump(sample_func())
    return _done(request)


def function_type_call_with_one_arg(request):
    """Test view dumping the result of calling a function with one argument."""
    dump(sample_func_param(32))
    return _done(request)


def function_type_call_with_kwarg(request):
    """Test view dumping the result of calling a function with an argument and a keyword argument."""
    dump(sample_func_param("test_param", some_kwarg=True))
    return _done(request)


def function_type_call_with_args(request):
    """Test view dumping the result of calling a function with several arguments."""
    dump(sample_func_param("test_param", "extra_arg_1", 2, True))
    return _done(request)
