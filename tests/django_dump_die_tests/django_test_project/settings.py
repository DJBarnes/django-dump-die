"""
Project testing settings, so that tests can run project as if it was a proper Django application.
"""

# System Imports.
import os
import sys
from warnings import filterwarnings

# Third-party Imports
import django

# region Main settings for testing

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

INSTALLED_APPS = (
    "django.contrib.sessions",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "django_dump_die",
    "django_dump_die_tests.django_test_project",
)

MIDDLEWARE = [
    "django_dump_die.middleware.DumpAndDieMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
]

ROOT_URLCONF = "django_dump_die_tests.django_test_project.urls"

USE_TZ = True

TIME_ZONE = "UTC"

SECRET_KEY = "test_secret_key"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
            ],
        },
    },
]


STATIC_URL = "/static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# This should normally be False for tests, but since these tests are testing
# a tool used for development and debugging, it must be True.
DEBUG = True

# endregion Main settings for testing


# region Package settings for testing

# Suppress or show testcase debug printout, based on UnitTest execution method.
if "pytest" in sys.modules:
    # Running Pytest env.
    # Pytest only shows console output on test failure, so we want it on.
    DJANGO_EXPANDED_TESTCASES_DEBUG_PRINT = True
else:
    # Running other testing env (mostly likely "django manage.py test").
    # manage.py shows all console output always, even on success.
    # So we want it off to avoid information overload and spam.
    DJANGO_EXPANDED_TESTCASES_DEBUG_PRINT = False


# Browser for the browser (Selenium) tests, chosen per developer with the DJANGO_DD_SELENIUM_BROWSER
# environment variable: "firefox" (the default), "chrome", or "none" to skip the browser tests.
# Set DJANGO_DD_SELENIUM_HEADLESS=true to run the browser without a window.
DJANGO_DD_SELENIUM_BROWSER = os.environ.get("DJANGO_DD_SELENIUM_BROWSER", "firefox").lower()
DJANGO_EXPANDED_TESTCASES_SELENIUM_BROWSER = DJANGO_DD_SELENIUM_BROWSER
# Set DJANGO_DD_SELENIUM_BROWSER_BINARY to the browser's executable if it isn't found. Firefox installed as a
# snap (as on Ubuntu) is found by default: its /snap/bin/firefox is a launcher script, not the browser itself.
DJANGO_DD_SELENIUM_BROWSER_BINARY = os.environ.get("DJANGO_DD_SELENIUM_BROWSER_BINARY", "")
SNAP_FIREFOX_BINARY = "/snap/firefox/current/usr/lib/firefox/firefox"
if (
    not DJANGO_DD_SELENIUM_BROWSER_BINARY
    and DJANGO_DD_SELENIUM_BROWSER == "firefox"
    and os.path.exists(SNAP_FIREFOX_BINARY)
):
    DJANGO_DD_SELENIUM_BROWSER_BINARY = SNAP_FIREFOX_BINARY
if os.environ.get("DJANGO_DD_SELENIUM_HEADLESS", "").lower() in ("1", "true", "yes"):
    # Passed as browser options, because each browser spells its headless option differently.
    DJANGO_EXPANDED_TESTCASES_SELENIUM_EXTRA_BROWSER_OPTIONS = (
        ["-headless"] if DJANGO_DD_SELENIUM_BROWSER == "firefox" else ["--headless=new"]
    )

# endregion Package settings for testing


# region Django Version Specific Settings

# Check to see if on version greater than 5 and fix / suppress warnings from changes in that version.
if django.VERSION >= (5, 0):
    filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
    FORMS_URLFIELD_ASSUME_HTTPS = True

# endregion Django Version Specific Settings
