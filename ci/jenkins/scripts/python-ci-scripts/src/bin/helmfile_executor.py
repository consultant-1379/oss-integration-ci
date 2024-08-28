"""Module for executing helmfile related scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import time
import os
import sys
from datetime import timedelta
import traceback
import click

from lib import check_helmfile_deployment_status
from lib import get_all_microservices_from_helmfile
from lib import get_details_from_helmfile
from lib import helmfile
from lib import utils
from lib import optionality

from lib.decorators import log_verbosity_option
from lib.decorators import output_file
from lib.decorators import input_file
from lib.decorators import execution_type
from lib.decorators import helmfile_path
from lib.decorators import helmfile_url
from lib.decorators import helmfile_name
from lib.decorators import chart_name
from lib.decorators import chart_version
from lib.decorators import chart_repo
from lib.decorators import username
from lib.decorators import user_password
from lib.decorators import user_token
from lib.decorators import state_values_file
from lib.decorators import get_all_images
from lib.decorators import fetch_charts
from lib.decorators import chart_cache_directory
from lib.decorators import kubeconfig_file
from lib.decorators import namespace
from lib.decorators import file
from lib.decorators import deployment_tag_list
from lib.decorators import optional_tag_list
from lib.decorators import check_tag_list
from lib.decorators import check_full_version
from lib.decorators import tags_set_to_true_only
from lib.decorators import filter_by_days_past
from lib.decorators import project_file_name
from lib.decorators import microservice_skip_list
from lib.decorators import optional_key_value_list
from lib.decorators import artifactory_username
from lib.decorators import artifactory_password


LOG = logging.getLogger(__name__)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for CI Helmfile Executor."""


