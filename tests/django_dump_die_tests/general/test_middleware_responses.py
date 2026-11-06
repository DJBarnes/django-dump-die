"""
Tests for how the DumpDie middleware changes responses: the dump page, the error page, and what it never shows.
"""

# Third-Party Imports.
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import DumpAndDieMiddleware, dump

ERROR_PAGE = "<html><head><title>Error</title></head><body><h1>Error</h1></body></html>"


def process_response(response, has_non_dd_exception=False):
    """Run the middleware's response handling for a response from the rest of the middleware chain."""
    request = RequestFactory().get("/")
    if has_non_dd_exception:
        request.has_non_dd_exception = True
    return DumpAndDieMiddleware(lambda request: response)(request)


class DumpDieMiddlewareResponseTestCase(SimpleTestCase):
    """Verify the responses the middleware returns, and that dumps are only ever shown with DEBUG on."""

    def tearDown(self):
        middleware.dump_objects.clear()
        super().tearDown()

    @override_settings(DEBUG=True)
    def test_error_page_with_dumps_gets_the_new_content_length(self):
        """Verify adding the dumps to an error page updates its Content-Length, such as one set by CommonMiddleware."""
        response = HttpResponse(ERROR_PAGE, status=500)
        response["Content-Length"] = str(len(ERROR_PAGE))
        value = 42
        dump(value)

        response = process_response(response, has_non_dd_exception=True)

        self.assertIn('<div class="dump-toolbar">', response.content.decode("utf-8"))
        self.assertIn("<h1>Error</h1>", response.content.decode("utf-8"))
        self.assertEqual(response["Content-Length"], str(len(response.content)))

    @override_settings(DEBUG=True)
    def test_error_page_without_content_length_gets_none(self):
        """Verify adding the dumps to an error page doesn't add a Content-Length header that it didn't have."""
        value = 42
        dump(value)

        response = process_response(HttpResponse(ERROR_PAGE, status=500), has_non_dd_exception=True)

        self.assertIn('<div class="dump-toolbar">', response.content.decode("utf-8"))
        self.assertFalse(response.has_header("Content-Length"))

    def test_dumps_collected_before_debug_was_turned_off_are_not_shown(self):
        """Verify dumps collected while DEBUG was on are dropped, not shown, if DEBUG is off by the response."""
        for has_non_dd_exception in (False, True):
            with self.subTest(has_non_dd_exception=has_non_dd_exception):
                original = HttpResponse(ERROR_PAGE)
                secret = "collected while DEBUG was on"
                with override_settings(DEBUG=True):
                    dump(secret)

                with override_settings(DEBUG=False):
                    response = process_response(original, has_non_dd_exception=has_non_dd_exception)

                self.assertIs(response, original)
                self.assertEqual(response.content.decode("utf-8"), ERROR_PAGE)
                self.assertEqual(middleware.dump_objects, [])
