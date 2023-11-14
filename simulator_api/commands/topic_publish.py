"""Module that provides the Service command topic-publish. The purpose of this module is to expose the capability of publishing a topic with the Simulator container"""

import requests
from WebServerCore.ICommand import ICommand
from WebServerCore.utils.exception import InvalidInputException, UnsupportedCommand

import simulator_api.utils.logger as logging
from simulator_api.utils.utils import container_exec_cmd

def publish_topic(topic, message, msgtype):
    """Starts a process to echo a topic.

    Args:
        topic (string): Name of the topic from which to publish a message
        message (string): Message to publish
        msgtype (string): Type of message being published

    Returns:
        task_json (dict): Task json specifying the status of the publish.
    """    

    cmd = f'ign topic -p "{message}" -t {topic} --msgtype {msgtype}'
    _, _, task_json = container_exec_cmd(cmd, save_task_name = f"publish_{topic}", timeout = None)

    return task_json

class TopicPublish(ICommand):
    """Service Command to publish a topic in simulator"""
    def __init__(self):
        self._register_mandatory_argument(
            "topic",
            "Topic to be published.",
        )
        self._register_mandatory_argument(
            "message",
            "Message to be published.",
        )
        self._register_mandatory_argument(
            "msgtype",
            "Type of message published.",
        )

    def get_execute_latest(self, _url_params, url_specifics):
        return self.get_execute_v1(_url_params, url_specifics)

    def get_execute_v1(self, _url_params, url_specifics):
        raise UnsupportedCommand("Method not supported.")
    
    def post_execute_latest(self, url_params, body_data, url_specifics):
        return self.post_execute_v1(url_params, body_data, url_specifics)

    def post_execute_v1(self, url_params, body_data, url_specifics):
        """Version 1 Handler for post requests of topic-publish entrypoint.

        Args:
            url_params (dict): json containing the mandatory inputs for a publish POST request: 'topic', 'message' and 'msgtype'
            body_data (obj): optional body data
            url_specifics (obj): optional url specific inputs

        Returns:
            response (request): Response regarding the status of the publish topic.
        """        

        logging.debug("Topic publish command reached")

        topic, message, msgtype = url_params.get("topic"), url_params.get("message"), url_params.get("msgtype")
        if topic is None or topic == "" or message is None or message == "" or msgtype is None or msgtype == "":
            raise InvalidInputException()

        result = publish_topic(topic, message, msgtype)

        response = requests.Response()
        response._content = result  
        response.status_code = 200

        return response

    def command_description(self):
        description = {
            "command": "topic-publish",
            "method": "POST",
            "description": "This command will publish a topic in the simulator container and fetch the status of the publish.",
        }
        return description