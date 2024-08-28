"""Module for calling common commands."""

import subprocess
import logging
import os
import time

LOG = logging.getLogger(__name__)


class Response:
    """Holder class for exit status, stdout, and stderr."""

    def __init__(self, returncode, stdout, stderr=""):
        """Initialize Response object."""
        self.returncode = returncode
        self.stdout = stdout.strip()
        self.stderr = stderr

    def get_return_code(self):
        """Return return code."""
        return self.returncode

    def get_stdout(self):
        """Return stdout."""
        return self.stdout

    def get_stderr(self):
        """Return stderr."""
        return self.stderr


def __process_str(string, mask, verbose):
    """
    Process the response into a readable set of strings.

    Inputs:
        string : string to the be processed
        mask: Optional value if you want to obsecure a certain list of items i.e. password etc.
        verbose: Enable more debug logging if necessary

    Output:
        response with a readable string
    """
    response = ""
    for line in string.split("\n"):
        response = response + line + "\n"
        if verbose:
            _line = line
            if mask is not None:
                for item in mask:
                    _line = _line.replace(item, "****")
            LOG.debug(_line.strip())
    return response


# pylint: disable=too-many-arguments
def execute_command(cmd, mask, workspace=None, verbose=False, retry=0, sleep=10):
    """
    Execute commands on the command line.

    Inputs:
        cmd : Command to execute
        mask: list of values if you want to obsecure a certain list of items i.e. password etc.
        workspace: Where you wish to execute the command on
        verbose: Enable more debug logging if necessary
        retry: Can be used to set the number of times the command should be retried
        sleep: Can be used to set the duration to sleep between retries, default 10 seconds

    Output:
        result with the exit status, stdout, and stderr
    """
    _retry_count = int(retry) + 1
    if not workspace:
        workspace = os.getcwd()
    _cmd = cmd
    if mask:
        for item in mask:
            _cmd = cmd.replace(item, "****")
    LOG.info("Executing: %s", _cmd)
    response = ""
    stderr = ""
    while _retry_count > 0:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as proc:
            out, err = proc.communicate()
            response = __process_str(out.decode('utf-8'), mask, verbose)
            stderr = __process_str(err.decode('utf-8'), mask, verbose)

            if proc.returncode != 0:
                LOG.warning("Process exited with unexpected error code: %s", str(proc.returncode))
                if stderr != "":
                    LOG.warning(stderr)
                _retry_count -= 1
                if _retry_count > 0:
                    LOG.warning(f"Command {_cmd} failed, retry " +
                                f"{_retry_count} time(s) more."
                                f" Sleep {sleep} second")
                    time.sleep(sleep)
                    continue
            return Response(proc.returncode, response, stderr)
