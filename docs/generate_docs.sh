#!/usr/bin/env bash
###
 # Utility script to auto-generate/auto-update sphinx docs for project.
 # Forces entire docs build folder to re-build, in order to skip issue where sometimes docs don't update.
 ##


# Stop on error.
set -e


# Ensure bash is executing from script root, regardless of where it was invoked from.
cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


# Forcibly remove existing generated docs, to ensure build command actually updates everything properly.
if [[ -d "./build/" ]]
then
    rm -r "./build/"
fi
mkdir "./build/"


# Auto-generate docs source files, from actual Python code in project.
sphinx-apidoc -f -o ./source/api_reference/ ../django_dump_die/


# Remove modules .rst file, because we don't actually care about it.
if [[ -f "./source/modules.rst" ]]
then
    rm ./source/modules.rst
fi
if [[ -f "./source/api_reference/modules.rst" ]]
then
    rm ./source/api_reference/modules.rst
fi


# Generate sphinx docs from source files.
sphinx-build ./source/ ./build/
