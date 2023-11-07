import subprocess
import simulator_api.utils.logger as logging

def subprocess_timeout_compliant(cmd, timeout = None):

    try:
        # Compliant: makes sure to terminate the child process when
        # the timeout expires.

        cmd_ret = subprocess.run(
                                    f"{cmd}",
                                    shell=True,
                                    executable="/bin/bash",
                                    check=True,
                                    capture_output=True,
                                    timeout=timeout,
                                )

        result = cmd_ret.stdout
        exitcode = cmd_ret.returncode

    except subprocess.TimeoutExpired as e:

        return True, None, None
    
    return False, exitcode, result
        


