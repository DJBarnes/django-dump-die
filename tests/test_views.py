from django.test import TestCase as TestCase
from django.test import override_settings
from django.utils import html


@override_settings(DEBUG=True)
class GenericViewTestCase(TestCase):
    """Base class for all tests"""
    pass


class DumpDieViewTestCase(GenericViewTestCase):
    """Class for testing views"""

    def test_dd_for_string(self):
        response = self.client.get('/string/')
        expected = 'my test string'
        self.assertContains(response, html.escape(expected))
