"""Module that initializes Celery and defines tasks for asynchronous execution."""
import os
import json
import sqlite3
from datetime import datetime
from celery import Celery
from celery.signals import task_postrun

import simulator_api.utils.logger as logging
from simulator_api.utils.utils import parse_config
from simulator_api.utils.utils import container_exec_cmd


celery_instance = Celery(
    'entrypoint',
    broker='pyamqp://guest:guest@localhost:5672//',
    backend='db+sqlite:////opt/mov.ai/app/celery_data/results.sqlite3',
)
celery_instance.conf.broker_connection_retry_on_startup = True
celery_instance.conf.worker_hijack_root_logger = False
celery_instance.conf.task_track_started = True


@task_postrun.connect()
def task_post_run(task_id=None, state=None, **kwargs):
    """Adds the task id of a complete task to a finished_tasks table

    Args:
        task_id (string, optional): Id of the task to be executed. Defaults to None.
        state (string, optional): Name of the resulting state.. Defaults to None.
    """

    db_path = "/opt/mov.ai/app/celery_data/finished_tasks.sqlite3"

    # write info about a finished task into SQLite
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        # Create table to save values
        conn.execute(
            '''
                        CREATE TABLE IF NOT EXISTS celery_tasks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            task_id TEXT,
                            state TEXT,
                            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    '''
        )
    else:
        conn = sqlite3.connect(db_path)
    conn.execute('INSERT INTO celery_tasks (task_id, state, created) VALUES (?,?,?)', (task_id, state, datetime.now()))

    conn.commit()
    conn.close()


def retrieve_task_ids():
    """Retrieves all celery task ids of the current session

    Returns:
        task_ids (list): list of celery task ids
    """

    db_path = "/opt/mov.ai/app/celery_data/finished_tasks.sqlite3"

    task_ids = []
    if os.path.exists(db_path):

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute a SELECT query to retrieve task_id values
        cursor.execute('SELECT task_id FROM celery_tasks')

        # Fetch all the results
        task_ids = list(map(lambda x: x[0], cursor.fetchall()))

        # Close the database connection
        conn.close()

    return task_ids


def get_running_task_ids():
    """Returns all ids of tasks being run by celery"""

    # Get the task IDs of all active tasks
    active_tasks = [task['id'] for tasks in celery_instance.control.inspect().active().values() for task in tasks]
    logging.info(f"Celery tasks currently active: {active_tasks}")
    scheduled_tasks = [task['id'] for tasks in celery_instance.control.inspect().scheduled().values() for task in tasks]
    logging.info(f"Celery tasks that have an ETA or are scheduled for later processing: {scheduled_tasks}")
    reserved_tasks = [task['id'] for tasks in celery_instance.control.inspect().reserved().values() for task in tasks]
    logging.info(f"Celery tasks that have been claimed by workers: {reserved_tasks}")
    finished_tasks = retrieve_task_ids()
    logging.info(f"Celery tasks that have been finished by workers: {finished_tasks}")

    return active_tasks + scheduled_tasks + reserved_tasks + finished_tasks


@celery_instance.task()
def echo_topic(topic, timeout):
    """Handles topic echo inside the container.

    Args:
        topic (string): Name of the topic to echo
        timeout (int): Duration of echo in seconds.

    Returns:
        task_json (dict): Task json specifying the status of the echo.

    """

    cmd = f"ign topic -e -n 1 -t {topic}"
    task_json = container_exec_cmd(cmd, timeout=timeout)

    return task_json


@celery_instance.task()
def communication_test(topic_to_echo=None, topic_to_publish=None, world=None, duration=None):
    """Handles communication test inside the container.

    Returns:
        dict: Task json specifying the status of the communication test.

    """

    # initialize check list
    check_list = []

    # initialize command status
    status = 'RUNNING'

    # Get communication test variables
    cfg = parse_config()

    # Retrieve communication variables
    topic_to_echo = (
        cfg.get("communication", "topic_spawner") if (topic_to_echo is None or topic_to_echo == "") else topic_to_echo
    )
    topic_to_publish = (
        cfg.get("communication", "topic_sim")
        if (topic_to_publish is None or topic_to_publish == "")
        else topic_to_publish
    )
    world = cfg.get("communication", "world_name") if (world is None or world == "") else world
    timeout = int(cfg.get("communication", "timeout")) if (duration is None or duration == 0) else duration

    # Run communication smoke tests

    # Test sim to spawner communication through topic /test_from_sim (spawner must be listening to this topic)
    cmd = f'ign topic -p "data:\"test\"" -t {topic_to_echo} --msgtype ignition.msgs.StringMsg'
    check_list = container_exec_cmd(cmd, checklist=check_list)
    communication_test.update_state(state='PROGRESS', meta={'status': status, 'checklist': check_list})

    # Test spawner to sim communication through topic /test_from_spawner (spawner must be publishing this topic)
    cmd = f"ign topic -e -n 1 -t {topic_to_publish}"
    check_list = container_exec_cmd(cmd, timeout=timeout, checklist=check_list)
    communication_test.update_state(state='PROGRESS', meta={'status': status, 'checklist': check_list})

    # Test that Ignition is running correctly (/clock, /stats)
    ign_topics = json.loads(cfg.get("communication", "ignition_base_topics"))
    for topic in ign_topics:
        cmd = f"ign topic -e -n 1 -t {topic}"
        check_list = container_exec_cmd(cmd, timeout=1, checklist=check_list)
        communication_test.update_state(state='PROGRESS', meta={'status': status, 'checklist': check_list})

    # Test that a world is loaded correctly (/world/*/clock, /world/*/stats)
    ign_topics = [f"/world/{world}/clock", f"/world/{world}/stats"]
    for topic in ign_topics:
        cmd = f"ign topic -e -n 1 -t {topic}"
        check_list = container_exec_cmd(cmd, timeout=1, checklist=check_list)
        communication_test.update_state(state='PROGRESS', meta={'status': status, 'checklist': check_list})

    task_status = [check["status"] for check in check_list]
    status = "ERROR" if ("TIMEOUT" in task_status or "ERROR" in task_status) else "SUCCESS"

    return {'status': status, 'checklist': check_list}
