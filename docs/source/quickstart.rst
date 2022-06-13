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

4.  Ensure that you have **DEBUG** set to ``True`` in your Django ``settings.py`` file:

    .. code-block:: python

        DEBUG = True

    .. note::
        Neither the ``dump`` command nor the ``dd`` command will do
        anything if ``DEBUG`` is not set to ``True``.
        With that said, this is a tool for debugging.
        You should not include this package in production
        nor should you ever have ``DEBUG`` set to ``True`` in production.

5.  From a file that is part of the request / response cycle such as a Django
    View in ``views.py``, make a call to dd sending it the contents of a variable
    to inspect.

    **views.py**

    .. code-block:: python

        def my_awesome_view(request):
            dd(request)
