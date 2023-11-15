"""Module that provides the Service command communication-test. The purpose of this module is to expose the capability of retrieving the status of communication with the Simulator container"""

import requests
from WebServerCore.ICommand import ICommand

import simulator_api.utils.logger as logging
from simulator_api.celery_tasks.tasks import communication_test

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
            response (request): Response regarding the status of the communication test.
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
            url_params (dict): json containing the optional inputs for an echo POST request: 'echo-topic', 'publish-topic', 'world-name' and 'timeout'
            body_data (obj): optional body data
            url_specifics (obj): optional url inputs

        Returns:
            response (request): Callback id to be used to track result
        """        

        logging.debug("Post Communication Test command reached")

        # Check if optional params were provided
        if url_params is None or url_params=="": 
            task = communication_test.apply_async()
        else:
            echo_topic, publish_topic, world_name, duration = url_params.get("echo-topic"), url_params.get("publish-topic"), url_params.get("world-name"), url_params.get("timeout")
            task = communication_test.apply_async(args=(echo_topic, publish_topic, world_name, duration))

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