[![Build&Deploy MOVAI Ignition Gazebo](https://github.com/MOV-AI/containers-ign-simulator/actions/workflows/docker-ci.yml/badge.svg?branch=main)](https://github.com/MOV-AI/containers-ign-simulator/actions/workflows/docker-ci.yml)

# MOVAI Ignition Gazebo Container

Ignition Simulator Docker image for MOV.AI Framework

Image is built as follow :

| Flavour      | Base Image | IGN |
| ------------ | ---------- | ------ |
| ignition-fortress | movai-base-bionic:v1.4.9 | 1.0.3-1 |


## Build

Build IGN Simulator image based on MOVAI bionic :

    docker build -t ign-simulator:test . -f gazebo/Dockerfile

## Usage

- First of all, Install NVIDIA-DOCKER service to enable GPU resources inside the container:
```
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
&& curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
```

- Restart the docker service:
```
sudo systemctl restart docker
```

- Launch simulator:
```
xhost +local:docker
docker run -it -e MOVAI_ENV=qa -e DISPLAY=$DISPLAY ign-simulator:test ign gazebo
```
