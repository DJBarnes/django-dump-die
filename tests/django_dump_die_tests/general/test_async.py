"""
Tests for the DumpDie middleware under ASGI, with async views.
"""

# System Imports.
from unittest import skipIf
from unittest.mock import patch

# Third-Party Imports.
import django
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

# Async views, async middleware, and the AsyncClient came in Django 3.1.
ASYNC_SUPPORTED = django.VERSION >= (3, 1)
if ASYNC_SUPPORTED:
    from asgiref.sync import sync_to_async

    try:
        from asgiref.sync import iscoroutinefunction
    except ImportError:
        # asgiref before 3.6, as installed on Python 3.6.
        from asyncio import iscoroutinefunction
    from django.core.handlers import base
    from django.core.handlers.asgi import ASGIHandler

    from django_dump_die.middleware import DumpAndDieMiddleware


@skipIf(not ASYNC_SUPPORTED, "Async middleware needs Django 3.1 or later.")
@override_settings(DEBUG=True)
class DumpDieAsyncTestCase(TestCase):
    """Verify dumping from async views, and that the middleware runs async under ASGI."""

    async def test_dump_in_async_view_shows_dump_page(self):
        """Verify dump() in an async view shows the dump page instead of the view's response."""
        response = await self.async_client.get(reverse("django_dump_die__tests__general:async_dump"))
        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Dumped from an async view.", content)
        self.assertNotIn("Async page content.", content)

    async def test_dd_in_async_view_shows_dump_page(self):
        """Verify dd() in an async view shows the dump page."""
        response = await self.async_client.get(reverse("django_dump_die__tests__general:async_dd"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("Dd from an async view.", response.content.decode("utf-8"))

    async def test_queryset_dumped_in_async_view_is_rendered(self):
        """Verify a QuerySet dumped in an async view renders, which needs the dump page rendered in a thread."""
        await sync_to_async(User.objects.create)(username="async_user")
        response = await self.async_client.get(reverse("django_dump_die__tests__general:async_queryset"))
        content = response.content.decode("utf-8")

        # The QuerySet was evaluated while rendering, so its user is shown.
        self.assertEqual(response.status_code, 200)
        self.assertIn('<span class="type" title="User">User</span>', content)
        self.assertIn("async_user", content)
        self.assertNotIn("SynchronousOnlyOperation", content)

    def test_middleware_is_async_with_an_async_handler(self):
        """Verify the middleware is async when Django gives it an async handler, and sync otherwise."""

        async def async_get_response(request):
            return None

        def sync_get_response(request):
            return None

        self.assertTrue(DumpAndDieMiddleware.async_capable)
        self.assertTrue(DumpAndDieMiddleware.sync_capable)
        self.assertTrue(iscoroutinefunction(DumpAndDieMiddleware(async_get_response)))
        self.assertFalse(iscoroutinefunction(DumpAndDieMiddleware(sync_get_response)))

    @override_settings(MIDDLEWARE=["django_dump_die.middleware.DumpAndDieMiddleware"])
    def test_asgi_middleware_chain_does_not_switch_to_sync(self):
        """Verify that under ASGI, Django builds the middleware chain without wrapping anything in async_to_sync."""
        adapted = []

        def recording_async_to_sync(method, *args, **kwargs):
            adapted.append(method)
            return original_async_to_sync(method, *args, **kwargs)

        original_async_to_sync = base.async_to_sync
        with patch.object(base, "async_to_sync", recording_async_to_sync):
            ASGIHandler()

        self.assertEqual(adapted, [])
