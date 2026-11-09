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

# The configuration docs, which only exist in a checkout of the repository, not in an installed package.
CONFIGURATION_DOCS = Path(django_dump_die.__file__).resolve().parent.parent / "docs" / "source" / "configuration.rst"


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
