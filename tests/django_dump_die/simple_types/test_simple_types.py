"""
Tests for "simple" type DD output.
"""

# System Imports.
from unittest.mock import patch

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


@override_settings(DEBUG=True)
class DumpDieSimpleTypeTestCase(IntegrationTestCase):
    """Verify handling of dumped "simple" types."""

    def test_bool_display(self):
        """Verify dumping a "bool" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__bool"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_bool</span>
                    </span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_bytes_display(self):
        """Verify dumping a "bytes" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__bytes"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_bytes</span>
                    </span>:
                    <span class="type" title="bytes">bytes</span>
                    <code class="number">b'sample bytes'</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_const_display(self):
        """Verify dumping a "const" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__const"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="constant">SAMPLE_CONST</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Sample Constant Content'</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_decimal_display(self):
        """Verify dumping a "decimal" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__decimal"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_decimal</span>
                    </span>:
                    <span class="type" title="Decimal">Decimal</span>
                    <code class="number">42.4200000000000017053025658242404460906982421875</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_float_display(self):
        """Verify dumping a "float" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__float"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_float</span>
                    </span>:
                    <span class="type" title="float">float</span>
                    <code class="number">42.42</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_int_display(self):
        """Verify dumping a "int" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__int"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_int</span>
                    </span>:
                    <span class="type" title="int">int</span>
                    <code class="number">42</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_module_display(self):
        """Verify dumping a "module" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__module"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_module</span>
                    </span>:
                    <span class="type" title="module">module</span>
                    <code class="module"><module 'django.html'></code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_none_display(self):
        """Verify dumping a "none" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__none"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_none</span>
                    </span>:
                    <span class="type" title="null">null</span>
                    <code class="none">None</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )

    def test_string_display(self):
        """Verify dumping a "string" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = "django_dump_die__tests__simple:simple__string"

        self.assertGetResponse(
            self.url,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_string</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Sample String Content'</code>
                </div>
                """,
                "<hr>",
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">"done"</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'done'</code>
                </div>
                """,
            ],
            content_ends_before="<!--End Main Content-->",
        )
