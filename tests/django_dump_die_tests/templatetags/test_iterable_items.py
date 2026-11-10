"""
Tests for which items of a dumped iterable are listed: the first DJANGO_DD_MAX_ITERABLE_LENGTH, or the root object's
index_range, with one line for the items before and after them. QuerySets only fetch the rows that are dumped.
"""

# System Imports.
import re

# Third-Party Imports.
from django.contrib.auth.models import User
from django.db import connection
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext

# Internal Imports.
from django_dump_die_tests.collected_dumps import CollectDumpsMixin
from django_dump_die import middleware
from django_dump_die.middleware import dump
from django_dump_die.utils import generate_unique_from_obj


class Item:
    """Object to put in iterables, which is expanded when dumped."""

    def __init__(self, number):
        self.number = number


def render_dumped_objects():
    """Render everything collected by dump() calls, then clear the collected objects."""
    objects = middleware.get_dump_objects()[:]
    middleware.get_dump_objects().clear()
    return Template("{% load dump_die %}{% dump_objects objects %}").render(Context({"objects": objects}))


def index(number):
    """Return the label of an item's index."""
    return f'<span class="index" title="Index">{number}</span>'


def not_dumped(text):
    """Return the line shown in place of the items that aren't dumped, such as '… 5 more'."""
    return f'title="Not dumped, to keep large iterables fast. [^"]*">… {text}</span>'


def expanded(obj):
    """Return the start of the expanded section of an object."""
    return f'data-unique="{generate_unique_from_obj(obj)}"'


@override_settings(DEBUG=True)
class DumpDieIterableItemsTestCase(CollectDumpsMixin, SimpleTestCase):
    """Verify only the dumped items of an iterable are listed, followed by how many more there are."""

    def tearDown(self):
        middleware.get_dump_objects().clear()
        super().tearDown()

    def test_items_past_the_limit_are_not_listed(self):
        """Verify a list longer than the limit lists only its first items, simple ones too, then how many more."""
        numbers = list(range(100, 125))
        dump(numbers)
        content = render_dumped_objects()

        self.assertIn('<span class="type" title="list">list:25</span>', content)
        self.assertIn(index(19), content)
        self.assertIn('<code class="number">119</code>', content)
        self.assertNotIn(index(20), content)
        # Not just "120", which can be part of a unique.
        self.assertNotIn('<code class="number">120</code>', content)
        self.assertRegex(content, not_dumped("5 more"))

    @override_settings(DJANGO_DD_MAX_ITERABLE_LENGTH=2)
    def test_objects_past_the_limit_are_not_listed(self):
        """Verify objects past the limit aren't listed at all, not even by their unique."""
        items = [Item(1), Item(2), Item(3)]
        dump(items)
        content = render_dumped_objects()

        self.assertIn(expanded(items[0]), content)
        self.assertIn(expanded(items[1]), content)
        self.assertNotIn(generate_unique_from_obj(items[2]), content)
        self.assertRegex(content, not_dumped("1 more"))

    def test_list_within_the_limit_has_no_more_line(self):
        """Verify a list no longer than the limit lists every item, without a line for items not dumped."""
        numbers = list(range(20))
        dump(numbers)
        content = render_dumped_objects()

        self.assertIn(index(19), content)
        self.assertNotIn("…", content)

    @override_settings(DJANGO_DD_MAX_ITERABLE_LENGTH=2)
    def test_set_past_the_limit(self):
        """Verify a set lists only as many items as the limit, then how many more."""
        numbers = {1, 2, 3, 4, 5}
        dump(numbers)
        content = render_dumped_objects()

        self.assertIn('<span class="type" title="set">set:5</span>', content)
        self.assertEqual(content.count('<code class="number">'), 2)
        self.assertRegex(content, not_dumped("3 more"))

    @override_settings(DJANGO_DD_MAX_ITERABLE_LENGTH=2)
    def test_dict_lists_every_item(self):
        """Verify the limit doesn't apply to dicts, so that settings and request.META can be read in full."""
        values = {"first": 1, "second": 2, "third": 3}
        dump(values)
        content = render_dumped_objects()

        self.assertIn("third", content)
        self.assertNotIn("…", content)

    @override_settings(DJANGO_DD_MAX_ITERABLE_LENGTH=2)
    def test_nested_iterables_have_their_own_limit(self):
        """Verify the limit applies to each nested iterable, and the root's index_range only to the root."""
        rows = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        dump(rows, index_range=(0, 3))
        content = render_dumped_objects()

        for row in rows:
            self.assertIn(expanded(row), content)
        self.assertEqual(len(re.findall(not_dumped("1 more"), content)), 3)

    @override_settings(DJANGO_DD_MAX_ITERABLE_LENGTH=None)
    def test_no_limit(self):
        """Verify a limit of None lists every item, of the root and nested iterables."""
        items = [Item(number) for number in range(25)]
        dump([items])
        content = render_dumped_objects()

        for item in items:
            self.assertIn(expanded(item), content)
        self.assertNotIn("…", content)

    def test_index_range_in_the_middle(self):
        """Verify an index_range lists its items with their own indexes, after the items before it."""
        numbers = list(range(100, 130))
        dump(numbers, index_range=(10, 15))
        content = render_dumped_objects()

        self.assertRegex(content, not_dumped("10 before") + r"\s*</li>\s*<li>\s*" + index(10))
        self.assertIn(index(14), content)
        self.assertNotIn(index(9), content)
        self.assertNotIn(index(15), content)
        self.assertRegex(content, not_dumped("15 more"))

    def test_index_range_past_the_end(self):
        """Verify an index_range past the end lists only how many items are before it."""
        numbers = list(range(10))
        dump(numbers, index_range=(50, 60))
        content = render_dumped_objects()

        self.assertRegex(content, not_dumped("10 before"))
        self.assertNotIn(index(0), content)
        self.assertNotIn("more</span>", content)

    def test_large_list_lists_only_the_limit(self):
        """Verify a list of a million items is dumped as quickly as a short one, since only 20 items are listed."""
        numbers = list(range(1000000))
        dump(numbers)
        content = render_dumped_objects()

        self.assertEqual(content.count("<li>"), 21)
        self.assertRegex(content, not_dumped("999980 more"))


