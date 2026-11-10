Security
********

Django-Dump-Die is a debugging tool. It shows the inside of your objects,
which can include passwords, keys, session cookies, and personal data. This
page explains what it does to keep that safe, and what you need to do.


Only Use It With DEBUG On
=========================

``dump()``, ``dd()``, ``dump.br()``, and the ``{% dump %}`` template tag do
nothing unless ``DEBUG`` is ``True``. The middleware also never shows dumps
while ``DEBUG`` is off, even ones collected while it was on.

As with Django's own debug page, never set ``DEBUG`` to ``True`` on a site
that other people can reach, and don't install this package in production.
The example pages in ``django_dump_die.urls`` are for trying the package out
locally. Don't include them in a project that is deployed.


Dumps Are Shown to Whoever Opens the Page
=========================================

Dumped objects are collected for each request, and shown only in that
request's response, even when requests run at the same time. But anyone who
opens a page that dumps sees what it dumps. On a development server that
several people use, or a test server with ``DEBUG`` on, that can include
someone else's data, such as a dumped request with their session cookie,
which lets the other person log in as them.

Only use ``dump()`` and ``dd()`` on a server that only you use.


Sensitive Values Are Hidden
===========================

Like Django's debug page, dumps hide values whose names look sensitive, and
show ``********************`` in their place. Hover over the stars to see why
the value is hidden. A function whose name looks sensitive is not run for
:ref:`function results <function-results>`.

A value is hidden when its attribute, key, or function name:

* has a word such as ``password``, ``pass``, ``secret``, ``token``, ``auth``,
  ``credentials``, or ``signature``, such as ``SECRET_KEY``,
  ``db_password``, or ``access_token``;

* ends in ``password``, ``secret``, ``token``, or ``apikey``, such as
  ``csrfmiddlewaretoken``;

* is a key named after what it is for, such as ``api_key``, ``privateKey``,
  or ``session_key``;

* is the session cookie, named by Django's ``SESSION_COOKIE_NAME`` setting;

* is the request header that holds the cookies, ``HTTP_COOKIE`` in
  ``request.META`` or ``Cookie`` in ``request.headers``.

Words are found from underscores and from camelCase, so names that only
contain these letters, such as ``key``, ``author``, ``is_authenticated``, or
``passenger``, are still shown.

Only names are checked. A value you dump directly, such as
``dump(settings.SECRET_KEY)``, is shown, since you asked for it. So are
sensitive values that have no name, such as an item in a list.

To show every value, set
:ref:`DJANGO_DD_SHOW_SENSITIVE_VALUES <show-sensitive-values>` to ``True``.
Only do this on a server that only you use, and take care with screenshots
of your dumps.


Dumping Runs Code
=================

Dumping an object reads its attributes, which runs the code of its
properties, and a dumped QuerySet runs two queries, to count its rows and to
fetch the rows that are dumped. Function results, when they are
turned on, run the functions they list. A dump can therefore query the
database or change the state of an object, like any other code that reads
it.
