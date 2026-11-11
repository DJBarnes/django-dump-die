Version History
***************

Unreleased
==========

Action Needed When Upgrading
----------------------------

* **Changed: Python 3.10 and Django 4.2 or later are needed.** Support for
  Python 3.6 to 3.9 and Django 2.2 to 4.1 is removed. These are the oldest
  versions the package works with without extra code for older versions,
  and all of the removed versions are past their end of life. To keep using
  an older Python or Django, stay on 0.2.1.

Other Changes
-------------

* **Fixed: objects made while a page of dumps was shown could be shown as
  already shown.** A unique comes from the object's ``id()``, which Python
  reuses once an object is gone. Objects made while the page was shown, such
  as a function result, or a property that returns a new object each time,
  were gone once their part of the page was shown, and the next one could get
  the same unique, and be shown as already shown, without its contents. They
  are now kept until the page is done.

* **Added: a Relations section for model instances.** A dumped model
  instance shows its relations in their own section, after its Attributes:
  its foreign keys and one-to-one fields, its many-to-many fields, and its
  reverse relations, such as ``user_set``. Before, many-to-many fields and
  reverse relations were only listed as functions, which are hidden by
  default, even when ``prefetch_related()`` had loaded their rows, and a
  foreign key without a value was left out. Relations that return one object,
  such as foreign keys, are followed as before, up to
  ``DJANGO_DD_RELATED_OBJECT_DEPTH`` relations away, three by default,
  instead of until ``DJANGO_DD_MAX_RECURSION_DEPTH``. A dumped QuerySet
  fetches them with its rows, in one query, instead of one query for each
  related object of each row. Related managers show
  the rows ``prefetch_related()`` loaded, without a query, and can be
  followed too, with ``DJANGO_DD_RELATED_MANAGER_DEPTH``, which is off by
  default. Other relations say they aren't loaded, and how to load them. The
  section can be turned off with ``DJANGO_DD_INCLUDE_RELATIONS``, and
  collapsed with ``DJANGO_DD_RELATIONS_START_EXPANDED``. See "Relations" in
  the usage docs.
  (`#22 <https://github.com/DJBarnes/django-dump-die/issues/22>`_)

* **Added: dd() and dump() print to the console outside of a request.** In a
  management command, the shell, or a background task, ``dump()`` printed
  nothing, and kept the objects it collected for as long as the process ran,
  and ``dd()`` failed with an unreadable error. They now print the object to
  the console (stderr) as an indented tree, with the same limits, hidden
  sensitive values, and colors as the dump page, and ``dd()`` then stops with
  a message saying why. ``dd()`` and ``dump()`` are now built-ins as soon as
  Django starts, not only once the middleware is loaded, and can also be
  imported with ``from django_dump_die import dd, dump``. See "Outside of a
  Request" in the usage docs. Characters that could control the terminal,
  such as the escape sequences in a file name, are shown escaped.
  (`#21 <https://github.com/DJBarnes/django-dump-die/issues/21>`_)

* **Fixed: requests showed each other's dumps.** Dumped objects were
  collected in one list for the whole server. When requests ran at the same
  time, such as with ``runserver``'s threads or under ASGI, a request could
  show another's dumps, and the other then showed none. And a request that
  failed before its response was handled left its dumps for the next request
  that dumped anything. Each request now shows only its own dumps. Pages of
  dumps rendered at the same time also keep their own count of repeated
  objects.
  (`#34 <https://github.com/DJBarnes/django-dump-die/issues/34>`_)

0.2.1 (2026-11-09)
==================

* **Fixed: the Documentation link on PyPI.** It pointed at a version of the
  docs that isn't built. It now points at the docs of the newest release, and
  a new Changelog link points at this page.

* **Added: the history of versions before 0.2.0.** The entries for 0.1.0 to
  0.1.7 were written in 2026, from the project's commits, since those
  versions had no version history of their own.

* **Fixed: the 0.2.0 notes said 0.1.7 installed pytz.** It didn't: no
  version of the package has listed ``pytz`` as a dependency, so 0.2.0
  changed nothing about it. Timezones from ``pytz`` are dumped when it is
  installed, as before.

0.2.0 (2026-11-09)
==================

