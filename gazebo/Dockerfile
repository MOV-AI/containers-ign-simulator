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

# Copy runtime scripts
COPY ./gazebo/movai-entrypoint.sh /usr/local/bin/movai-entrypoint.sh

### Add apt repositories
RUN apt-get install python3-pip wget lsb-release gnupg curl && \
    python3 -m pip install vcstool || python3 -m pip3 install vcstool && \
    python3 -m pip install -U colcon-common-extensions || python3 -m pip3 install -U colcon-common-extensions && \
    export PATH=$PATH:$HOME/.local/bin/ && \
    apt-get install git

RUN mkdir -p ~/workspace/src && cd ~/workspace/src && \
    wget https://raw.githubusercontent.com/ignition-tooling/gazebodistro/master/collection-fortress.yaml && \
    vcs import < collection-fortress.yaml

RUN wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null && \
    apt-get update

RUN cd ~/workspace/src && \
    sudo apt -y install \
    $(sort -u $(find . -iname 'packages-'`lsb_release -cs`'.apt' -o -iname 'packages.apt' | grep -v '/\.git/') | sed '/ignition\|sdf/d' | tr '\n' ' ')

RUN cd ~/workspace/ && \
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


# echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-testing $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-testing.list > /dev/null