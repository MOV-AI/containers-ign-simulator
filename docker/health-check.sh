#!/bin/bash
set -eo pipefail

if ping="$(celery -A simulator_api.celery_tasks.tasks.celery_instance inspect ping --json)" && [ "$ping" = '{"celery@simulator": {"ok": "pong"}}' ]; then
	exit 0
fi

exit 1



