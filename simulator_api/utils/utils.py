import os
import subprocess
import configparser
from pathlib import Path
import simulator_api.utils.logger as logging


def parse_config():
    """Function to parse configuration file

    Returns:
        configParser: Configuration object containing all config variables
    """

    cfg = configparser.ConfigParser()

    # Read the configuration file
    path = Path(__file__)
    ROOT_DIR = os.path.dirname(path.parent.absolute())
    config_path = os.path.join(ROOT_DIR, "config.ini")
    logging.debug(f"Configuration file : {config_path}")
    cfg.read(config_path)

    # Check mandatory configuration variables
    mandatory_vars = ["topic_spawner", "topic_sim", "ignition_base_topics", "world_name"]
    for var in mandatory_vars:
        if cfg.get("communication", var) is None:
            raise ValueError(f"Missing mandatory configuration variable: {var}")

    return cfg


def container_exec_cmd(cmd, save_task_name=None, timeout=None):
    """Executes a shell command, evaluates the response and generates a status

    Args:
        cmd (string): Command to run.
        save_task_name (string, optional): Name tag to identify the operation. Defaults to None.
        timeout (int, optional): Duration of timeout for the command. Defaults to None.

    Returns:
        result (string): stdout of the operation
        task_status (string): state tag 'SUCCESS', 'ERROR' or 'TIMEOUT'
        task_json (json): dictionary describing the operation in detail
    """

    task_status = 'SUCCESS'

    timeout_flag, exitcode, result = subprocess_timeout_compliant(cmd, timeout=timeout)
    if timeout_flag:
        task_status = 'TIMEOUT'
        message = f"The command '{cmd}' timed out. Output: {result}."
        logging.debug(message)
    elif exitcode != 0:
        task_status = 'ERROR'
        message = f"The command '{cmd}' returned a non-zero exit status: {exitcode}. Output: {result}."
        logging.debug(message)
    else:
        message = f"The command '{cmd}' ran succesfully. Output: {result}."
        logging.debug(message)

    task_json = {'name': save_task_name, 'status': task_status, 'message': message}

    return result, task_status, task_json


def subprocess_timeout_compliant(cmd, timeout=None):
    """Performs a subprocess for a given timeout and terminates the process at the end of the timeout.

    Args:
        cmd (string): Command to be executed
        timeout (int, optional): Timeout duration for the process to be executed. Defaults to None.

    Returns:
        timeout_flag (bool): Flag to identify if a process has timed out.
        exitcode (int): Exitcode of the process.
        result (string): Stdout output of the process.
    """

    try:
        # Compliant: makes sure to terminate the child process when
        # the timeout expires.

        cmd_ret = subprocess.run(
            cmd, shell=True, executable="/bin/bash", check=True, capture_output=True, timeout=timeout
        )

        result = cmd_ret.stdout
        exitcode = cmd_ret.returncode

    except subprocess.TimeoutExpired:

        return True, None, None

    except subprocess.CalledProcessError as e:

        return False, e.returncode, e.stdout

    return False, exitcode, result
