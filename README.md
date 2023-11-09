[![Build&Deploy MOVAI Ignition Gazebo](https://github.com/MOV-AI/containers-ign-simulator/actions/workflows/docker-ci.yml/badge.svg?branch=main)](https://github.com/MOV-AI/containers-ign-simulator/actions/workflows/docker-ci.yml)

# MOVAI Ignition Gazebo Container

Ignition Simulator Docker image for MOV.AI Framework

Image is built as follow :

| Flavour      | Base Image | IGN |
| ------------ | ---------- | ------ |
| ignition-fortress | movai-base-focal:v2.4.3 | 1.0.3-1 |



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

- Launch simulator with nvidia GPU:
```
xhost +local:docker
docker run -it --privileged --runtime=nvidia -e MOVAI_ENV=qa -e QT_X11_NO_MITSHM=1 -e DISPLAY=$DISPLAY -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=graphics -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v /tmp/.docker.xauth:/tmp/.docker.xauth ign-simulator:test ign gazebo
```



### Simulator Web Server Application

#### Version 1

Specify status options in documentation and return enum

GET `api/v1/GetSimulatorStatus`

`{'status': 'ok', 'checklist': [{'status': 'timeout', 'name': "", 'message': ""},{'status': timeout, 'name': "", 'message': ""}, {'status': timeout, 'name': "", 'message': ""}]}`

#### Version 2

- Run sim - spawner comm test
    - define the topic name for the test
    - do an echo on spawner
    - POST `api/v1/topic {topic_name} {topic_data}`
    - result

- Run spawner - sim comm test 
    - define the topic name for the test
    - do an publish on spawner
    - POSt `api/v1/topic {topic_name} {timeout}` -> id
    - GET `api/v1/topic/id {echo_id}`
    - result

- Check ignition is running
    - topics clock and stats
    - POST `api/v1/topic {topic_name} {timeout}` -> id
    - GET `api/v1/topic {echo_id}`
    - result (if ignition is running or not) 
    - POST `api/v1/configure {config_json}`
    - POST `api/v1/run`

- Check if a world is properly loaded
    - define the world name to check
    - POST `api/v1/topic {topic_name} {timeout}` -> id
    - GET `api/v1/topic/id`
    - result (if topics are not listened to)
    - POST `api/v1/configure {config_json}`
    - POST `api/v1/run`

POST `api/v1/topic-echo {topic_name} {timeout}` -> id
GET `api/v1/topic-echo/id`

POST `api/v1/topic-pub {topic_name} {topic_data}`

POST `api/v1/configuration {config_json}`  # define the default world to be launched, environment variables
POST `api/v1/simulation_instance {config_json}` # display, distributed parameters, with world, without world, with gui without gui

Output format: `{'status': timeout|success|failure, 'message': "[error code] explanation"}`

POST `api/v1/communication-test {test_parameters}`  -> id
GET `api/v1/communication-test/id` 

Output format: `{'status': timeout|success|failure, 'checklist': [{'status': 'timeout', 'name': "", 'message': ""},{'status': timeout, 'name': "", 'message': ""}, {'status': timeout, 'name': "", 'message': ""}]}`