@cli.command()
@helmfile_path
@project_file_name
@input_file
@output_file
@execution_type
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def get_base_baseline(path_to_helmfile, execution_type, project_file_name, input_file, output_file, verbosity):
    """Get app versions and names from the helmfile."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='get_base_baseline')
    LOG.info('Obtaining Base Baseline versions from the helmfile')
    start_time = time.time()
    exit_code = 0
    try:
        helmfile.get_base_baseline(path_to_helmfile, execution_type, project_file_name, input_file, output_file)
    except Exception as exception:
        LOG.error('Command failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@chart_name
@chart_version
@chart_repo
@user_password
@username
@user_token
@log_verbosity_option
# pylint: disable=redefined-outer-name, too-many-arguments, broad-except
def download_helmfile(chart_name, chart_version, chart_repo, username, user_password, verbosity, user_token=None):
    """Download a given helmfile according to the details given."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='download_helmfile')
    LOG.info("Starting To Download the Helmfile")
    start_time = time.time()
    exit_code = 0
    try:
        helmfile.download_helmfile(chart_name, chart_version, chart_repo, username, user_password, user_token)
    except Exception as exception:
        LOG.error('Download of the Helmfile failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Download of the Helmfile completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@get_all_images
@fetch_charts
@log_verbosity_option
@helmfile_url
@chart_cache_directory
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def get_release_details_from_helmfile(state_values_file, path_to_helmfile, get_all_images,
                                      fetch_charts, helmfile_url, chart_cache_directory, verbosity):
    """Get all the CSAR to be created according to the helmfile and state values passed."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='get_csar_details_from_helmfile')
    LOG.info("Starting To Get Details from Helmfile")
    start_time = time.time()
    exit_code = 0
    try:
        get_details_from_helmfile.fetch_helmfile_details(
            state_values_file, path_to_helmfile, get_all_images,
            fetch_charts, helmfile_url, chart_cache_directory)
    except Exception as exception:
        LOG.error('Get Details from Helmfile failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Get CSAR Details from Helmfile completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@kubeconfig_file
@namespace
@deployment_tag_list
@optional_tag_list
@optional_key_value_list
@check_tag_list
@check_full_version
@log_verbosity_option
# pylint: disable=redefined-outer-name, too-many-arguments, broad-except
def check_helmfile_deployment(path_to_helmfile, kubeconfig_file, namespace,
                              deployment_tag_list, optional_tag_list, optional_key_value_list,
                              check_tag_list, check_full_version, verbosity):
    """Verify existing releases against expected releases given a helmfile, state-values, and list of tags."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='check_helmfile_deployment')
    LOG.info("Starting To Check Helmfile Deployment")
    start_time = time.time()
    exit_code = 0
    try:
        check_helmfile_deployment_status.check_helmfile_deployment(
            path_to_helmfile, kubeconfig_file, namespace,
            deployment_tag_list, optional_tag_list,
            optional_key_value_list, check_tag_list, check_full_version)
    except Exception as exception:
        LOG.error('Check Helmfile Deployment failed with the following error')
        LOG.info(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Check Helmfile Deployment completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def get_microservice_details_from_helmfile(state_values_file, path_to_helmfile, verbosity):
    """Get all the CSAR to be created according to the helmfile and state values passed."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='get_all_microservices_from_helmfile')
    LOG.info("Starting To Get Micro Service Details from Helmfile Applications")
    start_time = time.time()
    exit_code = 0
    try:
        get_all_microservices_from_helmfile.fetch_microservice_details(
            state_values_file, path_to_helmfile)
    except Exception as exception:
        LOG.error('Get Microservice Details from Helmfile failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Get Microservice Details from Helmfile completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@username
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def compare_application_versions_from_helmfile(state_values_file, path_to_helmfile, username, user_password, verbosity):
    """Compare Application versions from a helmfile to the latest versions in the relevant repo."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='compare_application_versions_from_helmfile')
    LOG.info("Starting To Compare App versions from Helmfile Application")
    os.environ["FUNCTIONAL_USER_USERNAME"] = username
    os.environ["FUNCTIONAL_USER_PASSWORD"] = user_password
    start_time = time.time()
    exit_code = 0
    try:
        helmfile.compare_application_versions_in_helmfile(
            state_values_file, path_to_helmfile)
    except Exception as exception:
        LOG.error('Compare Application Versions from Helmfile failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Compare Application Versions from Helmfile completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@chart_repo
@helmfile_name
@filter_by_days_past
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def get_latest_helmfile_version(chart_repo, helmfile_name, filter_by_days_past, verbosity):
    """Get the latest helmfile version from the specified repo."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='get_latest_helmfile_version')
    LOG.info("Starting Get Latest Helmfile Version")
    start_time = time.time()
    exit_code = 0
    try:
        utils.get_latest_artifact_version_from_repo(chart_repo, helmfile_name,
                                                    filter_by_days_past)
    except Exception as exception:
        LOG.error('Get Latest Helmfile Version failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Get Latest Helmfile Version completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@tags_set_to_true_only
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def get_app_version_from_helmfile(state_values_file, path_to_helmfile, tags_set_to_true_only, verbosity):
    """Get app versions and names from the helmfile."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='get_app_version_from_helmfile')
    LOG.info('Obtaining app versions from the helmfile')
    start_time = time.time()
    exit_code = 0
    try:
        helmfile.get_app_version_from_helmfile(state_values_file, path_to_helmfile, tags_set_to_true_only)
    except Exception as exception:
        LOG.error('Getting app version from helmfile: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Get app version comleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@microservice_skip_list
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def get_shared_images(path_to_helmfile, microservice_skip_list, verbosity):
    """Get the shared images within a helmfile."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='get_shared_images')
    LOG.info('Obtaining the shared images within the helmfile')
    start_time = time.time()
    exit_code = 0
    try:
        get_all_microservices_from_helmfile.get_shared_images(path_to_helmfile, microservice_skip_list)
    except Exception as exception:
        LOG.error('Obtaining the shared images failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Obtaining the shared images completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@file
@username
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def populate_repository_credentials(file, username, user_password, verbosity):
    """Update repository yaml file with credentials for entries where none are provided."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='populate_repository_credentials')
    LOG.info('Populate Repository Credentials: Updating repository yaml file %s', file)
    start_time = time.time()
    exit_code = 0
    try:
        utils.populate_repository_credentials_in_file(file, username, user_password)
    except Exception as exception:
        LOG.error('Populate Repository Credentials: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Populate Repository Credentials completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@chart_cache_directory
@artifactory_username
@artifactory_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def generate_optionality_maximum(state_values_file, path_to_helmfile, chart_cache_directory, artifactory_username,
                                 artifactory_password, verbosity):
    """Generate an optionality_maximuml.yaml."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='generate_optionality_maximum')
    LOG.info('Generating the optionality_maximum.yaml file')
    os.environ["GERRIT_USERNAME"] = artifactory_username
    os.environ["GERRIT_PASSWORD"] = artifactory_password
    start_time = time.time()
    exit_code = 0
    try:
        optionality.generate_optionality_maximum(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile,
                                                 chart_cache_directory=chart_cache_directory)
    except Exception as exception:
        LOG.error('Generating the optionality_maximum.yaml file failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Generating the optionality_maximum.yaml file completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@chart_name
@chart_version
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def check_helmfile_versions_against_given_versions(state_values_file, path_to_helmfile,
                                                   chart_name, chart_version, verbosity):
    """Check helmfile versions against given versions."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='check_helmfile_versions')
    LOG.info('Checking helmfile versions against the versions provided')
    start_time = time.time()
    exit_code = 0
    try:
        helmfile.check_helmfile_versions_for_snapshot_build(state_values_file, path_to_helmfile,
                                                            chart_name, chart_version)
    except Exception as exception:
        LOG.error('Checking the helmfile versions failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Checking the helmfile versions completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
