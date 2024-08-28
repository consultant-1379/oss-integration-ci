"""Module for executing site values related scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import time
import sys
import os
from datetime import timedelta
import traceback
import click

from lib import merge_files
from lib import site_values
from lib import utils

from lib.decorators import log_verbosity_option
from lib.decorators import path_base_yaml
from lib.decorators import path_override_yaml
from lib.decorators import path_output_yaml
from lib.decorators import check_values_only
from lib.decorators import file
from lib.decorators import optional_key_value_list
from lib.decorators import state_values_file
from lib.decorators import output_state_values_file
from lib.decorators import deployment_tag_list
from lib.decorators import optional_tag_list

LOG = logging.getLogger(__name__)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for Site Values Management."""


@cli.command()
@path_base_yaml
@path_override_yaml
@path_output_yaml
@check_values_only
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def merge_yaml_files(path_base_yaml, path_override_yaml, path_output_yaml, check_values_only,
                     verbosity):
    """Merge the base chart with the override file and output to new file."""
    workdir = "/ci-scripts/"
    logs_sub_directory = "output-files/ci-script-executor-logs"
    filename_postfix = "merge_yaml_files"
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory=workdir,
        logs_sub_directory=logs_sub_directory,
        filename_postfix=filename_postfix)
    LOG.info("Starting To Merge Files")
    start_time = time.time()
    exit_code = 0
    try:
        merge_files.merge_files_create_new_output_file(
            path_base_yaml, path_override_yaml, path_output_yaml, check_values_only)
    except Exception as exception:
        LOG.error('Merge of files failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        utils.log_string_to_a_file_as_variable(os.path.join(workdir, logs_sub_directory),
                                               "ERROR_" + filename_postfix + ".properties",
                                               exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Merge of Files completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@output_state_values_file
@deployment_tag_list
@optional_tag_list
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def update_site_values_file_enable_tags(state_values_file, output_state_values_file, deployment_tag_list,
                                        optional_tag_list, verbosity):
    """Output a site-values file using a site-values base file and a list of tags to update."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='update_site_values_file_enable_tags')
    LOG.info("Starting To Create Updated Site-values File")
    start_time = time.time()
    exit_code = 0
    try:
        utils.write_new_site_values_file_with_tags(state_values_file, output_state_values_file,
                                                   deployment_tag_list, optional_tag_list)
    except Exception as exception:
        LOG.error('Create Updated Site-values File failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Updated Site-values File completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def replacing_password(state_values_file, verbosity):
    """Obfuscating Functional Password in state_values_file."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='replacing_password')
    LOG.info("Starting to Obfuscate Password")
    start_time = time.time()
    exit_code = 0
    try:
        site_values.obfuscate_registry_password(state_values_file)
    except Exception as exception:
        LOG.error('Obfuscating Password has failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Obfuscating Password has completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@deployment_tag_list
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def set_deployment_tags(state_values_file, deployment_tag_list, verbosity):
    """Set the deployment tags according to the list inputted."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='set_deployment_tags')
    LOG.info("Starting to set the deployment tags")
    start_time = time.time()
    exit_code = 0
    try:
        site_values.set_deployment_tags(state_values_file, deployment_tag_list)
    except Exception as exception:
        LOG.error('Setting the deployment tags failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Set deployment tags completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def substitute_values(state_values_file, file, verbosity):
    """Substitute placeholder variables contained in a config file into a site values file."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='substitute_values')
    LOG.info('Substitute Values: Checking Content of config file %s', file)
    start_time = time.time()
    exit_code = 0
    try:
        if file != "default":
            utils.substitute_values_in_file(state_values_file, file)
        else:
            LOG.info('Substitute Values: No file detected. No Substitution was performed.')
    except Exception as exception:
        LOG.error('Substitute Values: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Substitute Values completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@optional_key_value_list
@path_output_yaml
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def create_site_values_file(optional_key_value_list, path_output_yaml, verbosity):
    """Create a new site values file from a comma separated string of keys with unique values."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='create_site_values_file')
    LOG.info("Creating new site values file.")
    start_time = time.time()
    exit_code = 0
    try:
        site_values.create_site_values_file(optional_key_value_list, path_output_yaml)
    except Exception as exception:
        LOG.error('Creating the site values file failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Site values file created successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
