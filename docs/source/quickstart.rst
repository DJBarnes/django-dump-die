Quickstart
**********

1.  Install the Django App via GitHub for now. Working on getting on Pypi soon.

    .. code-block:: bash

        python -m pip install -e git+https://github.com/DJBarnes/django-dump-die@master


2.  Add the corresponding app to your Django ``settings.py`` file:

    .. code-block:: python

        INSTALLED_APPS = [

            'django_dump_die',
            ...
        ]


3.  Add the corresponding middleware to your Django ``settings.py`` file:

    .. code-block:: python

        MIDDLEWARE = [


            'django_dump_die.middleware.DumpAndDieMiddleware',
            ...
        ]

4.  Ensure that you have DEBUG set to True in your Django ``settings.py`` file:

    .. code-block:: python

        DEBUG = True

    .. note::
        Neither the ``dump`` command nor the ``dd`` command will do
        anything if ``DEBUG`` is not set to ``True``.
        With that said, this is a tool for debugging.
        You should not include this package in production
        nor should you ever have ``DEBUG`` set to ``True`` in production.

5.  The middleware is where most of this package's heavy lifting happens.

    By having the middleware installed, you can run ``dump(<variable>)`` and/or
    ``dd(<variable>)`` anywhere you want, and it will run the dump logic.
    No importing or extra logic is required.

    Each ``dump(<variable>)`` command will add the passed object to an internal
    list that will be dumped either when a ``dd(<variable>)`` is used, or if the
    entirety of the request finishes. You can have as many ``dump(<variable>)``
    statements as you want leading up to a ``dd(<variable>)``.

    If you make a call to ``dd(<variable>)``, execution will immediately stop
    and all dumped objects (including the the one sent to dd) will be output.

    If you do not make a call to ``dd(<variable>)`` and only use
    ``dump(<variable>)`` statements, the request will continue processing until
    it is time to return the response. At this point, Django-Dump-Die will
    intercept and replace the response with the data that has been dumped thus
    far.
