#!/bin/bash
# File: movai-entrypoint.sh
set -e
printf "Mov.ai IGN Simulator - %s Edition\n" "$MOVAI_ENV"

# First run apt initializations
if [ ! -f "${MOVAI_HOME}/.first_run_apt" ]; then
    touch "${MOVAI_HOME}/.first_run_apt"

    if [ "$MOVAI_ENV" = "develop" ]; then
        MOVAI_PPA="dev"
    elif [ "$MOVAI_ENV" = "qa" ]; then
        MOVAI_PPA="testing"
    else
        MOVAI_PPA="main"
    fi
    # Update ppa with correct env and make sure it is not cohabiting with another one
    for ppa_env in dev testing main; do
        # remove any old repo
        sudo add-apt-repository -r -n "deb https://artifacts.cloud.mov.ai/repository/ppa-${ppa_env} ${ppa_env} main"
    done || true
    sudo add-apt-repository -n "deb [arch=all] https://artifacts.cloud.mov.ai/repository/ppa-$MOVAI_PPA $MOVAI_PPA main"
fi

export PATH=${MOVAI_HOME}/.local/bin:${PATH}
export PYTHONPATH=${APP_PATH}:${MOVAI_HOME}/sdk:${PYTHONPATH}

# if commands passed
[ $# -gt 0 ] && exec "$@"
# else
