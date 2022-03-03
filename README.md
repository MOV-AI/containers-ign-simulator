[![main](https://github.com/MOV-AI/containers-ros-tools/actions/workflows/docker-ci.yml/badge.svg?branch=main)](https://github.com/MOV-AI/containers-ros-tools/actions/workflows/docker-ci.yml)

# containers-ros-tools

Ignition Simulator Docker image for MOV.AI Framework

Image is built as follow :

| Flavour      | Base Image | IGN |
| ------------ | ---------- | ------ |
| ignition-gazebo | movai-base-bionic | 1.0.2-1 |

## About

## Usage

Build IGN Simulator image based on MOVAI bionic :

    docker build -t ign-gazebo . -f gazebo/Dockerfile

Run :

- First of all, Install NVIDIA-DOCKER service to enable GPU resources inside the container:

    distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt-get update
    sudo apt-get install -y nvidia-docker2

- Restart the docker service:

    sudo systemctl restart docker

- Launch simulator:

    xhost +local:docker
    docker run -it -e MOVAI_ENV=qa -e DISPLAY=$DISPLAY registry.cloud.mov.ai/devops/ign-simulator ign gazebo
