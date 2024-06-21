#!/usr/bin/env python
"""Run Django Tests"""
import os
import subprocess
import sys
from django.core.management import execute_from_command_line
from shutil import which


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_tests_with_pytest():
    """Run tests with pytest format.
    Has very helpful and verbose testing output.
    """

    # Set environment values.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    os.environ.setdefault("PYTHONPATH", ROOT_DIR)

    # Run tests.
    argv = ["pytest"] + sys.argv[1:]
    proc = subprocess.run(argv, check=False)
    return proc.returncode


def run_tests():
    """Run tests with manage.py format.
    Has less helpful testing output.
    """

    # Set environment values.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    # Run tests.
    argv = sys.argv[:1] + ["test"] + sys.argv[1:] + ["--buffer"]
    return execute_from_command_line(argv)


# Determine which testing format to run, based on environment.
# Pytest is preferred.
if __name__ == "__main__":
    if which("pytest") is not None:
        sys.exit(run_tests_with_pytest())
    else:
        sys.exit(run_tests())
