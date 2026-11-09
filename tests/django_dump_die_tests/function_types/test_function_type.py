"""
Tests for dumped functions and dumped function call results, each with its own view.

A function with a docstring is shown with its parameters and docstring. Without a docstring, it's dumped as an object.
"""

# System Imports.
from unittest.mock import patch

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase

UNIQUE = "data_9001"


@override_settings(DEBUG=True)
@patch("django_dump_die.templatetags.dump_die._generate_unique", side_effect=[(UNIQUE, "")] * 5000)
class DumpDieFunctionTypeTestCase(IntegrationTestCase):
    """Verify handling of dumped functions, and of dumped function call results."""

    def assertDump(self, url_name, expected):
        """Assert that a view's dump page shows the expected dump, before the final "done" dump."""
        self.assertGetResponse(
            "django_dump_die__tests__function:" + url_name,
            expected_title="DD",
            expected_header="Django DumpDie",
            content_starts_after="<!--Start Main Content-->",
            expected_content=[expected, "<hr>"],
            content_ends_before='<span class="string">"done"</span>',
        )

    def test_function_display(self, _mocked_unique):
        """Verify a function without parameters shows its name, empty parentheses, and its docstring."""
        self.assertDump(
            "function__basic",
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
        )

    def test_function_with_params_display(self, _mocked_unique):
        """Verify a function with parameters shows each of them, and its docstring on one line."""
        self.assertDump(
            "function__with_params",
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
        )

    def test_function_without_docstring_display(self, _mocked_unique):
        """Verify a function without a docstring is dumped as an object, without being called."""
        self.assertDump(
            "function__no_docstring",
            """
            <div class="dump-wrapper">
                <span class="dumped_object" title="Dumped Object">
                    <span class="function">no_docstring</span><span class="braces">(</span><span class="braces">)</span>
                </span>:
                <span class="type" title="function">function</span>
                <span class="braces">{</span>
            """,
        )

    def test_lambda_display(self, _mocked_unique):
        """Verify a lambda, which has no docstring, is dumped as an object, without being called."""
        self.assertDump(
            "function__lambda",
            """
            <div class="dump-wrapper">
                <span class="dumped_object" title="Dumped Object">
                    <span class="function">sample_lambda</span><span class="braces">(</span>
                    <span class="params">value</span><span class="braces">)</span>
                </span>:
                <span class="type" title="function">function</span>
                <span class="braces">{</span>
            """,
        )

    def test_bound_method_display(self, _mocked_unique):
        """Verify a method of an object shows the object's name, the method's name without self, and its docs."""
        self.assertDump(
            "function__bound_method",
            """
            <div class="dump-wrapper">
                <span class="dumped_function" title="Dumped Function">
                    <span class="dumped_name">sample_object</span><span class="dumped_name">.</span>
                    <span class="function">sample_class_func</span>
                    <span class="braces">(</span><span class="braces">)</span>
                </span>:
                <span class="docs">Sample class func doc string</span>
            </div>
            """,
        )

    def test_builtin_function_display(self, _mocked_unique):
        """Verify a built-in function shows its parameters and its docstring."""
        self.assertDump(
            "function__builtin",
            """
            <div class="dump-wrapper">
                <span class="dumped_function" title="Dumped Function">
                    <span class="function">len</span><span class="braces">(</span>
                    <span class="params">obj</span><span class="params">,</span><span class="params">/</span>
                    <span class="braces">)</span>
                </span>:
                <span class="docs">Return the number of items in a container.</span>
            </div>
            """,
        )

    def test_function_call_display(self, _mocked_unique):
        """Verify the result of a call without arguments is shown, named by the call."""
        self.assertDump(
            "function__call",
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
        )

    def test_function_call_with_one_arg_display(self, _mocked_unique):
        """Verify the result of a call with one argument is shown, named by the call and its argument."""
        self.assertDump(
            "function__call_with_one_arg",
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
        )

    def test_function_call_with_kwarg_display(self, _mocked_unique):
        """Verify the result of a call with an argument and a keyword argument is shown, named by the call."""
        self.assertDump(
            "function__call_with_kwarg",
            """
            <div class="dump-wrapper">
                <span class="dumped_object" title="Dumped Object">
                    <span class="function">sample_func_param</span>
                    <span class="braces">(</span>
                    <span class="string">"test_param"</span>
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
        )

    def test_function_call_with_args_display(self, _mocked_unique):
        """Verify the result of a call with several arguments is shown, named by the call and its arguments."""
        self.assertDump(
            "function__call_with_args",
            """
            <div class="dump-wrapper">
                <span class="dumped_object" title="Dumped Object">
                    <span class="function">sample_func_param</span>
                    <span class="braces">(</span>
                    <span class="string">"test_param"</span>
                    <span class="params">,</span>
                    <span class="string">"extra_arg_1"</span>
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
        )
