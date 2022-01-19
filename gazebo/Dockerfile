# This Dockerfile is used to build the ignition
FROM ubuntu:bionic

### Args
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/movai_ign_plugins/system
ARG IGN_GUI_PLUGIN_PATH=/movai_ign_plugins/gui
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER=/models_database/plugins/system
ARG IGN_GUI_PLUGIN_PATH_USER=/models_database/plugins/gui
ARG IGN_GAZEBO_RESOURCE_PATH=/models_database/my_models
ARG MOVAI_PPA=testing

### nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

### Common apt packages
RUN apt-get update && \
    apt-get install lsb-release=9.20170808ubuntu1 wget=1.19.4-1ubuntu2.2 gnupg=2.2.4-1ubuntu1.4 software-properties-common=0.96.24.32.18 -y --no-install-recommends

### Install ignition-fortress
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN wget --progress=dot:giga "https://packages.osrfoundation.org/gazebo.gpg" -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null  && \
    apt-get update && \
    apt-get install ignition-fortress=1.0.2-1~bionic -y --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

### Add movai source to list
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN wget -q https://artifacts.cloud.mov.ai/repository/movai-applications/gpg -O- | apt-key add - && \
    add-apt-repository "deb [arch=all] https://artifacts.cloud.mov.ai/repository/ppa-${MOVAI_PPA} ${MOVAI_PPA} main"

### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
RUN mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GUI_PLUGIN_PATH} && touch ${IGN_GUI_PLUGIN_PATH}/.keep

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:${IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER}
ENV IGN_GUI_PLUGIN_PATH=${IGN_GUI_PLUGIN_PATH}:${IGN_GUI_PLUGIN_PATH_USER}
### Set gazeo resource env
ENV IGN_GAZEBO_RESOURCE_PATH=${IGN_GAZEBO_RESOURCE_PATH}