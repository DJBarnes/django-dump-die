"""
Tests for "complex" type DD output.
"""

# System Imports.
from unittest.mock import patch

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


@override_settings(DEBUG=True)
class DumpDieComplexTypeTestCase(IntegrationTestCase):
    """Verify handling of dumped "complex" types."""
    url = 'django_dump_die:complex-type-example'

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
        """Test initial page descriptor output."""
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
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
            content_ends_before='Minimal object examples:',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_set_display(self, mocked_unique_generation):
        """Verify dumping a "set" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__set'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        # Test initial object display.
        # Note that sets are technically unordered, so we verify the general output,
        # and then use a separate unordered test to verify the child elements.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_set</span>
                    </span>:
                    <span class="type" title="set">set:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                # Note that we check for the presence of the general element, but not the direct values.
                # Sets are unordered, so these child values may appear in any ordering.
                """
                <li>
                    <span class="type" title="str">str</span>
                    <code class="string">""", """</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span>
                    <code class="string">""", """</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span>
                    <code class="string">""", """</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Set object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

        # Test child elements.
        # Due to unique generation mocking, new response starts where last one ended, so numbers are different.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                # Object child elements.
                """
                <li>
                    <span class="type" title="str">str</span> <code class="string">'A'</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span> <code class="string">'B'</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span> <code class="string">'C'</code>
                </li>
                """,
            ],
            content_starts_after="""
            <div
                class="li-wrapper collapse data_90011-attributes show"
                data-unique-attributes="data_90011-attributes"
            >
            """,
            content_ends_before="""
                                </div>
                            </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                <span class="braces">}</span>
            </div>
            """,
            ignore_content_ordering=True,
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_frozen_set_display(self, mocked_unique_generation):
        """Verify dumping a "frozen set" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__frozen_set'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        # Test initial object display.
        # Note that sets are technically unordered, so we verify the general output,
        # and then use a separate unordered test to verify the child elements.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_frozen_set</span>
                    </span>:
                    <span class="type" title="frozenset">frozenset:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                # Note that we check for the presence of the general element, but not the direct values.
                # Sets are unordered, so these child values may appear in any ordering.
                """
                <li>
                    <span class="type" title="str">str</span>
                    <code class="string">""", """</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span>
                    <code class="string">""", """</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span>
                    <code class="string">""", """</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" FrozenSet object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

        # Test child elements.
        # Due to unique generation mocking, new response starts where last one ended, so numbers are different.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                # Object child elements.
                """
                <li>
                    <span class="type" title="str">str</span> <code class="string">'D'</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span> <code class="string">'F'</code>
                </li>
                """,
                """
                <li>
                    <span class="type" title="str">str</span> <code class="string">'E'</code>
                </li>
                """,
            ],
            content_starts_after="""
            <div
                class="li-wrapper collapse data_90011-attributes show"
                data-unique-attributes="data_90011-attributes"
            >
            """,
            content_ends_before="""
                                </div>
                            </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                <span class="braces">}</span>
            </div>
            """,
            ignore_content_ordering=True,
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_tuple_display(self, mocked_unique_generation):
        """Verify dumping a "tuple" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__tuple'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_tuple</span>
                    </span>:
                    <span class="type" title="tuple">tuple:3</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'A'</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">12</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">2</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">)</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Tuple object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_list_display(self, mocked_unique_generation):
        """Verify dumping a "list" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__list'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_list</span>
                    </span>:
                    <span class="type" title="list">list:3</span>
                    <span class="braces">[</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'A'</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">12</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">2</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">]</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" List object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dict_display(self, mocked_unique_generation):
        """Verify dumping a "dict" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__dict'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_dict</span>
                    </span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="key" title="Key">'first'</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'A'</code>
                </li>
                <li>
                    <span class="key" title="Key">'second'</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">12</code>
                </li>
                <li>
                    <span class="key" title="Key">'third'</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Dict object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_querydict_display(self, mocked_unique_generation):
        """Verify dumping a "querydict" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__querydict'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_querydict</span>
                    </span>:
                    <span class="type" title="QueryDict">QueryDict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="key" title="Key">'first'</span>:
                    <span class="type" title="list">list:3</span>
                    <span class="braces">[</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9004"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9004">data_9004</span>
                        <span id="arrow-data_9004" class="arrow arrow-data_9004">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9004 " data-unique="data_9004">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9004-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9004-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9004-attributes show"
                                data-unique-attributes="data_9004-attributes"
                            >
                                <li>
                                    <span class="index" title="Index">0</span>:
                                    <span class="type" title="str">str</span> <code class="string">'"A"'</code>
                                </li>
                                <li>
                                    <span class="index" title="Index">1</span>:
                                    <span class="type" title="str">str</span> <code class="string">'"B"'</code>
                                </li>
                                <li>
                                    <span class="index" title="Index">2</span>:
                                    <span class="type" title="str">str</span> <code class="string">'"C"'</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">]</span>
                </li>
                """,
                """
                <li>
                    <span class="key" title="Key">'second'</span>:
                    <span class="type" title="list">list:1</span>
                    <span class="braces">[</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9008"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9008">data_9008</span>
                        <span id="arrow-data_9008" class="arrow arrow-data_9008">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9008 " data-unique="data_9008">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9008-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                            <span class="section_name">Attributes</span>
                            <span id="arrow-data_9008-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9008-attributes show"
                                data-unique-attributes="data_9008-attributes"
                            >
                                <li>
                                    <span class="index" title="Index">0</span>:
                                    <span class="type" title="str">str</span> <code class="string">'12'</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">]</span>
                </li>
                """,
                """
                <li>
                    <span class="key" title="Key">'third'</span>:
                    <span class="type" title="list">list:1</span>
                    <span class="braces">[</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90010"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90010">data_90010</span>
                        <span id="arrow-data_90010" class="arrow arrow-data_90010">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90010 " data-unique="data_90010">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90010-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90010-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90010-attributes show"
                                data-unique-attributes="data_90010-attributes"
                            >
                                <li>
                                    <span class="index" title="Index">0</span>:
                                    <span class="type" title="str">str</span> <code class="string">'True'</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">]</span>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" QueryDict object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_memory_view_display(self, mocked_unique_generation):
        """Verify dumping a "memory view" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__memory_view'

        # NOTE: Due to nesting of child-elements, this is a very large test.
        #   I'm unsure if there is value in testing literally every sub-element. Particularly given
        #   how large/long it makes this test overall.

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">sample_memory_view</span>
                    </span>:
                    <span class="type" title="memoryview">memoryview</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">c_contiguous</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">contiguous</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">f_contiguous</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">format</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'B'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">itemsize</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">1</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">nbytes</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">4</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">ndim</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">1</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">obj</span>:
                    <span class="type" title="bytearray">bytearray</span>
                    <code class="intermediate">bytearray(b'\\x08\\t\\n\\x0b')</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90010"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90010">data_90010</span>
                        <span id="arrow-data_90010" class="arrow arrow-data_90010">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90010 " data-unique="data_90010">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90010-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90010-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90010-attributes show"
                                data-unique-attributes="data_90010-attributes"
                            >
                                <li>
                                    <span class="index" title="Index">0</span>:
                                    <span class="type" title="int">int</span>
                                    <code class="number">8</code>
                                </li>
                                <li>
                                    <span class="index" title="Index">1</span>:
                                    <span class="type" title="int">int</span>
                                    <code class="number">9</code>
                                </li>
                                <li>
                                    <span class="index" title="Index">2</span>:
                                    <span class="type" title="int">int</span>
                                    <code class="number">10</code>
                                </li>
                                <li>
                                    <span class="index" title="Index">3</span>:
                                    <span class="type" title="int">int</span>
                                    <code class="number">11</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">readonly</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">False</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">shape</span>:
                    <span class="type" title="tuple">tuple:1</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90016"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90016">data_90016</span>
                        <span id="arrow-data_90016" class="arrow arrow-data_90016">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90016 " data-unique="data_90016">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90016-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90016-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90016-attributes show"
                                data-unique-attributes="data_90016-attributes"
                            >
                                <li>
                                    <span class="index" title="Index">0</span>:
                                    <span class="type" title="int">int</span>
                                    <code class="number">4</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">strides</span>:
                    <span class="type" title="tuple">tuple:1</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90018"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90018">data_90018</span>
                        <span id="arrow-data_90018" class="arrow arrow-data_90018">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90018 " data-unique="data_90018">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90018-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90018-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90018-attributes show"
                                data-unique-attributes="data_90018-attributes"
                            >
                                <li>
                                    <span class="index" title="Index">0</span>:
                                    <span class="type" title="int">int</span>
                                    <code class="number">1</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">suboffsets</span>:
                    <span class="type" title="tuple">tuple:0</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90020"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90020">data_90020</span>
                        <span id="arrow-data_90020" class="arrow arrow-data_90020">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90020 " data-unique="data_90020">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90020-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90020-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90020-attributes show"
                                data-unique-attributes="data_90020-attributes"
                            >
                                <span class="empty" title="No Attributes">No Attributes</span>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">8</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">9</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">2</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">10</code>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">3</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">11</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" MemoryView object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_enum_display(self, mocked_unique_generation):
        """Verify dumping a "list" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__enum'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">SampleEnum</span>
                    </span>:
                    <span class="type" title="Enum">Enum</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="constant" title="Constant">BLUE</span>:
                    <span class="type" title="SampleEnum">SampleEnum</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9003"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9003">data_9003</span>
                        <span id="arrow-data_9003" class="arrow arrow-data_9003">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9003 " data-unique="data_9003">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9003-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9003-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9003-attributes show"
                                data-unique-attributes="data_9003-attributes"
                            >
                                <li>
                                    <span class="access-modifier">+</span>
                                    <span class="attribute" title="Attribute">name</span>:
                                    <span class="type" title="str">str</span> <code class="string">'BLUE'</code>
                                </li>
                                <li>
                                    <span class="access-modifier">+</span>
                                    <span class="attribute" title="Attribute">value</span>:
                                    <span class="type" title="int">int</span> <code class="number">2</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="constant" title="Constant">RED</span>:
                    <span class="type" title="SampleEnum">SampleEnum</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9006"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9006">data_9006</span>
                        <span id="arrow-data_9006" class="arrow arrow-data_9006">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9006 " data-unique="data_9006">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9006-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9006-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9006-attributes show"
                                data-unique-attributes="data_9006-attributes"
                            >
                                <li>
                                    <span class="access-modifier">+</span>
                                    <span class="attribute" title="Attribute">name</span>:
                                    <span class="type" title="str">str</span> <code class="string">'RED'</code>
                                </li>
                                <li>
                                    <span class="access-modifier">+</span>
                                    <span class="attribute" title="Attribute">value</span>:
                                    <span class="type" title="int">int</span> <code class="number">1</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Enum object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_multilevel_set_display(self, mocked_unique_generation):
        """Verify dumping a multi-level "set" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__multi_level__set'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        # Test initial object display.
        # Note that sets are technically unordered, so we verify the general output,
        # and then use a separate unordered test to verify the child elements.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_set</span>
                    </span>:
                    <span class="type" title="set">set:2</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                # Note that we check for the presence of the general element, but not the direct values.
                # Sets are unordered, so these child values may appear in any ordering.
                """
                <li>
                    <span class="type" title="tuple">tuple:3</span>
                    <span class="braces">(</span>
                    <a
                """,
                """
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,
                """
                <li>
                    <span class="type" title="tuple">tuple:3</span>
                    <span class="braces">(</span>
                    <a
                """,
                """
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Multi-Level Set object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

        # Test child elements.
        # Due to unique generation mocking, new response starts where last one ended, so numbers are different.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                # Object child elements.
                # Due to being unordered, we have to verify opening tags and actual child content separately.
                """
                <li>
                    <span class="type" title="tuple">tuple:3</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90017"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90017">data_90017</span>
                        <span id="arrow-data_90017" class="arrow arrow-data_90017">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90017 " data-unique="data_90017">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90017-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90017-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90017-attributes show"
                                data-unique-attributes="data_90017-attributes"
                            >
                """,
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="str">str</span> <code class="string">'B'</code>
                </li>
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="int">int</span> <code class="number">24</code>
                </li>
                <li>
                    <span class="index" title="Index">2</span>:
                    <span class="type" title="bool">bool</span> <code class="bool">False</code>
                </li>
                """,
                """
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,
                """
                <li>
                    <span class="type" title="tuple">tuple:3</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90021"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90021">data_90021</span>
                        <span id="arrow-data_90021" class="arrow arrow-data_90021">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90021 " data-unique="data_90021">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90021-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90021-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90021-attributes show"
                                data-unique-attributes="data_90021-attributes"
                            >
                """,
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="str">str</span> <code class="string">'A'</code>
                </li>
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="int">int</span> <code class="number">12</code>
                </li>
                <li>
                    <span class="index" title="Index">2</span>:
                    <span class="type" title="bool">bool</span> <code class="bool">True</code>
                </li>
                """,
                """
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">)</span>
                </li>
                """,
            ],
            content_starts_after="""
            <div
                class="li-wrapper collapse data_90016-attributes show"
                data-unique-attributes="data_90016-attributes"
            >
            """,
            content_ends_before="""
                                </div>
                            </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                <span class="braces">}</span>
            </div>
            """,
            ignore_content_ordering=True,
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_multilevel_tuple_display(self, mocked_unique_generation):
        """Verify dumping a multi-level "tuple" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__multi_level__tuple'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_tuple</span>
                    </span>:
                    <span class="type" title="tuple">tuple:2</span>
                    <span class="braces">(</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9003"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9003">data_9003</span>
                        <span id="arrow-data_9003" class="arrow arrow-data_9003">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9003 " data-unique="data_9003">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9003-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9003-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9003-attributes show"
                                data-unique-attributes="data_9003-attributes"
                            >
                                <li>
                                    <span class="key" title="Key">'first'</span>:
                                    <span class="type" title="str">str</span> <code class="string">'A'</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'second'</span>:
                                    <span class="type" title="int">int</span> <code class="number">12</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'third'</span>:
                                    <span class="type" title="bool">bool</span> <code class="bool">True</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9007"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9007">data_9007</span>
                        <span id="arrow-data_9007" class="arrow arrow-data_9007">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9007 " data-unique="data_9007">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9007-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9007-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9007-attributes show"
                                data-unique-attributes="data_9007-attributes"
                            >
                                <li>
                                    <span class="key" title="Key">'fourth'</span>:
                                    <span class="type" title="str">str</span> <code class="string">'B'</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'fifth'</span>:
                                    <span class="type" title="int">int</span> <code class="number">24</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'sixth'</span>:
                                    <span class="type" title="bool">bool</span> <code class="bool">False</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">)</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Multi-Level Tuple object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_multilevel_list_display(self, mocked_unique_generation):
        """Verify dumping a multi-level "list" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__multi_level__list'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_list</span>
                    </span>:
                    <span class="type" title="list">list:2</span>
                    <span class="braces">[</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="index" title="Index">0</span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9003"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9003">data_9003</span>
                        <span id="arrow-data_9003" class="arrow arrow-data_9003">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9003 " data-unique="data_9003">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9003-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9003-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9003-attributes show"
                                data-unique-attributes="data_9003-attributes"
                            >
                                <li>
                                    <span class="key" title="Key">'first'</span>:
                                    <span class="type" title="str">str</span> <code class="string">'A'</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'second'</span>:
                                    <span class="type" title="int">int</span> <code class="number">12</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'third'</span>:
                                    <span class="type" title="bool">bool</span> <code class="bool">True</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,
                """
                <li>
                    <span class="index" title="Index">1</span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9007"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9007">data_9007</span>
                        <span id="arrow-data_9007" class="arrow arrow-data_9007">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9007 " data-unique="data_9007">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9007-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9007-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9007-attributes show"
                                data-unique-attributes="data_9007-attributes"
                            >
                                <li>
                                    <span class="key" title="Key">'fourth'</span>:
                                    <span class="type" title="str">str</span> <code class="string">'B'</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'fifth'</span>:
                                    <span class="type" title="int">int</span> <code class="number">24</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'sixth'</span>:
                                    <span class="type" title="bool">bool</span> <code class="bool">False</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">]</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Multi-Level List object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_multilevel_dict_display(self, mocked_unique_generation):
        """Verify dumping a multi-level "dict" type has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__multi_level__dict'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_dict</span>
                    </span>:
                    <span class="type" title="dict">dict:2</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="key" title="Key">'initial'</span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9003"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9003">data_9003</span>
                        <span id="arrow-data_9003" class="arrow arrow-data_9003">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9003 " data-unique="data_9003">
                    <ul class="attribute-list">
                        <a
                            class="arrow-toggle show always-show"
                            title="[Ctrl+click] Expand all children"
                            data-target=".data_9003-attributes"
                            data-dd-type="attr"
                            aria-label="Open/Close"
                            aria-expanded=""
                        >
                            <span class="section_name">Attributes</span>
                            <span id="arrow-data_9003-attributes" class="arrow"></span>
                        </a>
                        <div
                            class="li-wrapper collapse data_9003-attributes show"
                            data-unique-attributes="data_9003-attributes"
                        >
                            <li>
                                <span class="key" title="Key">'first'</span>:
                                <span class="type" title="str">str</span> <code class="string">'A'</code>
                            </li>
                            <li>
                                <span class="key" title="Key">'second'</span>:
                                <span class="type" title="int">int</span> <code class="number">12</code>
                            </li>
                            <li>
                                <span class="key" title="Key">'third'</span>:
                                <span class="type" title="bool">bool</span> <code class="bool">True</code>
                            </li>
                        </div>
                    </ul>
                    <ul class="attribute-list"></ul></div>
                    <span class="braces">}</span>
                </li>
                """,
                """
                <li>
                    <span class="key" title="Key">'secondary'</span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9007"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                    <span class="unique" data-highlight-unique="data_9007">data_9007</span>
                    <span id="arrow-data_9007" class="arrow arrow-data_9007">
                    ▶
                    </span>
                    </a>
                    <div class="dd-wrapper collapse data_9007 " data-unique="data_9007">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9007-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_9007-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9007-attributes show"
                                data-unique-attributes="data_9007-attributes"
                            >
                                <li>
                                    <span class="key" title="Key">'fourth'</span>:
                                    <span class="type" title="str">str</span> <code class="string">'B'</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'fifth'</span>:
                                    <span class="type" title="int">int</span> <code class="number">24</code>
                                </li>
                                <li>
                                    <span class="key" title="Key">'sixth'</span>:
                                    <span class="type" title="bool">bool</span> <code class="bool">False</code>
                                </li>
                            </div>
                        </ul>
                        <ul class="attribute-list"></ul>
                    </div>
                    <span class="braces">}</span>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Multi-Level Dict object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_list_subitem_display(self, mocked_unique_generation):
        """Verify dumping a "list" type sub-item has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__sub_item__list'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_list</span>
                        <span class="braces">[</span>
                        <span class="number">0</span>
                        <span class="braces">]</span>
                    </span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="key" title="Key">'first'</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'A'</code>
                </li>
                <li>
                    <span class="key" title="Key">'second'</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">12</code>
                </li>
                <li>
                    <span class="key" title="Key">'third'</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" List sub-item object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_tuple_subitem_display(self, mocked_unique_generation):
        """Verify dumping a "tuple" type sub-item has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__sub_item__tuple'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_tuple</span>
                        <span class="braces">[</span>
                        <span class="number">0</span>
                        <span class="braces">]</span>
                    </span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="key" title="Key">'first'</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'A'</code>
                </li>
                <li>
                    <span class="key" title="Key">'second'</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">12</code>
                </li>
                <li>
                    <span class="key" title="Key">'third'</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Tuple sub-item object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_tuple_subitem_func_display(self, mocked_unique_generation):
        """Verify dumping a "tuple" type sub-item function has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__sub_item__tuple_func'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_function" title="Dumped Function">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_tuple</span>
                        <span class="braces">[</span>
                        <span class="number">0</span>
                        <span class="braces">]</span>
                        <span class="dumped_name">.</span>
                        <span class="function">items</span>
                        <span class="braces">(</span>
                        <span class="braces">)</span>
                    </span>:
                """,

                # Object child elements.
                """
                <span class="docs">D.items() -> a set-like object providing a view on D's items</span>
                """,

                # Object closing tags.
                """
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Tuple sub-item function object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dict_subitem_display(self, mocked_unique_generation):
        """Verify dumping a "dict" type sub-item has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__sub_item__dict'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">self</span>
                        <span class="dumped_name">.</span>
                        <span class="dumped_name">sample_multilevel_dict</span>
                        <span class="braces">[</span>
                        <span class="string">'initial'</span>
                        <span class="braces">]</span>
                    </span>:
                    <span class="type" title="dict">dict:3</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="key" title="Key">'first'</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'A'</code>
                </li>
                <li>
                    <span class="key" title="Key">'second'</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">12</code>
                </li>
                <li>
                    <span class="key" title="Key">'third'</span>:
                    <span class="type" title="bool">bool</span>
                    <code class="bool">True</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Dict sub-item object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_enum_subitem_display(self, mocked_unique_generation):
        """Verify dumping a "enum" type sub-item has expected output."""

        # Override url, to use testing-specific view, which will only display a single object.
        self.url = 'django_dump_die_tests:complex__sub_item__enum'

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_900{index}', ''),
            ]
        mocked_unique_generation.side_effect = side_effects

        # For first enum sub-item.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">SampleEnum</span>
                        <span class="dumped_name">.</span>
                        <span class="constant">RED</span>
                    </span>:
                    <span class="type" title="SampleEnum">SampleEnum</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9002"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9002">data_9002</span>
                        <span id="arrow-data_9002" class="arrow arrow-data_9002">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9002 " data-unique="data_9002">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9002-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9002-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9002-attributes show"
                                data-unique-attributes="data_9002-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">name</span>:
                    <span class="type" title="str">str</span> <code class="string">'RED'</code>
                </li>
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">value</span>:
                    <span class="type" title="int">int</span> <code class="number">1</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Enum sub-item object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )

        # For second enum sub-item.
        self.assertGetResponse(
            self.url,
            expected_title='DD',
            expected_header='Django DumpDie',
            expected_content=[
                '<hr>',

                # Object opening tags.
                """
                <div class="dump-wrapper">
                    <span class="dumped_object" title="Dumped Object">
                        <span class="dumped_name">SampleEnum</span>
                        <span class="dumped_name">.</span>
                        <span class="constant">BLUE</span>
                    </span>:
                    <span class="type" title="SampleEnum">SampleEnum</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90016"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90016">data_90016</span>
                        <span id="arrow-data_90016" class="arrow arrow-data_90016">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90016 " data-unique="data_90016">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90016-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_90016-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90016-attributes show"
                                data-unique-attributes="data_90016-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">name</span>:
                    <span class="type" title="str">str</span> <code class="string">'BLUE'</code>
                </li>
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">value</span>:
                    <span class="type" title="int">int</span> <code class="number">2</code>
                </li>
                """,

                # Object closing tags.
                """
                                    </div>
                                </ul>
                            <ul class="attribute-list"></ul>
                        </div>
                    <span class="braces">}</span>
                </div>
                """,

                '<hr>',
            ],
            content_starts_after='Displaying example of "complex type" Enum sub-item object output.',
            content_ends_before="""<span class="string">'done'</span>""",
        )
