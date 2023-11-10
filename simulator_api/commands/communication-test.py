"""Module that provides the Service command communication-test. The purpose of this module is to expose the capability of retrieving the status of communication with the Simulator container"""

import requests
from WebServerCore.ICommand import ICommand

import simulator_api.utils.logger as logging
from simulator_api.celery_tasks.celery_tasks import communication_test

class CommunicationTest(ICommand):
    """Service Command to retrieve the status of communication with simulator"""

    def get_execute_latest(self, _url_params, task_id):
        return self.get_execute_v1(_url_params, task_id)

    def get_execute_v1(self, _url_params, task_id):

        logging.info("Get Simulator Status command reached")

        task = communication_test.AsyncResult(task_id)
    
        if task.state == 'PENDING': message = {'status': 'Celery Task is pending'}
        elif task.state != 'FAILURE': message = task.info  # Include any additional info you want
        else: message = {'status': 'Celery Task failed'}

        response = requests.Response()
        response._content = message  
        response.status_code = 200

        return response
    
    def post_execute_latest(self, url_params, body_data):
        return self.post_execute_v1(url_params, body_data)

    def post_execute_v1(self, url_params, body_data):
        logging.info("Post Communication Test command reached")

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