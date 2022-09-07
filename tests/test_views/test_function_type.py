"""
Tests for "function" type DD output.
"""

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


@override_settings(DEBUG=True)
class DumpDieViewFunctionTestCase(IntegrationTestCase):
    """Verify handling of dumped function types."""
    url = 'django_dump_die:function-example'

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
                        <span class="string">'Displaying example of function object output.'</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Displaying example of function object output.'</code>
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
            content_ends_before='<span class="string">\'Function examples:\'</span>',
        )

    def test_basic_func_display(self):
        """Verify dumping a "basic function" type (no args) has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_function" title="Dumped Function">
                        <span class="function">sample_func</span>
                        <span class="braces">(</span>
                        <span class="braces">)</span>
                    </span>:
                    <span class="docs">Sample doc string</span>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='Function examples:',
            content_ends_before='sample_func_param',
        )

    def test_func_with_args_display(self):
        """Verify dumping a "function" type (with args/kwargs) has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_function" title="Dumped Function">
                        <span class="function">sample_func_param</span><span class="braces">(</span>
                        <span class="params">param1</span><span class="params">,</span>
                        <span class="params">*</span>
                        <span class="params">args</span>
                        <span class="params">,</span>
                        <span class="params">some_kwarg</span>
                        <span class="params">=</span>
                        <span class="params">None</span>
                        <span class="params">,</span>
                        <span class="params">**</span>
                        <span class="params">kwargs</span>
                        <span class="braces">)</span>
                    </span>:
                    <span class="docs">Sample param doc string. :param param1: Doc for param1.</span>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='sample_func',
            content_ends_before='Function call examples:',
        )

    def test_basic_func_call_display(self):
        """Verify dumping a called "basic function" type (no args) has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="function">sample_func</span>
                        <span class="braces">(</span>
                        <span class="braces">)</span>
                    </span>:
                    <span class="type" title="int">int</span>
                    <code class="number">42</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after='Function call examples:',
            content_ends_before="""
                <span class="function">sample_func_param</span>
                    <span class="braces">(</span>
                    <span class="number">32</span>
                    <span class="braces">)</span>
                </span>
            """,
        )

    def test_func_call_with_one_arg_display(self):
        """Verify dumping a called "basic function" type (one arg) has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="function">sample_func_param</span>
                            <span class="braces">(</span>
                            <span class="number">32</span>
                            <span class="braces">)</span>
                        </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'MyReturnValue with param1 as: 32'</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after="""
            <span class="function">sample_func</span>
            <span class="braces">(</span>
            <span class="braces">)</span>
            """,
            content_ends_before="""
            <span class="function">sample_func_param</span>
            <span class="braces">(</span>
            <span class="string">'test_param'</span>
            <span class="params">,</span>
            <span class="params">some_kwarg</span>
            <span class="params">=</span>
            <span class="params">True</span>
            <span class="braces">)</span>
            """,
        )

    def test_func_call_with_args_kwargs_display(self):
        """Verify dumping a called function type (with args & kwargs) has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="function">sample_func_param</span>
                        <span class="braces">(</span>
                        <span class="string">'test_param'</span>
                        <span class="params">,</span>
                        <span class="params">some_kwarg</span>
                        <span class="params">=</span>
                        <span class="params">True</span>
                        <span class="braces">)</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'MyReturnValue with param1 as: test_param'</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after="""
            <span class="function">sample_func_param</span>
            <span class="braces">(</span>
            <span class="number">32</span>
            <span class="braces">)</span>
            """,
            content_ends_before="""
            <span class="function">sample_func_param</span>
            <span class="braces">(</span>
            <span class="string">'test_param'</span>
            <span class="params">,</span>
            <span class="string">'extra_arg_1'</span>
            <span class="params">,</span>
            <span class="number">2</span>
            <span class="params">,</span>
            <span class="params">True</span>
            <span class="braces">)</span>
            """,
        )

    def test_func_call_with_multiple_args_display(self):
        """Verify dumping a called function type (with multiple args) has expected output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="function">sample_func_param</span>
                        <span class="braces">(</span>
                        <span class="string">'test_param'</span>
                        <span class="params">,</span>
                        <span class="string">'extra_arg_1'</span>
                        <span class="params">,</span>
                        <span class="number">2</span>
                        <span class="params">,</span>
                        <span class="params">True</span>
                        <span class="braces">)</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'MyReturnValue with param1 as: test_param'</code>
                </div>
                """,
                '<hr>',
            ],
            content_starts_after="""
            <span class="dumped_object" title="Dumped Object">
                <span class="function">sample_func_param</span>
                <span class="braces">(</span>
                <span class="string">'test_param'</span>
                <span class="params">,</span>
                <span class="params">some_kwarg</span>
                <span class="params">=</span>
                <span class="params">True</span>
                <span class="braces">)</span>
            </span>
            """,
            content_ends_before='done',
        )
