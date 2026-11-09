# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`django-dump-die` is a reusable Django app (not a project) that adds Laravel/Symfony-style `dump()` and `dd()` debugging helpers. Dumped objects replace the page response with an expandable HTML tree. Nothing happens unless `settings.DEBUG` is `True`. User-facing docs live in `docs/source/` (Sphinx, published to ReadTheDocs). Built with flit; the version is `__version__` in `django_dump_die/__init__.py`.

## Commands

Dependencies come from Pipenv: `pipenv install --dev` (`Pipfile.lock` is gitignored, so there is nothing to `sync`).

```bash
pipenv run python runtests.py                    # pytest (settings and pythonpath come from pyproject.toml)
pipenv run python runtests.py --with-coverage    # plus an HTML report in .django_dump_die_coverage_html_report/
pipenv run python runtests.py --force-django-manage-test   # same tests with manage.py test
pipenv run pytest tests/django_dump_die_tests/simple_types/test_simple_types.py
pipenv run pytest "tests/django_dump_die_tests/general/test_general.py::DumpDieGeneralTestCase::test_debug_off_skips_all_dumps"
tox                                              # Python 3.6–3.14 × Django 2.2–6.1 matrix, browser, docs, warnings
pipenv run ruff format .                         # format with Ruff (line length 120; settings in pyproject.toml)
pipenv run ruff check .                          # lint with Ruff; CI runs both
pipenv run sphinx-build -WE docs/source docs/build   # CI builds docs with warnings as errors
./docs/generate_docs.sh                          # regenerates docs/source/api_reference with sphinx-apidoc
```

`runtests.py` runs pytest, Django and coverage with its own interpreter (`sys.executable`), so inside tox the tests use that environment's Django.

## Conventions

- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `chore`. Commits are GPG-signed (`commit.gpgsign` is set in this repo's local git config).
- Each user-facing change adds an entry to the "Unreleased" section at the top of `docs/source/version_history.rst` in the same commit (add the section if the last release removed it).
- Supported versions are kept wide on purpose (Python ≥3.6, Django ≥2.2) until a complete release; don't drop old versions without asking.

## Architecture

**Request flow** (`django_dump_die/middleware.py`):
- On init, `DumpAndDieMiddleware` injects `dd` and `dump` into `__builtins__`, so calling code doesn't import them. That is why editors flag `dd(...)` as undefined, which is intentional.
- `dump(obj)` adds the object's info to a module-level `dump_objects` list. This list is shared across the whole server and isn't thread safe. After the response, `_process_response` replaces it with `dd_view` if anything was dumped (never with `DEBUG` off), or, with `DJANGO_DD_SHOW_DUMPS_ABOVE_PAGE` on, adds the dumps above an HTML page's content with `_add_dumps_above_page`; responses that can't take them (not HTML, no `<body>`, streaming, redirects, compressed) still get `dd_view`.
- `dump.br()` (`dump_break`, attached as an attribute of `dump` so it needs no built-in name of its own) adds a `utils.DumpBreak` marker entry, with an optional `size`; `_dump_objects.html` renders it as a break, using the `is_dump_break` filter.
- The middleware is sync- and async-capable. With an async `get_response` (ASGI, Django 3.1+), `__acall__` awaits the chain and only switches to a thread (`sync_to_async`) to render the dump page when something was dumped; both paths share `_process_response`. Imports of asgiref are guarded, since Django 2.2 doesn't install it.
- `dd(obj)` raises the `DumpAndDie` exception. `process_exception` catches it, adds the object to the dumped list, and returns `dd_view`.
- Any other unhandled exception marks the request (`has_non_dd_exception`). If something was dumped and `DEBUG` is on, the dumps are added above Django's error page with the same `_add_dumps_above_page` (head from `partials/_head.html`, body from `partials/_above_page.html`), unless `DJANGO_DD_SHOW_DUMPS_ON_ERROR_PAGE` is off. `_set_content` keeps `Content-Length` right.
- `views/dd_view.py` reads the toolbar and theme settings and renders `templates/django_dump_die/dd.html` (or a partial, as a string).

**Object capture** (`utils.get_dumped_object_info`): it inspects the call stack and tokenizes the source line of the `dd`/`dump` call to recover the variable's name and location. It returns a tuple `(filename, linenumber, obj_name, obj, function_doc, start_index, end_index, original_obj)` that the templates unpack. Enums are converted to a fake `utils.Enum` class, and `deepcopy=True` keeps the original object so that uniques can still be computed.

**Rendering** (`templatetags/dump_die.py`): rendering recurses through templates. `dump_object` is an inclusion tag, and its template (`partials/_dump_object.html` → `output_types/*.html` → `partials/_attributes.html` / `_functions.html`) calls `dump_object` again for each child. Each object is classified as one of:
- **simple**: `constants.SIMPLE_TYPES`. Prints the value only.
- **intermediate**: `constants.INTERMEDIATE_TYPES`, such as datetimes and paths. Expands one level; its children are rendered as simple.
- **complex**: everything else. Fully recursive, limited by `MAX_RECURSION_DEPTH`. Of an iterable (not a dict), `utils.get_members` lists only the items in its `utils.ItemRange` (the first `MAX_ITERABLE_LENGTH`, or the root's `index_range`), with a `NotDumpedItems` placeholder for those before and after. A QuerySet is never iterated or measured with `len()`: it is counted with `count()` and sliced, so only the dumped rows are fetched.

The tag tracks each object's "unique" (based on its `id`) in a `skip_set` and module-level maps (`repeat_iteration_tracker`, `deepcopy_unique_map`). This avoids infinite loops and renders objects it has already seen as back-references. The template `{% dump %}` tag checks `settings.DEBUG` itself, and loads the CSS/JS only for the first dump on a page.

**Front-end** (`static/django_dump_die/js/dd.js`): plain JavaScript; the page loads Bootstrap 4's CSS but no jQuery or Bootstrap JS. Each `.arrow-toggle` (`data-dd-toggle="collapse"` when collapsible; without it the section is "always show") is directly followed by its `.dd-wrapper`/`.li-wrapper` section and contains its `.arrow`, and `dd.js` relies on that structure. One delegated click handler opens/closes a section with Bootstrap's `.collapsing` height transition; CTRL+click and the toolbar buttons set many sections at once without animation. Keep it linear in page size: no per-element handlers or document-wide queries per element (see #30). Dumped output can sit inside another page (template tag, dumps above a page), so every lookup is limited to `.dump-wrapper` (`SCOPE`), and `dd.js` can be loaded twice (`var` plus `window.djangoDumpDie ||`). Likewise, `dd.css` and `_custom_color_theme.html` scope class selectors with `:where(.dump-wrapper)`, which keeps their specificity unchanged so custom themes still override them; page-level rules use `html.dump-die-page`.

**Settings** (`app_settings.py`): every `DJANGO_DD_*` option is an attribute of `app_settings`, named without the prefix (`app_settings.MAX_RECURSION_DEPTH` reads `DJANGO_DD_MAX_RECURSION_DEPTH`). Each is a `Setting(default)` descriptor on `AppSettings` that reads the Django setting on every access, so `override_settings` works; tests use it instead of patching. Being attributes, a misspelled setting is caught: `general/test_app_settings.py` checks that every `app_settings.NAME` in the package, and every `DJANGO_DD_*` name in the package, tests and docs (except the `DJANGO_DD_SELENIUM_*` environment variables), is a setting. To add a setting, add a `Setting` to `AppSettings` and a section to `docs/source/configuration.rst`; the same test file checks the two match. `constants.py` only holds real constants (types, `DEFAULT_FUNCTION_RESULTS`, `BREAK_STYLES`).

**Example views**: `views/example_views.py` and `views/example_helpers.py` (sample classes, Django models, and a form) power the browsable example pages in `django_dump_die/urls.py`, which ship with the package. The sample models live in that shipped module.

## Tests

- `tests/` is **not** a Python package; it is on the path (`pythonpath = [".", "tests"]`), and the test code is the uniquely named package `django_dump_die_tests`. This lets another Django project (for example `~/github/package_tester`) install this test project next to `django-adminlte2-pdq`'s `django_adminlte2_pdq_tests`. Don't add `tests/__init__.py`, and don't import anything as `tests.…`.
- `tests/django_dump_die_tests/django_test_project/` holds the settings (`DJANGO_SETTINGS_MODULE = django_dump_die_tests.django_test_project.settings`), the root urls (no `app_name`, so other projects can include it), the test views index page at `/tests/`, and `apps.py` (label `django_dump_die_tests`).
- Test folders: `simple_types/`, `intermediate_types/`, `complex_types/`, `function_types/` and `django_types/` each have their own test views and urls, one dump per view with fixed values (namespaces `django_dump_die__tests__simple`, `__intermediate`, `__complex`, `__function`, `__django`). `django_types/` checks the type and a few rows of each object, since Django's own attributes differ between versions. `example_views/` only smoke-tests the shipped example pages (each loads, with its description and main objects); `templatetags/` and `utils/` test those modules directly; `general/` covers middleware, settings, themes and DEBUG behavior.
- `browser/` holds Selenium tests of `dd.js` (`django_expanded_test_cases.LiveServerTestCase`). They skip without `selenium`; the browser is chosen with `DJANGO_DD_SELENIUM_BROWSER` (`firefox` default, `chrome`, `none`), `DJANGO_DD_SELENIUM_HEADLESS` (headless by default; `false` shows the window), and `DJANGO_DD_SELENIUM_BROWSER_BINARY` (snap Firefox is found automatically). In a window, Firefox first shows an error page for `window-position=0,0`, a Chrome flag that django-expanded-test-cases passes to every browser (brodriguez8774/django-expanded-test-cases#23); it doesn't affect the tests. From a VS Code shell on Ubuntu, snap Firefox needs a clean environment (`env -i ...`) or crashes at startup; set `DJANGO_DD_SELENIUM_BROWSER=none` to skip them in a normal run.
- Use `subTest` only to loop over data, with keyword labels (`self.subTest(style=..., size=...)`). A scenario with its own setup gets its own test method instead. Label values must be plain data, such as strings and numbers, not classes, functions or other objects: on Python below 3.10, pytest-subtests sends them between pytest-xdist workers, and fails if it can't serialize them. `subTest` results need pytest 9 (Python 3.10+, built in) or the pytest-subtests plugin (older Python); the `test` extras install the right one.
- Tests use `django_expanded_test_cases.IntegrationTestCase.assertGetResponse` to assert exact rendered HTML fragments, and patch `django_dump_die.templatetags.dump_die._generate_unique` for stable uniques. Any change to a template or to the markup the templatetag emits usually requires updating these expected strings. Expected output must not depend on the machine or Python version (paths, tracebacks, builtin docstrings).
