"""Module that provides the Service command topic-publish. The purpose of this module is to expose the capability of publishing a topic with the Simulator container"""

import requests
from WebServerCore.ICommand import ICommand
from WebServerCore.utils.exception import InvalidInputException, UnsupportedCommand

import simulator_api.utils.logger as logging
from simulator_api.async_tasks.async_tasks import container_exec_cmd

def publish_topic(topic, message, msgtype):
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

    def get_execute_latest(self, _url_params):
        return self.get_execute_v1(_url_params)

    def get_execute_v1(self, _url_params):
        raise UnsupportedCommand("Method not supported.")
    
    def post_execute_latest(self, url_params, body_data):
        return self.post_execute_v1(url_params, body_data)

    def post_execute_v1(self, url_params, body_data):
        logging.info("Topic publish command reached")

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