"""Test views for dumped Django types, one dump per view."""

# Third-Party Imports.
from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

# Internal Imports.
from django_dump_die.middleware import dd, dump
from django_dump_die.views.example_helpers import SampleRelation


class ContactForm(forms.Form):
    """Form with one field, for dumping a form and its bound field."""

    name = forms.CharField(max_length=20)


def _done(request):
    """End the view with dd(), so that the dump page is shown. The page after it is never rendered."""
    dd("done")
    return render(request, "django_dump_die/sample.html", {})


def django_type_model_instance(request):
    """Test view dumping a model instance. It isn't saved, so the test database isn't needed."""
    sample_model = SampleRelation(id=3, relate_name="Sample relation")
    dump(sample_model)
    return _done(request)


def django_type_model_class(request):
    """Test view dumping a model class."""
    dump(SampleRelation)
    return _done(request)


def django_type_form(request):
    """Test view dumping a form with submitted data."""
    sample_form = ContactForm(data={"name": "Ada"})
    dump(sample_form)
    return _done(request)


def django_type_bound_field(request):
    """Test view dumping one field of a form with submitted data."""
    sample_form = ContactForm(data={"name": "Ada"})
    dump(sample_form["name"])
    return _done(request)


def django_type_safe_string(request):
    """Test view dumping a string marked as safe for HTML, which is a subclass of str."""
    sample_safe_string = mark_safe("<b>Bold</b> text")
    dump(sample_safe_string)
    return _done(request)


def django_type_lazy_string(request):
    """Test view dumping a lazy translation string, which isn't a str until it's used."""
    sample_lazy_string = gettext_lazy("Sample lazy text")
    dump(sample_lazy_string)
    return _done(request)


def django_type_request(request):
    """Test view dumping the request."""
    dump(request)
    return _done(request)


def django_type_http_response(request):
    """Test view dumping a response."""
    sample_response = HttpResponse("Sample content", status=201)
    dump(sample_response)
    return _done(request)


def django_type_template_response(request):
    """Test view dumping a rendered template response."""
    sample_template_response = TemplateResponse(request, "django_dump_die/sample.html", {})
    sample_template_response.render()
    dump(sample_template_response)
    return _done(request)
