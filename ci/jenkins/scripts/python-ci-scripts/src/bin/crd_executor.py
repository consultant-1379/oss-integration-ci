"""Module for executing crd related scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import time
import sys
from datetime import timedelta
import traceback
import os
import click

from lib import crds
from lib import helmfile
from lib import kubectl
from lib import utils

# pylint: disable=redefined-builtin
from lib.decorators import dir
from lib.decorators import log_verbosity_option
from lib.decorators import chart_name
from lib.decorators import chart_version
from lib.decorators import chart_repo
from lib.decorators import image
from lib.decorators import helmfile_path
from lib.decorators import kubeconfig_file
from lib.decorators import namespace


LOG = logging.getLogger(__name__)


def username(func):
    """Set a decorator for the username."""
    return click.option('--username', 'username', envvar='GERRIT_USERNAME', required=True, type=str,
                        help='This is the username to log into Artifactory. This can also be set as an environment '
                             'variable, GERRIT_USERNAME, if extra security is needed'
                        )(func)


def password(func):
    """Set a decorator for the password."""
    return click.option('--password', 'password', envvar='GERRIT_PASSWORD', required=True, type=str,
                        help='This is the user password to log into Artifactory, This can also be set as an '
                             'environment variable, GERRIT_PASSWORD, if extra security is needed'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for CRD Management."""


@cli.command()
@helmfile_path
@chart_name
@chart_version
@chart_repo
@image
@username
@password
@log_verbosity_option
# pylint: disable=redefined-outer-name, too-many-arguments, broad-except
def get_crd_details_from_chart(path_to_helmfile, chart_name, chart_version, chart_repo, image, username, password,
                               verbosity):
    """Retrieve CRD details from a chart and generate a new property file with chart details."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='get_crd_details_from_chart')
    LOG.info("Starting To Check for CRD details within helm chart")
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
    start_time = time.time()
    exit_code = 0
    try:
        crds.compile_crd_details_from_app_chart(
            path_to_helmfile, chart_name, chart_version, chart_repo, image)
    except Exception as exception:
        LOG.error('Check for CRD details failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Check for CRD details completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def update_crds_helmfile(path_to_helmfile, verbosity):
    """Update releases in the crds-helmfile with 'installed: true', if the release is dependent on certain 'tags'."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='update_crds_helmfile')
    LOG.info("Updating crds-helmfile.yaml...")
    start_time = time.time()
    exit_code = 0
    try:
        helmfile.update_crd_helmfile(path_to_helmfile)
    except Exception as exception:
        LOG.error('crds-helmfile.yaml file update failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('crds-helmfile.yaml file update completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def remove_crd_components(namespace, kubeconfig_file, verbosity):
    """Delete CRD components."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_crd_components')
    LOG.info('Deleting EO and EIAE CRD components together to completely clean the cluster')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_crds(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Deleting CRD namespace failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('CRD components deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@dir
@image
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def check_crs_from_templates_dir(dir, image, verbosity):
    """Validate CRD manifests from a specified directory using Kubeconform."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='test_crs_from_templates_dir')
    LOG.info('Analyzing CRD and CR template files...')
    start_time = time.time()
    exit_code = 0
    try:
        crds.check_crs_from_templates_dir(dir, image)
    except Exception as exception:
        LOG.error('Analyzing CRD and CR template files failed with following errors')
        LOG.info(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Analyzing CRD and CR template files completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
