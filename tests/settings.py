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
