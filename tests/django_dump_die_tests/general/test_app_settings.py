"""
Tests for the DumpDie settings, read through app_settings.
"""

# System Imports.
import re
from pathlib import Path

# Third-Party Imports.
from django.test import SimpleTestCase, override_settings

# Internal Imports.
import django_dump_die
from django_dump_die.app_settings import AppSettings, Setting, app_settings

PACKAGE_DIR = Path(django_dump_die.__file__).resolve().parent
TESTS_DIR = Path(__file__).resolve().parent.parent
# The configuration docs, which only exist in a checkout of the repository, not in an installed package.
DOCS_DIR = PACKAGE_DIR.parent / "docs" / "source"
CONFIGURATION_DOCS = DOCS_DIR / "configuration.rst"
# Environment variables for the browser tests, which share the prefix but aren't settings.
NOT_SETTINGS = ("DJANGO_DD_SELENIUM_",)


def get_setting_names():
    """Return the names of all DumpDie settings, with the DJANGO_DD_ prefix."""
    return sorted(value.setting_name for value in vars(AppSettings).values() if isinstance(value, Setting))


class DumpDieAppSettingsTestCase(SimpleTestCase):
    """Verify settings are read from the Django settings each time they are used, with their defaults."""

    def test_default_is_used_when_the_setting_is_not_set(self):
        """Verify a setting the project doesn't set has its default."""
        self.assertEqual(app_settings.MAX_RECURSION_DEPTH, 5)
        self.assertIs(app_settings.SHOW_SENSITIVE_VALUES, False)

    def test_setting_is_read_each_time_it_is_used(self):
        """Verify a changed Django setting is used right away, such as by override_settings."""
        with override_settings(DJANGO_DD_MAX_RECURSION_DEPTH=2):
            self.assertEqual(app_settings.MAX_RECURSION_DEPTH, 2)
        self.assertEqual(app_settings.MAX_RECURSION_DEPTH, 5)

    def test_changing_a_default_list_does_not_change_the_default(self):
        """Verify each use of a list or dict default gets its own copy."""
        app_settings.ADDITIONAL_SIMPLE_TYPES.append("Changed")
        app_settings.FUNCTION_RESULTS["Changed"] = ["changed"]

        self.assertEqual(app_settings.ADDITIONAL_SIMPLE_TYPES, [])
        self.assertEqual(app_settings.FUNCTION_RESULTS, {})

    def test_setting_on_the_class_is_the_setting_itself(self):
        """Verify a setting looked up on the class, not an instance, is its Setting, with its Django setting name."""
        self.assertIsInstance(AppSettings.MAX_RECURSION_DEPTH, Setting)
        self.assertEqual(AppSettings.MAX_RECURSION_DEPTH.setting_name, "DJANGO_DD_MAX_RECURSION_DEPTH")

    def test_every_setting_is_documented(self):
        """Verify each setting has a section in the configuration docs, and every documented setting exists."""
        if not CONFIGURATION_DOCS.exists():
            self.skipTest("The docs are only in a checkout of the repository.")

        documented = re.findall(r"^(DJANGO_DD_[A-Z_]+)\n=+$", CONFIGURATION_DOCS.read_text(encoding="utf-8"), re.M)

        self.assertEqual(sorted(documented), get_setting_names())

    def test_package_only_uses_settings_that_exist(self):
        """Verify every app_settings attribute the package reads is a setting, so that a misspelled one is caught."""
        for path in sorted(PACKAGE_DIR.rglob("*.py")):
            for name in re.findall(r"\bapp_settings\.([A-Za-z_]\w*)", path.read_text(encoding="utf-8")):
                with self.subTest(file=str(path.relative_to(PACKAGE_DIR)), name=name):
                    self.assertIsInstance(vars(AppSettings).get(name), Setting)

    def test_every_setting_name_exists(self):
        """Verify every DJANGO_DD_ name in the package, tests, and docs is a setting, such as in override_settings().

        The version history is left out, since it can name settings that were removed.
        """
        paths = [*PACKAGE_DIR.rglob("*.py"), *PACKAGE_DIR.rglob("*.html"), *TESTS_DIR.rglob("*.py")]
        paths += [path for path in DOCS_DIR.glob("*.rst") if path.name != "version_history.rst"]
        settings_names = get_setting_names()
        for path in sorted(paths):
            for name in sorted(set(re.findall(r"\bDJANGO_DD_[A-Z][A-Z0-9_]*", path.read_text(encoding="utf-8")))):
                if not name.startswith(NOT_SETTINGS):
                    with self.subTest(file=path.name, name=name):
                        self.assertIn(name, settings_names)
