"""
Test helper that collects the objects dumped in a test, as a request does.
"""

# Internal Imports.
from django_dump_die.functions import collect_dumps


class CollectDumpsMixin:
    """Collect the objects each test dumps, as during a request, so that the test can render them.

    Outside of a request, dump() prints to the console instead. Put it before the TestCase class.
    """

    def setUp(self):
        super().setUp()
        collecting = collect_dumps()
        collecting.__enter__()
        self.addCleanup(collecting.__exit__, None, None, None)
