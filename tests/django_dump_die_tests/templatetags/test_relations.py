"""
Tests for the Relations section of dumped model instances: which relations are followed, which show what is already
loaded, and which only say they aren't loaded.
"""

# System Imports.
import re
from unittest.mock import patch

# Third-Party Imports.
from django.db import connection
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

# Internal Imports.
from django_dump_die import middleware
from django_dump_die.console import format_dump
from django_dump_die.middleware import dump
from django_dump_die import utils
from django_dump_die.utils import get_related_object_lookups, get_relations
from django_dump_die.views.example_helpers import SampleDjangoModel
from django_dump_die_tests.collected_dumps import CollectDumpsMixin
from django_dump_die_tests.django_test_project.models import Author, AuthToken, Book, Note, Profile, Tag


def render_dumped_objects():
    """Render everything collected by dump() calls, then clear the collected objects."""
    objects = middleware.get_dump_objects()[:]
    middleware.get_dump_objects().clear()
    return Template("{% load dump_die %}{% dump_objects objects %}").render(Context({"objects": objects}))


def relation(name, title="Related Object"):
    """Return the start of a relation's row, by its name."""
    return f'<span class="attribute" title="{title}">{name}</span>:'


def not_loaded(name, title="Related Object"):
    """Return a pattern for a relation's row that says it isn't loaded."""
    return re.escape(relation(name, title)) + r'\s*<span class="empty" title="Not loaded, [^"]*">Not loaded</span>'