Action Needed When Upgrading
----------------------------

* **Changed: sensitive values are hidden.** Like Django's debug page, dumps
  now show ``********************`` in place of values whose names look
  sensitive, such as ``SECRET_KEY``, ``password``, ``access_token``, the
  session cookie, and the ``Cookie`` header. Functions with such names are not
  run for function results. To show them again, set
  ``DJANGO_DD_SHOW_SENSITIVE_VALUES = True``. See the new Security page of the
  docs for the names that are hidden, and for other things to watch out for.

Other Changes
-------------

* **Changed: large iterables and QuerySets are dumped quickly.** Only the
  items that are dumped are listed, the first
  ``DJANGO_DD_MAX_ITERABLE_LENGTH`` or those in the ``index_range``. The
  items after them are shown as one line with how many more there are, such
  as ``… 980 more``, and those before an ``index_range`` as one line such as
  ``… 18 before``. Before, every item had its own line, simple values such as
  numbers showed every value, and a list of a million items took minutes. A
  QuerySet no longer loads every row: it is counted with ``count()``, and only
  the rows that are dumped are fetched. It is also dumped as itself, labeled
  ``QuerySet`` with its own attributes and functions, instead of as a list.
  Dicts are not limited, as before.
  (`#54 <https://github.com/DJBarnes/django-dump-die/issues/54>`_)

* **Fixed: DJANGO_DD_MAX_ITERABLE_LENGTH = None failed.** The docs say
  ``None`` means no limit, but dumping a list of objects failed with a
  ``TypeError``.

* **Fixed: deep copying an object that refers back to itself failed.** Such
  as any Django form, whose bound fields refer to their form. The dump failed
  with a ``RecursionError``, with ``deepcopy=True`` or the new
  ``DJANGO_DD_DEEPCOPY`` setting.

* **Fixed: uniques could be wrong, and their records grew without limit.**
  The records used to count an object dumped more than once, and to match
  deep copies to their originals, were kept for as long as the server ran.
  They grew with every dump, and since a unique comes from the object's
  ``id()``, which Python reuses, an object could be taken for one dumped on
  an earlier page, and get the wrong unique. They are now kept for one page.

* **Added: a setting to deep copy every dump.** With the new
  ``DJANGO_DD_DEEPCOPY`` setting on, each dump shows the object as it was at
  the time of the call, as with ``deepcopy=True``, so that dumping one object
  before and after a change shows both states. ``deepcopy=True`` or
  ``deepcopy=False`` in a call still overrides it. Objects that can't be
  copied are dumped as they are, with a ``(not copied)`` note, instead of
  raising an error. The default of the ``deepcopy`` argument is now ``None``,
  which uses the setting.

* **Fixed: override_settings didn't change most settings.** Most
  ``DJANGO_DD_*`` settings were read once, when the package was imported, so
  ``override_settings`` in a project's tests had no effect on them. All
  settings are now read each time they are used.

* **Added: dumps above the page.** With the new
  ``DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE`` setting on, ``dump()`` without ``dd()``
  shows the dumps above the page's own content, instead of replacing the page.
  Responses that aren't HTML pages are still replaced. Dumps on Django's
  error page, after an unhandled exception, can now be turned off with
  ``DJANGO_DD_SHOW_DUMPS_ON_ERROR_PAGE``, and their toolbar no longer covers
  the top of the error page.
  (`#45 <https://github.com/DJBarnes/django-dump-die/issues/45>`_)

* **Fixed: dumps in a page changed the page's own elements.** With the
  ``{% dump %}`` template tag, the dumps' styles also applied to the page's
  own elements with the same class names, such as ``type``, ``key``, or
  ``number``, and their script opened and closed the page's own elements with
  the ``arrow-toggle`` class. The dumps also replaced the page's favicon.
  Styles and scripts now only apply to dumped output, and the script can be
  loaded more than once on a page.

* **Fixed: some values were added to the dump page as HTML.** A dict key
  whose ``repr()`` was marked safe, such as one built with ``format_html()``,
  was added to the page as HTML instead of shown as text. Every value is now
  escaped.

