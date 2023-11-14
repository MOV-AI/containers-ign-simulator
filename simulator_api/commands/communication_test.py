"""Module that provides the Service command communication-test. The purpose of this module is to expose the capability of retrieving the status of communication with the Simulator container"""

import os
import json
import requests
import configparser
from pathlib import Path
from WebServerCore.ICommand import ICommand

import simulator_api.utils.logger as logging
from simulator_api.celery_instance.celery import celery_instance
from simulator_api.utils.utils import container_exec_cmd

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

class CommunicationTest(ICommand):
    """Service Command to retrieve the status of communication with simulator"""

    def get_execute_latest(self, _url_params, task_id):
        return self.get_execute_v1(_url_params, task_id)

    def get_execute_v1(self, _url_params, task_id):
        """ Version 1 Handler for get requests of communication-test entrypoint.

        Args:
            _url_params (obj): optional url params
            task_id (string): callback id used to retrieve results of a previous POST request.

        Returns:
            request: Response regarding the status of the communication test.
        """        

        logging.debug("Get Simulator Status command reached")

        task = communication_test.AsyncResult(task_id)
    
        if task.state == 'PENDING': message = {'status': 'Celery Task is pending'}
        elif task.state != 'FAILURE': message = task.info  # Include any additional info you want
        else: message = {'status': 'Celery Task failed'}

        response = requests.Response()
        response._content = message  
        response.status_code = 200

        return response
    
    def post_execute_latest(self, url_params, body_data, url_specifics):
        return self.post_execute_v1(url_params, body_data, url_specifics)

    def post_execute_v1(self, url_params, body_data, url_specifics):
        """ Version 1 Handler for post requests of communication-test entrypoint.

        Args:
            url_params (obj): optional url params
            body_data (obj): optional body data
            url_specifics (obj): optional url inputs

        Returns:
            request: Callback id to be used to track result
        """        

        logging.debug("Post Communication Test command reached")

        task = communication_test.apply_async()

        response = requests.Response()
        response._content = {'task_id': task.id}
        response.status_code = 202
        return response

    def command_description(self):
        description = {
            "command": "communication-test",
            "method": "GET, POST",
            "description": "This command will start communication tests with simulator container and fetch the status of the communication tests.",
        }
        return description