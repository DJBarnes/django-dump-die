#!/bin/bash

# Constants for colors
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PINK='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'
ANCHOR='\e]8;;'
END_ANCHOR='\e]8;;\a'

# Abort if any command fails
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "${DIR}"

#arg[0] = method to run.
args=("$@")

location="$( pwd; )";
action="${args[0]:-"all_tests"}"

if [ "${action}" = "all_tests" ]; then
    echo -e "${BLUE}Running All Tests With Coverage Report${NC}"
    pipenv run ${location}/runtests.py -nauto --cov=. --ignore=.tox --disable-pytest-warnings --cov-report html:${location}/.django_dump_die_coverage_html_report
    echo -e "${BLUE}Report can be accessed at:"
    echo -e "${YELLOW}file://${location}/.django_dump_die_coverage_html_report/index.html${NC}"
    echo -e "${GREEN}Done!${NC}"
fi

if [ "${action}" = "lt_100" ]; then
    echo -e "${BLUE}Running All Tests With Coverage Report${NC}"
    pipenv run ${location}/runtests.py -nauto --cov=. --ignore=.tox --disable-pytest-warnings --cov-report=
    echo -e "${BLUE}Generating HTML${NC}"
    pipenv run coverage html --skip-covered -d ${location}/.django_dump_die_coverage_html_report
    echo -e "${BLUE}Report can be accessed at:"
    echo -e "${YELLOW}file://${location}/.django_dump_die_coverage_html_report/index.html${NC}"
    echo -e "${GREEN}Done!${NC}"
fi