* **Fixed: the error page with dumps could be cut off.** After an unhandled
  exception, dumps are added to Django's error page. The page kept its old
  ``Content-Length``, such as one set by ``CommonMiddleware``, so the browser
  stopped reading it early.

* **Fixed: dumps were shown after DEBUG was turned off.** Objects dumped while
  ``DEBUG`` was on, such as in a test that turns it on, were still shown on
  the next response after it was turned off. They are now dropped instead.

* **Fixed: some strings and form fields were dumped badly.** Subclasses of
  ``str``, such as Django's ``SafeString`` from ``mark_safe()`` or a rendered
  page, were dumped one character at a time, and lazy translation strings from
  ``gettext_lazy()`` were dumped as ``__proxy__`` objects. Both are now shown
  as their text, like a ``str``, with their own type, or ``lazy str``. A form's
  bound field showed only ``<BoundField object at 0x...>``. It now shows its
  rendered widget, as text, and its attributes, such as ``name``, ``label``,
  and ``errors``, one level deep. An intermediate object shown again, as
  already output, also kept its color.
  (`#50 <https://github.com/DJBarnes/django-dump-die/issues/50>`_)

* **Fixed: some dumped objects got the wrong name.** The name shown for a
  dumped object comes from the line that called ``dump()`` or ``dd()``. It was
  wrong when one line had two calls, such as ``dump(user); dump(order)``,
  which named both ``order``. It was also wrong after a comment that mentions
  ``dump(...)``, and for an argument containing a string with a comma and an
  equals sign. On Python 3.6 and 3.7, a call over several lines had no name.
  Names also lost the spaces between their parts, so ``a if b else c`` was
  shown as ``aifbelsec``. The call is now found from the running code, and its
  first argument is read with Python's tokenizer.
  (`#46 <https://github.com/DJBarnes/django-dump-die/issues/46>`_)

* **Added: function results.** With ``DJANGO_DD_INCLUDE_FUNCTION_RESULTS`` on,
  a new Function Results section shows what some functions of a dumped object
  return: a few built-in ones for dates and times, the methods listed in a
  class's ``dd_function_results`` attribute, and the functions set by class
  name in ``DJANGO_DD_FUNCTION_RESULTS``. Only functions that need no
  arguments are run, and an error is shown in place of a result. It's off by
  default, since it runs code on every dump page.
  ``DJANGO_DD_FUNCTION_RESULTS_START_EXPANDED`` sets whether the section
  starts open.
  (`#11 <https://github.com/DJBarnes/django-dump-die/issues/11>`_,
  `#12 <https://github.com/DJBarnes/django-dump-die/issues/12>`_)

* **Added: properties and class attributes are marked.** In the Attributes
  section, properties show ``@property`` before their name, and cached
  properties, from Django or ``functools``, show ``@cached_property``, in the
  same ``identifiers.decorator`` color as the static and class method markers.
  Attributes whose value comes from the object's class, instead of the object
  itself, are shown in a slightly different grey, with a "Class Attribute"
  tooltip. Their color can be set with ``identifiers.class_attribute`` in
  ``DJANGO_DD_COLOR_SCHEME``.
  (`#40 <https://github.com/DJBarnes/django-dump-die/issues/40>`_)

* **Fixed: the Functions section could be closed when it was the only
  section.** With ``DJANGO_DD_INCLUDE_ATTRIBUTES`` off and
  ``DJANGO_DD_INCLUDE_FUNCTIONS`` on, the Functions section is always shown,
  without an arrow, but clicking its name still hid it, and there was no
  arrow to show that it could be opened again. It now stays shown, like the
  Attributes section does when it's the only one.

* **Fixed: dumping a callable called it.** When a dumped object could be
  called, the dump page's templates called it while rendering it, as Django
  templates do. A dumped function was run once, or three times if it had no
  docstring, in which case its return value was dumped instead of the
  function. A class was dumped as a new instance of it, or as an empty string
  if its constructor needed arguments. Dumped functions, classes, and other
  callables are now shown without being called. The ``{% dump %}`` template
  tag still can't dump a callable, since Django calls it before the tag gets
  it.

