import os
from celery import Celery
import simulator_api.utils.utils

import simulator_api.utils.logger as logging

celery = Celery(
    'entrypoint',
    broker='pyamqp://guest:guest@localhost:5672//',
    backend='db+sqlite:///results.sqlite3'
)
celery.conf.worker_hijack_root_logger = False

def container_exec_cmd(cmd, save_task_name = None, timeout = None):

    task_status = 'OK'

    timeout_flag, exitcode, result = simulator_api.utils.utils.subprocess_timeout_compliant(cmd, timeout = timeout)
    if timeout_flag:
        task_status = 'NOK'
        message = f"The command '{cmd}' timed out. Output: {result}."
        logging.info(message)
    elif exitcode != 0:
        task_status = 'NOK'
        message = f"The command '{cmd}' returned a non-zero exit status: {exitcode}. Output: {result}."
        logging.info(message)
    else:
        message = f"The command '{cmd}' ran succesfully. Output: {result}."
        logging.info(message)

    task_json = {
        'name': save_task_name,
        'timeout': timeout_flag,
        'exitcode': exitcode,
        'message': message
    }

    return result, task_status, task_json

@celery.task
def echo_topic(topic, timeout):
    """Handles topic echo inside the container."""

    cmd = f"ign topic -e -n 1 -t {topic}"
    _, _, task_json = container_exec_cmd(cmd, save_task_name = f"echo_{topic}", timeout = timeout)
    
    return task_json

@celery.task
def communication_test():
    """Handles communication test inside the container."""

    # initialize check list
    check_list = []

    # initialize command status
    status = 'OK'
    
    # Run communication smoke tests

    # Test sim to spawner communication through topic /test_from_sim (spawner must be listening to this topic)
    cmd = 'ign topic -p "data:\"test\"" -t /test_from_sim --msgtype ignition.msgs.StringMsg'
    _, task_status, task_json = container_exec_cmd(cmd, save_task_name = "simulation_to_spawner_communication")
    if task_status != 'OK': status = task_status
    check_list.append(task_json)

    # Test spawner to sim communication through topic /test_from_spawner (spawner must be publishing this topic)
    # change the timeout to be input
    cmd = f"ign topic -e -n 1 -t /test_from_spawner"
    _, task_status, task_json = container_exec_cmd(cmd, save_task_name = "spawner_to_simulator_communication", timeout = 5)
    if task_status != 'OK': status = task_status
    check_list.append(task_json)

    # Verify if ignition is launched and if not launch it with world empty
    # ign_command='pgrep -f "ign gazebo"'
    # timeout_flag, exitcode, result = simulator_api.utils.utils.subprocess_timeout_compliant(ign_command)
    # # if ignition is not running
    # if timeout_flag or exitcode != 0:
    #     message = f"Ignition is not running."
    #     logging.info(message)
    #     # launch ignition in thread
    #     ign_file = "/tmp/ign_output.logs"
    #     cmd = "ign gazebo -s empty.sdf -v"
    #     with open(ign_file, "w+") as output_file:
    #         ignition_process = simulator_api.utils.utils.subprocess_redirecting_stdout(cmd, output_file)

    #     # verify ignition is fully started
    #     log_to_wait_for = "Ignition"
    #     while not os.path.exists(ign_file): continue
    #     with open(ign_file, "r") as file:
    #         line = file.readline()
    #         while not log_to_wait_for in line: line = file.readline()
    #         logging.info(f"Ignition is running.")

    # Test that Ignition is running correctly (/clock, /stats)
    for topic in ["/clock","/stats"]:
        cmd = f"ign topic -e -n 1 -t {topic}"
        _, task_status, task_json = container_exec_cmd(cmd, save_task_name = f"ignition_running{topic.replace('/','_')}_check", timeout = 1)    
        if task_status != 'OK': status = task_status
        check_list.append(task_json)        
        
    # Test that a world is loaded correctly (/world/*/clock, /world/*/stats)
    # cmd = f"ign topic -l | grep 'world.*clock\|world.*stats'"
    # result = self.container_exec_cmd(cmd, save_task_name = "world_running") 
    # topic_names = result.decode('utf-8').strip().split('\n') if len(result.decode('utf-8')) > 0 else []
    world_name = os.environ.get('IGN_WORLD_NAME')
    topic_names = [f"/world/{world_name}/clock", f"/world/{world_name}/stats"]
    for topic in topic_names:
        cmd = f"ign topic -e -n 1 -t {topic}"
        _, task_status, task_json = container_exec_cmd(cmd, save_task_name = f"world_running{topic.replace('/','_')}_check", timeout = 1)  
        if task_status != 'OK': status = task_status
        check_list.append(task_json)          

    # if launched ignition stop it
    # if (timeout_flag or exitcode != 0):
    #     # Kill process
    #     ignition_process.terminate()
    #     # Delete the temporary file
    #     if os.path.exists(ign_file): os.remove(ign_file)

    return {'status' : status, 'checklist' : check_list}