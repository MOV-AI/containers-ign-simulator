FROM registry.cloud.mov.ai/devops/py-buildserver:latest AS py_builder

WORKDIR /tmp
COPY build-requirements.txt ./
COPY setup.py ./
COPY simulator ./simulator
COPY README.md ./

RUN python3 -m pip install pip==23.3.1 --upgrade --no-cache-dir \
 && python3 -m pip install -r build-requirements.txt --no-cache-dir \
 && python3 -m build .

ARG DOCKER_REGISTRY="pubregistry.aws.cloud.mov.ai"
FROM pubregistry.aws.cloud.mov.ai/ce/movai-base-focal:v2.4.3
# This Dockerfile is used to build the ignition

### Args
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/movai_ign_plugins/system
ARG IGN_GUI_PLUGIN_PATH=/movai_ign_plugins/gui
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER=/models_database/plugins/system
ARG IGN_GUI_PLUGIN_PATH_USER=/models_database/plugins/gui
ARG IGN_GAZEBO_RESOURCE_PATH=/models_database/my_models

ENV MOVAI_ENV="release"

ENV PYTHON_VERSION=3
ENV APP_NAME="simulator"
ENV PORT=8081

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

# Copy runtime scripts
COPY ./gazebo/movai-entrypoint.sh /usr/local/bin/movai-entrypoint.sh

# Deploy application code inside the container
COPY --from=py_builder /tmp/dist/*.whl /tmp_packages/

RUN python3 -m pip install --no-cache-dir \
    --index-url="$PIP_PACKAGE_REPO" \
    --extra-index-url https://pypi.org/simple \
    /tmp_packages/*.whl && \
    rm -rf /tmp_packages/ 

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:${IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER}
ENV IGN_GUI_PLUGIN_PATH=${IGN_GUI_PLUGIN_PATH}:${IGN_GUI_PLUGIN_PATH_USER}

### Set gazebo resource env
ENV IGN_GAZEBO_RESOURCE_PATH=${IGN_GAZEBO_RESOURCE_PATH}