* **Changed: the middleware is async-capable.** On Django 3.1 or later, under
  ASGI, ``DumpAndDieMiddleware`` runs async, so Django no longer wraps the rest
  of the middleware chain in ``async_to_sync`` around it, and normal requests
  don't switch threads for it. ``dump()`` and ``dd()`` work in async views, and
  the dump page is rendered in a thread so that dumped QuerySets can be
  evaluated. Under WSGI nothing changes.
  (`#33 <https://github.com/DJBarnes/django-dump-die/issues/33>`_)

* **Added: breaks between dumps.** ``dump.br()`` shows a break between the
  objects dumped before and after it: a blank row, as tall as a one-line dump,
  with a dashed line across it. ``DJANGO_DD_BREAK_STYLE`` sets the line to
  ``"dashed"``, ``"solid"``, ``"dotted"``, or ``"blank"``. A break can also be
  several lines tall, with ``dump.br(size=3)`` for one break or
  ``DJANGO_DD_BREAK_SIZE`` for the default (``1``).
  (`#26 <https://github.com/DJBarnes/django-dump-die/issues/26>`_)

* **Fixed: some custom color theme keys were ignored.** In
  ``DJANGO_DD_COLOR_SCHEME``, ``meta.braces``, ``identifiers.dumped_name``, and
  ``types.default`` had no effect, ``identifiers.params`` was ignored when a
  theme was forced with ``DJANGO_DD_FORCE_LIGHT_THEME`` or
  ``DJANGO_DD_FORCE_DARK_THEME``, and setting ``meta.access_modifier`` or
  ``identifiers.constant`` without ``braces`` or ``dumped_name`` wrote an empty
  color. Each key now sets its own color.

* **Added: static and class methods are marked.** In the Functions section,
  static methods show ``@staticmethod`` and class methods show
  ``@classmethod`` before their name. Their color can be set with
  ``identifiers.decorator`` in ``DJANGO_DD_COLOR_SCHEME``.
  (`#15 <https://github.com/DJBarnes/django-dump-die/issues/15>`_)

* **Fixed: the dump template tag restyled the whole page.** ``{% dump %}``
  loaded Bootstrap 4's CSS and the dump page's styles for ``body`` and ``hr``,
  which changed the fonts, colors, and layout of the page around the dump, and
  clashed with a page's own Bootstrap, such as AdminLTE's Bootstrap 3. The
  package no longer loads Bootstrap's CSS, and its CSS now only styles the
  dumped output. The dump page itself looks the same as before.
  (`#19 <https://github.com/DJBarnes/django-dump-die/issues/19>`_)

* **Fixed: DJANGO_DD_INCLUDE_MAGIC_METHODS didn't show magic methods.** Magic
  names also start with an underscore, so they were left out unless
  ``DJANGO_DD_INCLUDE_PRIVATE_MEMBERS`` was on too. They now only follow
  ``DJANGO_DD_INCLUDE_MAGIC_METHODS``.

* **Fixed: index_range didn't select the items of the dumped object.** It was
  checked against the dumped object itself instead of its direct children, so
  a range starting at 0 expanded every item, and any other range expanded
  nothing, not even the dumped object. It now selects the direct children, as
  documented.

* **Fixed: a start index that isn't a number crashed index_range.** A start
  index such as ``index_range=("a", 2)`` raised ``ValueError``. It's now
  ignored, like an end index that isn't a number.

* **Fixed: dumping a QuerySet whose query fails crashed the dump page.** If a
  dumped QuerySet raises a database error, such as when its table doesn't
  exist, the dump shows the error with its traceback, like other objects that
  raise while being inspected.

* **Fixed: the Django example pages crashed.** The Django model, Django types,
  and "full category" example pages raised an error: they queried tables that
  the sample models don't have, read an image file that the package doesn't
  ship, and removed a field from the sample model on the first visit. They now
  render on every visit, without a database table or files on disk.

* **Changed: expanding and collapsing is fast on large dumps.** Opening one
  section, and the toolbar's Expand and Collapse buttons, used to take longer
  the more the page dumped: for a list of 100 nested dicts, one click took
  almost a second, and Expand All took over two minutes. Each click now only
  updates its own section, and the toolbar buttons update every section in one
  pass. Single sections still slide open and closed.
  (`#30 <https://github.com/DJBarnes/django-dump-die/issues/30>`_)

