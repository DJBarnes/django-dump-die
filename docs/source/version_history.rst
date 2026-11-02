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
