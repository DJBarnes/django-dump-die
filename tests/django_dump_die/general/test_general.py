"""
Tests for general DD functionality.
"""

# System Imports.
from unittest.mock import patch

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


class DumpDieGeneralTestCase(IntegrationTestCase):
    """Verify handling of dumped "simple" types."""

    @override_settings(DEBUG=True)
    def test_view_returns_normal_response_when_no_dumps_used(self):
        """Verify view returns normal response when no dumps used"""
        url = "django_dump_die:index"

        self.assertGetResponse(
            url,
            expected_title="Django DumpDie Examples",
            expected_header="Django DumpDie Example Index Page",
            expected_content=[
                "<p>The following pages provide example output when using the Django DumpDie package.</p>"
            ],
            expected_not_content=["<div><h1>Django DumpDie</h1></div>"],
        )

    def test_dump_without_a_dd_still_shows_dump_view(self):
        """Verify that only using dump and no dd still shows the dump view."""
        pass

    def test_dd_without_any_dumps_still_shows_dump_view(self):
        """Verify that only using dd and no dumps still shows the dump view."""
        pass

    @override_settings(DEBUG=False)
    def test_debug_off_skips_all_dumps(self):
        """Verify no dumps occur when debug is off."""
        url = "django_dump_die:simple-type-example"

        self.assertGetResponse(
            url,
            expected_title="Sample page",
            expected_header="Sample page",
            expected_content=["<p>Sample page body content</p>"],
            expected_not_content=["<div><h1>Django DumpDie</h1></div>"],
        )

    @override_settings(DEBUG=False)
    def test_debug_off_skips_all_template_dumps(self):
        """Verify no template dumps occur when debug is off."""
        url = "django_dump_die:template-dump-example"

        self.assertGetResponse(
            url,
            expected_title="Template Dump Example",
            expected_header="Template Dump Example",
            expected_content=["<p>After dump content</p>"],
            expected_not_content=['<div class="dump-wrapper">'],
        )

    @override_settings(DEBUG=True)
    @patch("django_dump_die.templatetags.dump_die._generate_unique")
    def test_debug_on_correctly_shows_template_dumps(self, mocked_unique_generation):
        """Verify template dumps occur when debug is on."""
        url = "django_dump_die:template-dump-example"

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f"data_900{index}", ""),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            url,
            expected_title="Template Dump Example",
            expected_header="Template Dump Example",
            expected_content=[
                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="empty">Unknown_Object_Name</span>
                    </span>:
                    <span class="type" title="SimpleClass">SimpleClass</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9000"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9000">data_9000</span>
                        <span id="arrow-data_9000" class="arrow arrow-data_9000">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9000 " data-unique="data_9000">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9000-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9000-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9000-attributes show"
                                data-unique-attributes="data_9000-attributes"
                            >
                """,
                # Object child elements.
                # Note that we check for the presence of the general element, but not the direct values.
                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,
            ],
            content_starts_after="<body>",
            content_ends_before="</body>",
        )

    def test_view_that_raise_an_exception_is_not_caught_by_the_dump_logic(self):
        """Test that an unrelated unhandled exception being raised is not caught by the dump logic"""
        pass