@override_settings(DEBUG=True)
class DumpDieRelationsTestCase(CollectDumpsMixin, TestCase):
    """Verify the Relations section of a dumped model instance."""

    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name="Ada")
        Profile.objects.create(author=cls.author, bio="Writes things.")
        AuthToken.objects.create(author=cls.author, key="secret-key")
        cls.tag = Tag.objects.create(name="science")
        book = Book.objects.create(author=cls.author, title="Notes")
        book.tags.add(cls.tag)

    def dumped(self, obj):
        """Dump an object, and return the page and the queries it ran, including the dump's own."""
        with CaptureQueriesContext(connection) as queries:
            dump(obj)
            content = render_dumped_objects()
        return content, [query["sql"] for query in queries.captured_queries]

    def test_related_object_is_followed(self):
        """Verify related objects that aren't loaded are loaded and shown, in a Relations section, up to the depth."""
        book = Book.objects.get(title="Notes")
        content, queries = self.dumped(book)

        # The book's author is one relation away, and the author's profile two, so both are within the default 3.
        self.assertIn('<span class="section_name">Relations</span>', content)
        self.assertIn(relation("author"), content)
        self.assertIn("&#x27;Ada&#x27;", content)
        self.assertIn("&#x27;Writes things.&#x27;", content)
        self.assertEqual(len(queries), 2, queries)

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0)
    def test_related_object_not_followed_at_depth_zero(self):
        """Verify a foreign key that isn't loaded says so, with how to load it, and isn't queried, at depth 0."""
        book = Book.objects.get(title="Notes")
        content, queries = self.dumped(book)

        self.assertRegex(content, not_loaded("author"))
        self.assertIn("select_related(&quot;author&quot;)", content)
        self.assertEqual(queries, [])

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0)
    def test_loaded_related_object_is_shown_at_depth_zero(self):
        """Verify a foreign key loaded with select_related() is shown without a query, even at depth 0."""
        book = Book.objects.select_related("author").get(title="Notes")
        content, queries = self.dumped(book)

        self.assertIn("&#x27;Ada&#x27;", content)
        self.assertEqual(queries, [])

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=1)
    def test_depth_counts_relations_from_the_dumped_object(self):
        """Verify relations of a related object are one more relation away, and not followed past the depth."""
        book = Book.objects.get(title="Notes")
        content, queries = self.dumped(book)

        # The book's author is one relation away. The author's profile is two.
        self.assertIn("&#x27;Ada&#x27;", content)
        self.assertRegex(content, not_loaded("profile"))
        self.assertEqual(len(queries), 1)

    def test_reverse_one_to_one(self):
        """Verify a reverse one-to-one is followed, and shows None when there is no related object."""
        content, _queries = self.dumped(Author.objects.get(name="Ada"))
        self.assertIn("&#x27;Writes things.&#x27;", content)

        lonely = Author.objects.create(name="Lonely")
        content, _queries = self.dumped(lonely)
        self.assertRegex(content, re.escape(relation("profile")) + r'\s*<span class="type" title="null">null</span>')

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0)
    def test_reverse_one_to_one_looked_up_without_an_object(self):
        """Verify a reverse one-to-one already looked up, without an object, shows None without a query."""
        lonely = Author.objects.create(name="Lonely")
        with self.assertRaises(Profile.DoesNotExist):
            lonely.profile  # noqa: B018 - Looking it up stores that there is no profile.
        content, queries = self.dumped(lonely)

        self.assertRegex(content, re.escape(relation("profile")) + r'\s*<span class="type" title="null">null</span>')
        self.assertEqual(queries, [])

    def test_relations_without_a_value(self):
        """Verify relations without anything to load show None without a query: an unset foreign key and generic key."""
        note = Note(text="Unattached")
        content, queries = self.dumped(note)

        self.assertRegex(content, re.escape(relation("content_type")) + r'\s*<span class="type" title="null">')
        self.assertRegex(content, re.escape(relation("target")) + r'\s*<span class="type" title="null">')
        self.assertEqual(queries, [])

    def test_generic_foreign_key(self):
        """Verify a generic foreign key with a value is followed, or says it isn't loaded at depth 0."""
        note_id = Note.objects.create(target=self.tag, text="About a tag").pk

        content, _queries = self.dumped(Note.objects.get(pk=note_id))
        self.assertIn("&#x27;science&#x27;", content)

        # A note fetched again, since following the relation above stored its object on that note.
        note = Note.objects.get(pk=note_id)
        with override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0):
            content, queries = self.dumped(note)
        self.assertRegex(content, not_loaded("target"))
        self.assertEqual(queries, [])

    def test_related_manager_is_not_loaded(self):
        """Verify a related manager says it isn't loaded, with how to load it, without a query."""
        book = Book.objects.get(title="Notes")
        with self.settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0):
            content, queries = self.dumped(book)

        self.assertRegex(content, not_loaded("tags", "Related Manager"))
        self.assertIn("prefetch_related(&quot;tags&quot;)", content)
        self.assertIn("DJANGO_DD_RELATED_MANAGER_DEPTH", content)
        self.assertEqual(queries, [])

    def test_prefetched_related_manager_is_shown(self):
        """Verify a related manager's rows loaded with prefetch_related() are shown, without a query, both ways."""
        book = Book.objects.prefetch_related("tags").get(title="Notes")
        author = Author.objects.prefetch_related("books").get(name="Ada")

        with self.settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0):
            book_content, book_queries = self.dumped(book)
            author_content, author_queries = self.dumped(author)

        self.assertRegex(
            book_content, re.escape(relation("tags", "Related Manager")) + r'\s*<span class="type"[^>]*>QuerySet:1'
        )
        self.assertIn("&#x27;science&#x27;", book_content)
        self.assertIn("&#x27;Notes&#x27;", author_content)
        self.assertEqual(book_queries + author_queries, [])

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0, DJANGO_DD_RELATED_MANAGER_DEPTH=1)
    def test_related_manager_is_followed(self):
        """Verify a related manager within DJANGO_DD_RELATED_MANAGER_DEPTH is counted, and its rows fetched."""
        book = Book.objects.get(title="Notes")
        content, queries = self.dumped(book)

        self.assertRegex(
            content, re.escape(relation("tags", "Related Manager")) + r'\s*<span class="type"[^>]*>QuerySet:1'
        )
        self.assertIn("&#x27;science&#x27;", content)
        self.assertEqual(len(queries), 2, queries)
        self.assertIn("COUNT(", queries[0])
        # The tag's own books are two relations away, past the depth.
        self.assertRegex(content, not_loaded("books", "Related Manager"))

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0, DJANGO_DD_RELATED_MANAGER_DEPTH=1)
    def test_followed_related_manager_fetches_only_the_rows_shown(self):
        """Verify a followed related manager with more rows than the limit only fetches the rows shown."""
        book = Book.objects.get(title="Notes")
        book.tags.add(*Tag.objects.bulk_create([Tag(name=f"tag{number:02}") for number in range(24)]))
        content, queries = self.dumped(book)

        self.assertRegex(
            content, re.escape(relation("tags", "Related Manager")) + r'\s*<span class="type"[^>]*>QuerySet:25'
        )
        self.assertIn("… 5 more", content)
        self.assertIn("LIMIT 20", queries[1])

    def test_related_manager_of_an_unsaved_object(self):
        """Verify a related manager that can't be used, on an object that isn't saved, shows why."""
        content, _queries = self.dumped(Book(title="Draft"))

        self.assertRegex(
            content, re.escape(relation("tags", "Related Manager")) + r'\s*<span class="empty"[^>]*>ValueError: '
        )

    @override_settings(DJANGO_DD_INCLUDE_FUNCTIONS=True)
    def test_relations_are_not_attributes_or_functions(self):
        """Verify relations are only in the Relations section, and not also attributes or functions."""
        content, _queries = self.dumped(Book.objects.get(title="Notes"))

        self.assertNotIn('<span class="attribute" title="Attribute">author</span>', content)
        self.assertNotIn('<span class="function">tags</span>', content)
        self.assertIn('<span class="attribute" title="Attribute">author_id</span>', content)

    def test_sensitive_relation_is_hidden_without_loading(self):
        """Verify a relation whose name looks sensitive is hidden, and not loaded."""
        author = Author.objects.get(name="Ada")
        content, queries = self.dumped(author)

        self.assertRegex(content, re.escape(relation("auth_token")) + r'\s*<span class="empty"[^>]*>\*{20}</span>')
        self.assertNotIn("secret-key", content)
        self.assertFalse(any("authtoken" in query for query in queries))

    @override_settings(DJANGO_DD_INCLUDE_RELATIONS=False)
    def test_relations_turned_off(self):
        """Verify the Relations section can be left out, and then no relations are loaded."""
        content, queries = self.dumped(Book.objects.get(title="Notes"))

        self.assertNotIn('<span class="section_name">Relations</span>', content)
        self.assertEqual(queries, [])

    def test_relations_start_expanded(self):
        """Verify the Relations section starts expanded by default, and collapsed with the setting off."""
        book = Book.objects.select_related("author").get(title="Notes")
        content, _queries = self.dumped(book)
        self.assertRegex(content, r'class="li-wrapper collapse \S+-relations show"')

        with override_settings(DJANGO_DD_RELATIONS_START_EXPANDED=False):
            content, _queries = self.dumped(book)
        self.assertRegex(content, r'class="li-wrapper collapse \S+-relations "')

    @override_settings(DJANGO_DD_INCLUDE_ATTRIBUTES=False, DJANGO_DD_RELATIONS_START_EXPANDED=False)
    def test_relations_always_shown_when_the_only_section(self):
        """Verify the Relations section is always expanded when it is the only section, like the others."""
        book = Book.objects.select_related("author").get(title="Notes")
        content, _queries = self.dumped(book)

        self.assertRegex(content, r'class="li-wrapper collapse \S+-relations show"')

    def test_relations_are_found_both_ways_and_hidden_ones_left_out(self):
        """Verify forward and reverse relations are found, by their accessor, and hidden ones (related_name "+") not."""
        self.assertEqual([found.name for found in get_relations(Author())], ["auth_token", "books", "profile"])
        self.assertEqual([found.name for found in get_relations(Book())], ["author", "editor", "tags"])
        self.assertEqual(get_relations({"name": "Ada"}), [])

    def test_objects_that_are_not_model_instances_have_no_relations(self):
        """Verify only model instances have a Relations section."""
        content, _queries = self.dumped({"name": "Ada"})

        self.assertNotIn('<span class="section_name">Relations</span>', content)

    def test_relation_that_fails_shows_its_error(self):
        """Verify a relation that fails to load, such as from a table that doesn't exist, shows the error."""
        sample = SampleDjangoModel(id=1, sample_foreign_id=5)
        content, _queries = self.dumped(sample)

        self.assertRegex(
            content,
            re.escape(relation("sample_foreign")) + r'\s*<span class="empty" title="Reading this relation failed.">'
            r"OperationalError: no such table: django_dump_die_samplerelation</span>",
        )

    def test_relations_in_the_console(self):
        """Verify the console shows relations after the attributes, as the page does."""
        book = Book.objects.select_related("author").get(title="Notes")
        dump(book)
        output = format_dump(middleware.get_dump_objects().pop())

        self.assertIn("\n    author: Author ", output)
        self.assertIn("\n        name: 'Ada'\n", output)
        self.assertIn("\n    tags: Not loaded\n", output)


