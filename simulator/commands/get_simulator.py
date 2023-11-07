"""Module that provides the Service command GetSimulatorStatus. The purpose of this module is to expose the capability of retrieving the status of communication with the Simulator container"""

import requests
import subprocess
from LambdaCore.ICommand import ICommand
from LambdaCore.utils.exception import UnsupportedCommand

import simulator.utils.logger as logging
import simulator.utils.utils

class GetSimulatorStatus(ICommand):
    """Service Command to retrieve the status of communication with simulator"""

    def get_execute(self, _url_params):

        logging.info("Get Simulator Status command reached")


        output = self.handle_get()

        response = requests.Response()
        response._content = output  
        response.status_code = 200
        return response

    def post_execute(self, url_params, body_data):
        """Method contract implemented to guarantee this call is not supported"""
        raise UnsupportedCommand("Method not supported.")

    def command_description(self):
        description = {
            "command": "GetSimulatorStatus",
            "method": "GET",
            "description": "This command will fetch the status of communication with simulator container.",
        }
        return description

    def handle_get(self):
        """Handles GET requests inside the container."""
        
        # Run communication smoke tests

        # Test spawner to sim communication through topic /test (spawner must be publishing this topic)
        topic = "/test"
        result = self.ign_topic_is_published(topic)
        if result != 0: return result
        
        logging.info(f"Communication from spawner to simulator verified")

        # Test that Ignition is running (/clock, /stats)
        for topic in ["/clock","/stats"]:
            result = self.ign_topic_is_published(topic)
            if result != 0: return result
            
        logging.info(f"Ignition simulation is running")
            
        # Test that a world is loaded correctly (/world/*/clock, /world/*/stats)
        world_topics = "'world.*clock\|world.*stats'"
        topic_names = self.ign_topic_exists(world_topics)

        if len(topic_names) == 0: 
            logging.info(f"No world is loaded in simulation")
            return f"[exitcode = 124] The topic {topic} is not published\n"

        for topic in topic_names:
            result = self.ign_topic_is_published(topic)
            if result != 0: return result
                
        logging.info(f"Ignition World is properly loaded.")

        return f"[exitcode = {result}] Communication with simulator is healthy\n"
    
    def ign_topic_exists(self, topic_pattern: str):
        
        """Check that a given ign topic is listed inside the container.

        Args:
            topic_pattern: Topic string.

        """

        cmd = f"ign topic -l | grep {topic_pattern}"
        exitcode, result = simulator.utils.utils.subprocess_timeout_compliant(cmd, timeout = None)
        if exitcode != 0:
            logging.info(f"The command '{cmd}' returned a non-zero exit status: {exitcode}. Output: {result}")
            return []
        
        output = result.decode('utf-8').strip().split('\n')

        return output

    def ign_topic_is_published(self, topic: str):
        """Check that a given ign topic is being published inside the container.

        Args:
            topic: Topic string.

        """

        cmd = f"ign topic -e -n 1 -t {topic}"
        exitcode, _ = simulator.utils.utils.subprocess_timeout_compliant(cmd)
        if exitcode == 124:
            logging.info(f"[exitcode = {exitcode}] The command '{cmd}' timed out. The topic '{topic}' is not published")
            return f"[exitcode = {exitcode}] The topic {topic} is not published\n"
        if exitcode != 0:
            logging.info(f"[exitcode = {exitcode}] The command '{cmd}' returned a non-zero exit status. Failed to get simulator status on topic {topic}")
            return f"[exitcode = {exitcode}] Failed to get simulator status\n"
        
        return exitcode
