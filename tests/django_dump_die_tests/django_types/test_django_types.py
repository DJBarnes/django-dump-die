"""
Tests for dumped Django types, each with its own view.

These objects have many attributes, which differ between Django versions, so the tests check the dumped type and a
few rows that every supported version has, rather than the whole output.
"""

# System Imports.
import re

# Third-Party Imports.
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

# An escaped single quote. Django before 3.0 escapes it as &#39;, later versions as &#x27;.
QUOTE = r"&#(?:x27|39);"


def row_pattern(name, type_name, value, kind="attribute", decorator=None):
    """Regular expression for the row of an attribute or key, with its value's type and value.

    :param value: The expected value, as shown. Single quotes in it match either way of escaping them.
    :param kind: The row's CSS class: "attribute", "class_attribute", "constant", or "key".
    :param decorator: "property" or "cached_property" to expect that marker.
    """
    marker = r'<span class="decorator" title="[^"]*">@{0}</span>\s*'.format(decorator) if decorator else ""
    name_pattern = re.escape(name).replace("'", QUOTE)
    value_pattern = re.escape(value).replace("'", QUOTE)
    return (
        marker
        + r'<span class="{0}" title="[^"]*">{1}</span>:\s*'.format(kind, name_pattern)
        + r'<span class="type" title="{0}">{0}</span>\s*<code class="\w+">{1}</code>'.format(
            re.escape(type_name), value_pattern
        )
    )


@override_settings(DEBUG=True)
class DumpDieDjangoTypeTestCase(SimpleTestCase):
    """Verify handling of dumped Django types."""

    def get_dump(self, url_name):
        """Return the dump page's content for a view, from the start of its dump to the final "done" dump."""
        response = self.client.get(reverse("django_dump_die__tests__django:" + url_name))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        # The last dump on the page is the view's final dd("done").
        return content[content.index("<!--Start Main Content-->") : content.rindex('<div class="dump-wrapper">')]

    def assertDumpedType(self, content, dumped_name, type_name):
        """Assert the dump's name and type."""
        self.assertRegex(
            content,
            r'<span class="dumped_name">{0}</span>\s*</span>:\s*<span class="type" title="{1}">'.format(
                re.escape(dumped_name), re.escape(type_name)
            ),
        )

    def test_model_instance_display(self):
        """Verify a model instance shows its fields, and its primary key as a property."""
        content = self.get_dump("django__model_instance")

        self.assertDumpedType(content, "sample_model", "SampleRelation")
        self.assertRegex(content, row_pattern("id", "int", "3"))
        self.assertRegex(content, row_pattern("pk", "int", "3", decorator="property"))
        self.assertRegex(content, row_pattern("relate_name", "str", "'Sample relation'"))

    def test_model_class_display(self):
        """Verify a model class is dumped as the class, with its fields' descriptors, without being called."""
        content = self.get_dump("django__model_class")

        self.assertRegex(content, r'<span class="dumped_name">SampleRelation</span>\s*</span>:\s*<span class="type"')
        self.assertIn('<span class="type" title="ModelBase">ModelBase</span>', content)
        self.assertRegex(content, r'<span class="attribute" title="Attribute">relate_name</span>:\s*<span class="type"')

    def test_form_display(self):
        """Verify a form with submitted data shows that it is bound, and its data."""
        content = self.get_dump("django__form")

        self.assertDumpedType(content, "sample_form", "ContactForm")
        self.assertRegex(content, row_pattern("is_bound", "bool", "True"))
        self.assertRegex(content, row_pattern("'name'", "str", "'Ada'", kind="key"))

    def test_bound_field_display(self):
        """Verify a form's bound field is shown as a simple value, with its own color."""
        content = self.get_dump("django__bound_field")

        self.assertRegex(
            content,
            r'<span class="type" title="BoundField">BoundField</span>\s*'
            r'<code class="bound">&lt;django\.forms\.boundfield\.BoundField object at 0x[0-9a-fA-F]+&gt;</code>',
        )

    def test_request_display(self):
        """Verify the request shows its method, path, and request headers."""
        content = self.get_dump("django__request")

        self.assertDumpedType(content, "request", "WSGIRequest")
        self.assertRegex(content, row_pattern("method", "str", "'GET'"))
        self.assertRegex(content, row_pattern("path", "str", "'/tests/django/request/'"))
        self.assertRegex(content, row_pattern("'REQUEST_METHOD'", "str", "'GET'", kind="key"))

    def test_http_response_display(self):
        """Verify a response shows its status, and its content as a property."""
        content = self.get_dump("django__http_response")

        self.assertDumpedType(content, "sample_response", "HttpResponse")
        self.assertRegex(content, row_pattern("status_code", "int", "201"))
        self.assertRegex(content, row_pattern("reason_phrase", "str", "'Created'", decorator="property"))
        self.assertRegex(content, row_pattern("content", "bytes", "b'Sample content'", decorator="property"))

    def test_template_response_display(self):
        """Verify a rendered template response shows that it is rendered, and its status."""
        content = self.get_dump("django__template_response")

        self.assertDumpedType(content, "sample_template_response", "TemplateResponse")
        self.assertRegex(content, row_pattern("is_rendered", "bool", "True", decorator="property"))
        # Without a status of its own, a response uses the 200 that HttpResponseBase sets as a class attribute.
        self.assertRegex(content, row_pattern("status_code", "int", "200", kind="class_attribute"))
