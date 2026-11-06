"""
Tests for how the DumpDie middleware changes responses: the dump page, the error page, and what it never shows.
"""

# Third-Party Imports.
from django.http import FileResponse, HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import DumpAndDieMiddleware, dump

ERROR_PAGE = "<html><head><title>Error</title></head><body><h1>Error</h1></body></html>"
PAGE = '<html><head><title>Page</title></HEAD><BODY class="page"><h1>Page</h1></body></html>'


def get_response_that_keeps_the_dump_page(label):
    """Return a response that dumps can't be shown above, so that the dump page replaces it."""
    if label == "json":
        return JsonResponse({"page": "<body>"})
    if label == "redirect":
        return HttpResponseRedirect("/elsewhere/")
    if label == "streaming":
        return StreamingHttpResponse(iter([PAGE]))
    if label == "file":
        return FileResponse(iter([PAGE.encode("utf-8")]), content_type="text/html")
    if label == "compressed":
        response = HttpResponse(PAGE)
        response["Content-Encoding"] = "gzip"
        return response
    if label == "no body":
        return HttpResponse("<p>A fragment, such as for htmx.</p>")
    # Content that can't be decoded with the response's charset.
    return HttpResponse(b"<html><body>\xff</body></html>", content_type="text/html; charset=utf-8")


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


@override_settings(DEBUG=True, DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE=True)
class DumpDieAbovePageTestCase(SimpleTestCase):
    """Verify dumps shown above a page's own content, with DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE on."""

    def tearDown(self):
        middleware.dump_objects.clear()
        super().tearDown()

    def test_dumps_are_added_to_the_top_of_the_body(self):
        """Verify the dumps follow the body tag, with its attributes, and the CSS and JS end the head."""
        response = HttpResponse(PAGE)
        response["Content-Length"] = str(len(PAGE))
        value = 42
        dump(value)

        response = process_response(response)
        content = response.content.decode("utf-8")

        head, body = content.split('<BODY class="page">')
        self.assertIn("django_dump_die/css/dd.css", head)
        self.assertIn("django_dump_die/js/dd.js", head)
        self.assertTrue(head.endswith("</HEAD>"))
        self.assertTrue(body.lstrip().startswith('<div class="dump-die-above-page">'))
        self.assertLess(body.index('<span class="dumped_name">value</span>'), body.index("<h1>Page</h1>"))
        self.assertEqual(response["Content-Length"], str(len(response.content)))
        self.assertEqual(middleware.dump_objects, [])

    def test_page_without_a_head_gets_the_css_and_js_in_its_body(self):
        """Verify a page without a head gets the CSS and JS at the start of its body, before the dumps."""
        value = 42
        dump(value)

        response = process_response(HttpResponse("<body><h1>Page</h1></body>"))
        content = response.content.decode("utf-8")

        self.assertTrue(content.startswith("<body>"))
        self.assertLess(content.index("django_dump_die/css/dd.css"), content.index('class="dump-die-above-page"'))
        self.assertIn("<h1>Page</h1>", content)

    def test_page_in_another_charset_keeps_its_charset(self):
        """Verify the page is read and written in its own charset."""
        page = "<html><head></head><body><p>Caf\u00e9</p></body></html>"
        value = 42
        dump(value)

        response = process_response(HttpResponse(page.encode("latin-1"), content_type="text/html; charset=latin-1"))

        self.assertIn("<p>Caf\u00e9</p>", response.content.decode("latin-1"))
        self.assertIn('class="dump-die-above-page"', response.content.decode("latin-1"))

    def test_responses_that_are_not_html_pages_are_replaced_by_the_dump_page(self):
        """Verify responses that dumps can't be added to still get the dump page, so that the dumps aren't lost."""
        for label in ("json", "redirect", "streaming", "file", "compressed", "no body", "undecodable"):
            with self.subTest(response=label):
                value = 42
                dump(value)

                response = process_response(get_response_that_keeps_the_dump_page(label))
                content = response.content.decode("utf-8")

                self.assertEqual(response.status_code, 200)
                self.assertIn("<title>DD</title>", content)
                self.assertIn('<span class="dumped_name">value</span>', content)
                self.assertNotIn("dump-die-above-page", content)

    @override_settings(DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE=False)
    def test_page_is_replaced_by_default(self):
        """Verify the dump page replaces an HTML page when the setting is off, as it is by default."""
        value = 42
        dump(value)

        content = process_response(HttpResponse(PAGE)).content.decode("utf-8")

        self.assertIn("<title>DD</title>", content)
        self.assertNotIn("<h1>Page</h1>", content)


@override_settings(DEBUG=True)
class DumpDieErrorPageTestCase(SimpleTestCase):
    """Verify dumps added to Django's error page after an unhandled exception."""

    def tearDown(self):
        middleware.dump_objects.clear()
        super().tearDown()

    def test_dumps_are_added_above_the_error_page(self):
        """Verify the dumps are in the same wrapper as dumps above a page, so the toolbar doesn't cover the error."""
        value = 42
        dump(value)

        content = process_response(HttpResponse(ERROR_PAGE, status=500), has_non_dd_exception=True).content.decode()

        self.assertLess(content.index('<div class="dump-die-above-page">'), content.index("<h1>Error</h1>"))

    def test_error_that_is_not_an_html_page_is_returned_unchanged(self):
        """Verify an error response that dumps can't be added to, such as plain text, is kept, and dumps dropped."""
        original = HttpResponse("Error", status=500, content_type="text/plain")
        value = 42
        dump(value)

        response = process_response(original, has_non_dd_exception=True)

        self.assertIs(response, original)
        self.assertEqual(response.content, b"Error")
        self.assertEqual(middleware.dump_objects, [])

    @override_settings(DJANGO_DD_SHOW_DUMPS_ON_ERROR_PAGE=False)
    def test_error_page_is_left_unchanged_when_turned_off(self):
        """Verify the error page gets no dumps, and the dumps are dropped, when the setting is off."""
        value = 42
        dump(value)

        response = process_response(HttpResponse(ERROR_PAGE, status=500), has_non_dd_exception=True)

        self.assertEqual(response.content.decode("utf-8"), ERROR_PAGE)
        self.assertEqual(middleware.dump_objects, [])
