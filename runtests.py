#!/usr/bin/env python
"""Run Package Tests"""
import argparse
import os
import subprocess
import sys
from django.core.management import execute_from_command_line
from shutil import which

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def main():
    """Main method"""

    # Get the script dir
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Determine if pytest installed.
    has_pytest = which("pytest") is not None

    # Create parser and parse command line args.
    parser = argparse.ArgumentParser()
    parser.description = "Run project tests with either pytest or manage.py and optionally collect coverage."
    parser.add_argument(
        "--with-coverage",
        default=False,
        action="store_true",
        help="Whether to run coverage while testing and make an html report.",
    )
    parser.add_argument(
        "--less-than-100",
        default=False,
        action="store_true",
        help="Whether to limit coverage output to only files with less than 100 percent coverage.",
    )
    parser.add_argument(
        "--force-django-manage-test",
        default=False,
        action="store_true",
        help="Force using manage.py test even if pytest is installed. NOTE: Pytest provides better test output.",
    )

    args, extra_args = parser.parse_known_args()

    if has_pytest and not args.force_django_manage_test:
        # Run tests with pytest.
        run_tests_with_pytest(args, extra_args, script_dir)
    else:
        # Run tests with django manage.py test.
        run_tests_with_manage(args, extra_args, script_dir)


def run_tests_with_pytest(args, extra_args, script_dir):
    """Run tests with pytest."""

    if args.with_coverage:
        # Run pytest with coverage.
        run_tests_with_pytest_and_coverage(args, script_dir)
    else:
        # Run pytest without coverage
        print_info("Run pytest.")
        run_args = ["pytest"] + extra_args
        print_primary(f"Command: {' '.join(run_args)}")
        proc = subprocess.run(run_args, check=False)
        sys.exit(proc.returncode)


def run_tests_with_pytest_and_coverage(args, script_dir):
    """Run tests with pytest and coverage."""
    return_code = run_tests_with_pytest_and_create_coverage_data()

    # Run tests and collect the coverage data.
    if return_code != 0:
        print_error("Report not created. Error while running tests.")
        sys.exit(return_code)

    # If calculating less than 100% files
    if args.less_than_100:
        # Run coverage and report only < 100% covered.
        print_info("Create coverage with files less than 100 percent coverage.")
        return_code = create_html_coverage_report(script_dir, lt_100=True)
    else:
        # Run coverage and report everything.
        print_info("Create coverage for all files.")
        return_code = create_html_coverage_report(script_dir, lt_100=False)

    sys.exit(return_code)


def run_tests_with_pytest_and_create_coverage_data():
    """Run tests with pytest and create coverage"""
    print_info("Run pytest and create coverage data.")
    run_args = [
        "pytest",
        "-n",
        "auto",
        "--cov=.",
        "--disable-pytest-warnings",
        "--cov-report=",
    ]
    print("COMMAND:")
    print_primary(f"{' '.join(run_args)}")
    proc = subprocess.run(run_args, check=False)
    return proc.returncode


def run_tests_with_manage(args, extra_args, script_dir):
    """Run tests with manage.py."""

    # Set environment values.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    if args.with_coverage:
        # Run manage.py test with coverage.
        run_tests_with_manage_and_coverage(args, script_dir)
    else:
        # Run tests.
        run_args = sys.argv[:1] + ["test"] + extra_args + ["--buffer"]
        print("COMMAND:")
        print_primary(f"{' '.join(run_args)}")
        sys.exit(execute_from_command_line(run_args))


def run_tests_with_manage_and_coverage(args, script_dir):
    """Run tests with manage.py and coverage."""
    return_code = run_tests_with_manage_and_create_coverage_data(script_dir)

    # Run tests and collect the coverage data.
    if return_code != 0:
        print_error("Report not created. Error while running tests.")
        sys.exit(return_code)

    # If calculating less than 100% files
    if args.less_than_100:
        # Run coverage and report only < 100% covered.
        print_info("Create coverage with files less than 100 percent coverage.")
        return_code = create_html_coverage_report(script_dir, lt_100=True)
    else:
        # Run coverage and report everything.
        print_info("Create coverage for all files.")
        return_code = create_html_coverage_report(script_dir, lt_100=False)

    sys.exit(return_code)


def run_tests_with_manage_and_create_coverage_data(script_dir):
    """Run tests with manage and create coverage"""
    print_info("Run manage.py test and create coverage data.")

    virtual_env_path = os.environ["VIRTUAL_ENV"]

    run_args = [
        "coverage",
        "run",
        f"{virtual_env_path}/bin/django-admin",
        "test",
        "--pythonpath",
        f"{script_dir}",
    ]
    print("COMMAND:")
    print_primary(f"{' '.join(run_args)}")
    proc = subprocess.run(run_args, check=False)
    return proc.returncode


def create_html_coverage_report(script_dir, lt_100=False):
    """Create coverage report for all files"""
    path = f"{script_dir}/.django_dump_die_coverage_html_report"
    run_args = [
        "coverage",
        "html",
    ]
    if lt_100:
        run_args = run_args + ["--skip-covered"]
    run_args = run_args + ["-d", f"{path}"]

    print("COMMAND:")
    print_primary(f"{' '.join(run_args)}")

    proc = subprocess.run(run_args, check=False)
    if proc.returncode != 0:
        print_error("Error while generating coverage report.")
    else:
        print_primary("Report can be accessed at:")
        print_warning(f"file://{path}/index.html")
        print_success("Done!")
    return proc.returncode


def print_primary(objects):
    """Print colored as blue"""
    print(f"{BLUE}{objects}{NC}")


def print_info(objects):
    """Print colored as cyan"""
    print(f"{CYAN}{objects}{NC}")


def print_success(objects):
    """Print colored as green"""
    print(f"{GREEN}{objects}{NC}")


def print_warning(objects):
    """Print colored as yellow"""
    print(f"{YELLOW}{objects}{NC}")


def print_error(objects):
    """Print colored as red"""
    print(f"{RED}{objects}{NC}")


# Prevent running on import.
if __name__ == "__main__":
    main()
