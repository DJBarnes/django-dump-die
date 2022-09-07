"""
Project testing settings, so that tests can run project as if it was a proper Django application.
"""

# System Imports.
import sys


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
