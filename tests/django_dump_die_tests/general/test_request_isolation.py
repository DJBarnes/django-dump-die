"""
Tests that each request only shows its own dumps, and each page of dumps keeps its own records, even when requests
and pages run at the same time.
"""

# System Imports.
import asyncio
import contextvars
import threading

# Third-Party Imports.
from django.http import HttpResponse
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, override_settings

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.middleware import DumpAndDieMiddleware, dump
from django_dump_die.utils import generate_unique_from_obj

PAGE = "<html><head></head><body><h1>Page</h1></body></html>"
# How long a test waits for another thread or task, so that a broken test fails instead of hanging.
TIMEOUT = 10


def run_in_threads(*targets):
    """Run each target in its own thread, and return their results, or raise the first exception.

    Each runs in a new, empty context, as a thread does by default, so that the results don't depend on whether
    threads copy their parent's context, as they can on Python 3.14.
    """
    results = [None] * len(targets)
    errors = []

    def run(index, target):
        try:
            results[index] = contextvars.Context().run(target)
        except Exception as exception:  # Raised again in the test's thread below.
            errors.append(exception)

    threads = [threading.Thread(target=run, args=(index, target)) for index, target in enumerate(targets)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(TIMEOUT)
    if errors:
        raise errors[0]
    return results


def render_page():
    """Render a page of the objects dumped in this context, as the dump page does."""
    objects = middleware.get_dump_objects()[:]
    return Template("{% load dump_die %}{% dump_objects objects %}").render(Context({"objects": objects}))


@override_settings(DEBUG=True)
class DumpDieRequestIsolationTestCase(SimpleTestCase):
    """Verify each request shows only the objects dumped during it."""

    def tearDown(self):
        middleware.get_dump_objects().clear()
        super().tearDown()

    def test_requests_in_threads_show_only_their_own_dumps(self):
        """Verify two requests running at the same time in threads, as with runserver, each show their own dumps."""
        # Both requests dump before either one's response is handled, as when they run at the same time.
        both_dumped = threading.Barrier(2, timeout=TIMEOUT)

        def request(text):
            def view(request):
                dump(text)
                both_dumped.wait()
                return HttpResponse(PAGE)

            return lambda: DumpAndDieMiddleware(view)(RequestFactory().get("/")).content.decode("utf-8")

        first, second = run_in_threads(request("dumped by the first"), request("dumped by the second"))

        self.assertIn("dumped by the first", first)
        self.assertNotIn("dumped by the second", first)
        self.assertIn("dumped by the second", second)
        self.assertNotIn("dumped by the first", second)

    def test_async_requests_show_only_their_own_dumps(self):
        """Verify two async requests running at the same time on one event loop, as under ASGI, each show their own."""

        async def requests():
            # Set once both requests have dumped. (asyncio.Barrier needs Python 3.11.)
            both_dumped = asyncio.Event()
            dumped = []

            def request(text):
                async def view(request):
                    dump(text)
                    dumped.append(text)
                    if len(dumped) == 2:
                        both_dumped.set()
                    await asyncio.wait_for(both_dumped.wait(), TIMEOUT)
                    return HttpResponse(PAGE)

                return DumpAndDieMiddleware(view)(RequestFactory().get("/"))

            return await asyncio.gather(request("dumped by the first"), request("dumped by the second"))

        first, second = (response.content.decode("utf-8") for response in asyncio.run(requests()))

        self.assertIn("dumped by the first", first)
        self.assertNotIn("dumped by the second", first)
        self.assertIn("dumped by the second", second)
        self.assertNotIn("dumped by the first", second)

    def test_request_that_fails_leaves_no_dumps_for_the_next(self):
        """Verify a request that dumps, then fails before its response is handled, doesn't leave its dumps."""

        def failing_view(request):
            dump("dumped by the failed request")
            raise RuntimeError("The request failed.")

        with self.assertRaises(RuntimeError):
            DumpAndDieMiddleware(failing_view)(RequestFactory().get("/"))
        response = DumpAndDieMiddleware(lambda request: HttpResponse(PAGE))(RequestFactory().get("/"))

        self.assertEqual(response.content.decode("utf-8"), PAGE)

    def test_dumps_from_before_a_request_are_not_shown_in_it(self):
        """Verify a request starts without dumps, and dumps made outside of it are kept for where they were made."""
        dump("dumped outside the request")

        response = DumpAndDieMiddleware(lambda request: HttpResponse(PAGE))(RequestFactory().get("/"))

        self.assertEqual(response.content.decode("utf-8"), PAGE)
        self.assertEqual(len(middleware.get_dump_objects()), 1)


class Repeated:
    """Object dumped twice on a page."""

    def __init__(self):
        self.value = 1


class Paused:
    """Object that pauses its page while another page is rendered, by waiting while its members are read."""

    def __init__(self, paused, resume):
        self.paused = paused
        self.resume = resume

    @property
    def waits(self):
        """Wait for the other page, the first time the page reads it."""
        if not self.paused.is_set():
            self.paused.set()
            self.resume.wait(TIMEOUT)
        return "waited"


@override_settings(DEBUG=True)
class DumpDieRenderIsolationTestCase(SimpleTestCase):
    """Verify each page of dumps keeps its own records of repeated objects, while other pages are rendered."""

    def test_page_rendered_in_another_thread_does_not_reset_the_records(self):
        """Verify an object dumped twice on a page still gets its count, while another thread renders a page."""
        paused, resume = threading.Event(), threading.Event()
        repeated = Repeated()
        pause = Paused(paused, resume)

        def first_page():
            # The object is dumped twice, with an object between them that waits for the second page. So the second
            # page renders after the first dump of the object is rendered in full, and before the second.
            dump(repeated)
            dump(pause)
            dump(repeated)
            return render_page()

        def second_page():
            paused.wait(TIMEOUT)
            try:
                dump("on the second page")
                return render_page()
            finally:
                resume.set()

        first, second = run_in_threads(first_page, second_page)

        unique = generate_unique_from_obj(repeated)
        self.assertIn('data-unique="{0}"'.format(unique), first)
        self.assertIn('data-unique="{0}_1"'.format(unique), first)
        self.assertIn("on the second page", second)

    def test_dump_object_tag_outside_a_page_of_dumps(self):
        """Verify the dump_object tag works on its own, outside of a dump_objects tag, which sets up its records."""
        repeated = Repeated()

        def render():
            template = Template("{% load dump_die %}{% dump_object obj obj %}")
            return template.render(Context({"obj": repeated}))

        # A new context, without the records of a page rendered earlier.
        content = contextvars.Context().run(render)

        self.assertIn('data-unique="{0}"'.format(generate_unique_from_obj(repeated)), content)
