"""
Project testing settings, so that tests can run project as if it was a proper Django application.
"""

# System Imports.
import sys
from warnings import filterwarnings

# Third-party Imports
import django

# region Main settings for testing

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django_dump_die',
)

MIDDLEWARE = [
    'django_dump_die.middleware.DumpAndDieMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]

ROOT_URLCONF = 'tests.urls'

USE_TZ = True

TIME_ZONE = 'UTC'

SECRET_KEY = 'test_secret_key'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
}]


STATIC_URL = '/static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# This should normally be False for tests, but since these tests are testing
# a tool used for development and debugging, it must be True.
DEBUG = True

# endregion Main settings for testing

# region Package settings for testing

# Suppress or show testcase debug printout, based on UnitTest execution method.
if 'pytest' in sys.modules:
    # Running Pytest env.
    # Pytest only shows console output on test failure, so we want it on.
    DJANGO_EXPANDED_TESTCASES_DEBUG_PRINT = True
else:
    # Running other testing env (mostly likely "django manage.py test").
    # manage.py shows all console output always, even on success.
    # So we want it off to avoid information overload and spam.
    DJANGO_EXPANDED_TESTCASES_DEBUG_PRINT = False

# endregion Package settings for testing

# region Django Version Specific Settings

# Check to see if on version greater than 5 and fix / suppress warnings from changes in that version.
if django.VERSION >= (5, 0):
    filterwarnings(
        "ignore", "The FORMS_URLFIELD_ASSUME_HTTPS transitional setting is deprecated."
    )
    FORMS_URLFIELD_ASSUME_HTTPS = True

# endregion Django Version Specific Settings

# region Warning suppressions

# When running tests and converting all warnings to errors, there are errors related
# to the following that need to be ignored. The warnings only show up when converting to errors.
# If leaving as warnings, they are never output.
# TODO: Figure out why when converting warnings to errors, these warnings show up.

filterwarnings(
    "ignore",
    "Model 'django_dump_die.samplerelation' was already registered. Reloading models is not advised as it can lead to inconsistencies, most notably with related models.",RuntimeWarning,
)
filterwarnings(
    "ignore",
    "Model 'django_dump_die.samplemanyrelation' was already registered. Reloading models is not advised as it can lead to inconsistencies, most notably with related models.",RuntimeWarning,
)
filterwarnings(
    "ignore",
    "Model 'django_dump_die.sampleonerelation' was already registered. Reloading models is not advised as it can lead to inconsistencies, most notably with related models.",RuntimeWarning,
)
filterwarnings(
    "ignore",
    "Model 'django_dump_die.sampledjangomodel_sample_many' was already registered. Reloading models is not advised as it can lead to inconsistencies, most notably with related models.",
    RuntimeWarning,
)
filterwarnings(
    "ignore",
    "Model 'django_dump_die.sampledjangomodel' was already registered. Reloading models is not advised as it can lead to inconsistencies, most notably with related models.",RuntimeWarning,
)

# endregion Warning suppressions
