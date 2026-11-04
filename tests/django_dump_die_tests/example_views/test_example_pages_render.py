"""
Smoke tests for the example pages that don't have detailed output tests.

Each page should render the DumpDie page, with every object it dumps, through to its final dd("done").
"""

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase

# Example page url names, with text that their output should include. None if the page has no description dump.
EXAMPLE_PAGES = {
    "django_dump_die:iterable-type-example": 'Displaying example of "iterable" object output.',
    "django_dump_die:class-example": "Displaying example of class object output.",
    "django_dump_die:django-types-example": "Displaying example of Django specific object output.",
    "django_dump_die:django-model-example": "Displaying example of Django model object output.",
    "django_dump_die:numeric-example": 'Displaying example of "numeric type" object output.',
    "django_dump_die:datetime-example": 'Displaying example of "datetime" object output.',
    "django_dump_die:system-path-example": 'Displaying example of "syspath" object output.',
    "django_dump_die:full-category-example": None,
    "django_dump_die:full-purpose-example": None,
    "django_dump_die:edge-case-example": None,
}


@override_settings(DEBUG=True)
class DumpDieExamplePagesRenderTestCase(IntegrationTestCase):
    """Verify every example page renders its dump output."""

    def test_example_pages_render(self):
        """Verify each example page shows the DumpDie toolbar, its description, and its final dump."""
        for url, description in EXAMPLE_PAGES.items():
            with self.subTest(url=url):
                expected_content = ["<div><h1>Django DumpDie</h1></div>"]
                if description:
                    expected_content.append(description)
                expected_content.append('<span class="string">"done"</span>')

                self.assertGetResponse(
                    url,
                    expected_title="DD",
                    expected_header="Django DumpDie",
                    expected_content=expected_content,
                )
