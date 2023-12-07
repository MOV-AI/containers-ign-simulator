ARG DOCKER_REGISTRY="pubregistry.aws.cloud.mov.ai"
FROM ${DOCKER_REGISTRY}/ce/ignition-gazebo:v2.4.1
# This version is the latest stable version of ignition packages

# Freeze ignition packages in their current version
RUN pks=$(apt list --installed *ign* 2>/dev/null | awk -F'[/ ]' '{print $1}') && \
    for pk in $pks; do apt-mark hold $pk; done

# Apply proxy changes of base image v2.4.4 into container
COPY files/apt/movai-ubuntu-archive-proxy.list /etc/apt/sources.list.d/movai-ubuntu-archive-proxy.list
COPY files/apt/movai-ubuntu-ports-proxy.list /etc/apt/sources.list.d/movai-ubuntu-ports-proxy.list
COPY files/apt/movai-ros-proxy.list /etc/apt/sources.list.d/movai-ros-proxy.list

ARG APT_REPOSITORY="https://artifacts.aws.cloud.mov.ai/repository"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | gpg --dearmor -o /usr/share/keyrings/ros.key
RUN if [ "$(uname -m)" = "x86_64" ] ; then rm /etc/apt/sources.list.d/movai-ubuntu-ports-proxy.list ; fi &&\ 
    if [ "$(uname -m)" = "aarch64" ] || [ "$(uname -m)" = "armv7l" ] ; then rm /etc/apt/sources.list.d/movai-ubuntu-archive* && rm /etc/apt/sources.list.d/movai-ubuntu-security* ; fi &&\ 
    apt-get update && apt-get upgrade -y