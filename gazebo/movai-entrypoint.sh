#!/bin/bash
# File: movai-entrypoint.sh
set -e
printf "Mov.ai IGN Simulator - %s Edition\n" "$MOVAI_ENV"

export PATH=${MOVAI_HOME}/.local/bin:${PATH}
export PYTHONPATH=${APP_PATH}:${MOVAI_HOME}/sdk:${PYTHONPATH}

# if commands passed
[ $# -gt 0 ] && exec "$@"
# else
