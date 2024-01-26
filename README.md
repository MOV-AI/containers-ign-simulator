[![Build&Deploy MOVAI Ignition Gazebo](https://github.com/MOV-AI/containers-ign-simulator/actions/workflows/docker-ci.yml/badge.svg?branch=main)](https://github.com/MOV-AI/containers-ign-simulator/actions/workflows/docker-ci.yml)
 <a href="https://sonarcloud.io/summary/new_code?id=MOV-AI_containers-ign-simulator"><img alt="Quality Gate Status" src="https://sonarcloud.io/api/project_badges/measure?project=MOV-AI_containers-ign-simulator&metric=alert_status"></a>

# MOVAI Ignition Gazebo Container

Ignition Simulator Docker image for MOV.AI Framework

Image is built as follow :

| Flavour      | Base Image | IGN build from source |
| ------------ | ---------- | ------ |
| ignition-fortress | movai-base-focal:v2.4.4 | see https://github.com/MOV-AI/containers-ign-simulator/blob/main/docker/collection-fortress-12-23.yaml |



## Build

Build IGN Simulator image based on MOVAI bionic :

    docker build -t ign-simulator:test . -f docker/Dockerfile

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

- Launch simulator API:
```
docker run -td -e MOVAI_ENV=qa -e DISPLAY=$DISPLAY ign-simulator:test
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

## Simulator Web Server Application

The simulator web server api is reachable through port 8081 and offers 3 endpoints:
- `/api/communication-test`
- `/api/topic-echo`
- `/api/publish-echo`

If a get request is succesful, the response of every endpoint is a json, which always contains a **status** key with the value **SUCCESS**, **TIMEOUT** or **ERROR**, depending on the status of the task requested.

### Communication Test Endpoint

The communication test endpoint's purpose is to perform a series of communication tasks to check communication between the simulator container and the host where the tests are being requested. To achieve this goal, the endpoint offers two call methods:
- a `POST` method to start the series of comm tests, which returns a task id and can be called with or without arguments as follows:
    - `POST /api/communication-test`, in which case the followings parameters are set as default:
        - echo_topic =  /test_from_spawner_to_simulator
        - publish_topic = /test_from_simulator_to_spawner
        - world_name = empty
        - timeout = 5
    - `POST /api/communication-test?echo-topic=FILL&publish-topic=FILL&world-name=FILL&timeout=FILL`, in which case you can specify the topics to echo and publish, the world to verify and the duration of the echo.
    - output: task_id (string)
- a `GET` method to get the status of the comm tests, which
    - is called as `GET /api/communication-test/<task-id>`, where `<task-id>` corresponds to the id retrieved from the POST request.
    - outputs a response (json) with format `{"status": global_status, "checklist": [{"name": task_name, "status": task_status, "message": task_message}, ...]}`

The tasks performed are as follows:
- echo a defined topic during a specified duration; with the purpose of testing communication from host to simulator
- publish a defined message in a defined topic; with the purpose of testing communication from simulator to host
- echo the topics /clock and /stats; with the purpose of testing if a simulation instance is running
- echo the world specific topics /world/<world-name>/clock and /world/<world-name>/stats; with the purpose of testing if a specific world is properly loaded

### Topic Echo Endpoint

The topic echo endpoint's purpose is to perform an echo of a specified topic during a specified time in the simulator container. To achieve this goal, the endpoint offers two call methods:
- a `POST` method to start the echo, which returns a task id and must be called with arguments as follows:
    - `POST /api/topic-echo?topic=FILL&timeout=FILL`, where you need to specify the topic and the duration to echo for.
- a `GET` method to get the status of the echo, which
    - is called as `GET /api/topic-echo/<task-id>`, where `<task-id>` corresponds to the id retrieved from the POST request.
    - outputs a response (json) with format `{"name": task_name, "status": task_status, "message": task_message}`

### Topic Publish Endpoint

The topic publish endpoint's purpose is to publish a specified topic message in the simulator container. To achieve this goal, the endpoint offers one call method:
- a `POST` method to start the echo, which must be called with arguments as follows:
    - `POST /api/topic-publish?topic=FILL&message=FILL&msgtype=FILL`, where you need to specify the topic, the data to publish and the type of data to publish, equal to how it is specified in an ignition command.
    - outputs a response (json) with format `{"name": task_name, "status": task_status, "message": task_message}`

## License

[MOV.AI](https://www.mov.ai/)
