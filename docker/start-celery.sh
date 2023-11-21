#!/bin/bash

RABBITMQ_PID_FILE=/var/lib/rabbitmq/mnesia/rabbitmq.pid

# Wait for RabbitMQ to start up
rabbitmqctl wait $RABBITMQ_PID_FILE

# Start Celery worker after RabbitMQ is ready
su - movai -c 'celery -A simulator_api.celery_tasks.tasks.celery_instance worker --concurrency=2 --loglevel=info'
