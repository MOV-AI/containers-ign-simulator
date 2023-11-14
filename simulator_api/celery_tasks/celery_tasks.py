import os
import json
from pathlib import Path
import configparser
from celery import Celery
import simulator_api.utils.utils

import simulator_api.utils.logger as logging

celery = Celery(
    'entrypoint',
    broker='pyamqp://guest:guest@localhost:5672//',
    backend='db+sqlite:////opt/mov.ai/app/celery_data/results.sqlite3'
)
celery.conf.broker_connection_retry_on_startup = True
celery.conf.worker_hijack_root_logger = False
celery.conf.task_track_started = True

def container_exec_cmd(cmd, save_task_name = None, timeout = None):
    """Executes a shell command, evaluates the response and generates a status

    Args:
        cmd (string): Command to run.
        save_task_name (string, optional): Name tag to identify the operation. Defaults to None.
        timeout (int, optional): Duration of timeout for the command. Defaults to None.

    Returns:
        result (string): stdout of the operation
        task_status (string): state tag 'SUCCESS', 'ERROR' or 'TIMEOUT'
        task_json (json): dictionary describing the operation in detail
    """

    task_status = 'SUCCESS'

    timeout_flag, exitcode, result = simulator_api.utils.utils.subprocess_timeout_compliant(cmd, timeout = timeout)
    if timeout_flag:
        task_status = 'TIMEOUT'
        message = f"The command '{cmd}' timed out. Output: {result}."
        logging.debug(message)
    elif exitcode != 0:
        task_status = 'ERROR'
        message = f"The command '{cmd}' returned a non-zero exit status: {exitcode}. Output: {result}."
        logging.debug(message)
    else:
        message = f"The command '{cmd}' ran succesfully. Output: {result}."
        logging.debug(message)

    task_json = {
        'name': save_task_name,
        'status': task_status,
        'message': message
    }

    return result, task_status, task_json

def parse_config():
    """Function to parse configuration file

    Returns:
        configParser: Configuration object containing all config variables
    """    

    cfg = configparser.ConfigParser()

    # Read the configuration file
    path = Path(__file__)
    ROOT_DIR = path.parent.absolute()
    config_path = os.path.join(ROOT_DIR, "config.ini")
    logging.debug(f"Configuration file : {config_path}")
    cfg.read(config_path)

    ## Check mandatory configuration variables
    mandatory_vars = ["topic_spawner", "topic_sim", "ignition_base_topics", "world_name"]
    for var in mandatory_vars:
        if cfg.get("communication",var) is None: raise ValueError(f"Missing mandatory configuration variable: {var}") 

    return cfg


@celery.task()
def echo_topic(topic, timeout):
    """Handles topic echo inside the container.

    Args:
        topic (string): Name of the topic to echo
        timeout (int): Duration of echo in seconds.

    Returns:
        dict: Task json specifying the status of the echo.
    
    """

    cmd = f"ign topic -e -n 1 -t {topic}"
    _, _, task_json = container_exec_cmd(cmd, save_task_name = f"echo_{topic}", timeout = timeout)
    
    return task_json

@celery.task()
def communication_test():
    """Handles communication test inside the container."""

    # initialize check list
    check_list = []

    # initialize command status
    status = 'SUCCESS'

    # Get communication test variables
    cfg = parse_config()
    
    # Run communication smoke tests

    # Test sim to spawner communication through topic /test_from_sim (spawner must be listening to this topic)
    topic_sim = cfg.get("communication","topic_sim")
    cmd = f'ign topic -p "data:\"test\"" -t {topic_sim} --msgtype ignition.msgs.StringMsg'
    _, task_status, task_json = container_exec_cmd(cmd, save_task_name = "simulation_to_spawner_communication")
    if task_status != 'SUCCESS': status = task_status
    check_list.append(task_json)
    communication_test.update_state(state='PROGRESS', meta={'status': status + ' (intermediate)','checklist': check_list}) 

    # Test spawner to sim communication through topic /test_from_spawner (spawner must be publishing this topic)
    # change the timeout to be input
    topic_spawner = cfg.get("communication","topic_spawner")
    cmd = f"ign topic -e -n 1 -t {topic_spawner}"
    _, task_status, task_json = container_exec_cmd(cmd, save_task_name = "spawner_to_simulator_communication", timeout = 5)
    if task_status != 'SUCCESS': status = task_status
    check_list.append(task_json)
    communication_test.update_state(state='PROGRESS', meta={'status': status + ' (intermediate)','checklist': check_list}) 

    # Test that Ignition is running correctly (/clock, /stats)
    ign_topics = json.loads(cfg.get("communication","ignition_base_topics"))
    for topic in ign_topics:
        cmd = f"ign topic -e -n 1 -t {topic}"
        _, task_status, task_json = container_exec_cmd(cmd, save_task_name = f"ignition_running{topic.replace('/','_')}_check", timeout = 1)    
        if task_status != 'SUCCESS': status = task_status
        check_list.append(task_json) 
        communication_test.update_state(state='PROGRESS', meta={'status': status + ' (intermediate)','checklist': check_list})        
        
    # Test that a world is loaded correctly (/world/*/clock, /world/*/stats)
    world_name = cfg.get("communication","world_name")
    topic_names = [f"/world/{world_name}/clock", f"/world/{world_name}/stats"]
    for topic in topic_names:
        cmd = f"ign topic -e -n 1 -t {topic}"
        _, task_status, task_json = container_exec_cmd(cmd, save_task_name = f"world_running{topic.replace('/','_')}_check", timeout = 1)  
        if task_status != 'SUCCESS': status = task_status
        check_list.append(task_json) 
        communication_test.update_state(state='PROGRESS', meta={'status': status + ' (intermediate)','checklist': check_list})         

    return {'status' : status, 'checklist' : check_list}