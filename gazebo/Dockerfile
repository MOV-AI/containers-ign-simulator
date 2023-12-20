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
RUN curl -L --progress-bar "https://packages.osrfoundation.org/gazebo.gpg" -o /usr/share/keyrings/gazebo.gpg && \
    echo "deb  [signed-by=/usr/share/keyrings/gazebo.gpg] https://artifacts.aws.cloud.mov.ai/repository/ppa-proxy-gazebo focal main" | tee /etc/apt/sources.list.d/movai-gazebo.list > /dev/null && \
    curl -fsSL "$APT_REPOSITORY/movai-applications/gpg" | apt-key add - && \
    add-apt-repository "deb [arch=all] $APT_REPOSITORY/ppa-public main main" && \
    add-apt-repository "deb [arch=amd64] $APT_REPOSITORY/ppa-proxy-gazebo-backup gazebo-backup main" && \
### Install mobros 
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -i "https://artifacts.cloud.mov.ai/repository/pypi-edge/simple" --extra-index-url "https://pypi.org/simple" --no-cache-dir mobros==2.1.0.8 && \
    apt-get update && \
### Install ignition-fortress using mobros
    mobros install ignition-fortress=1.0.3-2~focal ocl-icd-libopencl1=2.2.11-1ubuntu1 -y && \ 
### Substitute ignition-sensors libraries by patched version
    pks=$(apt list --installed libignition-sensors6* 2>/dev/null | awk -F'[/ ]' '{print $1}' | grep lib) && \
    for pk in $pks; do dpkg -r --force-depends --ignore-depends=libignition-gazebo6-plugins,libignition-gazebo6-dev,ignition-fortress $pk; done && \
    apt-get download movai-ignition-sensors6=2.7.1-2 && \
    dpkg -i ./movai-ignition-sensors6_2.7.1-2_all.deb && \
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
