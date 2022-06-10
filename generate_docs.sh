#!/usr/bin/env bash
###
 # Utility script to auto-generate/auto-update sphinx docs for project.
 # Forces entire docs build folder to re-build, in order to skip issue where sometimes docs don't update.
 ##


# Stop on error.
set -e


# Ensure bash is executing from project root, regardless of where it was invoked from.
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


# Forcibly remove existing generated docs, to ensure build command actually updates everything properly.
if [[ -d "./docs/build/" ]]
then
    rm -r "./docs/build/"
fi
mkdir "./docs/build/"


# Auto-generate docs source files, from actual Python code in project.
sphinx-apidoc -o ./docs/source/ ./django_dump_die/


# Remove modules .rst file, because we don't actually care about it.
if [[ -f "./docs/source/modules.rst" ]]
then
    rm ./docs/source/modules.rst
fi


# Generate sphinx docs from source files.
sphinx-build ./docs/source/ ./docs/build/
