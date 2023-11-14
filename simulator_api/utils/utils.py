import subprocess
import simulator_api.utils.logger as logging

def subprocess_timeout_compliant(cmd, timeout = None):
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
                                    timeout=timeout
                                )

        result = cmd_ret.stdout
        exitcode = cmd_ret.returncode

    except subprocess.TimeoutExpired as e:

        return True, None, None
    
    except subprocess.CalledProcessError as e:

        return False, e.returncode, e.stdout
    
    return False, exitcode, result
        


