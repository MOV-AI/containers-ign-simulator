FROM registry.cloud.mov.ai/qa/ros-buildtools-noetic:v2.0.1 AS deb_builder

USER root

ARG LATEST_COMPONENTS=( )

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
### Create build workspace
RUN mkdir -p workspace/src && \
### Add apt repositories (gazebo + ros + yk + nvidia)
    wget --progress=dot:giga "https://packages.osrfoundation.org/gazebo.gpg" -O "/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg" && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null && \
    echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros2-latest.list && \
    wget --progress=dot:giga -O - "https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc" | apt-key add - && \
    add-apt-repository ppa:rmescandon/yq && \
    apt-get update && \
### Install vctools, colcon, yk and cuda-toolkit for building
    apt-get -y --no-install-recommends install python3-vcstool=0.3.0-1 python3-colcon-common-extensions=0.3.0-1 yq=4.16.2

### Get into workspace
WORKDIR /opt/mov.ai/app/workspace/src

# Copy build time data
COPY ./docker/update-collection-fortress-to-latest.bash ./update-collection-fortress-to-latest.bash
COPY ./docker/collection-fortress-12-23.yaml ./fixed-collection-fortress.yaml

### Generate fortress collection
RUN ./update-collection-fortress-to-latest.bash "${LATEST_COMPONENTS[@]}" && \
### Import source code
    vcs import < ./fixed-collection-fortress.yaml && \
### Install ignition fortress requirements
    apt-get update && \
    echo "$(sort -u $(find . -iname 'packages-'$(lsb_release -cs)'.apt' -o -iname 'packages.apt' | grep -v '/\.git/') | sed '/ignition\|sdf/d' | tr '\n' ' ')" > requirements.txt && \
    apt-get -y --no-install-recommends install \
    $(cat requirements.txt) && \
    apt-get clean && \
    rm -rf "/var/lib/apt/lists/*"

WORKDIR /opt/mov.ai/app/workspace

### Build ignition
RUN colcon graph && \
    colcon build --cmake-args "-DBUILD_TESTING=OFF" "-DCMAKE_BUILD_TYPE=Release" "-DCMAKE_CXX_FLAGS=-O3" --merge-install --install-base /opt/ignition

FROM python:3.8.10 AS py_builder

COPY ./scripts/setup-pypi-env.sh /usr/local/bin/setup-pypi-env.sh
COPY ./resources /usr/local/share/pypi-confs/resources

WORKDIR /tmp
COPY build-requirements.txt setup.py README.md ./
COPY simulator_api ./simulator_api

### Add experimental repositories to pip
RUN /usr/local/bin/setup-pypi-env.sh INT \
 && python3 -m pip install pip==23.3.1 --upgrade --no-cache-dir \
 && python3 -m pip install -r build-requirements.txt --no-cache-dir \
 && python3 -m build .

FROM pubregistry.aws.cloud.mov.ai/ce/movai-base-focal:v2.4.4
# This Dockerfile is used to build the ignition

### Args
# Arguments
ARG PIP_PACKAGE_REPO="https://artifacts.cloud.mov.ai/repository/pypi-experimental/simple"
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH=/movai_ign_plugins/system
ARG IGN_GUI_PLUGIN_PATH=/movai_ign_plugins/gui
ARG IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER=/models_database/plugins/system
ARG IGN_GUI_PLUGIN_PATH_USER=/models_database/plugins/gui
ARG IGN_GAZEBO_RESOURCE_PATH=/models_database/my_models
ARG APT_REPOSITORY="https://artifacts.aws.cloud.mov.ai/repository"

ENV MOVAI_ENV="release"

ENV PYTHON_VERSION=3
ARG PORT=8081

## Expose web server port
EXPOSE $PORT

### Rabbitmq variable that needs to be set in root before supervisord starts
ENV RABBITMQ_PID_FILE=/var/lib/rabbitmq/mnesia/rabbitmq.pid

