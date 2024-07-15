"""
Tests for general DD functionality.
"""

# Third-Party Imports.
from django.test import override_settings
from django_expanded_test_cases import IntegrationTestCase


class DumpDieGeneralTestCase(IntegrationTestCase):
    """Verify handling of dumped "simple" types."""

    url = "django_dump_die:simple-type-example"

    @override_settings(DEBUG=False)
    def test_debug_off_skips_all_dumps(self):
        """Verify no dumps occur when debug is off."""
        self.assertGetResponse(
            self.url,
            expected_title="Sample page",
            expected_header="Sample page",
            expected_content=["<p>Sample page body content</p>"],
            expected_not_content=["<div><h1>Django DumpDie</h1></div>"],
        )
