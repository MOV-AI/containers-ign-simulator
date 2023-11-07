import subprocess
import simulator.utils.logger as logging

def subprocess_timeout_compliant(cmd, timeout = 1):

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

        if e.stdout:
            logging.info(f"{e.stdout.decode().strip()}\n")
            return 124, e.stdout
        if e.stderr:
            logging.info(f"{e.stderr.decode().strip()}\n")

        return True, None, None
    
    return False, exitcode, result
        


