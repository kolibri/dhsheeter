#!/bin/bash

set -e

NO_DOCKER=${NO_DOCKER:0}

_target() {
    case $1 in
        help) ## displays help
            fn=$(basename "$0")
            echo "## Available targets:"
            grep -E '\)\s*##' $fn | sed "s|^[[:space:]]*\(.*\)) #\{2\} \(.*\)|\1: \2|g"
        ;;
        python-init) ## initialice python venv
            python -m venv .venv
            source .venv/bin/activate
            .venv/bin/pip install --no-cache-dir -r requirements.txt
        ;;
        sheets) ## build characters in python venv
            .venv/bin/python sheeter.py
        ;;
        sheets-docker) ## build characters in docker
            _compose_run sheeter python sheeter.py
        ;;
        container-build) ## builds docker container
            docker compose build
        ;;
        *)
    # backup target: tries to call one of the tools-function
    if [ -z "${@:2}" ]; then
        _target help
        exit 0
    fi

    TOOLS=`declare -F | sed -r 's/declare -f _(.*)/\1/g'`
    if [[ ${TOOLS[*]} =~ $1 ]]; then
        _"$1" "${@:2}"
    else
        echo "Target not found: " $1
    fi
    ;;
    esac
}

# tools definition
_compose_run() {
    echo "compose run: ${*:2}"
    docker compose run --remove-orphans "$1" "${@:2}"
}

_target "$@"
