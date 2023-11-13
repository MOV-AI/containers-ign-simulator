FROM registry.cloud.mov.ai/devops/py-buildserver:latest AS py_builder

COPY ./scripts/setup-pypi-env.sh /usr/local/bin/setup-pypi-env.sh 
COPY ./resources /usr/local/share/pypi-confs/resources

### Add experimental repositories to pip
RUN /usr/local/bin/setup-pypi-env.sh DEV

WORKDIR /tmp
COPY build-requirements.txt ./
COPY setup.py ./
COPY simulator_api ./simulator_api
COPY README.md ./

RUN python3 -m pip install pip==23.3.1 --upgrade --no-cache-dir \
 && python3 -m pip install -r build-requirements.txt --no-cache-dir \
 && python3 -m build .

FROM pubregistry.aws.cloud.mov.ai/ce/movai-base-focal:v2.4.4
# This Dockerfile is used to build the ignition

### Args
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/movai_ign_plugins/system
ARG IGN_GUI_PLUGIN_PATH=/movai_ign_plugins/gui
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER=/models_database/plugins/system
ARG IGN_GUI_PLUGIN_PATH_USER=/models_database/plugins/gui
ARG IGN_GAZEBO_RESOURCE_PATH=/models_database/my_models

ENV MOVAI_ENV="release"

ENV PYTHON_VERSION=3
ENV PORT=8081

## Expose web server port
EXPOSE $PORT

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

### Install ignition-fortress
RUN wget --progress=dot:giga "https://packages.osrfoundation.org/gazebo.gpg" -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null  && \
    echo "Package: *" >> /etc/apt/preferences.d/ros-gazebo && \
    echo "Pin: origin packages.osrfoundation.org" >> /etc/apt/preferences.d/ros-gazebo && \
    echo "Pin-Priority: 1001" >> /etc/apt/preferences.d/ros-gazebo && \
    apt-get update && \
    apt-get install ignition-fortress=1.0.3-2~focal -y --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
    mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GUI_PLUGIN_PATH} && touch ${IGN_GUI_PLUGIN_PATH}/.keep

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:${IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER}
ENV IGN_GUI_PLUGIN_PATH=${IGN_GUI_PLUGIN_PATH}:${IGN_GUI_PLUGIN_PATH_USER}

### Set gazebo resource env
ENV IGN_GAZEBO_RESOURCE_PATH=${IGN_GAZEBO_RESOURCE_PATH}

# Copy runtime scripts
COPY ./gazebo/movai-entrypoint.sh /usr/local/bin/movai-entrypoint.sh

COPY ./scripts/setup-pypi-env.sh /usr/local/bin/setup-pypi-env.sh 
COPY ./resources /usr/local/share/pypi-confs/resources

### Add experimental repositories to pip
RUN /usr/local/bin/setup-pypi-env.sh INT

## Install messaging broker for async calls
RUN apt-get update && \
    apt-get install -y gnupg curl && \
    apt-get install apt-transport-https && \
    curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null && \
    curl -1sLf "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf77f1eda57ebb1cc" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg > /dev/null && \
    curl -1sLf "https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.packagecloud.rabbitmq.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu jammy main" | tee /etc/apt/sources.list.d/rabbitmq.list > /dev/null && \
    echo "deb-src [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu jammy main" | tee /etc/apt/sources.list.d/rabbitmq.list > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ jammy main" | tee /etc/apt/sources.list.d/rabbitmq.list > /dev/null && \
    echo "deb-src [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ jammy main" | tee /etc/apt/sources.list.d/rabbitmq.list > /dev/null && \
    apt-get install -y erlang-base \
    erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
    erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
    erlang-runtime-tools erlang-snmp erlang-ssl \
    erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl --no-install-recommends -y && \
    apt-get install rabbitmq-server --fix-missing -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Install Supervisor
RUN apt-get update && apt-get install -y supervisor gunicorn

# Copy the Supervisor configuration file
COPY gazebo/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Deploy application code inside the container
COPY --from=py_builder /tmp/dist/*.whl /tmp_packages/

RUN python3 -m pip install --no-cache-dir \
    /tmp_packages/*.whl && \
    rm -rf /tmp_packages/ 