# This Dockerfile is used to build the ignition
FROM ubuntu:bionic

ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=movai_plugins/plugins/system
ARG IGN_GAZEBO_GUI_PLUGIN_PATH=movai_plugins/plugins/gui
ARG PPA_REPOSITORY="deb [arch=all] https://artifacts.cloud.mov.ai/repository/ppa-testing testing main"
ARG GPG="https://artifacts.cloud.mov.ai/repository/movai-applications/gpg"

### nvidia-container-runtime
ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

### Install ignition-fortress
RUN apt-get update && \
    apt-get install lsb-release wget gnupg -y && \
    wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null  && \
    apt-get update && \
    apt-get install ignition-fortress -y && \
    rm -rf /var/lib/apt/lists/*

### Add movai source to list
# RUN curl -fsSL ${GPG} | apt-key add - && \
# RUN apt-get update && apt-get install software-properties-common
# RUN add-apt-repository "${PPA_REPOSITORY}"

### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
RUN mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GAZEBO_GUI_PLUGIN_PATH}} && touch ${IGN_GAZEBO_GUI_PLUGIN_PATH}}/.keep

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}
ENV IGN_GAZEBO_GUI_PLUGIN_PATH=${IGN_GAZEBO_GUI_PLUGIN_PATH}
