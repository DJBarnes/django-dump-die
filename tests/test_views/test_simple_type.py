"""
Tests for "simple" type DD output.
"""

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


@override_settings(DEBUG=True)
class DumpDieSimpleTypeTestCase(IntegrationTestCase):
    """Verify handling of dumped "simple" types."""
    url = 'django_dump_die:simple-type-example'

    def test_toolbar_display(self):
        """Verify page properly displays toolbar."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                # Check toolbar header.
                '<div class="dump-toolbar">',
                '<div><h1>Django DumpDie</h1></div>',

                # Check existence of buttons.
                '<p id="expand-all" class="button">Expand All</p>',
                '<p id="expand-1st-lvl" class="button">Expand First Level</p>',
                '<p id="expand-2nd-lvl" class="button">Expand Second Level</p>',
                '<p id="collapse-all" class="button">Collapse All</p>',
                '<p id="collapse-1st-lvl" class="button">Collapse First Level</p>',
                '<p id="collapse-2nd-lvl" class="button">Collapse Second Level</p>',

                '<div class="static-padding"></div>',
            ],
            content_starts_after='<body>',
            content_ends_before='<div class="dump-wrapper">',
        )

    def test_page_descriptor_display(self):
        """Verify initial page descriptor output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
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
                '<hr>',
                # Check visual-padding lines.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">''</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="string">''</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='<div class="static-padding"></div>',
            content_ends_before='<span class="constant">SAMPLE_CONST</span>',
        )

    def test_constant_display(self):
        """Verify dumping a "constant" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="constant">SAMPLE_CONST</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Sample Constant Content'</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='<div class="static-padding"></div>',
            content_ends_before='sample_module',
        )

    def test_module_display(self):
        """Verify dumping a "module" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_module</span>
                    </span>:
                    <span class="type" title="module">module</span>
                    <code class="module"><module 'django.html'></code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='SAMPLE_CONST',
            content_ends_before='sample_bytes',
        )

    def test_bytes_display(self):
        """Verify dumping a "bytes" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_bytes</span>
                    </span>:
                    <span class="type" title="bytes">bytes</span>
                    <code class="number">b'sample bytes'</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_module',
            content_ends_before='sample_int',
        )

    def test_int_display(self):
        """Verify dumping a "int" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_int</span>
                    </span>:
                    <span class="type" title="int">int</span>
                    <code class="number">42</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_bytes',
            content_ends_before='sample_float',
        )

    def test_float_display(self):
        """Verify dumping a "float" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_float</span>
                    </span>:
                    <span class="type" title="float">float</span>
                    <code class="number">42.42</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_int',
            content_ends_before='sample_decimal',
        )

    def test_decimal_display(self):
        """Verify dumping a "decimal" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_decimal</span>
                    </span>:
                    <span class="type" title="Decimal">Decimal</span>
                    <code class="number">42.4200000000000017053025658242404460906982421875</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_float',
            content_ends_before='sample_string',
        )

    def test_string_display(self):
        """Verify dumping a "string" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_string</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Sample String Content'</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_decimal',
            content_ends_before='sample_none',
        )

    def test_none_display(self):
        """Verify dumping a "None" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_none</span>
                    </span>:
                    <span class="type" title="null">null</span>
                    <code class="none">None</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_string',
            content_ends_before='sample_bool',
        )

    def test_bool_display(self):
        """Verify dumping a "bool" type has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_bool</span>
                    </span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_none',
            content_ends_before='done',
        )

    # # TODO: Finish this test. May require more work with django to test.
    # # def test_dd_for_bound_field(self):
    # #     response = self.client.get('/simple?type=bound_field')
    # #     expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_bound</span></span>: <code class="bound">?????</code>'
    # #     self.assertContains(response, expected, html=True)
