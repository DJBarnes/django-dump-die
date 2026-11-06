"""
Smoke tests for the example pages that ship with the package.

Each page should render the DumpDie page, with its description and its main objects, through to its final dd("done").
The output for each type is tested in detail with its own test views, in the other test folders.
"""

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase

# Example page url names, with their description, and the names of some of the objects they dump. None if the page
# has no description dump.
EXAMPLE_PAGES = {
    "django_dump_die:simple-type-example": (
        'Displaying example of "simple type" object output.',
        ["sample_int", "sample_none", "sample_module"],
    ),
    "django_dump_die:numeric-example": (
        'Displaying example of "numeric type" object output.',
        ["sample_int", "sample_decimal", "sample_complex"],
    ),
    "django_dump_die:intermediate-type-example": (
        'Displaying example of "intermediate type" object output.',
        ["sample_dt_date", "sample_complex", "pure_path"],
    ),
    "django_dump_die:datetime-example": (
        'Displaying example of "datetime" object output.',
        ["sample_dt_datetime", "sample_tz_time", "sample_dt_timedelta"],
    ),
    "django_dump_die:system-path-example": (
        'Displaying example of "syspath" object output.',
        ["os_path", "pure_path"],
    ),
    "django_dump_die:complex-type-example": (
        'Displaying example of "complex type" object output.',
        ["sample_list", "sample_multilevel_dict", "SampleEnum"],
    ),
    "django_dump_die:iterable-type-example": (
        'Displaying example of "iterable" object output.',
        ["sample_set", "sample_tuple", "sample_memory_view"],
    ),
    "django_dump_die:class-example": (
        "Displaying example of class object output.",
        ["SimpleClass", "sample_simple_class", "sample_complex_class"],
    ),
    "django_dump_die:function-example": (
        'Displaying example of "function" object output.',
        ['<span class="function">sample_func_param</span>'],
    ),
    "django_dump_die:django-types-example": (
        "Displaying example of Django specific object output.",
        ["sample_django_model_populated", "sample_request"],
    ),
    "django_dump_die:django-model-example": (
        "Displaying example of Django model object output.",
        ["SampleDjangoModel", "sample_django_model_empty", "sample_model_form"],
    ),
    "django_dump_die:django-request-response-cycle-example": (
        'Displaying Django "request-response-cycle" example output.',
        ["sample_query_dict", "sample_request", "sample_template_response"],
    ),
    "django_dump_die:edge-case-example": (
        "Displaying example of various edge-case output.",
        ["Output of parens as string within dd parameters:"],
    ),
    "django_dump_die:full-category-example": (None, ["sample_int", "sample_dt_date", "sample_list"]),
    "django_dump_die:full-purpose-example": (None, ["sample_decimal", "sample_dict"]),
}


@override_settings(DEBUG=True)
class DumpDieExamplePagesRenderTestCase(IntegrationTestCase):
    """Verify every example page renders its dump output."""

    def test_example_pages_render(self):
        """Verify each example page shows the DumpDie toolbar, its description, its main objects, and its last dump."""
        for url, (description, objects) in EXAMPLE_PAGES.items():
            with self.subTest(url=url):
                expected_content = ["<div><h1>Django DumpDie</h1></div>"]
                if description:
                    expected_content.append(description)
                # The page is shown through to the final dd("done"), which comes after everything else.
                expected_content.append('<span class="string">"done"</span>')

                response = self.assertGetResponse(
                    url,
                    expected_title="DD",
                    expected_header="Django DumpDie",
                    expected_content=expected_content,
                )
                content = response.content.decode("utf-8")
                for obj in objects:
                    self.assertIn(obj, content)

    def test_toolbar_has_its_buttons(self):
        """Verify the toolbar shows the Expand and Collapse buttons for everything, and for each level."""
        self.assertGetResponse(
            "django_dump_die:simple-type-example",
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                '<div class="dump-toolbar">',
                "<div><h1>Django DumpDie</h1></div>",
                '<p id="expand-all" class="button">Expand All</p>',
                '<p id="expand-1st-lvl" class="button">Expand First Level</p>',
                '<p id="expand-2nd-lvl" class="button">Expand Second Level</p>',
                '<p id="collapse-all" class="button">Collapse All</p>',
                '<p id="collapse-1st-lvl" class="button">Collapse First Level</p>',
                '<p id="collapse-2nd-lvl" class="button">Collapse Second Level</p>',
                '<div class="static-padding"></div>',
            ],
            content_starts_after="<body>",
            content_ends_before='<div class="dump-wrapper">',
        )
