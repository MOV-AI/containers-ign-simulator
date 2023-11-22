"""Module that initializes Celery and defines tasks for asynchronous execution."""
import os
import json
import sqlalchemy
from datetime import datetime
from celery import Celery
from celery.signals import after_task_publish, task_postrun

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

task_id_table_name = 'celery_tasks'
task_id_db_path = f"/opt/mov.ai/app/celery_data/{task_id_table_name}.sqlite3"


@after_task_publish.connect()
def save_task_id(headers=None, **kwargs):
    """Adds the task id of a task to a celery_tasks table

    Args:
        headers (dict, optional): Task message headers. Defaults to None.
    """

    engine = sqlalchemy.create_engine(f'sqlite:///{task_id_db_path}')
    # Create the Metadata Object
    meta = sqlalchemy.MetaData()

    if not sqlalchemy.inspection.inspect(engine).has_table(task_id_table_name):
        table = sqlalchemy.Table(
            task_id_table_name,
            meta,
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('task_id', sqlalchemy.String),
            sqlalchemy.Column('state', sqlalchemy.String),
            sqlalchemy.Column('created', sqlalchemy.DateTime),
        )
        # Check if the table already exists before creating it
        meta.create_all(engine)
    else:
        # Load table
        table = sqlalchemy.Table(task_id_table_name, meta, autoload_with=engine)

    # Add row
    with engine.connect() as conn:
        conn.execute(
            sqlalchemy.insert(table).values(
                {'task_id': headers['id'], 'state': "SENT", 'created': datetime.now()}
            )
        )
        conn.commit()


@task_postrun.connect()
def task_post_run(task_id=None, state=None, **kwargs):
    """Adds the task id of a complete task to a celery_tasks table
    Args:
        task_id (string, optional): Id of the task to be executed. Defaults to None.
        state (string, optional): Name of the resulting state.. Defaults to None.
    """

    engine = sqlalchemy.create_engine(f'sqlite:///{task_id_db_path}')
    meta = sqlalchemy.MetaData()
    table = sqlalchemy.Table(task_id_table_name, meta, autoload_with=engine)

    # Update state
    with engine.connect() as conn:
        conn.execute(
            sqlalchemy.update(table)
            .where(table.columns.task_id == task_id)
            .values({'state': state})
        )
        conn.commit()


def get_task_ids():
    """Retrieves all celery task ids of the current session

    Returns:
        task_ids (list): list of celery task ids
    """

    task_ids = []
    if os.path.exists(task_id_db_path):

        engine = sqlalchemy.create_engine(f'sqlite:///{task_id_db_path}')
        meta = sqlalchemy.MetaData()
        table = sqlalchemy.Table(task_id_table_name, meta, autoload_with=engine)

        # Fetch all the results
        with engine.connect() as conn:
            task_ids = list(
                map(
                    lambda x: f"{x[0]} (state = {x[1]})",
                    conn.execute(
                        sqlalchemy.select(table.columns.task_id, table.columns.state)
                    ).fetchall(),
                )
            )

    return task_ids


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
        cfg.get("communication", "topic_spawner")
        if (topic_to_echo is None or topic_to_echo == "")
        else topic_to_echo
    )
    topic_to_publish = (
        cfg.get("communication", "topic_sim")
        if (topic_to_publish is None or topic_to_publish == "")
        else topic_to_publish
    )
    world = cfg.get("communication", "world_name") if (world is None or world == "") else world
    timeout = (
        int(cfg.get("communication", "timeout"))
        if (duration is None or duration == 0)
        else duration
    )

    # Run communication smoke tests

    # Test sim to spawner communication through topic /test_from_sim (spawner must be listening to this topic)
    cmd = f'ign topic -p "data:\"test\"" -t {topic_to_echo} --msgtype ignition.msgs.StringMsg'
    check_list = container_exec_cmd(cmd, checklist=check_list)
    communication_test.update_state(
        state='PROGRESS', meta={'status': status, 'checklist': check_list}
    )

    # Test spawner to sim communication through topic /test_from_spawner (spawner must be publishing this topic)
    cmd = f"ign topic -e -n 1 -t {topic_to_publish}"
    check_list = container_exec_cmd(cmd, timeout=timeout, checklist=check_list)
    communication_test.update_state(
        state='PROGRESS', meta={'status': status, 'checklist': check_list}
    )

    # Test that Ignition is running correctly (/clock, /stats)
    ign_topics = json.loads(cfg.get("communication", "ignition_base_topics"))
    for topic in ign_topics:
        cmd = f"ign topic -e -n 1 -t {topic}"
        check_list = container_exec_cmd(cmd, timeout=1, checklist=check_list)
        communication_test.update_state(
            state='PROGRESS', meta={'status': status, 'checklist': check_list}
        )

    # Test that a world is loaded correctly (/world/*/clock, /world/*/stats)
    ign_topics = [f"/world/{world}/clock", f"/world/{world}/stats"]
    for topic in ign_topics:
        cmd = f"ign topic -e -n 1 -t {topic}"
        check_list = container_exec_cmd(cmd, timeout=1, checklist=check_list)
        communication_test.update_state(
            state='PROGRESS', meta={'status': status, 'checklist': check_list}
        )

    task_status = [check["status"] for check in check_list]
    status = "ERROR" if ("TIMEOUT" in task_status or "ERROR" in task_status) else "SUCCESS"

    return {'status': status, 'checklist': check_list}
