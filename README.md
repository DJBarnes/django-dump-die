Django Dump & Die
============================

Django App providing a mechanism for extracting the details of any python variable and dumping it to the browser.
This is effectively a debugging tool, used to quickly and easily output an object's full data to screen.

Inspired by the dump and dump/die functionality from Symfony / Laravel.


## Installation
Import the package via either:

    pip install django-dump-die

or

    pipenv install django-dump-die

<br>

Then add the corresponding middleware to your Django `settings.py` file:

    MIDDLEWARE = [
        ...

        'dump_die.middleware.DumpAndDieMiddleware',

        ...
    ]


## Usage
The middleware is where most of this package's heavy lifting happens.

By having the middleware installed, you can run `dd(<value>)` anywhere you want, and it will run the dump logic.
No importing is required, nor is any extra logic. Just type "dd" anywhere you want in a python file and it will run.

<br>

Note that most editors will give a red error squiggle for the dd command.

This is intentional, and the command will still run. This is because this command is meant to be used for debugging,
and is not meant to stay long-term. The red squiggle helps identify it as something that should be removed before
any actual commits.