@override_settings(DEBUG=True)
class DumpDieRelatedObjectBatchingTestCase(CollectDumpsMixin, TestCase):
    """Verify a dumped QuerySet fetches the related objects the dump follows with its rows, in one query."""

    @classmethod
    def setUpTestData(cls):
        for number in range(3):
            author = Author.objects.create(name=f"author{number}")
            Profile.objects.create(author=author, bio=f"bio{number}")
            AuthToken.objects.create(author=author, key=f"key{number}")
            Book.objects.create(author=author, title=f"book{number}")

    def dumped(self, obj):
        """Dump an object, and return the page and the queries it ran."""
        with CaptureQueriesContext(connection) as queries:
            dump(obj)
            content = render_dumped_objects()
        return content, [query["sql"] for query in queries.captured_queries]

    def test_queryset_fetches_related_objects_with_its_rows(self):
        """Verify the rows' authors and their profiles come in the same query as the rows, not one query each."""
        content, queries = self.dumped(Book.objects.order_by("title"))

        self.assertEqual(len(queries), 2, queries)
        self.assertIn("COUNT(", queries[0])
        self.assertIn("JOIN", queries[1])
        for number in range(3):
            self.assertIn(f"&#x27;bio{number}&#x27;", content)
        # A sensitive relation is never read, so it isn't fetched either.
        self.assertNotIn("authtoken", queries[1])

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=1)
    def test_only_related_objects_within_the_depth_are_fetched(self):
        """Verify related objects past DJANGO_DD_RELATED_OBJECT_DEPTH aren't fetched, and say they aren't loaded."""
        content, queries = self.dumped(Book.objects.order_by("title"))

        self.assertEqual(len(queries), 2, queries)
        self.assertNotIn("profile", queries[1])
        self.assertRegex(content, not_loaded("profile"))

    @override_settings(DJANGO_DD_RELATED_OBJECT_DEPTH=0)
    def test_nothing_is_fetched_at_depth_zero(self):
        """Verify no related objects are fetched with the rows when relations aren't followed."""
        _content, queries = self.dumped(Book.objects.order_by("title"))

        self.assertEqual(len(queries), 2, queries)
        self.assertNotIn("JOIN", queries[1])

    def test_lookups_of_the_followed_relations(self):
        """Verify the lookups are the followed relations: not sensitive ones, or the one back to where they came."""
        self.assertCountEqual(
            get_related_object_lookups(Book, 3), ["author", "author__profile", "editor", "editor__profile"]
        )
        self.assertEqual(get_related_object_lookups(Book, 1), ["author", "editor"])
        self.assertEqual(get_related_object_lookups(Book, 0), [])

    def test_querysets_that_select_related_does_not_work_with(self):
        """Verify QuerySets that select_related() can't be added to are dumped as before, with their rows."""
        for label, queryset in (
            ("only", Book.objects.order_by("title").only("title")),
            ("values", Book.objects.order_by("title").values("title")),
            ("union", Book.objects.filter(title="book0").union(Book.objects.filter(title="book1"))),
        ):
            with self.subTest(queryset=label):
                content, _queries = self.dumped(queryset)
                self.assertIn("book0", content)

    def test_rows_are_fetched_alone_if_fetching_them_with_related_objects_fails(self):
        """Verify a QuerySet whose rows can't be fetched with their related objects is still dumped, without them."""

        class FailsWhenFetched:
            """Stands in for a QuerySet with select_related() that fails when its rows are fetched."""

            def __getitem__(self, index):
                raise ValueError("The rows can't be fetched this way.")

        with patch.object(utils, "_with_related_objects", return_value=FailsWhenFetched()):
            content, _queries = self.dumped(Book.objects.order_by("title"))

        self.assertIn("&#x27;bio0&#x27;", content)
