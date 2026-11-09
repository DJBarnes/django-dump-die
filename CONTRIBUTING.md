## Contributing

[fork]: /fork
[pr]: /compare
[style]: https://docs.astral.sh/ruff/
[code-of-conduct]: CODE_OF_CONDUCT.md

Hi there! We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

Please note that this project is released with a [Contributor Code of Conduct][code-of-conduct]. By participating in this project you agree to abide by its terms.

## Issues and PRs

If you have suggestions for how this project could be improved, or want to report a bug, open an issue! We'd love all and any contributions. If you have questions, too, we'd love to hear them.

We'd also love PRs. If you're thinking of a large PR, we advise opening up an issue first to talk about it, though! Look at the links below if you're not sure how to open a PR.

## Submitting a pull request

1. [Fork][fork] and clone the repository.
1. Configure and install Pipenv: `python -m pip install pipenv`.
1. Create a virtual environment using pipenv for the latest supported version of python.
1. Configure and install the dependencies: `pipenv install --dev`.
1. Make sure the tests pass on your machine: `pipenv run python runtests.py`.
1. Ensure you are able to run tests with code coverage: `pipenv run python runtests.py --with-coverage`.
1. Create a new branch: `git checkout -b my-branch-name`.
1. Make your change, add tests, and make sure the tests still pass.
1. Push to your fork and [submit a pull request][pr].
1. Pat your self on the back and wait for your pull request to be reviewed and merged.

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

- Format and lint your code with [Ruff][style]: `pipenv run ruff format .` and `pipenv run ruff check .` (settings are in `pyproject.toml`).
- Write and update tests.
- Verify new functionality and tests do not reduce test coverage.
- Keep your changes as focused as possible. If there are multiple changes you would like to make that are not dependent upon each other, consider submitting them as separate pull requests.
- Write commit messages as [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): summary`, for example `fix(middleware): ...` or `test: ...`.
- Add an entry for each user-facing change to the "Unreleased" section at the top of `docs/source/version_history.rst`, in the same commit. If there is none yet since the last release, add it.

Work in Progress pull requests are also welcome to get feedback early on, or if there is something blocking you.

## Tests

The tests live in `tests/django_dump_die_tests/`. `tests/` is not a Python package; it is put on the path (see `pythonpath` in `pyproject.toml`), so the test code is imported as `django_dump_die_tests`. This name is unique to this package, so another Django project can install the test project next to the test projects of other packages.

- `django_test_project/` is the Django project the tests run in: its settings, its root urls, and the test views index page at `/tests/`. It is also an app with the label `django_dump_die_tests`.
- The other folders hold the tests, grouped by what they check: `simple_types/`, `complex_types/`, `function_types/`, `django_types/`, `general/` (middleware, template tag, and DEBUG behavior), and `example_views/` (the example pages shipped in the package). Folders with their own test views also have `views.py` and `urls.py`.

To run one file or one test:

```bash
pipenv run pytest tests/django_dump_die_tests/simple_types/test_simple_types.py
pipenv run pytest "tests/django_dump_die_tests/general/test_general.py::DumpDieGeneralTestCase::test_debug_off_skips_all_dumps"
```

`python runtests.py --force-django-manage-test` runs the same tests with `manage.py test` instead of pytest. To run the full matrix of Python and Django versions, run `tox`.

### Browser tests

`browser/` holds Selenium tests of the dump page's JavaScript (expanding, collapsing, the toolbar, and duplicate highlighting). They run with the rest of the tests when `selenium` is installed (it is in the Pipfile's dev packages), and need a browser. Choose it with environment variables:

- `DJANGO_DD_SELENIUM_BROWSER`: `firefox` (the default), `chrome`, or `none` to skip the browser tests.
- `DJANGO_DD_SELENIUM_HEADLESS=true`: run the browser without a window.
- `DJANGO_DD_SELENIUM_BROWSER_BINARY`: the browser's executable, if Selenium doesn't find it. Firefox installed as a snap (as on Ubuntu) is found without it.

`tox -e browser` runs only the browser tests, in headless Firefox.

## Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
- [GitHub Help](https://help.github.com)