@override_settings(DEBUG=True)
class DumpDieQuerySetItemsTestCase(CollectDumpsMixin, TestCase):
    """Verify a dumped QuerySet fetches only the rows that are dumped, and counts the rest."""

    @classmethod
    def setUpTestData(cls):
        User.objects.bulk_create([User(username=f"user{number:02}") for number in range(25)])

    def tearDown(self):
        middleware.get_dump_objects().clear()
        super().tearDown()

    def test_queryset_fetches_only_the_dumped_rows(self):
        """Verify the QuerySet is counted, and only the first rows fetched, not loaded in full."""
        users = User.objects.order_by("username")
        with CaptureQueriesContext(connection) as queries:
            dump(users)
            content = render_dumped_objects()

        sql = [query["sql"] for query in queries.captured_queries]
        self.assertEqual(len(sql), 2, sql)
        self.assertIn("COUNT(", sql[0])
        self.assertIn("LIMIT 20", sql[1])
        self.assertIn('<span class="type" title="QuerySet">QuerySet:25</span>', content)
        self.assertIn("user19", content)
        self.assertNotIn("user20", content)
        self.assertRegex(content, not_dumped("5 more"))
        # A QuerySet is dumped as itself, with its own members, and not as a list.
        self.assertIn(">ordered</span>", content)
        self.assertNotIn(">append</span>", content)

    def test_evaluated_queryset_runs_no_query(self):
        """Verify a QuerySet that was already evaluated is counted and dumped from its results, with no query."""
        users = User.objects.order_by("username")
        list(users)
        with CaptureQueriesContext(connection) as queries:
            dump(users)
            content = render_dumped_objects()

        self.assertEqual(len(queries), 0)
        self.assertIn('<span class="type" title="QuerySet">QuerySet:25</span>', content)
        self.assertRegex(content, not_dumped("5 more"))

    def test_index_range_of_queryset(self):
        """Verify an index_range of a QuerySet fetches only its rows, with an offset."""
        users = User.objects.order_by("username")
        with CaptureQueriesContext(connection) as queries:
            dump(users, index_range=(5, 8))
            content = render_dumped_objects()

        self.assertIn("LIMIT 3 OFFSET 5", queries.captured_queries[-1]["sql"])
        self.assertRegex(content, not_dumped("5 before"))
        self.assertIn(index(5), content)
        self.assertIn("user07", content)
        self.assertNotIn("user08", content)
        self.assertRegex(content, not_dumped("17 more"))

    def test_deep_copied_queryset_fetches_only_the_dumped_rows(self):
        """Verify matching a deep-copied QuerySet to the original, for their uniques, doesn't load all their rows."""
        users = User.objects.order_by("username")
        with CaptureQueriesContext(connection) as queries:
            dump(users, deepcopy=True)
            content = render_dumped_objects()

        sql = [query["sql"] for query in queries.captured_queries]
        self.assertEqual(len(sql), 2, sql)
        self.assertIn('<span class="type" title="QuerySet">QuerySet:25</span>', content)

    def test_queryset_nested_in_another_object(self):
        """Verify a QuerySet that isn't the dumped object itself also fetches only the dumped rows."""
        values = {"users": User.objects.order_by("username")}
        with CaptureQueriesContext(connection) as queries:
            dump(values)
            content = render_dumped_objects()

        self.assertEqual(len(queries), 2)
        self.assertIn("LIMIT 20", queries.captured_queries[1]["sql"])
        self.assertIn('<span class="type" title="QuerySet">QuerySet:25</span>', content)
