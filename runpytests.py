#!/usr/bin/env python
"""Run Pytest Tests"""
import os
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def runtests():
    """Run tests"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    os.environ.setdefault("PYTHONPATH", ROOT_DIR)
    argv = ["pytest"] + sys.argv[1:]
    subprocess.run(argv, check=False)


if __name__ == "__main__":
    runtests()
