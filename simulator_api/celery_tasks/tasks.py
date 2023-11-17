"""Module that initializes Celery and defines tasks for asynchronous execution."""
import json
from celery import Celery
from simulator_api.utils.utils import parse_config
from simulator_api.utils.utils import container_exec_cmd
from celery.signals import after_task_publish
import simulator_api.utils.logger as logging

celery_instance = Celery(
    'entrypoint',
    broker='pyamqp://guest:guest@localhost:5672//',
    backend='db+sqlite:////opt/mov.ai/app/celery_data/results.sqlite3',
)
celery_instance.conf.broker_connection_retry_on_startup = True
celery_instance.conf.worker_hijack_root_logger = False
celery_instance.conf.task_track_started = True


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    """Updates the state of a task if it has been requested

    Args:
        sender (string, optional): Name of the task being sent. Defaults to None.
        headers (dict, optional): Task message headers. Defaults to None.
    """

    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = celery_instance.tasks.get(sender)
    backend = task.backend if task else celery_instance.backend

    backend.store_result(headers['id'], {'status': 'Celery Task is pending'}, "SENT")


def get_running_task_ids():
    """Returns all ids of tasks being run by celery"""

    # Get the task IDs of all active tasks
    active_tasks = [task['id'] for tasks in celery_instance.control.inspect().active().values() for task in tasks]
    logging.info(f"Celery tasks currently active: {active_tasks}")
    scheduled_tasks = [task['id'] for tasks in celery_instance.control.inspect().scheduled().values() for task in tasks]
    logging.info(f"Celery tasks that have an ETA or are scheduled for later processing: {scheduled_tasks}")
    reserved_tasks = [task['id'] for tasks in celery_instance.control.inspect().reserved().values() for task in tasks]
    logging.info(f"Celery tasks that have been claimed by workers: {reserved_tasks}")

    return active_tasks + scheduled_tasks + reserved_tasks


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
