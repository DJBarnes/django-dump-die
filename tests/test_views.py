
import datetime
import os
from django.test import override_settings
from django.utils import timezone
from django_expanded_test_cases import IntegrationTestCase
from freezegun import freeze_time
from unittest.mock import patch


# Set datetime for freezegun and template render comparison.
# Ensures that seconds,etc match exactly for what is rendered vs what we check.
# Note that we replace microseconds to ensure these values are NOT identical.
now_dt_time = datetime.datetime.now()
now_tz_time = timezone.now()
# now_dt_time = datetime.datetime.now().replace(microsecond=123456)
# now_tz_time = timezone.now().replace(microsecond=234567)
# now_dt_time = now_dt_time.replace(microsecond=123456)
# now_tz_time = now_tz_time.replace(microsecond=234567)

project_path = os.getcwd()


@override_settings(DEBUG=True)
class GenericViewTestCase(IntegrationTestCase):
    """Base class for all tests."""
    # Default url to "simple type" here. Override in all classes that inherit.
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


class DumpDieSimpleTypeTestCase(GenericViewTestCase):
    """Verify handling of dumped "simple" types."""
    url = 'django_dump_die:simple-type-example'

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


class DumpDieIntermediateTypeTestCase(GenericViewTestCase):
    """Verify handling of dumped "intermediate" types."""
    url = 'django_dump_die:intermediate-type-example'

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
                        <span class="string">'Displaying example of "intermediate type" object output.'</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Displaying example of "intermediate type" object output.'</code>
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
            content_ends_before='Python type examples:',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_bytes_array_display(self, mocked_unique_generation):
        """Verify dumping a "bytes array" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_bytes_array</span>
                    </span>:
                    <span class="type" title="bytearray">bytearray</span>
                    <code class="intermediate">bytearray(b'\\x08\\t\\n\\x0b')</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
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
            content_starts_after='Python type examples:',
            content_ends_before='sample_complex',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_complex_display(self, mocked_unique_generation):
        """Verify dumping a "complex" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_complex</span>
                    </span>:
                    <span class="type" title="complex">complex</span>
                    <code class="intermediate">(3-1j)</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">imag</span>:
                    <span class="type" title="float">float</span>
                    <code class="number">-1.0</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">real</span>:
                    <span class="type" title="float">float</span>
                    <code class="number">3.0</code>
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
            content_starts_after='sample_bytes_array',
            content_ends_before='Date/Time examples:',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dt_date_display(self, mocked_unique_generation):
        """Verify dumping a "datetime date" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_dt_date</span>
                    </span>:
                    <span class="type" title="date">date</span>
                """
                """
                <code class="intermediate">{0}</code>
                """.format(now_dt_time.date()),
                """
                <span class="braces">{</span>
                <a
                    class="arrow-toggle collapsed"
                    title="[Ctrl+click] Expand all children"
                    data-toggle="collapse"
                    data-target=".data_9001"
                    data-dd-type="type"
                    data-object-depth="1"
                    aria-label="Close"
                    aria-expanded="false"
                >
                    <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                    <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                </a>
                <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                    <ul class="attribute-list">
                        <a
                            class="arrow-toggle show always-show"
                            title="[Ctrl+click] Expand all children"
                            data-target=".data_9001-attributes"
                            data-dd-type="attr"
                            aria-label="Open/Close"
                            aria-expanded=""
                        >
                            <span class="section_name">Attributes</span>
                                <span id="arrow-data_9001-attributes" class="arrow">
                            </span>
                        </a>
                """,

                # Object child elements.
                """
                <div
                    class="li-wrapper collapse data_9001-attributes show"
                    data-unique-attributes="data_9001-attributes"
                >
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">day</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.day),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">max</span>:
                    <span class="type" title="date">date</span>
                    <code class="intermediate">9999-12-31</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">min</span>:
                    <span class="type" title="date">date</span>
                    <code class="intermediate">0001-01-01</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">month</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.month),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">resolution</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">1 day, 0:00:00</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">year</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.year),

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
            content_starts_after='Date/Time examples:',
            content_ends_before='sample_tz_date',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_tz_date_display(self, mocked_unique_generation):
        """Verify dumping a "timezone date" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_tz_date</span>
                    </span>:
                    <span class="type" title="date">date</span>
                """
                """
                <code class="intermediate">{0}</code>
                """.format(now_dt_time.date()),
                """
                <span class="braces">{</span>
                <a
                    class="arrow-toggle collapsed"
                    title="[Ctrl+click] Expand all children"
                    data-toggle="collapse"
                    data-target=".data_9001"
                    data-dd-type="type"
                    data-object-depth="1"
                    aria-label="Close"
                    aria-expanded="false"
                >
                    <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                    <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                </a>
                <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                    <ul class="attribute-list">
                        <a
                            class="arrow-toggle show always-show"
                            title="[Ctrl+click] Expand all children"
                            data-target=".data_9001-attributes"
                            data-dd-type="attr"
                            aria-label="Open/Close"
                            aria-expanded=""
                        >
                            <span class="section_name">Attributes</span>
                                <span id="arrow-data_9001-attributes" class="arrow">
                            </span>
                        </a>
                        <div
                            class="li-wrapper collapse data_9001-attributes show"
                            data-unique-attributes="data_9001-attributes"
                        >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">day</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.day),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">max</span>:
                    <span class="type" title="date">date</span>
                    <code class="intermediate">9999-12-31</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">min</span>:
                    <span class="type" title="date">date</span>
                    <code class="intermediate">0001-01-01</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">month</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.month),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">resolution</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">1 day, 0:00:00</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">year</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.year),

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
            content_starts_after='sample_dt_date',
            content_ends_before='sample_dt_datetime',
        )

    # @freeze_time(now_dt_time)
    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_dt_datetime_display(self, mocked_unique_generation):
    #     """Verify dumping a "datetime datetime" type has expected output."""
    #
    #     # Override default "unique" generation logic, for reproduce-able tests.
    #     # This generates enough uniques to guarantee mock does not raise errors.
    #     side_effects = []
    #     for index in range(5000):
    #         side_effects += [
    #             (f'data_9001', ''),
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
    #                     <span class="dumped_name">sample_dt_datetime</span>
    #                 </span>:
    #                 <span class="type" title="FakeDatetime">FakeDatetime</span>
    #             """
    #             """
    #             <code class="intermediate">{0}</code>
    #             """.format(now_dt_time),
    #             """
    #             <span class="braces">{</span>
    #             <a
    #                 class="arrow-toggle collapsed"
    #                 title="[Ctrl+click] Expand all children"
    #                 data-toggle="collapse"
    #                 data-target=".data_9001"
    #                 data-dd-type="type"
    #                 data-object-depth="1"
    #                 aria-label="Close"
    #                 aria-expanded="false"
    #             >
    #                 <span class="unique" data-highlight-unique="data_9001">data_9001</span>
    #                 <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
    #             </a>
    #             <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
    #                 <ul class="attribute-list">
    #                     <a
    #                         class="arrow-toggle show always-show"
    #                         title="[Ctrl+click] Expand all children"
    #                         data-target=".data_9001-attributes"
    #                         data-dd-type="attr"
    #                         aria-label="Open/Close"
    #                         aria-expanded=""
    #                     >
    #                         <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_9001-attributes" class="arrow">
    #                         </span>
    #                     </a>
    #                     <div
    #                         class="li-wrapper collapse data_9001-attributes show"
    #                         data-unique-attributes="data_9001-attributes"
    #                     >
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">day</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.day),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">fold</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">0</code>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">hour</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.hour),
    #             # """
    #             # <li>
    #             #     <span class="access-modifier">+</span>
    #             #     <span class="attribute" title="Attribute">max</span>:
    #             #     <span class="type" title="datetime">datetime</span>
    #             #     <code class="intermediate">9999-12-31 23:59:59.999999</code>
    #             # </li>
    #             # """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">microsecond</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.microsecond),
    #             # """
    #             # <li>
    #             #     <span class="access-modifier">+</span>
    #             #     <span class="attribute" title="Attribute">min</span>:
    #             #     <span class="type" title="datetime">datetime</span>
    #             #     <code class="intermediate">0001-01-01 00:00:00</code>
    #             # </li>
    #             # """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">minute</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.minute),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">month</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.month),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">resolution</span>:
    #                 <span class="type" title="timedelta">timedelta</span>
    #                 <code class="intermediate">0:00:00.000001</code>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">second</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.second),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">tzinfo</span>:
    #                 <span class="type" title="null">null</span>
    #                 <code class="none">None</code>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">year</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_dt_time.year),
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
    #         content_starts_after='sample_tz_date',
    #         content_ends_before='sample_tz_datetime',
    #     )

    # @freeze_time(now_tz_time)
    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_tz_datetime_display(self, mocked_unique_generation):
    #     """Verify dumping a "timezone datetime" type has expected output."""
    #
    #     # Override default "unique" generation logic, for reproduce-able tests.
    #     # This generates enough uniques to guarantee mock does not raise errors.
    #     side_effects = []
    #     for index in range(5000):
    #         side_effects += [
    #             (f'data_9001', ''),
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
    #                     <span class="dumped_name">sample_tz_datetime</span>
    #                 </span>:
    #                 <span class="type" title="FakeDatetime">FakeDatetime</span>
    #             """,
    #             """
    #             <code class="intermediate">{0}</code>
    #             """.format(now_tz_time),
    #             """
    #             <span class="braces">{</span>
    #             <a
    #                 class="arrow-toggle collapsed"
    #                 title="[Ctrl+click] Expand all children"
    #                 data-toggle="collapse"
    #                 data-target=".data_9001"
    #                 data-dd-type="type"
    #                 data-object-depth="1"
    #                 aria-label="Close"
    #                 aria-expanded="false"
    #             >
    #                 <span class="unique" data-highlight-unique="data_9001">data_9001</span>
    #                 <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
    #             </a>
    #             <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
    #                 <ul class="attribute-list">
    #                     <a
    #                         class="arrow-toggle show always-show"
    #                         title="[Ctrl+click] Expand all children"
    #                         data-target=".data_9001-attributes"
    #                         data-dd-type="attr"
    #                         aria-label="Open/Close"
    #                         aria-expanded=""
    #                     >
    #                         <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_9001-attributes" class="arrow">
    #                         </span>
    #                     </a>
    #                     <div
    #                         class="li-wrapper collapse data_9001-attributes show"
    #                         data-unique-attributes="data_9001-attributes"
    #                     >
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">day</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.day),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">fold</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">0</code>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">hour</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.hour),
    #             # """
    #             # <li>
    #             #     <span class="access-modifier">+</span>
    #             #     <span class="attribute" title="Attribute">max</span>:
    #             #     <span class="type" title="datetime">datetime</span>
    #             #     <code class="intermediate">9999-12-31 23:59:59.999999</code>
    #             # </li>
    #             # """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">microsecond</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.microsecond),
    #             # """
    #             # <li>
    #             #     <span class="access-modifier">+</span>
    #             #     <span class="attribute" title="Attribute">min</span>:
    #             #     <span class="type" title="datetime">datetime</span>
    #             #     <code class="intermediate">0001-01-01 00:00:00</code>
    #             # </li>
    #             # """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">minute</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.minute),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">month</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.month),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">resolution</span>:
    #                 <span class="type" title="timedelta">timedelta</span>
    #                 <code class="intermediate">0:00:00.000001</code>
    #             </li>
    #             ""","""
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">second</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.second),
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">tzinfo</span>:
    #                 <span class="type" title="timezone">timezone</span>
    #                 <code class="intermediate">UTC</code>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="access-modifier">+</span>
    #                 <span class="attribute" title="Attribute">year</span>:
    #                 <span class="type" title="int">int</span>
    #                 <code class="number">{0}</code>
    #             </li>
    #             """.format(now_tz_time.year),
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
    #         content_starts_after='sample_dt_datetime',
    #         content_ends_before='sample_dt_time',
    #     )

    @freeze_time(now_dt_time)
    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dt_time_display(self, mocked_unique_generation):
        """Verify dumping a "datetime time" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_dt_time</span>
                    </span>:
                    <span class="type" title="time">time</span>
                """,
                """
                <code class="intermediate">{0}</code>
                """.format(now_dt_time.time()),
                """
                <span class="braces">{</span>
                <a
                    class="arrow-toggle collapsed"
                    title="[Ctrl+click] Expand all children"
                    data-toggle="collapse"
                    data-target=".data_9001"
                    data-dd-type="type"
                    data-object-depth="1"
                    aria-label="Close"
                    aria-expanded="false"
                >
                    <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                    <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                </a>
                <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                    <ul class="attribute-list">
                        <a
                            class="arrow-toggle show always-show"
                            title="[Ctrl+click] Expand all children"
                            data-target=".data_9001-attributes"
                            data-dd-type="attr"
                            aria-label="Open/Close"
                            aria-expanded=""
                        >
                            <span class="section_name">Attributes</span>
                                <span id="arrow-data_9001-attributes" class="arrow">
                            </span>
                        </a>
                        <div
                            class="li-wrapper collapse data_9001-attributes show"
                            data-unique-attributes="data_9001-attributes"
                        >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">fold</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">0</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">hour</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.hour),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">max</span>:
                    <span class="type" title="time">time</span>
                    <code class="intermediate">23:59:59.999999</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">microsecond</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.microsecond),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">min</span>:
                    <span class="type" title="time">time</span>
                    <code class="intermediate">{0}</code>
                </li>
                """.format(now_dt_time.time().min),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">minute</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.minute),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">resolution</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">0:00:00.000001</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">second</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_dt_time.second),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">tzinfo</span>:
                    <span class="type" title="null">null</span>
                    <code class="none">None</code>
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
            content_starts_after='sample_tz_datetime',
            content_ends_before='sample_tz_time',
        )

    @freeze_time(now_tz_time)
    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_tz_time_display(self, mocked_unique_generation):
        """Verify dumping a "timezone time" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_tz_time</span>
                    </span>:
                    <span class="type" title="time">time</span>
                """,
                """
                <code class="intermediate">{0}</code>
                """.format(now_tz_time.time()),
                """
                <span class="braces">{</span>
                <a
                    class="arrow-toggle collapsed"
                    title="[Ctrl+click] Expand all children"
                    data-toggle="collapse"
                    data-target=".data_9001"
                    data-dd-type="type"
                    data-object-depth="1"
                    aria-label="Close"
                    aria-expanded="false"
                >
                    <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                    <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                </a>
                <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                    <ul class="attribute-list">
                        <a
                            class="arrow-toggle show always-show"
                            title="[Ctrl+click] Expand all children"
                            data-target=".data_9001-attributes"
                            data-dd-type="attr"
                            aria-label="Open/Close"
                            aria-expanded=""
                        >
                            <span class="section_name">Attributes</span>
                                <span id="arrow-data_9001-attributes" class="arrow">
                            </span>
                        </a>
                        <div
                            class="li-wrapper collapse data_9001-attributes show"
                            data-unique-attributes="data_9001-attributes"
                        >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">fold</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">0</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">hour</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_tz_time.hour),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">max</span>:
                    <span class="type" title="time">time</span>
                    <code class="intermediate">23:59:59.999999</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">microsecond</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_tz_time.microsecond),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">min</span>:
                    <span class="type" title="time">time</span>
                    <code class="intermediate">{0}</code>
                </li>
                """.format(now_tz_time.time().min),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">minute</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_tz_time.minute),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">resolution</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">0:00:00.000001</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">second</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">{0}</code>
                </li>
                """.format(now_tz_time.second),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">tzinfo</span>:
                    <span class="type" title="null">null</span>
                    <code class="none">None</code>
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
            content_starts_after='sample_dt_time',
            content_ends_before='sample_dt_timedelta',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dt_timedelta_display(self, mocked_unique_generation):
        """Verify dumping a "datetime timedelta" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_dt_timedelta</span>
                    </span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">1 day, 0:00:00</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">days</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">1</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">max</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">999999999 days, 23:59:59.999999</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">microseconds</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">0</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">min</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">-999999999 days, 0:00:00</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">resolution</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">0:00:00.000001</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">seconds</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">0</code>
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
            content_starts_after='sample_tz_time',
            content_ends_before='sample_tz_timedelta',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_tz_timedelta_display(self, mocked_unique_generation):
        """Verify dumping a "timezone timedelta" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_tz_timedelta</span>
                    </span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">2 days, 0:00:00</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">days</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">2</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">max</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">999999999 days, 23:59:59.999999</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">microseconds</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">0</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">min</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">-999999999 days, 0:00:00</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">resolution</span>:
                    <span class="type" title="timedelta">timedelta</span>
                    <code class="intermediate">0:00:00.000001</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">seconds</span>:
                    <span class="type" title="int">int</span>
                    <code class="number">0</code>
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
            content_starts_after='sample_dt_timedelta',
            content_ends_before='sample_pytz_timezone',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_pytz_timezone_display(self, mocked_unique_generation):
        """Verify dumping a "pytz timezone" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_pytz_timezone</span>
                    </span>:
                    <span class="type" title="pytz_timezone">pytz_timezone</span>
                    <code class="intermediate">UTC</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">zone</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'UTC'</code>
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
            content_starts_after='sample_tz_timedelta',
            content_ends_before='sample_zoneinfo_timezone',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_zoneinfo_timezone_display(self, mocked_unique_generation):
        """Verify dumping a "zoneinfo timezone" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_zoneinfo_timezone</span>
                    </span>:
                    <span class="type" title="ZoneInfo">ZoneInfo</span>
                    <code class="intermediate">UTC</code>
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">key</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'UTC'</code>
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
            content_starts_after='sample_pytz_timezone',
            content_ends_before='Python pathlib examples:',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_pure_path_display(self, mocked_unique_generation):
        """Verify dumping a "pure path" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                    <span class="dumped_name">sample_pure_path</span>
                </span>:
                <span class="type" title="PurePosixPath">PurePosixPath</span>
                """,
                """
                <code class="intermediate">{0}</code>
                """.format(project_path),
                """
                <span class="braces">{</span>
                <a
                    class="arrow-toggle collapsed"
                    title="[Ctrl+click] Expand all children"
                    data-toggle="collapse"
                    data-target=".data_9001"
                    data-dd-type="type"
                    data-object-depth="1"
                    aria-label="Close"
                    aria-expanded="false"
                >
                    <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                    <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                </a>
                <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                    <ul class="attribute-list">
                        <a
                            class="arrow-toggle show always-show"
                            title="[Ctrl+click] Expand all children"
                            data-target=".data_9001-attributes"
                            data-dd-type="attr"
                            aria-label="Open/Close"
                            aria-expanded=""
                        >
                            <span class="section_name">Attributes</span>
                            <span id="arrow-data_9001-attributes" class="arrow"></span>
                        </a>
                        <div
                            class="li-wrapper collapse data_9001-attributes show"
                            data-unique-attributes="data_9001-attributes"
                        >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">anchor</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'/'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">drive</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">name</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'django-dump-die'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">parent</span>:
                    <span class="type" title="PurePosixPath">PurePosixPath</span>
                    <code class="intermediate">{0}</code>
                </li>
                """.format(os.path.dirname(project_path)),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">parents</span>:
                    <span class="type" title="_PathParents">_PathParents</span>
                    <code class="default"><PurePosixPath.parents></code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">parts</span>:
                    <span class="type" title="tuple">tuple</span>
                    <code class="default">{0}</code>
                </li>
                """.format(tuple(['/'] + project_path.split('/')[1:])),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">root</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'/'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">stem</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'django-dump-die'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">suffix</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">suffixes</span>:
                    <span class="type" title="list">list</span>
                    <code class="default">[]</code>
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
            content_starts_after='Python pathlib examples:',
            content_ends_before='sample_posix_path',
        )

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_posix_path_display(self, mocked_unique_generation):
        """Verify dumping a "posix path" type has expected output."""

        # Override default "unique" generation logic, for reproduce-able tests.
        # This generates enough uniques to guarantee mock does not raise errors.
        side_effects = []
        for index in range(5000):
            side_effects += [
                (f'data_9001', ''),
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
                        <span class="dumped_name">sample_posix_path</span>
                    </span>:
                    <span class="type" title="PosixPath">PosixPath</span>
                """,
                """
                    <code class="intermediate">{0}</code>
                """.format(project_path),
                """
                    <span class="braces">{</span>
                    <a
                        class="arrow-toggle collapsed"
                        title="[Ctrl+click] Expand all children"
                        data-toggle="collapse"
                        data-target=".data_9001"
                        data-dd-type="type"
                        data-object-depth="1"
                        aria-label="Close"
                        aria-expanded="false"
                    >
                        <span class="unique" data-highlight-unique="data_9001">data_9001</span>
                        <span id="arrow-data_9001" class="arrow arrow-data_9001">▶</span>
                    </a>
                    <div class="dd-wrapper collapse data_9001 " data-unique="data_9001">
                        <ul class="attribute-list">
                            <a
                                class="arrow-toggle show always-show"
                                title="[Ctrl+click] Expand all children"
                                data-target=".data_9001-attributes"
                                data-dd-type="attr"
                                aria-label="Open/Close"
                                aria-expanded=""
                            >
                                <span class="section_name">Attributes</span>
                                    <span id="arrow-data_9001-attributes" class="arrow">
                                </span>
                            </a>
                            <div
                                class="li-wrapper collapse data_9001-attributes show"
                                data-unique-attributes="data_9001-attributes"
                            >
                """,

                # Object child elements.
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">anchor</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'/'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">drive</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">name</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'django-dump-die'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">parent</span>:
                    <span class="type" title="PosixPath">PosixPath</span>
                    <code class="intermediate">{0}</code>
                </li>
                """.format(os.path.dirname(project_path)),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">parents</span>:
                    <span class="type" title="_PathParents">_PathParents</span>
                    <code class="default"><PosixPath.parents></code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">parts</span>:
                    <span class="type" title="tuple">tuple</span>
                    <code class="default">{0}</code>
                </li>
                """.format(tuple(['/'] + project_path.split('/')[1:])),
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">root</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'/'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">stem</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'django-dump-die'</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">suffix</span>:
                    <span class="type" title="str">str</span>
                    <code class="string">''</code>
                </li>
                """,
                """
                <li>
                    <span class="access-modifier">+</span>
                    <span class="attribute" title="Attribute">suffixes</span>:
                    <span class="type" title="list">list</span>
                    <code class="default">[]</code>
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
            content_starts_after='sample_pure_path',
            content_ends_before='done',
        )


class DumpDieComplexTypeTestCase(GenericViewTestCase):
    """Verify handling of dumped "complex" types."""
    url = 'django_dump_die:complex-type-example'

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


class DumpDieViewFunctionTestCase(GenericViewTestCase):
    """Verify handling of dumped function types."""
    url = 'django_dump_die:function-example'

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
        """Verify dumping a "function" type (with args/kwawrgs) has expected output."""
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
