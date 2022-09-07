"""
Tests for "complex" type DD output.
"""


# Third-Party Imports.
from django.test import override_settings
from unittest.mock import patch
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
            content_ends_before='Basic object examples:',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_set_display(self, mocked_unique_generation):
        """Verify dumping a "set" type has expected output."""

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
                        data-target=".data_9004"
                        data-dd-type="type"
                        data-object-depth="1"
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
                                    <span id="arrow-data_9004-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9004-attributes show"
                                data-unique-attributes="data_9004-attributes"
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
            content_starts_after='Basic object examples:',
            content_ends_before='sample_frozen_set',
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
                class="li-wrapper collapse data_900119-attributes show"
                data-unique-attributes="data_900119-attributes"
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
                        data-target=".data_9008"
                        data-dd-type="type"
                        data-object-depth="1"
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
                                    <span id="arrow-data_9008-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9008-attributes show"
                                data-unique-attributes="data_9008-attributes"
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
            content_starts_after='sample_set',
            content_ends_before='sample_tuple',
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
                class="li-wrapper collapse data_900123-attributes show"
                data-unique-attributes="data_900123-attributes"
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
                        data-target=".data_90012"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90012">data_90012</span>
                        <span id="arrow-data_90012" class="arrow arrow-data_90012">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90012 " data-unique="data_90012">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90012-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_90012-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90012-attributes show"
                                data-unique-attributes="data_90012-attributes"
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
            content_starts_after='sample_frozen_set',
            content_ends_before='sample_list',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_list_display(self, mocked_unique_generation):
        """Verify dumping a "list" type has expected output."""

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
            content_starts_after='sample_tuple',
            content_ends_before='sample_dict',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dict_display(self, mocked_unique_generation):
        """Verify dumping a "dict" type has expected output."""

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
                        data-target=".data_90020"
                        data-dd-type="type"
                        data-object-depth="1"
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
                                    <span id="arrow-data_90020-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90020-attributes show"
                                data-unique-attributes="data_90020-attributes"
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
            content_starts_after='sample_list',
            content_ends_before='sample_memory_view',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_memory_view_display(self, mocked_unique_generation):
        """Verify dumping a "memory view" type has expected output."""

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
                    <span class="type" title="memoryview">memoryview:4</span>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_90024"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90024">data_90024</span>
                        <span id="arrow-data_90024" class="arrow arrow-data_90024">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90024 " data-unique="data_90024">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90024-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_90024-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90024-attributes show"
                                data-unique-attributes="data_90024-attributes"
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
                        data-target=".data_90032"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90032">data_90032</span>
                        <span id="arrow-data_90032" class="arrow arrow-data_90032">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90032 " data-unique="data_90032">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90032-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90032-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90032-attributes show"
                                data-unique-attributes="data_90032-attributes"
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
                        data-target=".data_90038"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90038">data_90038</span>
                        <span id="arrow-data_90038" class="arrow arrow-data_90038">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90038 " data-unique="data_90038">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90038-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90038-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90038-attributes show"
                                data-unique-attributes="data_90038-attributes"
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
                        data-target=".data_90040"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90040">data_90040</span>
                        <span id="arrow-data_90040" class="arrow arrow-data_90040">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90040 " data-unique="data_90040">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90040-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90040-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90040-attributes show"
                                data-unique-attributes="data_90040-attributes"
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
                        data-target=".data_90042"
                        data-dd-type="type"
                        data-object-depth="2"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_90042">data_90042</span>
                        <span id="arrow-data_90042" class="arrow arrow-data_90042">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_90042 " data-unique="data_90042">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_90042-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                <span id="arrow-data_90042-attributes" class="arrow"></span>
                            </a>
                            <div
                                class="li-wrapper collapse data_90042-attributes show"
                                data-unique-attributes="data_90042-attributes"
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
            content_starts_after='sample_dict',
            content_ends_before='Elaborate object examples:',
        )

    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_complex_set_display(self, mocked_unique_generation):
    #     """Verify dumping a multi-level "set" type has expected output."""
    #
    #     # Override default "unique" generation logic, for reproduce-able tests.
    #     # This generates enough uniques to guarantee mock does not raise errors.
    #     # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
    #     side_effects = []
    #     for index in range(5000):
    #         side_effects += [
    #             (f'data_900{index}', ''),
    #         ]
    #     mocked_unique_generation.side_effect = side_effects
    #
    #     # Test initial object display.
    #     # Note that sets are technically unordered, so we verify the general output,
    #     # and then use a separate unordered test to verify the child elements.
    #     self.assertGetResponse(
    #         self.url,
    #         expected_title='DD',
    #         expected_header='Django DumpDie',
    #         expected_content=[
    #             '<hr>',
    #
    #             # Object opening tags.
    #             """
    #             <div class="dump-wrapper">
    #                 <span class="dumped_object" title="Dumped Object">
    #                     <span class="dumped_name">sample_complex_set</span>
    #                 </span>:
    #                 <span class="type" title="set">set:2</span>
    #                 <span class="braces">{</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90049"
    #                     data-dd-type="type"
    #                     data-object-depth="1"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90049">data_90049</span>
    #                     <span id="arrow-data_90049" class="arrow arrow-data_90049">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90049 " data-unique="data_90049">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90049-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                                 <span id="arrow-data_90049-attributes" class="arrow">
    #                             </span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90049-attributes show"
    #                             data-unique-attributes="data_90049-attributes"
    #                         >
    #             """,
    #
    #             # Object child elements.
    #             # Note that we check for the presence of the general element, but not the direct values.
    #             # Sets are unordered, so these child values may appear in any ordering.
    #             """
    #             <li>
    #                 <span class="type" title="tuple">tuple:3</span>
    #                 <span class="braces">(</span>
    #                 <a
    #             """,
    #             """
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">)</span>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="type" title="tuple">tuple:3</span>
    #                 <span class="braces">(</span>
    #                 <a
    #             """,
    #             """
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">)</span>
    #             </li>
    #             """,
    #
    #             # Object closing tags.
    #             """
    #                                 </div>
    #                             </ul>
    #                         <ul class="attribute-list"></ul>
    #                     </div>
    #                 <span class="braces">}</span>
    #             </div>
    #             """,
    #
    #             '<hr>',
    #         ],
    #         content_starts_after='Elaborate object examples:',
    #         content_ends_before='sample_complex_set',
    #     )
    #
    #     # Test child elements.
    #     # Due to unique generation mocking, new response starts where last one ended, so numbers are different.
    #     self.assertGetResponse(
    #         self.url,
    #         expected_title='DD',
    #         expected_header='Django DumpDie',
    #         expected_content=[
    #             # Object child elements.
    #             """
    #             <li>
    #                 <span class="type" title="tuple">tuple:3</span>
    #                 <span class="braces">(</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90050"
    #                     data-dd-type="type"
    #                     data-object-depth="2"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90050">data_90050</span>
    #                     <span id="arrow-data_90050" class="arrow arrow-data_90050">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90050 " data-unique="data_90050">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90050-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_90050-attributes" class="arrow"></span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90050-attributes show"
    #                             data-unique-attributes="data_90050-attributes"
    #                         >
    #                             <li>
    #                                 <span class="index" title="Index">0</span>:
    #                                 <span class="type" title="str">str</span>
    #                                 <code class="string">'A'</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">1</span>:
    #                                 <span class="type" title="int">int</span>
    #                                 <code class="number">12</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">2</span>:
    #                                 <span class="type" title="bool">bool</span>
    #                                 <code class="bool">True</code>
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">)</span>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="type" title="tuple">tuple:3</span>
    #                 <span class="braces">(</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90054"
    #                     data-dd-type="type"
    #                     data-object-depth="2"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90054">data_90054</span>
    #                     <span id="arrow-data_90054" class="arrow arrow-data_90054">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90054 " data-unique="data_90054">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90054-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_90054-attributes" class="arrow"></span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90054-attributes show"
    #                             data-unique-attributes="data_90054-attributes"
    #                         >
    #                             <li>
    #                                 <span class="index" title="Index">0</span>:
    #                                 <span class="type" title="str">str</span>
    #                                 <code class="string">'B'</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">1</span>:
    #                                 <span class="type" title="int">int</span>
    #                                 <code class="number">24</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">2</span>:
    #                                 <span class="type" title="bool">bool</span>
    #                                 <code class="bool">False</code>
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">)</span>
    #             </li>
    #             """,
    #         ],
    #         content_starts_after="""
    #         <div
    #             class="li-wrapper collapse data_900121-attributes show"
    #             data-unique-attributes="data_900119-attributes"
    #         >
    #         """,
    #         content_ends_before="""
    #                             </div>
    #                         </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #             <span class="braces">}</span>
    #         </div>
    #         """,
    #         ignore_content_ordering=True,
    #     )

    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_complex_tuple_display(self, mocked_unique_generation):
    #     """Verify dumping a multi-level "tuple" type has expected output."""
    #
    #     # Override default "unique" generation logic, for reproduce-able tests.
    #     # This generates enough uniques to guarantee mock does not raise errors.
    #     side_effects = []
    #     for index in range(5000):
    #         side_effects += [
    #             (f'data_900{index}', ''),
    #         ]
    #     mocked_unique_generation.side_effect = side_effects
    #
    #     self.assertGetResponse(
    #         self.url,
    #         expected_title='DD',
    #         expected_header='Django DumpDie',
    #         expected_content=[
    #             '<hr>',
    #
    #             # Object opening tags.
    #             """
    #             <div class="dump-wrapper">
    #                 <span class="dumped_object" title="Dumped Object">
    #                     <span class="dumped_name">sample_complex_tuple</span>
    #                 </span>:
    #                 <span class="type" title="tuple">tuple:2</span>
    #                 <span class="braces">{</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90020"
    #                     data-dd-type="type"
    #                     data-object-depth="1"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90020">data_90020</span>
    #                     <span id="arrow-data_90020" class="arrow arrow-data_90020">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90020 " data-unique="data_90020">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90020-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                                 <span id="arrow-data_90020-attributes" class="arrow">
    #                             </span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90020-attributes show"
    #                             data-unique-attributes="data_90020-attributes"
    #                         >
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #                 <span class="key" title="Key">'first'</span>:
    #                 <span class="type" title="str">str</span>
    #                 <code class="string">'A'</code>
    #             </li>
    #             <li>
    #                 <span class="key" title="Key">'second'</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">12</code>
    #             </li>
    #             <li>
    #                 <span class="key" title="Key">'third'</span>:
    #                 <span class="type" title="bool">bool</span>
    #                 <code class="bool">True</code>
    #             </li>
    #             """,
    #
    #             # Object closing tags.
    #             """
    #                                 </div>
    #                             </ul>
    #                         <ul class="attribute-list"></ul>
    #                     </div>
    #                 <span class="braces">}</span>
    #             </div>
    #             """,
    #
    #             '<hr>',
    #         ],
    #         content_starts_after='sample_list',
    #         content_ends_before='sample_memory_view',
    #     )
