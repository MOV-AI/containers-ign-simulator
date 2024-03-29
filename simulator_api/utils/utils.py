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
    mandatory_vars = ["topic_to_echo", "topic_to_publish", "ignition_base_topics", "world_name"]
    for var in mandatory_vars:
        if cfg.get("communication", var) is None:
            raise ValueError(f"Missing mandatory configuration variable: {var}")

    return cfg


def container_exec_cmd(cmd, timeout=None, checklist=None):
    """Executes a shell command, evaluates the response and generates a status

    Args:
        cmd (string): Command to run.
        timeout (int, optional): Duration of timeout for the command. Defaults to None.
        checklist (list, optional): list of task status.

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
        message = (
            f"The command '{cmd}' returned a non-zero exit status: {exitcode}. Output: {result}."
        )
        logging.debug(message)
    else:
        message = f"The command '{cmd}' ran succesfully. Output: {result}."
        logging.debug(message)

    task_json = {'command': cmd, 'status': task_status}
    if result and exitcode != 0:
        task_json['exitcode'] = exitcode
        task_json['output'] = result.decode()

    if checklist is not None:
        checklist.append(task_json)
        return checklist

    return task_json


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
            cmd,
            shell=True,
            executable="/bin/bash",
            check=True,
            capture_output=True,
            timeout=timeout,
        )

    except subprocess.TimeoutExpired:
        return True, 0, None

    except subprocess.CalledProcessError as e:
        return False, e.returncode, e.stdout + e.stderr

    return False, cmd_ret.returncode, cmd_ret.stdout
