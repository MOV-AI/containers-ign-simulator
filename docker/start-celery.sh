#!/bin/bash

# Wait for RabbitMQ to start up
rabbitmqctl wait --pid 1

# Start Celery worker after RabbitMQ is ready
su - movai -c 'celery -A simulator_api.celery_tasks.tasks.celery_instance worker --concurrency=2 --loglevel=info'
