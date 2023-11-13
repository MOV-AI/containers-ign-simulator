"""Module that provides the Service command configuration. The purpose of this module is to expose the capability of applying a simulation configuration to the Simulator container"""

import json
import requests
from WebServerCore.ICommand import ICommand
from WebServerCore.utils.exception import InvalidInputException, UnsupportedCommand

import simulator_api.utils.logger as logging
from simulator_api.celery_tasks.celery_tasks import container_exec_cmd

def apply_configuration(config_json):

    status = 'SUCCESS'
    checklist = []
    for key, value in config_json.items():
        _, task_status, task_json = container_exec_cmd(f"export {key}={value}", save_task_name=f"export_{key}", timeout=None)
        checklist += [task_json]
        if task_status != 'SUCCESS': status = 'ERROR'

    return {'status' : status, 'checklist' : checklist}

class Configuration(ICommand):
    """Service Command to apply a configuration in simulator"""
    def __init__(self):
        self._register_mandatory_argument(
            "config",
            "Configuration file to be applied.",
        )

    def get_execute_latest(self, _url_params, url_specifics):
        return self.get_execute_v1(_url_params)

    def get_execute_v1(self, _url_params, url_specifics):
        raise UnsupportedCommand("Method not supported.")
    
    def post_execute_latest(self, url_params, body_data, url_specifics):
        return self.post_execute_v1(url_params, body_data, url_specifics)

    def post_execute_v1(self, url_params, body_data, url_specifics):
        raise UnsupportedCommand("Method not supported.")
        
    
    def put_execute_latest(self, url_params, body_data, url_specifics):
        return self.put_execute_v1(url_params, body_data, url_specifics)
    
    def put_execute_v1(self, url_params, body_data, url_specifics):
        """Version 1 Handler for put requests of configuration entrypoint.

        Args:
            url_params (obj): 
            body_data (obj): 
            url_specifics (obj): optional url specific inputs

        Returns:
            request: Response regarding the status of the configuration setting.
        """        

        logging.debug("Configuration command reached")

        config_string = url_params.get("config")
        if config_string is None or config_string == "":
            raise InvalidInputException()
        
        config_dict = json.loads(config_string)

        result = apply_configuration(config_dict)

        logging.info(result)

        response = requests.Response()
        response._content = result  
        response.status_code = 200

        return response

    def command_description(self):
        description = {
            "command": "configuration",
            "method": "PUT",
            "description": "This command will apply a configuration in the simulator container.",
        }
        return description