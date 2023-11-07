"""Module that provides the Service command GetSimulatorStatus. The purpose of this module is to expose the capability of retrieving the status of communication with the Simulator container"""

import requests
from LambdaCore.ICommand import ICommand
from LambdaCore.utils.exception import UnsupportedCommand

import simulator_api.utils.logger as logging
import simulator_api.utils.utils

class GetSimulatorStatus(ICommand):
    """Service Command to retrieve the status of communication with simulator"""
    def __init__(self):
        # initialize check list
        self.check_list = []
        self.status = 'OK'


    def get_execute_v1(self, _url_params):

        logging.info("Get Simulator Status command reached")

        output = self.handle_get()

        response = requests.Response()
        response._content = output  
        response.status_code = 200
        return response

    def post_execute_v1(self, url_params, body_data):
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

        # Test sim to spawner communication through topic /test_from_sim (spawner must be listening to this topic)
        cmd = 'ign topic -p "data:\"test\"" -t /test_from_sim --msgtype ignition.msgs.StringMsg'
        _ = self.container_exec_cmd(cmd, save_task_name = "simulation_to_spawner_communication")

        # Test spawner to sim communication through topic /test_from_spawner (spawner must be publishing this topic)
        # change the timeout to be input
        cmd = f"ign topic -e -n 1 -t /test_from_spawner"
        _ = self.container_exec_cmd(cmd, save_task_name = "spawner_to_simulator_communication", timeout = 5)

        # Verify if ignition is launched and if not launch it

        # Test that Ignition is running correctly (/clock, /stats)
        for topic in ["/clock","/stats"]:
            cmd = f"ign topic -e -n 1 -t {topic}"
            _ = self.container_exec_cmd(cmd, save_task_name = f"ignition_running{topic.replace('/','_')}_check", timeout = 1)            

        # Verify if world.sdf is launched and if not launch it
            
        # Test that a world is loaded correctly (/world/*/clock, /world/*/stats)
        cmd = f"ign topic -l | grep 'world.*clock\|world.*stats'"
        result = self.container_exec_cmd(cmd, save_task_name = "world_running") 
        topic_names = result.decode('utf-8').strip().split('\n') if len(result.decode('utf-8')) > 0 else []
        for topic in topic_names:
            cmd = f"ign topic -e -n 1 -t {topic}"
            _ = self.container_exec_cmd(cmd, save_task_name = f"world_running{topic.replace('/','_')}_check", timeout = 1)            

        # if launched ignition kill it
        # if launched world kill it

        return {'status' : self.status, 'checklist' : self.check_list}
    
    def container_exec_cmd(self, cmd, save_task_name = None, timeout = None):

        timeout_flag, exitcode, result = simulator_api.utils.utils.subprocess_timeout_compliant(cmd, timeout = timeout)
        if timeout_flag:
            self.status = 'NOK'
            message = f"The command '{cmd}' timed out. Output: {result}."
            logging.info(message)
        elif exitcode != 0:
            self.status = 'NOK'
            message = f"The command '{cmd}' returned a non-zero exit status: {exitcode}. Output: {result}."
            logging.info(message)
        else:
            message = f"The command '{cmd}' ran succesfully. Output: {result}."
            logging.info(message)

        if not(save_task_name is None):
            self.check_list.append({
                'name': save_task_name,
                'timeout': timeout_flag,
                'exitcode': exitcode,
                'message': message
            })

        return result