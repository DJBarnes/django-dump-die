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

Other Changes
-------------

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
