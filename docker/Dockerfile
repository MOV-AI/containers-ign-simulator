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


SHELL ["/bin/bash", "-o", "pipefail", "-c"]

### Add apt repositories
RUN curl -L --progress-bar "https://packages.osrfoundation.org/gazebo.gpg" -o /usr/share/keyrings/gazebo.gpg && \
    echo "deb  [signed-by=/usr/share/keyrings/gazebo.gpg] https://artifacts.aws.cloud.mov.ai/repository/ppa-proxy-gazebo focal main" | tee /etc/apt/sources.list.d/movai-gazebo.list > /dev/null && \
    curl -fsSL "$APT_REPOSITORY/movai-applications/gpg" | apt-key add - && \
    add-apt-repository "deb [arch=all] $APT_REPOSITORY/ppa-public main main" && \
    add-apt-repository "deb [arch=amd64] $APT_REPOSITORY/ppa-proxy-gazebo-backup gazebo-backup main" && \
### Install mobros 
    python3 -m pip install pip==23.3.1 --upgrade --no-cache-dir && \
    python3 -m pip install -i "https://artifacts.cloud.mov.ai/repository/pypi-edge/simple" --extra-index-url "https://pypi.org/simple" --no-cache-dir mobros==2.1.0.8 && \
    apt-get update && \
### Install ignition-fortress using mobros
    mobros install ignition-fortress=1.0.3-2~focal ocl-icd-libopencl1=2.2.11-1ubuntu1 -y && \ 
### Substitute ignition-sensors libraries by patched version
    pks=$(apt list --installed libignition-sensors6* 2>/dev/null | awk -F'[/ ]' '{print $1}' | grep lib) && \
    for pk in $pks; do dpkg -r --force-depends --ignore-depends=libignition-gazebo6-plugins,libignition-gazebo6-dev,ignition-fortress $pk; done && \
    apt-get download movai-ignition-sensors6=2.7.1-2 && \
    dpkg -i ./movai-ignition-sensors6_2.7.1-2_all.deb && \
## Install messaging broker for async calls, supervisord and gunicorn
    apt-get install -y gnupg=2.2.19-3ubuntu2.2  apt-transport-https=2.0.2 rabbitmq-server=3.8.2-0ubuntu1 supervisor=4.1.0-1ubuntu1 gunicorn=20.0.4-3 --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
### Set up plugin directories (add .keep to be not removed by deb package on uninstall)
    mkdir -p ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH} && touch ${IGN_GAZEBO_SYSTEM_PLUGIN_PATH}/.keep && \
    mkdir -p ${IGN_GUI_PLUGIN_PATH} && touch ${IGN_GUI_PLUGIN_PATH}/.keep && \
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
