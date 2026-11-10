"""
Tests for general DD functionality.
"""

# System Imports.
import re
from unittest.mock import patch

# Third-Party Imports.
from django.template import Context, Template
from django.test import override_settings
from django.urls import reverse
from django_expanded_test_cases import IntegrationTestCase

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import dump


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

    @override_settings(DEBUG=True)
    def test_break_is_shown_between_dumps(self):
        """Verify dump.br() shows a break between the objects dumped before and after it."""
        content = self.client.get(reverse("django_dump_die__tests__general:break")).content.decode("utf-8")

        before = content.index("Before the break.")
        dump_break = content.index('<div class="dump-wrapper dump-break dump-break-dashed" title="Break"></div>')
        after = content.index("After the break.")
        self.assertLess(before, dump_break)
        self.assertLess(dump_break, after)

    @override_settings(DEBUG=False)
    def test_break_does_nothing_when_debug_is_off(self):
        """Verify dump.br() adds nothing to the dumped objects when debug is off."""
        middleware.dump_objects.clear()

        dump.br()

        self.assertEqual(middleware.dump_objects, [])

    @override_settings(DEBUG=True)
    def test_break_style_setting(self):
        """Verify each break style gives its class."""
        url = reverse("django_dump_die__tests__general:break")
        for style in ("dashed", "solid", "dotted", "blank"):
            with self.subTest(style=style):
                with override_settings(DJANGO_DD_BREAK_STYLE=style):
                    content = self.client.get(url).content.decode("utf-8")

                self.assertIn('class="dump-wrapper dump-break dump-break-{0}"'.format(style), content)

    @override_settings(DEBUG=True)
    def test_unknown_break_style_setting_raises_an_error(self):
        """Verify a break style that isn't one of the documented styles raises an error."""
        with override_settings(DJANGO_DD_BREAK_STYLE="wavy"):
            with self.assertRaisesMessage(ValueError, "DJANGO_DD_BREAK_STYLE must be one of"):
                self.client.get(reverse("django_dump_die__tests__general:break"))

    @override_settings(DEBUG=True)
    def test_break_size_sets_the_height(self):
        """Verify dump.br(size=...) sets each break's height in lines."""
        content = self.client.get(reverse("django_dump_die__tests__general:break_sizes")).content.decode("utf-8")
        breaks = re.findall(
            r'<div class="dump-wrapper dump-break dump-break-dashed"([^>]*) title="Break"></div>', content
        )
        # A size 1 break needs no height of its own.
        self.assertEqual(breaks, ["", ' style="--dump-break-size: 2"', ' style="--dump-break-size: 5"'])

    @override_settings(DEBUG=True)
    def test_break_size_setting_sets_the_default_height(self):
        """Verify DJANGO_DD_BREAK_SIZE sets the height of breaks that have no size of their own."""
        with override_settings(DJANGO_DD_BREAK_SIZE=3):
            content = self.client.get(reverse("django_dump_die__tests__general:break")).content.decode("utf-8")
        self.assertIn('class="dump-wrapper dump-break dump-break-dashed" style="--dump-break-size: 3"', content)

    @override_settings(DEBUG=True)
    def test_invalid_break_size_setting_raises_an_error(self):
        """Verify a DJANGO_DD_BREAK_SIZE that isn't a whole number of lines raises an error."""
        for size in (0, "2", True):
            with self.subTest(setting=size):
                with override_settings(DJANGO_DD_BREAK_SIZE=size):
                    with self.assertRaisesMessage(ValueError, "DJANGO_DD_BREAK_SIZE must be a whole number of lines"):
                        self.client.get(reverse("django_dump_die__tests__general:break"))

    def test_break_with_an_invalid_size_raises_an_error(self):
        """Verify dump.br() refuses a size that isn't a whole number of lines, whether debug is on or off."""
        for debug in (True, False):
            for size in (0, -1, 2.5, "2", True):
                with self.subTest(debug=debug, size=size), override_settings(DEBUG=debug):
                    with self.assertRaisesMessage(ValueError, "dump.br() size must be a whole number of lines"):
                        dump.br(size=size)
        middleware.dump_objects.clear()

    @override_settings(DEBUG=True)
    def test_custom_color_theme_keys_each_set_their_own_color(self):
        """Verify each documented color theme key, set on its own, colors its own element and nothing is left empty."""
        url = reverse("django_dump_die__tests__general:dd_only")
        theme_keys = {
            "meta": {
                "arrow": ".arrow",
                "access_modifier": ".access-modifier",
                "braces": ".braces",
                "empty": ".empty",
                "location": ".location",
                "type": ".type",
                "unique": ".unique",
            },
            "identifiers": {
                "section_name": ".section_name",
                "attribute": ".attribute",
                "constant": ".constant",
                "dumped_name": ".dumped_name",
                "function": ".function",
                "index": ".index",
                "key": ".key",
                "params": ".params",
                "decorator": ".decorator",
                "class_attribute": ".class_attribute",
            },
            "types": {
                "bool": ".bool",
                "bound": ".bound",
                "default": ".default",
                "docs": ".docs",
                "intermediate": ".intermediate",
                "module": ".module",
                "none": ".none",
                "number": ".number",
                "string": ".string",
            },
        }
        for group, keys in theme_keys.items():
            for key, selector in keys.items():
                with self.subTest(key=f"{group}.{key}"):
                    with override_settings(DJANGO_DD_COLOR_SCHEME={group: {key: "#123456"}}):
                        content = self.client.get(url).content.decode("utf-8")

                    self.assertRegex(content, re.escape(selector) + r" \{\s*color: #123456;")
                    self.assertNotRegex(content, r"color: ;")

    @override_settings(DEBUG=True)
    def test_forced_themes_use_their_default_class_attribute_color(self):
        """Verify the forced light and dark themes each have their own default class attribute color."""
        url = reverse("django_dump_die__tests__general:dd_only")
        for forced_setting, default_color in (
            ("DJANGO_DD_FORCE_LIGHT_THEME", "#93a1a1"),
            ("DJANGO_DD_FORCE_DARK_THEME", "#586e75"),
        ):
            with self.subTest(setting=forced_setting):
                with override_settings(**{forced_setting: True}):
                    content = self.client.get(url).content.decode("utf-8")
                forced_part = content[content.index("/* Forcing color themes */") :]
                self.assertRegex(forced_part, r"\.class_attribute \{\s*color: " + default_color)

    @override_settings(DEBUG=True)
    def test_forced_themes_use_the_custom_class_attribute_color(self):
        """Verify the forced light and dark themes use the color theme's class attribute color."""
        url = reverse("django_dump_die__tests__general:dd_only")
        theme = {"identifiers": {"class_attribute": "#123456"}}
        for forced_setting in ("DJANGO_DD_FORCE_LIGHT_THEME", "DJANGO_DD_FORCE_DARK_THEME"):
            with self.subTest(setting=forced_setting):
                with override_settings(**{forced_setting: True, "DJANGO_DD_COLOR_SCHEME": theme}):
                    content = self.client.get(url).content.decode("utf-8")
                forced_part = content[content.index("/* Forcing color themes */") :]
                self.assertRegex(forced_part, r"\.class_attribute \{\s*color: #123456")

    @override_settings(DEBUG=True)
    def test_forced_themes_use_the_custom_params_color(self):
        """Verify the forced light and dark themes use the color theme's params color."""
        url = reverse("django_dump_die__tests__general:dd_only")
        for forced_setting in ("DJANGO_DD_FORCE_LIGHT_THEME", "DJANGO_DD_FORCE_DARK_THEME"):
            with self.subTest(setting=forced_setting):
                settings = {forced_setting: True, "DJANGO_DD_COLOR_SCHEME": {"identifiers": {"params": "#123456"}}}
                with override_settings(**settings):
                    content = self.client.get(url).content.decode("utf-8")

                forced_part = content[content.index("/* Forcing color themes */") :]
                self.assertRegex(forced_part, r"\.params \{\s*color: #123456")

    @override_settings(DEBUG=True)
    def test_custom_color_theme_sets_the_decorator_color(self):
        """Verify the method and property markers use the theme's decorator color, and only that color."""
        url = reverse("django_dump_die__tests__general:dd_only")
        decorator_rule = re.compile(r"\.decorator \{\s*color: #123456;")

        with override_settings(DJANGO_DD_COLOR_SCHEME={"identifiers": {"decorator": "#123456"}}):
            content = self.client.get(url).content.decode("utf-8")
        self.assertRegex(content, decorator_rule)

        # A custom type color doesn't change the decorators, which keep their default color.
        with override_settings(DJANGO_DD_COLOR_SCHEME={"meta": {"type": "#123456"}}):
            content = self.client.get(url).content.decode("utf-8")
        self.assertNotRegex(content, decorator_rule)
        self.assertNotIn(".decorator", content)

    @override_settings(DEBUG=True)
    def test_dump_page_and_template_dumps_do_not_load_bootstrap(self):
        """Verify neither the dump page nor the dump template tag loads Bootstrap or jQuery."""
        for url_name in ("django_dump_die__tests__general:dd_only", "django_dump_die:template-dump-example"):
            with self.subTest(url=url_name):
                content = self.client.get(reverse(url_name)).content.decode("utf-8").lower()

                self.assertNotIn("bootstrap", content)
                self.assertNotIn("jquery", content)
                self.assertIn("django_dump_die/css/dd.css", content)

    @override_settings(DEBUG=True)
    def test_dump_without_a_dd_still_shows_dump_view(self):
        """Verify that only using dump and no dd still shows the dump view."""
        self.assertGetResponse(
            "django_dump_die__tests__general:dump_only",
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=["Dumped without dd."],
            expected_not_content=["<p>Sample page body content</p>"],
        )

    @override_settings(DEBUG=True, DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE=True)
    def test_dump_shows_above_the_page_when_turned_on(self):
        """Verify dumps are shown above the page's own content, and the page is kept, when the setting is on."""
        response = self.assertGetResponse(
            "django_dump_die__tests__general:dump_only",
            expected_title="Sample page",
            expected_content=[
                '<div class="dump-die-above-page">',
                "Django DumpDie",
                "Dumped without dd.",
                "<h1>Sample page</h1>",
                "<p>Sample page body content</p>",
            ],
        )
        content = response.content.decode("utf-8")
        self.assertIn("django_dump_die/css/dd.css", content[: content.index("</head>")])

    @override_settings(DEBUG=True, DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE=True)
    def test_dd_still_replaces_the_page_when_dumps_are_shown_above_it(self):
        """Verify dd() still shows the dump page, since it stops the view before there is a page."""
        self.assertGetResponse(
            "django_dump_die__tests__general:dd_only",
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=["Only dd, without dumps."],
            expected_not_content=['<div class="dump-die-above-page">'],
        )

    @override_settings(DEBUG=True)
    def test_dd_without_any_dumps_still_shows_dump_view(self):
        """Verify that only using dd and no dumps still shows the dump view."""
        self.assertGetResponse(
            "django_dump_die__tests__general:dd_only",
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=["Only dd, without dumps."],
        )

    @override_settings(DEBUG=True, DJANGO_DD_FORCE_LIGHT_THEME=True, DJANGO_DD_FORCE_DARK_THEME=True)
    def test_forcing_both_light_and_dark_themes_raises_an_error(self):
        """Verify the dump page refuses settings that force both the light and the dark theme."""
        with self.assertRaisesMessage(ValueError, "You can't force both light and dark themes."):
            self.client.get(reverse("django_dump_die__tests__general:dd_only"))

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
    def test_template_dumps_load_css_and_js_once_per_page(self):
        """Verify several template dumps on one page only include the dump css and js once."""
        template = Template("{% load dump_die %}{% dump first %}{% dump second %}")

        content = template.render(Context({"first": 1, "second": 2}))

        self.assertEqual(content.count('class="dump-wrapper"'), 2)
        self.assertEqual(content.count("django_dump_die/css/dd.css"), 1)

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
                        data-dd-toggle="collapse"
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

    @override_settings(DEBUG=True)
    def test_dumping_a_queryset_whose_query_fails_shows_the_error(self):
        """Verify a QuerySet whose query raises a database error is dumped with the error, not a crash."""
        # Uses the test client directly: assertGetResponse's debug output prints the response context, which would
        # run the failing query itself.
        response = self.client.get(reverse("django_dump_die__tests__general:database_error"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn('<span class="type" title="QuerySet">QuerySet</span>', content)
        self.assertIn("Exception Type: OperationalError", content)
        self.assertIn("no such table: django_dump_die_samplerelation", content)

    @override_settings(DEBUG=True)
    def test_unhandled_exception_shows_dumps_on_the_error_page(self):
        """Verify an unrelated unhandled exception is not caught, and earlier dumps are added to its error page."""
        self.client.raise_request_exception = False

        response = self.client.get(reverse("django_dump_die:unhandled-exception-case-example"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 500)
        self.assertIn("This is a test type error", content)
        self.assertIn('<div class="dump-toolbar">', content)
        self.assertIn('<span class="dumped_name">exception_obj</span>', content)

    @override_settings(DEBUG=False)
    def test_debug_off_leaves_unhandled_exception_error_page_unchanged(self):
        """Verify the error page of an unhandled exception gets no dump output when debug is off."""
        self.client.raise_request_exception = False

        response = self.client.get(reverse("django_dump_die:unhandled-exception-case-example"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 500)
        self.assertIn("<h1>Server Error (500)</h1>", content)
        self.assertNotIn("dump-toolbar", content)
        self.assertNotIn("django_dump_die", content)

    @patch("django_dump_die.templatetags.dump_die._generate_unique")
    @override_settings(DEBUG=True)
    def test_dumping_of_object_that_causes_an_exception_does_not_crash_dump_functionality(
        self,
        mocked_unique_generation,
    ):
        """Test dumping of object that causes an exception does not crash dump functionality"""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f"data_900{index}", ""),
            ]
        mocked_unique_generation.side_effect = side_effects

        url = "django_dump_die:obj-inspection-exception-case-example"

        self.assertGetResponse(
            url,
            expected_title="DD",
            expected_header="Django DumpDie",
            expected_content=[
                # Check page descriptor.
                """
                <div class="dump-wrapper dump-break dump-break-dashed" title="Break"></div>
                """,
                "<hr>",
                # Check visual-padding lines.
                """
                <div class="dump-wrapper">
                <span class="dumped_object" title="Dumped Object">
                    <span class="dumped_name">exception_obj</span>
                </span>:
                <span class="type" title="ExceptionObject">ExceptionObject</span>
                <span class="braces">{</span>
                <a
                    class="arrow-toggle collapsed"
                    title="[Ctrl+click] Expand all children"
                    data-dd-toggle="collapse"
                    data-target=".data_9000"
                    data-dd-type="type"
                    data-object-depth="1"
                    aria-label="Close"
                    aria-expanded="false"
                >
                    <span class="unique" data-highlight-unique="data_9000">data_9000</span>
                    <span id="arrow-data_9000" class="arrow arrow-data_9000">
                        ▶
                    </span>
                </a>
                <div
                    class="dd-wrapper collapse data_9000 "
                    data-unique="data_9000"
                >
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
                            <li>
                                <span class="empty" title="Exception Occurred
                                    Exception Type: IndexError
                                    Exception Value: list index out of range
                                    Traceback (most recent call last):
                """,
                # File paths, line numbers and code markers in the traceback depend on the machine and on the Python
                # version. So only check that the frames from this package are there.
                'dump_die.py", line',
                "in get_obj_values",
                "members = get_members(obj, item_range)",
                'utils.py", line',
                "in get_members",
                "members = inspect.getmembers(obj)",
                'example_helpers.py", line',
                "in trigger",
                "return self.my_list[1]",
                """
                                    End of traceback"
                                >
                                    EXCEPTION
                                </span>:
                                <span class="type" title="str">str</span>
                                <code class="string">'list index out of range'</code>
                            </li>
                        </div>
                    </ul>
                    <ul class="attribute-list">
                    </ul>
                </div>
                <span class="braces">}</span>
                """,
                "<hr>",
                """
                <div class="dump-wrapper dump-break dump-break-dashed" title="Break"></div>
                """,
                "<hr>",
            ],
            content_starts_after='<div class="static-padding"></div>',
            content_ends_before="done",
        )
