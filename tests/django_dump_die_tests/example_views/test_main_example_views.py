"""
Tests main example views.
"""

# System Imports.

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


@override_settings(DEBUG=True)
class SimpleTypeExampleViewTestCase(IntegrationTestCase):
    """Verify handling of dumped "simple" types."""

    url = "django_dump_die:simple-type-example"

    def test_toolbar_display(self):
        """Verify page properly displays toolbar."""
        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check toolbar header.
                '<div class="dump-toolbar">',
                "<div><h1>Django DumpDie</h1></div>",
                # Check existence of buttons.
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

    def test_page_descriptor_display(self):
        """Verify initial page descriptor output."""
        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check page descriptor.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">'Displaying example of "simple type" object output.'</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Displaying example of "simple type" object output.'</code>
                </div>
                """,
                "<hr>",
                # Check visual-padding lines.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">""</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">""</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                "<hr>",
            ],
            content_starts_after='<div class="static-padding"></div>',
            content_ends_before='<span class="constant">SAMPLE_CONST</span>',
        )


@override_settings(DEBUG=True)
class IntermediateTypeExampleViewTestCase(IntegrationTestCase):
    """Verify handling of dumped "intermediate" types."""

    url = "django_dump_die:intermediate-type-example"

    def test_toolbar_display(self):
        """Verify page properly displays toolbar."""
        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check toolbar header.
                '<div class="dump-toolbar">',
                "<div><h1>Django DumpDie</h1></div>",
                # Check existence of buttons.
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

    def test_page_descriptor_display(self):
        """Test initial page descriptor output."""
        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check page descriptor.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">'Displaying example of "intermediate type" object output.'</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Displaying example of "intermediate type" object output.'</code>
                </div>
                """,
                "<hr>",
                # Check visual-padding lines.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">""</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">""</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                "<hr>",
            ],
            content_starts_after='<div class="static-padding"></div>',
            content_ends_before="Python bytes array examples:",
        )


@override_settings(DEBUG=True)
class ComplexTypeExampleViewTestCase(IntegrationTestCase):
    """Verify handling of dumped "complex" types."""

    url = "django_dump_die:complex-type-example"

    def test_toolbar_display(self):
        """Verify page properly displays toolbar."""
        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check toolbar header.
                '<div class="dump-toolbar">',
                "<div><h1>Django DumpDie</h1></div>",
                # Check existence of buttons.
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

    def test_page_descriptor_display(self):
        """Test initial page descriptor output."""
        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check page descriptor.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">'Displaying example of "complex type" object output.'</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Displaying example of "complex type" object output.'</code>
                </div>
                """,
                "<hr>",
                # Check visual-padding lines.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">""</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">""</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                "<hr>",
            ],
            content_starts_after='<div class="static-padding"></div>',
            content_ends_before="Minimal object examples:",
        )