* **Changed: jQuery and Bootstrap's JavaScript are no longer loaded.** The dump
  page and the ``{% dump %}`` template tag only load Bootstrap's CSS and the
  package's own JavaScript. A page that uses ``{% dump %}`` keeps its own
  jQuery and Bootstrap versions, and its Bootstrap no longer also handles the
  dump's sections, which now use ``data-dd-toggle`` instead of
  ``data-toggle``.

* **Fixed: the Attributes arrow didn't change when the section opened or
  closed.** It now does, like the other arrows.

* **Changed: more Python and Django versions are supported and tested.**
  The package supports Python 3.6 to 3.14 and Django 2.2 to 6.1, and the
  tests run on each Django LTS release and the newest releases, on every
  Python version that release supports. 0.1.7 listed Python 3.8 and Django
  3.2 as the minimums.

* **Added: dumped objects show on error pages.** When a view calls ``dump()``
  and then raises an exception that doesn't come from ``dd()``, the dumped
  objects are shown at the top of Django's error page. This only happens when
  ``DEBUG`` is ``True``.

* **Fixed: the dump template tag ran with DEBUG off.** ``{% dump %}`` now
  renders nothing unless ``DEBUG`` is ``True``, the same as ``dump()`` and
  ``dd()``.

* **Fixed: the package installed a top-level tests package.** 0.1.7 also
  installed its own tests as a top-level ``tests`` package, which could shadow
  a project's own ``tests`` package. Only ``django_dump_die`` is installed now.

* **Added: more example pages.** The example pages in ``django_dump_die.urls``
  now include dumping from a template, dumping an object that raises an
  exception while it is inspected, and an unhandled exception after dumps.

* **Removed: test-only urls and views.** ``django_dump_die.test_urls`` and
  ``django_dump_die.views.test_views`` were only used by the package's tests,
  and moved out of the package.


0.1.7 (2023-09-17)
==================

* No changes to the package. Updates to how the docs are built on
  ReadTheDocs, and a code of conduct.


0.1.6 (2023-09-03)
==================

Action Needed When Upgrading
----------------------------

* **Changed: Python 3.8 and Django 3.2 or later are needed.** Support for
  Python 3.11 and Django 4.1 and 4.2 was added, and support for Python 3.7
  and Django 3.0 and 3.1 removed.

Other Changes
-------------

* **Fixed: enum members were dumped incorrectly on Python 3.11.**


0.1.5 (2022-10-24)
==================

Action Needed When Upgrading
----------------------------

* **Changed: the default DJANGO_DD_MAX_RECURSION_DEPTH is 5.** It was 20.
  Set ``DJANGO_DD_MAX_RECURSION_DEPTH`` to dump deeper objects.

Other Changes
-------------

* **Fixed: DJANGO_DD_MAX_ITERABLE_LENGTH and DJANGO_DD_MAX_RECURSION_DEPTH
  didn't limit dumps correctly.**

* **Fixed: a dict's length wasn't shown after its type.**


0.1.4 (2022-09-09)
==================

* **Added: the traceback of an object that fails while it is dumped.** When
  reading an object's members raises an exception, the dump shows an
  ``EXCEPTION`` row. Hover over it to see the exception's type, message, and
  traceback.

* **Fixed: Django QueryDict objects, such as request.GET, failed to dump.**
  Immutable ones, as Django gives requests, raised an error.

* **Fixed: dumping a model class with a many-to-many field failed.**

* **Added: a Built-In Examples page in the docs.**


0.1.3 (2022-07-19)
==================

* **Fixed: import errors on Python before 3.9, and without pytz.** The
  package needed ``zoneinfo``, which was added in Python 3.9, and ``pytz``.
  Both are now optional, and their timezones are dumped when they are
  available.


0.1.2 (2022-06-28)
==================

* No changes to the package. The docs say to install it from PyPI, and the
  README links to them.


0.1.1 (2022-06-28)
==================

* No changes to the package. Fixed its version number in the docs and the
  package settings.


0.1.0 (2022-06-28)
==================

* First release: ``dd()`` and ``dump()`` show dumped objects in an expandable
  tree, in place of the page, with color themes and highlighting of the same
  object where it is shown more than once.
