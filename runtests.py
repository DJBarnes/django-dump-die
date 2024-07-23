#!/usr/bin/env python
"""Run Package Tests.

Current expected testing methods are 'manage.py' and 'pytest',
with 'pytest' being the preferred method.
"""
import argparse
import os
import subprocess
import sys
from shutil import which

# Terminal color constants.
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
NC = "\033[0m"
# Path constants.
VIRTUAL_ENV_PATH = os.environ["VIRTUAL_ENV"]
SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
# Pytest command args.
PYTEST_ARGS = ["pytest"]
PYTEST_COVERAGE_ARGS = PYTEST_ARGS + [
    "-n",
    "auto",
    "--cov=.",
    "--disable-pytest-warnings",
    "--cov-report=",
]
# Manage command args.
MANAGE_ARGS = [
    f"{VIRTUAL_ENV_PATH}/bin/django-admin",
    "test",
    "--pythonpath",
    f"{SCRIPT_DIR}",
]
MANAGE_COVERAGE_ARGS = ["coverage", "run"] + MANAGE_ARGS


def main():
    """Main entry point method."""

    # Determine if pytest installed.
    has_pytest = which("pytest") is not None

    # Parse command line args.
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

    args, extra_args = parser.parse_known_args()

    # Handle based on args.
    if has_pytest and not args.force_django_manage_test:
        # Run tests with pytest.
        run_tests_with_pytest(args, extra_args)
    else:
        # Run tests with django manage.py test.
        run_tests_with_manage(args, extra_args)


def run_tests_with_pytest(args, extra_args):
    """Run tests with pytest."""

    # Set up run_args based on whether creating coverage or not.
    if args.with_coverage:
        print_info("Running tests with pytest and creating coverage data.")
        # Run command and get return code.
        return_code = run_command(PYTEST_COVERAGE_ARGS)
        # If return_code is non-zero, exit with return code.
        if return_code != 0:
            exit_with_code(return_code)
        # Create html coverage report and get return code.
        return_code = create_html_coverage_report(lt_100=args.less_than_100)
        # Exit with return code.
        exit_with_code(return_code)
    else:
        print_info("Running tests with pytest.")
        # Collect run args.
        run_args = PYTEST_ARGS + extra_args
        # Run command and get return code.
        return_code = run_command(run_args)
        # Exit with return code.
        exit_with_code(return_code)


def run_tests_with_manage(args, extra_args):
    """Run tests with manage.py."""

    # Set environment values.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    # Set up run_args based on whether creating coverage or not.
    if args.with_coverage:
        print_info("Running tests with manage.py test and creating coverage data.")
        # Run command and get return code.
        return_code = run_command(MANAGE_COVERAGE_ARGS)
        # If return_code is non-zero, exit with return code.
        if return_code != 0:
            exit_with_code(return_code)
        # Create html coverage report and get return code.
        return_code = create_html_coverage_report(lt_100=args.less_than_100)
        # Exit with return code.
        exit_with_code(return_code)
    else:
        print_info("Running tests with manage.py test.")
        # Collect run args.
        run_args = MANAGE_ARGS + extra_args + ["--buffer"]
        # Run command and get return code.
        return_code = run_command(run_args)
        # Exit with return code.
        exit_with_code(return_code)


def create_html_coverage_report(lt_100=False):
    """Create coverage report for all files"""
    # Create path to store the report in.
    path = f"{SCRIPT_DIR}/.django_dump_die_coverage_html_report"
    # Print info message and set up run_args for command.
    if lt_100:
        print_info("Creating coverage report for files with less than 100 percent coverage.")
        run_args = ["coverage", "html", "--skip-covered", "-d", f"{path}"]
    else:
        print_info("Creating coverage report for all files.")
        run_args = ["coverage", "html", "-d", f"{path}"]
    # Execute command and get return code.
    return_code = run_command(run_args)
    # If return_code is non-zero, exit with return code.
    if return_code != 0:
        exit_with_code(return_code)
    # Print some success info and return the return code.
    print_primary("Coverage report generated. Report can be accessed at:")
    print_warning(f"file://{path}/index.html")
    return return_code


def run_command(run_args):
    """Run the commands provided by the run_args and return the exit code."""
    print_command(f"{' '.join(run_args)}")
    proc = subprocess.run(run_args, check=False)
    return proc.returncode


def exit_with_code(exit_code):
    """Print out the exit code and exit."""
    if exit_code != 0:
        print_error(f"Testing failed with exit code of: {exit_code}")
    else:
        print_success(f"Testing completed successfully with exit code of: {exit_code}")
    sys.exit(exit_code)


def print_primary(objects):
    """Print colored as blue."""
    print(f"{BLUE}{objects}{NC}")


def print_info(objects):
    """Print colored as cyan."""
    print(f"{CYAN}{objects}{NC}")


def print_success(objects):
    """Print colored as green."""
    print(f"{GREEN}{objects}{NC}")


def print_warning(objects):
    """Print colored as yellow."""
    print(f"{YELLOW}{objects}{NC}")


def print_error(objects):
    """Print colored as red."""
    print(f"{RED}{objects}{NC}")


def print_command(command):
    """Print command that will execute."""
    print(f"COMMAND: {BLUE}{command}{NC}")


# Prevent running on import.
if __name__ == "__main__":
    main()
