#!/usr/bin/env python
"""Run Package Tests.

Current expected testing methods are `manage.py` and `pytest`,
with `pytest` being the preferred method.
"""

# System Imports.
import argparse
import os
import subprocess
import sys
from shutil import which

# Third-Party Imports.
from django.core.management import execute_from_command_line

try:
    from colorama import Back, Fore, Style

    COLORAMA_PRESENT = True
except ImportError:
    # If we got this far, colorama package is not provided in environment.
    COLORAMA_PRESENT = False


# Define output colors.
if COLORAMA_PRESENT:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    NC = Style.RESET_ALL
else:
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    CYAN = ""
    NC = ""


def main():
    """Entry point."""

    # Get the script directory.
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Determine if pytest installed.
    has_pytest = which("pytest") is not None

    # Parse provided command line args.
    parser = argparse.ArgumentParser()
    parser.description = "Run project tests with either pytest or manage.py and optionally collect coverage."
    parser.add_argument(
        "--with-coverage",
        default=False,
        action="store_true",
        help="Run coverage while testing and make an html report.",
    )
    parser.add_argument(
        "--less-than-100",
        default=False,
        action="store_true",
        help="Limit coverage output to only files with less than 100 percent coverage.",
    )
    parser.add_argument(
        "--force-django-manage-test",
        default=False,
        action="store_true",
        help="Force using manage.py test even if pytest is installed. NOTE: Pytest provides better test output.",
    )
    parser.add_argument(
        "--show-return-code",
        default=False,
        action="store_true",
        help="Display return code at end of testing.",
    )
    args, extra_args = parser.parse_known_args()

    # Handle based on args.
    if has_pytest and not args.force_django_manage_test:
        # Run tests with pytest.
        run_tests_with_pytest(args, extra_args, script_dir)
    else:
        # Run tests with django manage.py test.
        run_tests_with_manage(args, extra_args, script_dir)


# region Pytest Tests


def run_tests_with_pytest(args, extra_args, script_dir):
    """Run tests with pytest format.
    Has helpful and verbose testing output.
    """

    if args.with_coverage:
        # Run pytest with coverage.
        run_tests_with_pytest_and_coverage(args, extra_args, script_dir)
    else:
        # Run pytest without coverage.
        print_info("Running tests with pytest...")

        # Generate command.
        run_args = ["pytest"] + extra_args
        print_primary(f"Command: {' '.join(run_args)}")

        # Run command.
        proc = subprocess.run(run_args, check=False)

        # Terminate with process exit code.
        exit_script(args, proc.returncode)


def run_tests_with_pytest_and_coverage(args, extra_args, script_dir):
    """Run tests with pytest and coverage."""
    return_code = execute_pytest_coverage_tests(extra_args)

    # Run tests and collect the coverage data.
    if return_code != 0:
        print_error("Report not created. Error while running tests.")
        exit_script(args, return_code)

    # If calculating less than 100% files.
    if args.less_than_100:
        # Run coverage and report only < 100% covered.
        print_info("Creating coverage report for files less than 100 percent coverage...")
        return_code = create_html_coverage_report(script_dir, lt_100=True)
    else:
        # Run coverage and report everything.
        print_info("Creating coverage report for all files...")
        return_code = create_html_coverage_report(script_dir, lt_100=False)

    # Terminate with process exit code.
    exit_script(args, return_code)


def execute_pytest_coverage_tests(extra_args):
    """Actual command logic to run tests with pytest and create coverage data."""
    print_info("Running pytest and creating coverage data...")

    # Generate command.
    run_args = [
        "pytest",
        "-n",
        "auto",
        "--cov=.",
        "--disable-pytest-warnings",
        "--cov-report=",
    ] + extra_args
    print_primary(f"COMMAND: {' '.join(run_args)}")

    # Run command.
    proc = subprocess.run(run_args, check=False)

    # Return process exit code.
    return proc.returncode


# endregion Pytest Tests


# region Manage.py Tests


def run_tests_with_manage(args, extra_args, script_dir):
    """Run tests with manage.py format.
    Has less helpful testing output than pytest.
    """

    # Set environment values.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    if args.with_coverage:
        # Run manage.py test with coverage.
        run_tests_with_manage_and_coverage(args, extra_args, script_dir)
    else:
        # Run manage.py tests without coverage.
        print_info("Running tests with manage.py...")

        # Generate command.
        run_args = sys.argv[:1] + ["test"] + ["--buffer"] + extra_args
        print_primary(f"COMMAND: {' '.join(run_args)}")

        # Run command.
        return_code = execute_from_command_line(run_args)

        # Terminate with process exit code.
        exit_script(args, return_code)


def run_tests_with_manage_and_coverage(args, extra_args, script_dir):
    """Run tests with manage.py and coverage."""
    return_code = execute_manage_coverage_tests(extra_args, script_dir)

    # Run tests and collect the coverage data.
    if return_code != 0:
        print_error("Report not created. Error while running tests.")
        exit_script(args, return_code)

    # If calculating less than 100% files.
    if args.less_than_100:
        # Run coverage and report only < 100% covered.
        print_info("Creating coverage report for files less than 100 percent coverage...")
        return_code = create_html_coverage_report(script_dir, lt_100=True)
    else:
        # Run coverage and report everything.
        print_info("Creating coverage report for all files...")
        return_code = create_html_coverage_report(script_dir, lt_100=False)

    # Terminate with process exit code.
    exit_script(args, return_code)


def execute_manage_coverage_tests(extra_args, script_dir):
    """Actual command logic tun tests with manage and create coverage data."""
    print_info("Running manage.py and creating coverage data...")

    # Generate command.
    virtual_env_path = os.environ["VIRTUAL_ENV"]
    run_args = [
        "coverage",
        "run",
        f"{virtual_env_path}/bin/django-admin",
        "test",
        "--pythonpath",
        f"{script_dir}",
        "--buffer",
    ] + extra_args
    print_primary(f"COMMAND: {' '.join(run_args)}")

    # Run command.
    proc = subprocess.run(run_args, check=False)

    # Return process exit code.
    return proc.returncode


# endregion Manage.py Tests


def create_html_coverage_report(script_dir, lt_100=False):
    """Create coverage report."""
    path = f"{script_dir}/.django_dump_die_coverage_html_report"

    # Generate command.
    run_args = [
        "coverage",
        "html",
    ]
    if lt_100:
        run_args = run_args + ["--skip-covered"]
    run_args = run_args + ["-d", f"{path}"]
    print_primary(f"COMMAND: {' '.join(run_args)}")

    # Run command.
    proc = subprocess.run(run_args, check=False)

    # Handle based on process return code.
    if proc.returncode != 0:
        print_error("Error while generating coverage report.")
    else:
        print_primary("Coverage report generated. Report can be accessed at:")
        print_warning(f"file://{path}/index.html")
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


def exit_script(args, return_code):
    """Print exit message and terminate script."""

    # Show return code + exit message if arg provided.
    if args.show_return_code:
        print_info(f'Testing completed with exit code of "{return_code}"')

    # Exit with return code.
    sys.exit(return_code)


# Prevent running on import.
if __name__ == "__main__":
    main()
