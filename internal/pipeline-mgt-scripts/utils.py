"""This module contains a list of utility functions."""

from datetime import datetime
import logging
import os
import subprocess
from pathlib import Path

LOG = logging.getLogger(__name__)


def get_log_level_from_verbosity(verbosity):
    """
    Return a log level based on a given verbosity number.

    Input:
        verbosity: Verbosity number (0-4) that maps to a log-level property
    """
    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG
    }
    return log_levels.get(verbosity, "Invalid verbosity level")


def initialize_logging(verbosity, working_directory, logs_sub_directory, filename_postfix):
    """
    Initialize the logging to standard output and standard out at different verbosities.

    Returns
    -------
        Log file path relative to the working directory.

    """
    log_format = "[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s"
    absolute_log_directory = Path(working_directory) / Path(logs_sub_directory)
    absolute_log_directory.mkdir(parents=True, exist_ok=True)
    # pylint: disable=consider-using-f-string
    relative_log_file_path = str(Path(logs_sub_directory) / datetime.now().strftime(
        '%Y-%m-%dT%H_%M_%S%z_{0}.log'.format(filename_postfix))
                                 )
    absolute_log_file_path = str(Path(working_directory) / Path(relative_log_file_path))
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))
    stream_handler.setLevel(get_log_level_from_verbosity(verbosity))
    logging.basicConfig(filename=absolute_log_file_path, format=log_format, level=logging.DEBUG)
    logging.getLogger('').addHandler(stream_handler)
    logging.getLogger("kubernetes").setLevel(logging.INFO)
    return relative_log_file_path


def str_to_bool(input_str):
    """Return True if string converts to a true-like value."""
    return input_str.lower() in ("yes", "true")


def join_command_stdout_and_stderr(command):
    """
    Return a string joining the standard output and standard error strings from a command object.

    Input:
        command: Subprocess command object
    """
    returned_string = ''
    decoded_stdout = command.stdout.decode('utf-8')
    decoded_stderr = command.stderr.decode('utf-8')
    if decoded_stdout != "":
        returned_string += decoded_stdout
    if decoded_stdout != "" and decoded_stderr != "":
        returned_string += "\n"
    if decoded_stderr != "":
        returned_string += decoded_stderr
    return returned_string


def run_cli_command(command_and_args_list, **subprocess_run_options):
    """
    Run the given cli command and arguments through pythons subprocess run, with the given options.

    Input:
        command_and_args_list: List of commands to execute
        **subprocess_run_options: Optional key/value parameters for subprocess call
    """
    LOG.debug('Adding all environment variables from the image, to the subprocess.run env variables')
    if 'env' not in subprocess_run_options:
        subprocess_run_options['env'] = {}
    subprocess_run_options['env'] = {**subprocess_run_options['env'], **dict(os.environ.items())}
    LOG.debug('Running the following cli command: %s', ' '.join(command_and_args_list))
    # pylint: disable=subprocess-run-check
    return subprocess.run(command_and_args_list, **subprocess_run_options)
