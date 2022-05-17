from unittest.mock import patch
from django.test import TestCase as TestCase
from django.test import override_settings


@override_settings(DEBUG=True)
class GenericViewTestCase(TestCase):
    """Base class for all tests"""
    pass


class DumpDieViewFunctionTestCase(GenericViewTestCase):
    """Class for testing dumped functions via a view"""

    def test_dd_for_standard_function(self):
        """Test that dumping a function has expected output"""
        response = self.client.get('/function?type=standard')
        expected = '<span class="dumped_function" title="Dumped Function"><span class="function">test_function</span><span class="braces">(</span><span class="params">arg1</span><span class="braces">)</span></span>: <span class="docs">Standard Test Function Documentation.</span>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_attached_function(self):
        """Test that dumping a function has expected output"""

        response = self.client.get('/function?type=attached')
        expected = '<span class="dumped_function" title="Dumped Function"><span class="dumped_name">test_obj</span><span class="dumped_name">.</span><span class="function">test_function</span><span class="braces">(</span><span class="braces">)</span></span>: <span class="docs">Attached Test Function Documentation.</span>'
        self.assertContains(response, expected, html=True)


class DumpDieViewSimpleTestCase(GenericViewTestCase):
    """Class for testing dumped simple types via a view"""

    def test_dd_for_bool(self):
        """Test that dumping a bool has expected output"""
        response = self.client.get('/simple?type=bool')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_bool</span></span>: <span class="type" title="bool">bool</span> <code class="bool">True</code>'
        self.assertContains(response, expected, html=True)

    # TODO: Finish this test. May require more work with django to test.
    # def test_dd_for_bound_field(self):
    #     response = self.client.get('/simple?type=bound_field')
    #     expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_bound</span></span>: <code class="bound">?????</code>'
    #     self.assertContains(response, expected, html=True)

    def test_dd_for_bytes(self):
        """Test that dumping bytes has expected output"""
        response = self.client.get('/simple?type=bytes')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_bytes</span></span>: <span class="type" title="bytes">bytes</span> <code class="number">b&#x27;test bytes&#x27;</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_decimal(self):
        """Test that dumping a Decimal has expected output"""
        response = self.client.get('/simple?type=decimal')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_decimal</span></span>: <span class="type" title="Decimal">Decimal</span> <code class="number">23.5</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_float(self):
        """Test that dumping a float has expected output"""
        response = self.client.get('/simple?type=float')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_float</span></span>: <span class="type" title="float">float</span> <code class="number">23.5</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_int(self):
        """Test that dumping a int has expected output"""
        response = self.client.get('/simple?type=int')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_int</span></span>: <span class="type" title="int">int</span> <code class="number">23</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_module(self):
        """Test that dumping a module has expected output"""
        response = self.client.get('/simple?type=module')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_module</span></span>: <span class="type" title="module">module</span> <code class="module">&lt;module &#x27;django.http&#x27;&gt;</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_string(self):
        """Test that dumping a string has expected output"""
        response = self.client.get('/simple?type=string')
        expected = '<span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_string</span></span>: <span class="type" title="str">str</span> <code class="string">&#x27;test string&#x27;</code>'
        self.assertContains(response, expected, html=True)


