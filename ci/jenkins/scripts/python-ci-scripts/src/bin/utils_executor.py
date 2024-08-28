"""Module for executing utils scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import time
import sys
from datetime import timedelta
import traceback
import click

from lib import utils
from lib import containers

# pylint: disable=redefined-builtin
from lib.decorators import dir
from lib.decorators import file
from lib.decorators import image
from lib.decorators import properties_file
from lib.decorators import log_verbosity_option
from lib.decorators import yaml_file
from lib.decorators import json_file

LOG = logging.getLogger(__name__)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for CI Script Executor."""


@cli.command()
@image
@file
@properties_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def get_dm_url_and_tag(image, file, properties_file, verbosity):
    """Set the DM tag from the file inputted and output to the properties file given."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='get_dm_version')
    LOG.info('Setting the Deployment Manager version')
    start_time = time.time()
    exit_code = 0
    try:
        utils.get_dm_url_and_tag_details(image, file, properties_file)
    except Exception as exception:
        LOG.error('Setting the Deployment Manager details failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Setting the Deployment Manager details completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@file
@dir
@properties_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def extract_tar_file(file, dir, properties_file, verbosity):
    """Extract a given tar file."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='extract_tar_file')
    LOG.info("Starting To Extract Tar file")
    start_time = time.time()
    exit_code = 0
    try:
        utils.extract_tar_file_and_archive_base_directory(file, dir, properties_file)
    except Exception as exception:
        LOG.error('Extract of tar the file failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Extract of the tar file completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def cleaning_up_workspace_from_properties_file(file, verbosity):
    """Clean workspace from details in property file using AM package manager (Internal Only)."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='cleaning_up_workspace_from_properties_file')
    LOG.info('Cleaning up charts: Using property file %s', file)
    start_time = time.time()
    exit_code = 0
    try:
        containers.cleaning_up_workspace_from_properties_file(file)
    except Exception as exception:
        LOG.error('Cleaning up charts within the workspace failed with the following error:')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Cleaning up charts completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@yaml_file
@json_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def convert_yaml_to_json(yaml_file, json_file, verbosity):
    """Convert a yaml file to a json file for further processing."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='convert_yaml_to_json')
    LOG.info('Converting %s yaml file to %s json file', yaml_file, json_file)
    start_time = time.time()
    exit_code = 0
    try:
        utils.convert_yaml_to_json(yaml_file, json_file)
    except Exception as exception:
        LOG.error('Converting yaml file to json file failed with the following error:')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Converting yaml file to json file completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
