"""
Tests for "request/response cycle" type DD output.
"""

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


@override_settings(DEBUG=True)
class DumpDieDjangoRequestResponseCycleTestCase(IntegrationTestCase):
    """Verify handling of dumped "Django request-response cycle" types."""
    url = 'django_dump_die:django-request-response-cycle-example'

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
                        <span class="string">'Displaying Django request-response-cycle example output.'</span>
                    </span>:
                    <span class="type" title="str">str</span>
                    <code class="string">'Displaying Django request-response-cycle example output.'</code>
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
            content_ends_before='QueryDict object',
        )

    # TODO/NOTES:
    #   Due to the number of "unique" values being generated in a Request object, it seems to error out with these
    #   tests. Either we get a StopIteration error, due to an insufficient mock range, or we get a RecursionError
    #   due to too many calls when we raise this mock value.
    #
    #   At the moment, I'm unsure of if there's a way around this to physically test this page logic.
    #
    #   Note: The below QueryDict test technically passes (at least when this was written, as of early Aug 2022) IF you
    #   edit the view itself to stop further dd output after displaying the QueryDict. But as soon as you include the
    #   Request object, then the above described errors occur.
    #
    #   And at least for now, I'd rather have all output types displayed for manual user-examination when physically
    #   loading this page in a browser, rather than comment out the "Request object dump", just for the sake of
    #   UnitTests.
    #
    #
    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_querydict_display(self, mocked_unique_generation):
    #     """Verify dumping a "QueryDict" type has expected output."""
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
    #     # Test object display.
    #     self.assertGetResponse(
    #         self.url,
    #         expected_title='DD',
    #         expected_header='Django DumpDie',
    #         expected_content=[
    #             '<hr>',
    #
    #             # Object descriptor.
    #             """
    #             <div class="dump-wrapper">
    #                 <span class="dumped_object" title="Dumped Object">
    #                     <span class="string">'QueryDict object (GET and POST are instances of this):'</span>
    #                 </span>:
    #                 <span class="type" title="str">str</span>
    #                 <code class="string">'QueryDict object (GET and POST are instances of this):'</code>
    #             </div>
    #             """,
    #
    #             '<hr>',
    #             # Object opening tags.
    #             """
    #             <div class="dump-wrapper">
    #                 <span class="dumped_object" title="Dumped Object">
    #                     <span class="dumped_name">sample_query_dict</span>
    #                 </span>:
    #                 <span class="type" title="QueryDict">QueryDict:0</span>
    #                 <span class="braces">{</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_9008"
    #                     data-dd-type="type"
    #                     data-object-depth="1"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_9008">data_9008</span>
    #                     <span id="arrow-data_9008" class="arrow arrow-data_9008">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_9008 " data-unique="data_9008">
    #                 <ul class="attribute-list">
    #                 <a
    #                     class="arrow-toggle show always-show"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-target=".data_9008-attributes"
    #                     data-dd-type="attr"
    #                     aria-label="Open/Close"
    #                     aria-expanded=""
    #                 >
    #                     <span class="section_name">Attributes</span>
    #                         <span id="arrow-data_9008-attributes" class="arrow">
    #                     </span>
    #                 </a>
    #                 <div
    #                     class="li-wrapper collapse data_9008-attributes show"
    #                     data-unique-attributes="data_9008-attributes"
    #                 >
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #                 <span class="key" title="Key">'one_val'</span>:
    #                 <span class="type" title="list">list:1</span>
    #                 <span class="braces">[</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90010"
    #                     data-dd-type="type"
    #                     data-object-depth="2"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90010">data_90010</span>
    #                     <span id="arrow-data_90010" class="arrow arrow-data_90010">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90010 " data-unique="data_90010">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90010-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_90010-attributes" class="arrow"></span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90010-attributes show"
    #                             data-unique-attributes="data_90010-attributes"
    #                         >
    #                             <li>
    #                                 <span class="index" title="Index">0</span>:
    #                                 <span class="type" title="str">str</span> <code class="string">'test'</code>
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">]</span>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="key" title="Key">'two_vals'</span>:
    #                 <span class="type" title="list">list:2</span>
    #                 <span class="braces">[</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90012"
    #                     data-dd-type="type"
    #                     data-object-depth="2"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90012">data_90012</span>
    #                     <span id="arrow-data_90012" class="arrow arrow-data_90012">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90012 " data-unique="data_90012">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90012-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_90012-attributes" class="arrow"></span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90012-attributes show"
    #                             data-unique-attributes="data_90012-attributes"
    #                         >
    #                             <li>
    #                                 <span class="index" title="Index">0</span>:
    #                                 <span class="type" title="str">str</span> <code class="string">'one'</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">1</span>:
    #                                 <span class="type" title="str">str</span> <code class="string">'2'</code>
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">]</span>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="key" title="Key">'example_field_list'</span>:
    #                 <span class="type" title="list">list:3</span>
    #                 <span class="braces">[</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90015"
    #                     data-dd-type="type"
    #                     data-object-depth="2"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90015">data_90015</span>
    #                     <span id="arrow-data_90015" class="arrow arrow-data_90015">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90015 " data-unique="data_90015">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90015-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_90015-attributes" class="arrow"></span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90015-attributes show"
    #                             data-unique-attributes="data_90015-attributes"
    #                         >
    #                             <li>
    #                                 <span class="index" title="Index">0</span>:
    #                                 <span class="type" title="str">str</span> <code class="string">'username'</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">1</span>:
    #                                 <span class="type" title="str">str</span> <code class="string">'first_name'</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">2</span>:
    #                                 <span class="type" title="str">str</span> <code class="string">'last_name'</code>
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">]</span>
    #             </li>
    #             """,
    #             """
    #             <li>
    #                 <span class="key" title="Key">'example_types'</span>:
    #                 <span class="type" title="list">list:4</span>
    #                 <span class="braces">[</span>
    #                 <a
    #                     class="arrow-toggle collapsed"
    #                     title="[Ctrl+click] Expand all children"
    #                     data-toggle="collapse"
    #                     data-target=".data_90019"
    #                     data-dd-type="type"
    #                     data-object-depth="2"
    #                     aria-label="Close"
    #                     aria-expanded="false"
    #                 >
    #                     <span class="unique" data-highlight-unique="data_90019">data_90019</span>
    #                     <span id="arrow-data_90019" class="arrow arrow-data_90019">▶</span>
    #                 </a>
    #                 <div class="dd-wrapper collapse data_90019 " data-unique="data_90019">
    #                     <ul class="attribute-list">
    #                         <a
    #                             class="arrow-toggle show always-show"
    #                             title="[Ctrl+click] Expand all children"
    #                             data-target=".data_90019-attributes"
    #                             data-dd-type="attr"
    #                             aria-label="Open/Close"
    #                             aria-expanded=""
    #                         >
    #                             <span class="section_name">Attributes</span>
    #                             <span id="arrow-data_90019-attributes" class="arrow"></span>
    #                         </a>
    #                         <div
    #                             class="li-wrapper collapse data_90019-attributes show"
    #                             data-unique-attributes="data_90019-attributes"
    #                         >
    #                             <li>
    #                                 <span class="index" title="Index">0</span>:
    #                                 <span class="type" title="null">null</span> <code class="none">None</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">1</span>:
    #                                 <span class="type" title="bool">bool</span> <code class="bool">True</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">2</span>:
    #                                 <span class="type" title="int">int</span> <code class="number">5</code>
    #                             </li>
    #                             <li>
    #                                 <span class="index" title="Index">3</span>:
    #                                 <span class="type" title="float">float</span> <code class="number">3.0</code>
    #                             </li>
    #                         </div>
    #                     </ul>
    #                     <ul class="attribute-list"></ul>
    #                 </div>
    #                 <span class="braces">]</span>
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
    #         content_starts_after='QueryDict object',
    #         content_ends_before='Request object',
    #     )

    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_request_display(self, mocked_unique_generation):
    #     """Verify dumping a "Request" type has expected output."""
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
    #     # Test object display.
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
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #             </li>
    #             """,
    #             """
    #             <li>
    #             </li>
    #             """,
    #             """
    #             <li>
    #             </li>
    #             """,
    #
    #             # Object closing tags.
    #             """
    #                                 </div>
    #                             </ul>
    #                         <ul class="attribute-list"></ul>
    #                     </div>
    #                 <span class="braces">]</span>
    #             </div>
    #             """,
    #
    #             '<hr>',
    #         ],
    #         content_starts_after='',
    #         # content_ends_before='',
    #     )

    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_http_response_display(self, mocked_unique_generation):
    #     """Verify dumping a "HttpResponse" type has expected output."""
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
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #             </li>
    #             """,
    #             """
    #             <li>
    #             </li>
    #             """,
    #             """
    #             <li>
    #             </li>
    #             """,
    #
    #             # Object closing tags.
    #             """
    #                                 </div>
    #                             </ul>
    #                         <ul class="attribute-list"></ul>
    #                     </div>
    #                 <span class="braces">]</span>
    #             </div>
    #             """,
    #
    #             '<hr>',
    #         ],
    #         content_starts_after='',
    #         # content_ends_before='',
    #     )

    # @patch('django_dump_die.templatetags.dump_die._generate_unique')
    # def test_template_response_display(self, mocked_unique_generation):
    #     """Verify dumping a "TemplateResponse" type has expected output."""
    #     # Override default "unique" generation logic, for reproduce-able tests.
    #     # This generates enough uniques to guarantee mock does not raise errors.
    #     # Unlike above tests, we need to give each object custom uniques, to ensure child-objects display.
    #     side_effects = []
    #     for index in range(5000):
    #         side_effects += [
    #             (f'data_900{index}', ''),
    #         ]
    #     mocked_unique_generation.side_effect = side_effects
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
    #             """,
    #
    #             # Object child elements.
    #             """
    #             <li>
    #             </li>
    #             """,
    #             """
    #             <li>
    #             </li>
    #             """,
    #             """
    #             <li>
    #             </li>
    #             """,
    #
    #             # Object closing tags.
    #             """
    #                                 </div>
    #                             </ul>
    #                         <ul class="attribute-list"></ul>
    #                     </div>
    #                 <span class="braces">]</span>
    #             </div>
    #             """,
    #
    #             '<hr>',
    #         ],
    #         content_starts_after='',
    #         # content_ends_before='',
    #     )
