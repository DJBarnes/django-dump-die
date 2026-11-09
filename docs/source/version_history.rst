Version History
***************

Unreleased
==========

Action Needed When Upgrading
----------------------------

* **Changed: pytz is no longer installed with the package.** 0.1.7 listed
  ``pytz`` as a dependency. Timezone objects from ``pytz`` are still dumped
  correctly when it is installed. If your project uses ``pytz``, add it to
  your project's own requirements.

* **Changed: sensitive values are hidden.** Like Django's debug page, dumps
  now show ``********************`` in place of values whose names look
  sensitive, such as ``SECRET_KEY``, ``password``, ``access_token``, the
  session cookie, and the ``Cookie`` header. Functions with such names are not
  run for function results. To show them again, set
  ``DJANGO_DD_SHOW_SENSITIVE_VALUES = True``. See the new Security page of the
  docs for the names that are hidden, and for other things to watch out for.

Other Changes
-------------

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
