"""Module that provides the Service command GetSimulatorStatus. The purpose of this module is to expose the capability of retrieving the status of communication with the Simulator container"""

import requests
from WebServerCore.ICommand import ICommand
from WebServerCore.utils.exception import UnsupportedCommand

import simulator_api.utils.logger as logging
from simulator_api.async_tasks.async_tasks import handle_get

class communicationtest(ICommand):
    """Service Command to retrieve the status of communication with simulator"""

    def get_execute_latest(self, _url_params, task_id):
        return self.get_execute_v1(_url_params, task_id)

    def get_execute_v1(self, _url_params, task_id):

        logging.info("Get Simulator Status command reached")

        task = handle_get.AsyncResult(task_id)
    
        if task.state == 'PENDING': message = {'status': 'Task is pending'}
        elif task.state != 'FAILURE': message = {'status': 'Task is in progress','result': task.info}  # Include any additional info you want
        else: message = {'status': 'Task failed'}

        response = requests.Response()
        response._content = message  
        response.status_code = 200

        logging.info(message)

        return response
    
    def post_execute_latest(self, url_params, body_data):
        raise self.post_execute_v1(url_params, body_data)

    def post_execute_v1(self, url_params, body_data):
        logging.info("Post Communication Test command reached")

        task = handle_get.apply_async()

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