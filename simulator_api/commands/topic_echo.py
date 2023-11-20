"""Module that provides the Service command topic-echo.
The purpose of this module is to expose the capability of echoing a topic with the Simulator container"""

import requests
from WebServerCore.ICommand import ICommand
from WebServerCore.utils.exception import InvalidInputException
from werkzeug.exceptions import BadRequest

import simulator_api.utils.logger as logging
from simulator_api.utils.utils import parse_config
from simulator_api.celery_tasks.tasks import echo_topic


class TopicEcho(ICommand):
    """Service Command to echo a topic in simulator"""

    def __init__(self):
        self._register_mandatory_argument(
            "topic",
            "Topic to be echoed.",
        )
        self._register_mandatory_argument(
            "timeout",
            "Timeout duration for the echo.",
        )

    def get_execute_latest(self, _url_params, task_id):
        return self.get_execute_v1(_url_params, task_id)

    def get_execute_v1(self, _url_params, task_id):
        """Version 1 Handler for get requests of topic-echo entrypoint.

        Args:
            _url_params (obj): optional url parameters
            task_id (string): callback id used to retrieve results of a previous POST request.

        Returns:
            response (request): Response regarding the status of the echo topic.
        """

        logging.debug("Topic Echo command reached")

        task = echo_topic.AsyncResult(task_id)

        if task.state == 'PENDING':
            message = {'status': 'Celery Task is pending'}
        elif task.state != 'FAILURE':
            message = task.info  # Include any additional info you want
        else:
            message = {'status': 'Celery Task failed'}

        response = requests.Response()
        response._content = message
        response.status_code = 200

        return response

    def post_execute_latest(self, url_params, body_data, url_specifics):
        return self.post_execute_v1(url_params, body_data, url_specifics)

    def post_execute_v1(self, url_params, body_data, url_specifics):
        """Version 1 Handler for post requests of topic-echo entrypoint.

        Args:
            url_params (dict): json containing the mandatory inputs for an echo POST request: 'topic' and 'timeout'
            body_data (obj): optional body data
            url_specifics (obj): optional url specific inputs

        Returns:
            response (request): Callback id to be used to track result
        """

        logging.debug("Topic Echo command reached")

        # Get maximum timeout allowed
        cfg = parse_config()
        max_timeout = int(cfg.get("communication", "max_timeout"))

        topic, timeout = url_params.get("topic"), url_params.get("timeout")
        if topic is None or topic == "" or timeout is None or timeout == "":
            raise InvalidInputException()
        if topic[0] != "/":
            raise BadRequest(f"Not valid topic: {topic}")
        try:
            timeout = int(timeout)
        except ValueError:
            raise BadRequest(f"Not valid timeout: {timeout}")
        if timeout > max_timeout:
            raise BadRequest(f"Timeout larger than maximum allowed ({max_timeout}): {timeout}")

        task = echo_topic.apply_async(
            args=(
                topic,
                timeout,
            )
        )

        response = requests.Response()
        response._content = {'task_id': task.id}
        response.status_code = 202
        return response

    def command_description(self):
        description = {
            "command": "topic-echo",
            "method": "GET, POST",
            "description": "This command will echo a topic in the simulator container and return the status.",
        }
        return description
