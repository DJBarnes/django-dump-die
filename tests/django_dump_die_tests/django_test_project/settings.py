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

# Hash passwords quickly. Django's default hasher is slow on purpose, which only slows tests down.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

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

# Don't create django-expanded-test-cases' default test users. It creates four before every test, and these tests
# only make anonymous requests, so they never use them.
DJANGO_EXPANDED_TESTCASES_AUTO_GENERATE_USERS = False


# Browser for the browser (Selenium) tests, chosen per developer with the DJANGO_DD_SELENIUM_BROWSER
# environment variable: "firefox" (the default), "chrome", or "none" to skip the browser tests.
# The browser runs headless, without a window, so that it doesn't get in the way of other work. Set
# DJANGO_DD_SELENIUM_HEADLESS=false to watch it, such as while debugging a test.
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
if os.environ.get("DJANGO_DD_SELENIUM_HEADLESS", "true").lower() not in ("0", "false", "no"):
    # Passed as browser options, because each browser spells its headless option differently.
    DJANGO_EXPANDED_TESTCASES_SELENIUM_EXTRA_BROWSER_OPTIONS = (
        ["-headless"] if DJANGO_DD_SELENIUM_BROWSER == "firefox" else ["--headless=new"]
    )
# Each browser driver gets the next port from this start value. Give each pytest-xdist worker ("gw0", "gw1", ...)
# its own range, so that drivers in parallel workers don't try to use the same port.
_XDIST_WORKER = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
DJANGO_EXPANDED_TESTCASES_SELENIUM_DEBUG_PORT_START_VALUE = 9221 + 100 * int(_XDIST_WORKER.lstrip("gw") or 0)

# endregion Package settings for testing


# region Django Version Specific Settings

# Check to see if on version greater than 5 and fix / suppress warnings from changes in that version.
if django.VERSION >= (5, 0):
    filterwarnings("ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated.")
    FORMS_URLFIELD_ASSUME_HTTPS = True

# endregion Django Version Specific Settings
