"""Module for executing scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import time
import sys
import os
from datetime import timedelta
import traceback
import click

from lib import csar
from lib import get_details_from_helmfile
from lib import get_all_microservices_from_helmfile
from lib import download_existing_csars
from lib import registry
from lib import site_values
from lib import merge_files
from lib import check_helmfile_deployment_status
from lib import utils
from lib import crds
from lib import helm
from lib import helmfile
from lib import kubectl
from lib import containers
from lib import optionality

# pylint: disable=redefined-builtin
from lib.decorators import dir
from lib.decorators import log_verbosity_option
from lib.decorators import csar_repo_option
from lib.decorators import applications_to_check_option
from lib.decorators import manifest_file
from lib.decorators import images_file
from lib.decorators import artifact_url
from lib.decorators import chart_name
from lib.decorators import chart_version
from lib.decorators import chart_repo
from lib.decorators import state_values_file
from lib.decorators import kubeconfig_file
from lib.decorators import namespace
from lib.decorators import release_name
from lib.decorators import ignore_exists
from lib.decorators import dockerconfig_file
from lib.decorators import secret_name
from lib.decorators import cluster_role
from lib.decorators import service_account
from lib.decorators import from_literals
from lib.decorators import resource_name
from lib.decorators import retries
from lib.decorators import docker_auth_config
from lib.decorators import flow_area
from lib.decorators import cluster_name
from lib.decorators import path_base_yaml
from lib.decorators import path_override_yaml
from lib.decorators import path_output_yaml
from lib.decorators import check_values_only
from lib.decorators import file
from lib.decorators import output_state_values_file
from lib.decorators import helmfile_path
from lib.decorators import helmfile_url
from lib.decorators import helmfile_name
from lib.decorators import helmfile_version
from lib.decorators import helmfile_repo
from lib.decorators import username
from lib.decorators import user_id
from lib.decorators import user_password
from lib.decorators import user_token
from lib.decorators import get_all_images
from lib.decorators import fetch_charts
from lib.decorators import chart_cache_directory
from lib.decorators import deployment_tag_list
from lib.decorators import optional_tag_list
from lib.decorators import check_tag_list
from lib.decorators import check_full_version
from lib.decorators import tags_set_to_true_only
from lib.decorators import filter_by_days_past
from lib.decorators import image
from lib.decorators import message
from lib.decorators import name
from lib.decorators import git_repo_local
from lib.decorators import gerrit_branch
from lib.decorators import gerrit_change_number
from lib.decorators import timeout
from lib.decorators import properties_file
from lib.decorators import create_tickets
from lib.decorators import skip_list
from lib.decorators import microservice_skip_list

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
def get_dm_url_and_tag(image, file, properties_file, verbosity):    # pragma: no cover
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
@image
@message
@git_repo_local
@gerrit_branch
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def generate_gerrit_patch(image, message, git_repo_local, gerrit_branch, verbosity):    # pragma: no cover
    """Generate Gerrit Review."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='generate_gerrit_patch')
    LOG.info('Generate a Gerrit Review for the inputted Repo')
    start_time = time.time()
    exit_code = 0
    try:
        containers.run_gerrit_create_patch(image, message, git_repo_local, gerrit_branch)
    except Exception as exception:
        LOG.error('Gerrit patch creation failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Gerrit patch creation completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@image
@timeout
@gerrit_change_number
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def check_gerrit_review_submittable(image, gerrit_change_number, timeout, verbosity):   # pragma: no cover
    """Generate Gerrit Review."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='check_gerrit_review_submittable')
    LOG.info('Checking Gerrit Review to see if submittable')
    start_time = time.time()
    exit_code = 0
    try:
        containers.check_gerrit_review_submittable(image, gerrit_change_number, timeout)
    except Exception as exception:
        LOG.error('Check for Gerrit Review to see if submittable, failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Gerrit Review submittable check completed successfully')
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
def extract_tar_file(file, dir, properties_file, verbosity):    # pragma: no cover
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
@chart_name
@chart_version
@chart_repo
@user_password
@username
@user_token
@log_verbosity_option
# pylint: disable=redefined-outer-name, too-many-arguments, broad-except, duplicate-code
def download_helmfile(chart_name, chart_version, chart_repo, username, user_password,
                      verbosity, user_token=None):  # pragma: no cover
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
@helmfile_path
@chart_name
@chart_version
@chart_repo
@image
@log_verbosity_option
# pylint: disable=redefined-outer-name, too-many-arguments, broad-except, duplicate-code
def get_crd_details_from_chart(path_to_helmfile, chart_name, chart_version, chart_repo, image,
                               verbosity):      # pragma: no cover
    """Download a given helm chart.

    Used to download a given helm chart according to the details given.
    Uses helm repo add and helm pull to retrieve the chart.
    """
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='get_crd_details_from_chart')
    LOG.info("Starting To Check for CRD details within helm chart")
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
@path_base_yaml
@path_override_yaml
@path_output_yaml
@check_values_only
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def merge_yaml_files(path_base_yaml, path_override_yaml, path_output_yaml, check_values_only,
                     verbosity):    # pragma: no cover
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
@helmfile_path
@get_all_images
@fetch_charts
@log_verbosity_option
@helmfile_url
@chart_cache_directory
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def get_release_details_from_helmfile(state_values_file, path_to_helmfile, get_all_images, fetch_charts,
                                      helmfile_url, chart_cache_directory, verbosity):    # pragma: no cover
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
@check_tag_list
@check_full_version
@log_verbosity_option
# pylint: disable=redefined-outer-name, too-many-arguments, broad-except, duplicate-code
def check_helmfile_deployment(path_to_helmfile, kubeconfig_file, namespace,
                              deployment_tag_list, optional_tag_list, check_tag_list,
                              check_full_version, verbosity):   # pragma: no cover
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
            deployment_tag_list, optional_tag_list, check_tag_list, check_full_version)
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
@output_state_values_file
@deployment_tag_list
@optional_tag_list
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def create_site_values_file_with_tag_updates(state_values_file, output_state_values_file, deployment_tag_list,
                                             optional_tag_list, verbosity):     # pragma: no cover
    """Output a site-values file using a site-values base file and a list of tags to update."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='create_site_values_file_with_tag_updates')
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
@helmfile_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def get_microservice_details_from_helmfile(state_values_file, path_to_helmfile, verbosity):     # pragma: no cover
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
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def compare_application_versions_from_helmfile(state_values_file, path_to_helmfile, verbosity):     # pragma: no cover
    """Compare Application versions from a helmfile to the latest versions in the relevant repo."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='compare_application_versions_from_helmfile')
    LOG.info("Starting To Compare App versions from Helmfile Application")
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
@state_values_file
@helmfile_path
@chart_name
@chart_repo
@chart_version
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def compare_microservice_versions_from_application(state_values_file, path_to_helmfile, chart_name, chart_repo,
                                                   chart_version, verbosity):   # pragma: no cover
    """Compare Microservice versions from a chart to the latest versions in the relevant repo."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='compare_microservice_versions_from_application')
    LOG.info("Starting To compare Microservice versions from the Application")
    start_time = time.time()
    exit_code = 0
    try:
        get_all_microservices_from_helmfile.compare_microservice_versions_in_application(
            state_values_file, path_to_helmfile, chart_name, chart_repo, chart_version)
    except Exception as exception:
        LOG.error('Compare Microservice Versions from Application failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Compare Microservice Versions from Application completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@csar_repo_option
@applications_to_check_option
@log_verbosity_option
# pylint: disable=broad-except
def check_for_existing_csar(csar_repo_url, applications_to_check, verbosity):   # pragma: no cover
    """Check a specific CSAR repo for a CSAR with a matching version to avoid duplication during CSAR build."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='check_for_existing_csar')
    LOG.info("Starting Check For Existing CSARs")
    start_time = time.time()
    exit_code = 0
    try:
        csar.check_for_existing_csars_in_repo(csar_repo_url, applications_to_check)
    except Exception as exception:
        LOG.error('Check For Existing CSARs failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Check For Existing CSARs completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@csar_repo_option
@applications_to_check_option
@log_verbosity_option
# pylint: disable=broad-except
def download_existing_csar(csar_repo_url, applications_to_check, verbosity):    # pragma: no cover
    """Download the officially built CSAR from the CSAR REPO."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='download_existing_csar')
    LOG.info("Starting Download of CSARs")
    start_time = time.time()
    exit_code = 0
    try:
        download_existing_csars.download_existing_csars_from_repo(csar_repo_url, applications_to_check)
    except Exception as exception:
        LOG.error('Download of existing CSARs failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Download of existing CSARs completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def replacing_password(state_values_file, verbosity):   # pragma: no cover
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
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def set_deployment_tags(state_values_file, deployment_tag_list, verbosity):     # pragma: no cover
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
@chart_repo
@helmfile_name
@filter_by_days_past
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def get_latest_helmfile_version(chart_repo, helmfile_name, filter_by_days_past, verbosity):     # pragma: no cover
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
@namespace
@kubeconfig_file
@name
@user_id
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def check_and_create_internal_registry_secret(namespace, kubeconfig_file, name,
                                              user_id, user_password, verbosity):   # pragma: no cover
    """Set registry secret if none exists."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='check_and_create_internal_registry_secret')
    LOG.info("Creating the internal Registry for EVNFM Pre Deployment step")
    start_time = time.time()
    exit_code = 0
    try:
        registry.create_internal_registry_secret(namespace, kubeconfig_file, name,
                                                 user_id, user_password)
    except Exception as exception:
        LOG.error('Create Internal Registry failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Internal Registry completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def substitute_values(state_values_file, file, verbosity):  # pragma: no cover
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
@namespace
@kubeconfig_file
@ignore_exists
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def create_namespace(namespace, kubeconfig_file, ignore_exists, verbosity):     # pragma: no cover
    """Create namespace if it doesn't exist, and otherwise fail unless ignore flag is set."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_namespace')
    LOG.info('Create Namespace: Namespace to create is %s', namespace)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.check_and_create_namespace(namespace, kubeconfig_file, ignore_exists)
    except Exception as exception:
        LOG.error('Create Namespace: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Namespace completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@secret_name
@kubeconfig_file
@dockerconfig_file
@ignore_exists
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def create_namespace_secret(namespace, secret_name, kubeconfig_file, dockerconfig_file,
                            ignore_exists, verbosity):  # pragma: no cover
    """Create namespace secret, fail the build if ignor-test is set to false and the secret already exists."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_namespace_secret')
    LOG.info('Create Namespace Secret: %s', secret_name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.check_and_create_namespace_secret(namespace, secret_name, kubeconfig_file,
                                                  dockerconfig_file, ignore_exists)
    except Exception as exception:
        LOG.error('Create Namespace Secret: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Namespace Secret completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def delete_namespace(namespace, kubeconfig_file, verbosity):    # pragma: no cover
    """Delete namespace if it exists."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_namespace')
    LOG.info('Delete Namespace: Namespace to delete is %s', namespace)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_namespace(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Delete Namespace: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Delete Namespace completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def cleaning_up_workspace_from_properties_file(file, verbosity):    # pragma: no cover
    """Clean workspace from details in property file using AM package manager."""
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
@file
@username
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def populate_repository_credentials(file, username, user_password, verbosity):  # pragma: no cover
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
@name
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def create_service_account(name, namespace, kubeconfig_file, verbosity):    # pragma: no cover
    """Create a service account resource."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_service_account')
    LOG.info('Create Service Account: Creating resource with name %s', name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_service_account(name, namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Create Service Account: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Service Account completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@kubeconfig_file
@namespace
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def remove_releases(namespace, kubeconfig_file, verbosity):     # pragma: no cover
    """Remove releases from a given namespace."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='removing_helm_releases_from_namespace')
    LOG.info("Removing Releases from the specified Namespace:")
    start_time = time.time()
    exit_code = 0
    try:
        helm.removing_helm_releases_from_namespace(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Removing releases has failed with the following error:')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Removing Releases has completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@name
@release_name
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def create_privileged_policy_cluster_role(name, release_name, namespace,
                                          kubeconfig_file, verbosity):   # pragma: no cover
    """Create a cluster role resource with a privileged policy."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_privileged_policy_cluster_role')
    LOG.info('Create Privileged Policy Cluster Role: Resource name to create is %s', name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_privileged_policy_cluster_role(name, release_name, namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Create Privileged Policy Cluster Role: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Privileged Policy Cluster Role completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@secret_name
@from_literals
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def create_generic_secret_from_literals(namespace, kubeconfig_file, secret_name,
                                        from_literals, verbosity):  # pragma: no cover
    """Set generic secret if none exists."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_generic_secret_from_literals')
    LOG.info("Creating the Generic Secret...")
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_generic_secret_from_literals(namespace, kubeconfig_file,
                                                    secret_name, from_literals)
    except Exception as exception:
        LOG.error('Create Generic Secret failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Generic Secret completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@kubeconfig_file
@cluster_role
@service_account
@name
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def create_cluster_rolebinding(kubeconfig_file, name,
                               cluster_role, service_account, verbosity):   # pragma: no cover
    """Create a cluster rolebinding."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='cleate_cluster_rolebinding')
    LOG.info("Creating Cluster Rolebinding %s", name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_cluster_rolebinding(kubeconfig_file,
                                           name, cluster_role,
                                           service_account)
    except Exception as exception:
        LOG.error('Create Cluster Rolebinding failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Cluster Rolebinding completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@name
@file
@resource_name
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_resource_with_yaml_file(namespace, kubeconfig_file, name,
                                   file, resource_name, verbosity):  # pragma: no cover
    """Create a resource with a YAML file."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_resource_with_file')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_resource_with_yaml_file(namespace, kubeconfig_file, name, file, resource_name)
    except Exception as exception:
        LOG.error('Creating a resource with a YAML file failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Creating a resource with a YAML file completed successfully')
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
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def get_app_version_from_helmfile(state_values_file, path_to_helmfile,
                                  tags_set_to_true_only, verbosity):   # pragma: no cover
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
@manifest_file
@images_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def combine_csar_build_info(manifest_file, images_file, verbosity):  # pragma: no cover
    """Combine the information from a CSAR's manifest.txt and images.txt."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='combine_csar_build_info')
    LOG.info("Combining the manifest.txt and images.txt information...")
    start_time = time.time()
    exit_code = 0
    try:
        csar.combine_csar_build_info(manifest_file, images_file)
    except Exception as exception:
        LOG.error('Combining the manifest.txt and images.txt files failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Combining the manifest.txt and images.txt files completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@state_values_file
@chart_name
@chart_version
@helmfile_name
@helmfile_version
@helmfile_repo
@chart_cache_directory
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def compare_csar_and_helmfile_images(chart_name, chart_version, path_to_helmfile, state_values_file,
                                     helmfile_name, helmfile_version, helmfile_repo, chart_cache_directory, verbosity):
    # pragma: no cover
    """Compare images contained within a CSAR to those within a helmfile."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='examine_csar_images')
    LOG.info("Starting a comparison of the images contained within the CSAR and the helmfile template")
    start_time = time.time()
    exit_code = 0
    try:
        csar.compare_csar_and_helmfile_images(chart_name, chart_version, path_to_helmfile, state_values_file,
                                              helmfile_name, helmfile_version, helmfile_repo, chart_cache_directory)
    except Exception as exception:
        LOG.error('The images comparison failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Image comparison completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def update_crds_helmfile(path_to_helmfile, verbosity):  # pragma: no cover
    """Update the crds-helmfile.yaml file."""
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
@kubeconfig_file
@namespace
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def remove_sep_release(namespace, kubeconfig_file, verbosity):  # pragma: no cover
    """Remove sep helm release from a given namespace."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='remove_sep_release')
    LOG.info("Removing SEP Helm Release from the specified Namespace:")
    start_time = time.time()
    exit_code = 0
    try:
        helm.removing_sep_release_from_namespace(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Removing SEP Helm Release has failed with the following error:')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Removing SEP Helm Release has completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def remove_crd_components(namespace, kubeconfig_file, verbosity):   # pragma: no cover
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
@namespace
@kubeconfig_file
@timeout
@retries
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def wait_for_persistent_volumes_deletion(namespace, kubeconfig_file, timeout, retries, verbosity):  # pragma: no cover
    """Wait for Persistent Volumes Deletion."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='wait_for_persistent_volumes')
    LOG.info('Waiting for Persistent Volumes Deletion to complete')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.wait_for_persistent_volumes_deletion(namespace, kubeconfig_file, timeout, retries)
    except Exception as exception:
        LOG.error('Waiting for Persistent Volumes Deletion failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Persistent Volumes Deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def remove_cluster_roles(namespace, kubeconfig_file, verbosity):    # pragma: no cover
    """Delete Cluster roles."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_cluster_roles')
    LOG.info('Deleting cluster roles to completely clean the cluster')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_cluster_roles(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Deleting clusterroles failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Cluster roles deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def remove_cluster_role_bindings(namespace, kubeconfig_file, verbosity):    # pragma: no cover
    """Delete Cluster rolebindings."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_cluster_rolebindings')
    LOG.info('Deleting cluster rolebindings to completely clean the cluster')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_cluster_role_bindings(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Deleting cluster rolebindings failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Cluster rolebindings deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_name
@helmfile_version
@username
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def cncs_optionality_checker(helmfile_name, helmfile_version, username, user_password, verbosity):  # pragma: no cover
    """Check the CNCS optionality values."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='cncs_optionality_check')
    LOG.info('Checking the CNCS optionality values')
    start_time = time.time()
    exit_code = 0
    try:
        helm.check_cncs_optionality(helmfile_name, helmfile_version, username, user_password)
    except Exception as exception:
        LOG.error('CNCS optionality check failed with the following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('CNCS optionality check completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@dir
@image
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def check_crs_from_templates_dir(dir, image, verbosity):    # pragma: no cover
    """Generate separate CRD template files."""
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


@cli.command()
@name
@timeout
@kubeconfig_file
@namespace
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, duplicate-code
def uds_backend_job_wait(name, timeout, kubeconfig_file, namespace, verbosity):     # pragma: no cover
    """Wait for uds job to complete."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='uds_backend_job_wait')
    LOG.info('Waiting for UDS Backend Job to Complete ...')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.wait_for_condition("complete", f"jobs/{name}", timeout, kubeconfig_file, namespace)
    except Exception as exeception:
        LOG.error("Wait for uds backend job failure")
        LOG.info(traceback.format_exc())
        LOG.error(exeception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_path
@chart_cache_directory
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def generate_optionality_maximum(state_values_file, path_to_helmfile, chart_cache_directory, verbosity):
    """Generate an optionality_maximuml.yaml."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='generate_optionality_maximum')
    LOG.info('Generating the optionality_maximum.yaml file')
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
@artifact_url
@helmfile_name
@helmfile_version
@helmfile_repo
@helmfile_path
@state_values_file
@chart_name
@chart_cache_directory
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def download_and_compare_csar_build_info(artifact_url, helmfile_name, helmfile_version,
                                         helmfile_repo, path_to_helmfile, state_values_file,
                                         chart_name, chart_cache_directory, verbosity):     # pragma: no cover
    """Download and extract the csar-build-info.txt file."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='generate_optionality_maximum')
    LOG.info('Downloading and comparing the csar-build-info.txt file')
    start_time = time.time()
    exit_code = 0
    try:
        csar.download_and_compare_csar_build_info(artifact_url, helmfile_name, helmfile_version,
                                                  helmfile_repo, path_to_helmfile, state_values_file,
                                                  chart_name, chart_cache_directory)
    except Exception as exception:
        LOG.error('Downloading and comparing the csar-build-info.txt file failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Downloading and comparing the csar-build-info.txt file completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@microservice_skip_list
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def get_shared_images(path_to_helmfile, microservice_skip_list, verbosity):     # pragma: no cover
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
@helmfile_path
@create_tickets
@skip_list
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def create_outdated_images_tickets(path_to_helmfile, create_tickets, skip_list, verbosity):
    """Create Jira tickets for each chart with outdated images."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_outdated_images_tickets')
    LOG.info('Creating Jira tickets for each chart with outdated images')
    start_time = time.time()
    exit_code = 0
    try:
        get_all_microservices_from_helmfile.create_outdated_images_tickets(path_to_helmfile, create_tickets,
                                                                           skip_list)
    except Exception as exception:
        LOG.error('The creation of Jira tickets failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('The creation of Jira tickets completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@state_values_file
@docker_auth_config
@flow_area
@cluster_name
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, duplicate-code
def create_common_resources(namespace, kubeconfig_file, state_values_file, docker_auth_config, flow_area,
                            cluster_name, verbosity):   # pragma: no cover
    """Create common resources on a namespace for the deployment."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_common_resources')
    LOG.info('Creating the common secrets and configmap objects')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_testware_hostnames_configmap(namespace, kubeconfig_file, state_values_file)
        kubectl.create_global_testware_config_configmap(namespace, kubeconfig_file, docker_auth_config,
                                                        flow_area, cluster_name, state_values_file)
        kubectl.create_ddp_config_secret(namespace, kubeconfig_file, state_values_file)
    except Exception as exception:
        LOG.error('The creation of the common secrets and configmaps failed with the following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('The creation of the common secrets and configmaps completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
