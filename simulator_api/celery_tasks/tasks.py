import json
from celery import Celery
from simulator_api.utils.utils import parse_config
from simulator_api.utils.utils import container_exec_cmd

celery_instance = Celery(
    'entrypoint',
    broker='pyamqp://guest:guest@localhost:5672//',
    backend='db+sqlite:////opt/mov.ai/app/celery_data/results.sqlite3'
)
celery_instance.conf.broker_connection_retry_on_startup = True
celery_instance.conf.worker_hijack_root_logger = False
celery_instance.conf.task_track_started = True

@celery_instance.task()
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

@celery_instance.task()
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