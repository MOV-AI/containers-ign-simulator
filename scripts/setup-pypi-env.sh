#!/bin/bash
#
# Copyright 2021 MOV.AI
#
#    Licensed under the Mov.AI License version 1.0;
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        https://www.mov.ai/flow-license/
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
set -e

env=$1

TARGET_PIP_CONF="/etc/pip.conf"

SHARED_PIP_CONF_FOLDER="/usr/local/share/pypi-confs/resources"
DEV_PIP_CONF="$SHARED_PIP_CONF_FOLDER/pypi-dev/pip.conf"
INT_PIP_CONF="$SHARED_PIP_CONF_FOLDER/pypi-integration/pip.conf"
PROD_PIP_CONF="$SHARED_PIP_CONF_FOLDER/pypi-edge/pip.conf"

if [ -z "$env" ]; then
    printf "Please specify an environment to switch to (DEV, INT or PROD)."
    exit 1
fi

if  [ "$env" == "DEV" ]; then
  cp $DEV_PIP_CONF $TARGET_PIP_CONF
  exit 0
fi

if  [ "$env" == "INT" ]; then
  cp $INT_PIP_CONF $TARGET_PIP_CONF
  exit 0
fi

if  [ "$env" == "PROD" ]; then
  cp $PROD_PIP_CONF $TARGET_PIP_CONF
  exit 0
fi
