"""App configuration for DumpDie."""

# Third-Party Imports.
from django.apps import AppConfig


class DjangoDumpDieConfig(AppConfig):
    """Makes dd() and dump() built-ins when Django starts, so that they work without imports outside of requests too,
    such as in management commands and the shell. The middleware does the same for requests."""

    name = "django_dump_die"
    verbose_name = "Django Dump Die"

    def ready(self):
        # Imported here, since it imports from the rest of the package, which needs the apps to be loaded.
        from django_dump_die.functions import install_builtins  # noqa: PLC0415

        install_builtins()