class DumpDieViewDataStructureTestCase(GenericViewTestCase):
    """Class for testing dumped data structures via a view"""

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dd_for_list(self, mocked_unique_generation):
        """Test that dumping a list has expected output"""

        mocked_unique_generation.side_effect = [
            (f'list_{9000}', ''),
            (f'str_{9001}', ''),
            (f'int_{9002}', ''),
            (f'bool_{9003}', ''),
        ]

        response = self.client.get('/data_structure?type=list')
        expected = '''
            <span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_list</span></span>:
            <span class="type" title="list">list:3</span>
            <span class="braces">[</span>
            <a class="arrow-toggle collapsed" title="[Ctrl+click] Expand all children" data-toggle="collapse" data-target=".list_9000" data-dd-type="type" aria-label="Close" aria-expanded="false" >
                <span class="unique" data-highlight-unique="list_9000">list_9000</span>
                <span id="arrow-list_9000" class="arrow">▶</span>
            </a>
            <div
                class="dd-wrapper collapse list_9000"
                data-unique="list_9000"
            >
                <ul class="attribute-list">
                    <a class="arrow-toggle show always-show" title="[Ctrl+click] Expand all children" data-target=".list_9000-attributes" data-dd-type="attr" aria-label="Open/Close" aria-expanded="" >
                        <span>Attributes</span>
                        <span id="arrow-list_9000-attributes" class="arrow"></span>
                    </a>
                    <div
                        class="li-wrapper collapse list_9000-attributes show"
                        data-unique-attributes="list_9000-attributes"
                    >
                        <li>
                            <span class="index" title="Index">0</span>:
                            <span class="type" title="str">str</span>
                            <code class="string">&#x27;A&#x27;</code>
                        </li>
                        <li>
                            <span class="index" title="Index">1</span>:
                            <span class="type" title="int">int</span>
                            <code class="number">12</code>
                        </li>
                        <li>
                            <span class="index" title="Index">2</span>:
                            <span class="type" title="bool">bool</span>
                            <code class="bool">True</code>
                        </li>
                    </div>
                </ul>
                <ul class="attribute-list">
                </ul>
            </div>
            <span class="braces">]</span>
        '''
        self.assertContains(response, expected, html=True)

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dd_for_dict(self, mocked_unique_generation):
        """Test that dumping a dict has expected output"""

        mocked_unique_generation.side_effect = [
            (f'dict_{9004}', ''),
            (f'str_{9005}', ''),
            (f'int_{9006}', ''),
            (f'bool_{9007}', ''),
        ]

        response = self.client.get('/data_structure?type=dict')
        expected = '''
            <span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_dict</span></span>:
            <span class="type" title="dict">dict:3</span>
            <span class="braces">{</span>
            <a class="arrow-toggle collapsed" title="[Ctrl+click] Expand all children" data-toggle="collapse" data-target=".dict_9004" data-dd-type="type" aria-label="Close" aria-expanded="false" >
                <span class="unique" data-highlight-unique="dict_9004">dict_9004</span>
                <span id="arrow-dict_9004" class="arrow">▶</span>
            </a>
            <div
                class="dd-wrapper collapse dict_9004"
                data-unique="dict_9004"
            >
                <ul class="attribute-list">
                    <a class="arrow-toggle show always-show" title="[Ctrl+click] Expand all children" data-target=".dict_9004-attributes" data-dd-type="attr" aria-label="Open/Close" aria-expanded="" >
                        <span>Attributes</span>
                        <span id="arrow-dict_9004-attributes" class="arrow"></span>
                    </a>
                    <div
                        class="li-wrapper collapse dict_9004-attributes show"
                        data-unique-attributes="dict_9004-attributes"
                    >
                        <li>
                            <span class="key" title="Key">&#x27;char&#x27;</span>:
                            <span class="type" title="str">str</span>
                            <code class="string">&#x27;A&#x27;</code>
                        </li>
                        <li>
                            <span class="key" title="Key">&#x27;num&#x27;</span>:
                            <span class="type" title="int">int</span>
                            <code class="number">12</code>
                        </li>
                        <li>
                            <span class="key" title="Key">&#x27;bool&#x27;</span>:
                            <span class="type" title="bool">bool</span>
                            <code class="bool">True</code>
                        </li>
                    </div>
                </ul>
                <ul class="attribute-list">
                </ul>
            </div>
            <span class="braces">}</span>
        '''
        self.assertContains(response, expected, html=True)

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dd_for_tuple(self, mocked_unique_generation):
        """Test that dumping a tuple has expected output"""

        mocked_unique_generation.side_effect = [
            (f'tuple_{9008}', ''),
            (f'str_{9009}', ''),
            (f'int_{9010}', ''),
            (f'bool_{9011}', ''),
        ]

        response = self.client.get('/data_structure?type=tuple')
        expected = '''
            <span class="dumped_object" title="Dumped Object"><span class="dumped_name">test_tuple</span></span>:
            <span class="type" title="tuple">tuple:3</span>
            <span class="braces">(</span>
            <a class="arrow-toggle collapsed" title="[Ctrl+click] Expand all children" data-toggle="collapse" data-target=".tuple_9008" data-dd-type="type" aria-label="Close" aria-expanded="false" >
                <span class="unique" data-highlight-unique="tuple_9008">tuple_9008</span>
                <span id="arrow-tuple_9008" class="arrow">▶</span>
            </a>
            <div
                class="dd-wrapper collapse tuple_9008"
                data-unique="tuple_9008"
            >
                <ul class="attribute-list">
                    <a class="arrow-toggle show always-show" title="[Ctrl+click] Expand all children"data-target=".tuple_9008-attributes" data-dd-type="attr" aria-label="Open/Close" aria-expanded="" >
                        <span>Attributes</span>
                        <span id="arrow-tuple_9008-attributes" class="arrow"></span>
                    </a>
                    <div
                        class="li-wrapper collapse tuple_9008-attributes show"
                        data-unique-attributes="tuple_9008-attributes"
                    >
                        <li>
                            <span class="index" title="Index">0</span>:
                            <span class="type" title="str">str</span>
                            <code class="string">&#x27;A&#x27;</code>
                        </li>
                        <li>
                            <span class="index" title="Index">1</span>:
                            <span class="type" title="int">int</span>
                            <code class="number">12</code>
                        </li>
                        <li>
                            <span class="index" title="Index">2</span>:
                            <span class="type" title="bool">bool</span>
                            <code class="bool">True</code>
                        </li>
                    </div>
                </ul>
                <ul class="attribute-list">
                </ul>
            </div>
            <span class="braces">)</span>
        '''
        self.assertContains(response, expected, html=True)

    @patch('django_dump_die.templatetags.dump_die._generate_unique')
    def test_dd_for_set(self, mocked_unique_generation):
        """Test that dumping a set has expected output

        NOTE: This test more fragile than the others due to the way it is
        checking for the expected HTML. Due to the fact that this is testing a
        set, order is not guaranteed and thus makes testing a little more
        difficult when checking for the output HTML.
        """

        mocked_unique_generation.side_effect = [
            (f'set_{9012}', ''),
            (f'str_{9013}', ''),
            (f'int_{9014}', ''),
            (f'bool_{9015}', ''),
        ]

        response = self.client.get('/data_structure?type=set')
        expected_first_half = '''
            <span class="dumped_object" title="Dumped Object"> <span class="dumped_name">test_set</span> </span>:
            <span class="type" title="set">set:3</span>
            <span class="braces">{</span>
            <a class="arrow-toggle collapsed" title="[Ctrl+click] Expand all children" data-toggle="collapse" data-target=".set_9012" data-dd-type="type" aria-label="Close" aria-expanded="false" >
                <span class="unique" data-highlight-unique="set_9012">set_9012</span>
                <span id="arrow-set_9012" class="arrow"> ▶ </span>
            </a>
            <div
                class="dd-wrapper collapse set_9012 "
                data-unique="set_9012"
            >
                <ul class="attribute-list">
                    <a class="arrow-toggle show always-show" title="[Ctrl+click] Expand all children" data-target=".set_9012-attributes" data-dd-type="attr" aria-label="Open/Close" aria-expanded="" >
                        <span>Attributes</span>
                        <span id="arrow-set_9012-attributes" class="arrow">  </span>
                    </a>
                    <div
                        class="li-wrapper collapse set_9012-attributes show"
                        data-unique-attributes="set_9012-attributes"
                    >
        '''
        expected_first_half = ' '.join(expected_first_half.split())

        expected_last_half = '''
                        </li>
                    </div>
                </ul>
                <ul class="attribute-list">
                </ul>
            </div>
            <span class="braces">}</span>
        '''
        expected_last_half = ' '.join(expected_last_half.split())

        expected_set1 = '<li> <span class="type" title="str">str</span> <code class="string">&#x27;A&#x27;</code> </li>'
        expected_set2 = '<li> <span class="type" title="int">int</span> <code class="number">12</code> </li>'
        expected_set3 = '<li> <span class="type" title="bool">bool</span> <code class="bool">True</code> </li>'

        actual = ' '.join((response.content.decode()).split())

        # Can't just compare using html=True as the inner part is a set and
        # so order can't be guaranteed. Instead going to compare each
        # part individually removing any whitespace.
        # NOTE: This test is fragile as a result.
        self.assertIn(expected_first_half, actual)
        self.assertIn(expected_set1, actual)
        self.assertIn(expected_set2, actual)
        self.assertIn(expected_set3, actual)
        self.assertIn(expected_last_half, actual)
