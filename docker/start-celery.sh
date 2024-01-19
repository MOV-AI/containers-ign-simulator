#!/bin/bash

LOG_LEVEL=${LOG_LEVEL:-info}

# Wait for RabbitMQ to start up
rabbitmqctl wait $RABBITMQ_PID_FILE

# Start Celery worker after RabbitMQ is ready
su -w IGN_PARTITION -w IGN_IP -w IGN_RELAY -w IGN_CONFIG_PATH -w LD_LIBRARY_PATH - movai -c "celery -A simulator_api.celery_tasks.tasks.celery_instance worker --concurrency=2 --loglevel=$LOG_LEVEL"
