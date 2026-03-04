#!/bin/bash

set -e
_target() {
    case $1 in
        help) ## displays help
            fn=$(basename "$0")
            echo "## Available targets:"
            grep -E '\)\s*##' $fn | sed "s|^[[:space:]]*\(.*\)) #\{2\} \(.*\)|\1: \2|g"
        ;;
        python-init) ## initialize python venv
            python -m venv .venv
            source .venv/bin/activate
            .venv/bin/pip install --no-cache-dir -r requirements.txt
        ;;
        sheets) ## build characters in python venv
            .venv/bin/python sheeter.py
        ;;
        sheets-docker) ## build characters in docker
            echo "compose run: ${*:2}"
            docker compose run --remove-orphans sheeter python sheeter.py
        ;;
        container-build) ## build docker container
            docker compose build
        ;;
        *)

    if [ -z "${@:2}" ]; then
        echo "No target found."
        echo "Try this:"
        echo "cat README.md"
        echo ""
        _target help
        exit 0
    fi
    ;;
    esac
}

_target "$@"