# Copy runtime scripts and configuration files
COPY ./docker/movai-entrypoint.sh /usr/local/bin/movai-entrypoint.sh
COPY ./docker/start-celery.sh /usr/local/bin/start-celery.sh
COPY ./docker/celery-health-check.sh /usr/local/bin/celery-health-check.sh
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./scripts/setup-pypi-env.sh /usr/local/bin/setup-pypi-env.sh
COPY ./resources /usr/local/share/pypi-confs/resources

# Copy fortress install workspace
COPY --from=deb_builder /opt/ignition /opt/ignition
COPY --from=deb_builder /opt/mov.ai/app/workspace/src/requirements.txt /opt/mov.ai/app/requirements.txt


SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN wget --progress=dot:giga "https://packages.osrfoundation.org/gazebo.gpg" -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null  && \
    apt-get update && \
## Install messaging broker for async calls, supervisord and gunicorn
    apt-get install -y gnupg=2.2.19-3ubuntu2.2  apt-transport-https=2.0.2 rabbitmq-server=3.8.2-0ubuntu1 supervisor=4.1.0-1ubuntu1 gunicorn=20.0.4-3 --no-install-recommends && \
### Install fortress requirements 
    apt-get -y --no-install-recommends install $(cat requirements.txt) && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
    mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GUI_PLUGIN_PATH} && touch ${IGN_GUI_PLUGIN_PATH}/.keep && \
    ln -s /opt/ignition/bin/ign /usr/bin/ign && \
### Make scripts executable
    chmod +x /usr/local/bin/start-celery.sh /usr/local/bin/celery-health-check.sh && \
### Add experimental repositories to pip
    /usr/local/bin/setup-pypi-env.sh INT && \
### Allow movai user to run supervisord as root
    [ -f /etc/sudoers.d/movai ] || touch /etc/sudoers.d/movai && \
    echo "%sudo ALL=(ALL) NOPASSWD:SETENV: /usr/bin/supervisord" >> /etc/sudoers.d/movai


# Copy PIP package built outside docker file
COPY dist /tmp_packages/pre-built

# Deploy application code inside the container
COPY --from=py_builder /tmp/dist/*.whl /tmp_packages/docker-built/

RUN if [ -z "$(ls -A /tmp_packages/pre-built/*.whl)" ]; then INSTALL_DIR_PATH="/tmp_packages/docker-built";else INSTALL_DIR_PATH="/tmp_packages/pre-built" ; fi && \
    python3 -m pip install --no-cache-dir \
    --index-url="$PIP_PACKAGE_REPO" \
    --extra-index-url https://pypi.org/simple \
    "$INSTALL_DIR_PATH"/*.whl && \
    rm -rf /tmp_packages

USER movai

# Give celery and flask permissions to write on their volumes
RUN mkdir -p /opt/mov.ai/app/celery_data /opt/mov.ai/app/flask_data

# Declare volumes for Flask and Celery databases
VOLUME ["/opt/mov.ai/app/flask_data", "/opt/mov.ai/app/celery_data"]

# Set healthcheck
HEALTHCHECK --interval=5s --timeout=5s --start-period=5s --retries=3 CMD curl --fail http://localhost:8081/ || exit 1

### Set plugin env
ENV IGN_GAZEBO_SYSTEM_PLUGIN_PATH=${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}:${IGN_GAZEBO_SYSTEM_PLUGIN_PATH_USER}
ENV IGN_GUI_PLUGIN_PATH=${IGN_GUI_PLUGIN_PATH}:${IGN_GUI_PLUGIN_PATH_USER}

### Set gazebo resource env
ENV IGN_GAZEBO_RESOURCE_PATH=${IGN_GAZEBO_RESOURCE_PATH}
ENV IGN_CONFIG_PATH=/opt/ignition/share/ignition
ENV LD_LIBRARY_PATH=/opt/ignition/lib:${LD_LIBRARY_PATH}
