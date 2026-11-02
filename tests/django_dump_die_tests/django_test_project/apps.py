"""App config for the django-dump-die test project."""

# Third-Party Imports.
from django.apps import AppConfig


class DjangoDumpDieTestsConfig(AppConfig):
    """Test project app.

    Has an explicit label, so that it does not collide with the test project apps of other
    packages when installed alongside them in one project.
    """

    name = "django_dump_die_tests.django_test_project"
    label = "django_dump_die_tests"
