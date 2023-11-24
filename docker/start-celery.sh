#!/bin/bash

LOG_LEVEL=${LOG_LEVEL:-info}

# Wait for RabbitMQ to start up
rabbitmqctl wait $RABBITMQ_PID_FILE

# Start Celery worker after RabbitMQ is ready
# -w option is needed not to reset environment variables in the workers process
su -w IGN_PARTITION - movai -c "celery -A simulator_api.celery_tasks.tasks.celery_instance worker --concurrency=2 --loglevel=$LOG_LEVEL"