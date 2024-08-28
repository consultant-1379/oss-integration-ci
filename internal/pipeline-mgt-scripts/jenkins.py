"""Module for Jenkins operations."""
import logging
import os
import subprocess
import utils
import errors

LOG = logging.getLogger(__name__)
LR_BIN = "/usr/local/bin/lockable-resources"
JENKINS_DEFAULT_URL = "https://fem8s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/"


def run_lr_command(*lr_args):
    """
    Execute a lockable-resources command.

    Input:
        *lr_args: List of LR command arguments

    Returns
    -------
        Command object

    """
    if 'JENKINS_URL' not in os.environ:
        os.environ['JENKINS_URL'] = JENKINS_DEFAULT_URL
    if 'JENKINS_USER' not in os.environ:
        raise errors.MissingEnvVarError("Missing environment variable JENKINS_USER")
    if 'JENKINS_TOKEN' not in os.environ:
        raise errors.MissingEnvVarError("Missing environment variable JENKINS_TOKEN")
    command_and_args_list = [LR_BIN]
    command_and_args_list.extend(lr_args)
    command = utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command


def get_lockable_resource_cluster_list():
    """
    Get list of all clusters associated with lockable resources.

    Input:
        None

    Output:
        Lists lockable resources and returns / outputs list to a file
    """
    lr_list = run_lr_command('list')
    if lr_list.returncode == 0:
        entries = lr_list.stdout.decode('utf-8').split("\n")
        ret_list = []
        for entry in entries:
            entry = entry.strip().split("_")[0].lower()
            if entry != "" and entry not in ret_list:
                ret_list.append(entry)
        LOG.info("Clusters:")
        cluster_list = ",".join(ret_list)
        LOG.info(cluster_list)
        with open("/pipeline-mgt-scripts/output-files/lr_cluster_list", "w", encoding="utf-8") as output_list_file:
            output_list_file.write(cluster_list)
        return cluster_list
    LOG.error(lr_list.stderr.decode('utf-8'))
    raise errors.LRCLIError("Error listing lockable resources")
