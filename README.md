Django Dump & Die
============================

[![PyPI](https://img.shields.io/pypi/v/django-dump-die?color=blue)](https://img.shields.io/pypi/v/django-dump-die?color=blue)
[![Python Versions](https://img.shields.io/badge/python-%3E%3D3.8-brightgreen)](https://img.shields.io/badge/python-%3E%3D3.8-brightgreen)
[![Django Versions](https://img.shields.io/badge/django-%3E%3D3.2-brightgreen)](https://img.shields.io/badge/django-%3E%3D3.2-brightgreen)
[![Documentation Status](https://readthedocs.org/projects/django-dump-die/badge/?version=latest)](https://django-dump-die.readthedocs.io/en/latest/?badge=latest)
[![PyPI Downloads per Month](https://img.shields.io/pypi/dm/django-dump-die.svg)](https://pypi.python.org/pypi/django-dump-die)
[![GitHub](https://img.shields.io/github/license/DJBarnes/django-dump-die)](https://img.shields.io/github/license/DJBarnes/django-dump-die)


Django-Dump-Die is a [Django](https://www.djangoproject.com/) app that
provides a couple of debug tools, in the form of built-in methods
`dump` and `dd`. These allow sending details about a variable to the
browser for inspection.

Dumped variables are presented in an easy to read and
fully expandable / collapsible tree. You can easily understand complex objects
and the results of django queries with a simple call to either method.

When `dump` and/or `dd` are called, dump die will intercept the page
response and replace the contents of the response with detailed information
about the corresponding variables passed for inspection.

The entire concept is heavily based on the dump die functionality that comes
with Php's [Laravel](https://laravel.com/)
and [Symfony](https://symfony.com/) frameworks.

Full documentation on [ReadTheDocs](https://django-dump-die.readthedocs.io/en/latest/).

![dd_sample_output](https://user-images.githubusercontent.com/4390026/173413467-afcea349-a28b-42c0-bd18-5922df17b453.png)

## Quickstart
1.  Install the Django App via Pypi.
    ```shell
    python -m pip install django-dump-die
    ```

<br>

2.  Add the corresponding app to your Django ``settings.py`` file:
    ```python
    INSTALLED_APPS = [

        'django_dump_die',
        ...
    ]
    ```

<br>

3.  Add the corresponding middleware to your Django ``settings.py`` file:
    ```python
    MIDDLEWARE = [

        'django_dump_die.middleware.DumpAndDieMiddleware',
        ...
    ]
    ```

4.  Ensure that you have **DEBUG** set to ``True`` in your Django ``settings.py`` file:
    ```python
    DEBUG = True
    ```

    ---
    :information_source: **NOTE**
    Neither the `dump` command nor the `dd` command will do anything if **DEBUG** is not set to `True`.
    With that said, this is a tool for debugging. You should not include this package
    in production nor should you ever have **DEBUG** set to `True` in production.

    ---

5.  From a file that is part of the request / response cycle such as a Django
    View in `views.py`, make a call to dd sending it the contents of a variable
    to inspect.

    **views.py**
    ```python
    def my_awesome_view(request):
        dd(request)
    ```

## Usage
The middleware is where most of this package's heavy lifting happens.

By having the middleware installed, you can run ``dump(<variable>)`` and/or
``dd(<variable>)`` in any file that is part of the request response cycle,
and it will run the dump logic. No importing or extra logic is required.

Each ``dump(<variable>)`` command will add the passed object to an internal
list that will be dumped either when a ``dd(<variable>)`` is used, or if the
entirety of the request finishes. You can have as many ``dump(<variable>)``
statements as you want leading up to an optional ``dd(<variable>)``.

If you make a call to ``dd(<variable>)``, execution will immediately stop
and all dumped objects (including the the one sent to dd) will be output.

If you do not make a call to ``dd(<variable>)`` and only use
``dump(<variable>)`` statements, the request will continue processing until
it is time to return the response. At this point, Django-Dump-Die will
intercept and replace the response with the data that has been dumped thus
far.

---
:information_source: **NOTE**
Because dump die uses middleware to internally handle keeping track of
what to dump and then actually dumping the data to the browser, any
call to ``dump`` or ``dd`` must be done in a file that will be processed
during the request response cycle. Most commonly this will be a
``views.py`` file, but could also be utils called from a view.
Attempting to ``dump`` or ``dd`` from a console command will not work.

---

<br>

Example:
```python
# Sample classes for output.
class EmptyClass:
    """Empty Class."""
    pass


class SomeClass:
    """Some Class."""
    SAMPLE_CONST = 41

    def __init__(self, *args, **kwargs):
        self.my_number = 32
        self.my_string = 'A super cool string'
        self.works = True
        self.nothing = None
        self.bytes = bytes('My Bytes', 'utf-8')
        self.list_o_stuff = ['A', 'B', 'C']
        self.sample_set = {'A', 'B', 'C'}
        self.sample_tuple = ('A', 12, True)
        self.empty_class = EmptyClass()
        self.empty_class_dup = self.empty_class

    def do_work(self):
        """Do some work"""
        return True


# Example Usage
empty_class = EmptyClass()
some_class = SomeClass()

dump('Simple String')
dump(empty_class)
dd(some_class)
```
![django-dump-die-sample-output](https://user-images.githubusercontent.com/4390026/159033583-b2d4d98e-52c1-487e-93a3-5c56e7038893.png)

<br>

---
:information_source: **NOTE**
Most editors will give a red error squiggle for the dd command.
This is intentional, and the command will still run. This is because this
command is meant to be used for debugging, and is not meant to stay
long-term. The red squiggle helps identify it as something that should be
removed before any actual commits.

---

### Usage & Parameters
For further documentation on usage and parameters, see
[ReadTheDocs/Usage](https://django-dump-die.readthedocs.io/en/latest/usage.html)


## Configuration
The package has a few available configuration options and settings, which are
documented at
[ReadTheDocs/Configuration](https://django-dump-die.readthedocs.io/en/latest/configuration.html)
