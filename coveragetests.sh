#!/bin/bash

# Constants for colors
BLACK='\033[0;30m'
RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
LTGRAY='\033[0;37m'
GRAY='\033[1;30m'
LTRED='\033[1;31m'
LTGREEN='\033[1;32m'
YELLOW='\033[1;33m'
LTBLUE='\033[1;34m'
LTPURPLE='\033[1;35m'
LTCYAN='\033[1;36m'
WHITE='\033[1;37m'
NC='\033[0m'
ANCHOR='\e]8;;'
END_ANCHOR='\e]8;;\a'

# Abort if any command fails
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$DIR"

#arg[0] = method to run.
#arg[1] = workspaceFolder from VSCode * Project root.
#arg[2] = relativeFile from VSCode * Test file to run.
args=("$@")

location="$( pwd; )";
action="${args[0]:-"all_tests"}"
test_file="${args[2]}"

if [ "${action}" = "all_tests" ]; then
    echo -e "${BLUE}Running All Tests With Coverage Report${NC}"
    pipenv run coverage run --source . runtests.py ${test_file}
    echo -e "${BLUE}Generating HTML${NC}"
    pipenv run coverage html -d ${location}/.django_dump_die_coverage_html_report
    echo -e "${BLUE}Report can be accessed at: ${ORANGE}file://${location}/.django_dump_die_coverage_html_report/index.html${NC}"
    echo -e "${GREEN}Done!${NC}"
fi

if [ "${action}" = "all_tests_lt_100" ]; then
    echo -e "${BLUE}Running All Tests With Less Than 100% Coverage Report${NC}"
    pipenv run coverage run --source . runtests.py ${test_file}
    echo -e "${BLUE}Generating HTML${NC}"
    pipenv run coverage html --skip-covered -d ${location}/.django_dump_die_coverage_html_report
    echo -e "${BLUE}Report can be accessed at: ${ORANGE}file://${location}/.django_dump_die_coverage_html_report/index.html${NC}"
    echo -e "${GREEN}Done!${NC}"
fi
