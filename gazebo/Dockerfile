FROM registry.cloud.mov.ai/qa/ros-buildtools-noetic:v2.0.1 AS deb_builder

USER root

ARG LATEST_COMPONENTS=( )

### Create build workspace
RUN mkdir -p workspace/src && \
### Add apt repositories (gazebo + ros + yk + nvidia)
    wget --progress=dot:giga https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null && \
    echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros2-latest.list && \
    wget --progress=dot:giga -O - https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
    add-apt-repository ppa:rmescandon/yq && \
    apt-get update && \
### Install vctools, colcon, yk and cuda-toolkit for building
    apt-get -y --no-install-recommends install python3-vcstool=0.3.0-1 python3-colcon-common-extensions=0.3.0-1 yq=4.16.2

### Get into workspace
WORKDIR /opt/mov.ai/app/workspace/src

# Copy build time data
COPY ./gazebo/update-collection-fortress-to-latest.bash ./update-collection-fortress-to-latest.bash
COPY ./gazebo/collection-fortress-12-23.yaml ./fixed-collection-fortress.yaml

### Generate fortress collection
RUN ./update-collection-fortress-to-latest.bash "${LATEST_COMPONENTS[@]}" && \
### Import source code
    vcs import < ./fixed-collection-fortress.yaml && \
### Install ignition fortress requirements
    echo "$(sort -u $(find . -iname 'packages-'$(lsb_release -cs)'.apt' -o -iname 'packages.apt' | grep -v '/\.git/') | sed '/ignition\|sdf/d' | tr '\n' ' ')" > requirements.txt && \
    apt-get -y --no-install-recommends install \
    $(cat requirements.txt) && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/mov.ai/app/workspace

### Build ignition
RUN colcon graph && \
    colcon build --cmake-args "-DBUILD_TESTING=OFF" "-DCMAKE_BUILD_TYPE=Release" "-DCMAKE_CXX_FLAGS=-O3" --merge-install

FROM pubregistry.aws.cloud.mov.ai/ce/movai-base-focal:v2.4.4
# This Dockerfile is used to build the ignition

### Args
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/movai_ign_plugins/system
ARG IGN_GUI_PLUGIN_PATH=/movai_ign_plugins/gui
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER=/models_database/plugins/system
ARG IGN_GUI_PLUGIN_PATH_USER=/models_database/plugins/gui
ARG IGN_GAZEBO_RESOURCE_PATH=/models_database/my_models

ENV MOVAI_ENV="release"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Copy runtime scripts
COPY ./gazebo/movai-entrypoint.sh /usr/local/bin/movai-entrypoint.sh

# Copy install workspace
COPY --from=deb_builder /opt/mov.ai/app/workspace/install /opt/mov.ai/app/workspace/install
COPY --from=deb_builder /opt/mov.ai/app/workspace/src/requirements.txt /opt/mov.ai/app/workspace/src/requirements.txt

### Install ignition fortress requirements
RUN wget --progress=dot:giga https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null && \
    apt-get update && \
    apt-get -y --no-install-recommends install \
    $(cat workspace/src/requirements.txt) && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
RUN mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GUI_PLUGIN_PATH} && touch ${IGN_GUI_PLUGIN_PATH}/.keep

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:${IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER}
ENV IGN_GUI_PLUGIN_PATH=${IGN_GUI_PLUGIN_PATH}:${IGN_GUI_PLUGIN_PATH_USER}

### Set gazebo resource env
ENV IGN_GAZEBO_RESOURCE_PATH=${IGN_GAZEBO_RESOURCE_PATH}