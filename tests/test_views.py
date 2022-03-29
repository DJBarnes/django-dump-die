from django.test import TestCase as TestCase
from django.test import override_settings


@override_settings(DEBUG=True)
class GenericViewTestCase(TestCase):
    """Base class for all tests"""
    pass


class DumpDieViewTestCase(GenericViewTestCase):
    """Class for testing views"""

    def test_dd_for_bool(self):
        response = self.client.get('/simple?type=bool')
        expected = '<span title="Dumped Object">test_bool</span>: <code class="bool">True</code>'
        self.assertContains(response, expected, html=True)

    # TODO: Finish this test. May require more work with django to test.
    # def test_dd_for_bound_field(self):
    #     response = self.client.get('/simple?type=bound_field')
    #     expected = '<span title="Dumped Object">test_bound</span>: <code class="bound">?????</code>'
    #     self.assertContains(response, expected, html=True)

    def test_dd_for_bytes(self):
        response = self.client.get('/simple?type=bytes')
        expected = '<span title="Dumped Object">test_bytes</span>: <code class="number">b&#x27;test bytes&#x27;</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_decimal(self):
        # TODO: Fix this test as it should not need "Decimal('23.5)" and should be able to just test for 23.5.
        response = self.client.get('/simple?type=decimal')
        expected = '<span title="Dumped Object">test_decimal</span>: <code class="number">Decimal(\'23.5\')</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_float(self):
        response = self.client.get('/simple?type=float')
        expected = '<span title="Dumped Object">test_float</span>: <code class="number">23.5</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_int(self):
        response = self.client.get('/simple?type=int')
        expected = '<span title="Dumped Object">test_int</span>: <code class="number">23</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_module(self):
        response = self.client.get('/simple?type=module')
        expected = '<span title="Dumped Object">test_module</span>: <code class="module">&lt;module &#x27;django.http&#x27;&gt;</code>'
        self.assertContains(response, expected, html=True)

    def test_dd_for_string(self):
        response = self.client.get('/simple?type=string')
        expected = '<span title="Dumped Object">test_string</span>: <code class="string">&#x27;test string&#x27;</code>'
        self.assertContains(response, expected, html=True)

