"""
Models with each kind of relation, for the tests of the Relations section. Their tables are only in the test database.
"""

# Third-Party Imports.
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Author(models.Model):
    """Has a reverse one-to-one (profile), a reverse foreign key (books), a sensitive reverse one-to-one (auth_token),
    and a hidden reverse foreign key, from Book.editor."""

    name = models.CharField(max_length=100)


class Profile(models.Model):
    """One-to-one with an author."""

    author = models.OneToOneField(Author, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField()


class AuthToken(models.Model):
    """One-to-one with an author, named like a sensitive value on the author: author.auth_token."""

    author = models.OneToOneField(Author, on_delete=models.CASCADE, related_name="auth_token")
    key = models.CharField(max_length=40)


class Tag(models.Model):
    """Many-to-many with books, from the other side (tag.books)."""

    name = models.CharField(max_length=100)


class Book(models.Model):
    """Has a foreign key (author), a many-to-many (tags), and a foreign key with a hidden reverse relation (editor)."""

    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    editor = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="+")
    tags = models.ManyToManyField(Tag, related_name="books")
    title = models.CharField(max_length=100)


class Note(models.Model):
    """Has a generic foreign key (target)."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    target = GenericForeignKey("content_type", "object_id")
    text = models.TextField()
