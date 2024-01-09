ARG DOCKER_REGISTRY="pubregistry.aws.cloud.mov.ai"
FROM ${DOCKER_REGISTRY}/ce/movai-base-focal:v2.4.4
# This Dockerfile is used to build the ignition

### Args
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/movai_ign_plugins/system
ARG IGN_GUI_PLUGIN_PATH=/movai_ign_plugins/gui
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER=/models_database/plugins/system
ARG IGN_GUI_PLUGIN_PATH_USER=/models_database/plugins/gui
ARG IGN_GAZEBO_RESOURCE_PATH=/models_database/my_models
ARG APT_REPOSITORY="https://artifacts.aws.cloud.mov.ai/repository"

ENV MOVAI_ENV="release"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy runtime scripts and setup files
COPY ./gazebo/movai-entrypoint.sh /usr/local/bin/movai-entrypoint.sh
COPY ./gazebo/generate-collection-fortress.bash /usr/local/bin/generate-collection-fortress.bash
COPY ./gazebo/collection-fortress-12-23.yaml /usr/local/bin/fixed-collection-fortress.yaml

### Add apt repositories (gazebo + ros + yk)
RUN wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null && \
    echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros2-latest.list && \
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add - && \
    add-apt-repository ppa:rmescandon/yq && \
    apt-get update && \
### Install vctools, colcon and yk for building
    apt-get -y --no-install-recommends install python3-vcstool python3-colcon-common-extensions yq && \
    export PATH=$PATH:$HOME/.local/bin/ && \
### Create workspace
    mkdir -p workspace/src && \
    cd workspace/src && \
### Generate fortress collection
    /usr/local/bin/generate-collection-fortress.bash "gz-sensors" && \
### Import source code
    vcs import < /usr/local/bin/fixed-collection-fortress.yaml && \
### Install ignition fortress requirements
    apt -y --no-install-recommends install \
    $(sort -u $(find . -iname 'packages-'`lsb_release -cs`'.apt' -o -iname 'packages.apt' | grep -v '/\.git/') | sed '/ignition\|sdf/d' | tr '\n' ' ')

### Build ignition
RUN cd workspace && \
    colcon graph && \
    colcon build --cmake-args -DBUILD_TESTING=OFF --merge-install

### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
RUN mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GUI_PLUGIN_PATH} && touch ${IGN_GUI_PLUGIN_PATH}/.keep

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:${IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER}
ENV IGN_GUI_PLUGIN_PATH=${IGN_GUI_PLUGIN_PATH}:${IGN_GUI_PLUGIN_PATH_USER}

### Set gazebo resource env
ENV IGN_GAZEBO_RESOURCE_PATH=${IGN_GAZEBO_RESOURCE_PATH}