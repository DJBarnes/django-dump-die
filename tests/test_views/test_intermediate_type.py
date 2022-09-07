"""
Tests for "intermediate" type DD output.
"""

# System Imports.
import datetime
import os
import unittest
from unittest.mock import patch

# Third-Party Imports.
from django.test import override_settings
from django.utils import timezone
from freezegun import freeze_time
from django_expanded_test_cases import IntegrationTestCase

# Internal Imports.
from django_dump_die.constants import PYTZ_PRESENT, ZONEINFO_PRESENT


# Set datetime for freezegun and template render comparison.
# Ensures that seconds, etc match exactly for what is rendered vs what we check.
# Note that we replace microseconds to ensure these values are NOT identical.
now_dt_time = datetime.datetime.now()
now_tz_time = timezone.now()
# now_dt_time = datetime.datetime.now().replace(microsecond=123456)
# now_tz_time = timezone.now().replace(microsecond=234567)
# now_dt_time = now_dt_time.replace(microsecond=123456)
# now_tz_time = now_tz_time.replace(microsecond=234567)

project_path = os.getcwd()


@override_settings(DEBUG=True)
class DumpDieIntermediateTypeTestCase(IntegrationTestCase):
    """Verify handling of dumped "intermediate" types."""
    url = 'django_dump_die:intermediate-type-example'

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
            content_ends_before='Python pathlib examples:',
        )

    @unittest.skipIf(not PYTZ_PRESENT, 'Pytz not present. Likely Django >= 4.0.')
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
            content_ends_before='Python pathlib examples:',
        )

    @unittest.skipIf(not ZONEINFO_PRESENT, 'ZoneInfo not present. Likely Python < 3.9.')
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
            content_starts_after='sample_tz_timedelta',
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
