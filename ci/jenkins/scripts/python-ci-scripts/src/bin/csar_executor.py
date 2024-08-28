"""Module for executing csar related scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import os
import time
import sys
from datetime import timedelta
import traceback
import click

from lib import csar
from lib import utils
from lib import download_existing_csars

from lib.decorators import log_verbosity_option
from lib.decorators import csar_repo_option
from lib.decorators import applications_to_check_option
from lib.decorators import helmfile_path
from lib.decorators import helmfile_name
from lib.decorators import helmfile_version
from lib.decorators import helmfile_repo
from lib.decorators import chart_name
from lib.decorators import chart_version
from lib.decorators import chart_cache_directory
from lib.decorators import manifest_file
from lib.decorators import images_file
from lib.decorators import state_values_file
from lib.decorators import artifact_url


LOG = logging.getLogger(__name__)


def username(func):
    """Set a decorator for the username."""
    return click.option('--username', 'username', envvar='FUNCTIONAL_USER_USERNAME', required=True, type=str,
                        help='This is the username to log into Artifactory. This can also be set as an environment '
                             'variable, FUNCTIONAL_USER_USERNAME, if extra security is needed'
                        )(func)


def password(func):
    """Set a decorator for the password."""
    return click.option('--password', 'password', envvar='FUNCTIONAL_USER_PASSWORD', required=True, type=str,
                        help='This is the user password to log into Artifactory, This can also be set as an '
                             'environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for Helm Chart Management."""


@cli.command()
@username
@password
@csar_repo_option
@applications_to_check_option
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def check_for_existing_csar(csar_repo_url, applications_to_check, username, password, verbosity):
    """Check a specific CSAR repo for a CSAR with a matching version to avoid duplication during CSAR build."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='check_for_existing_csar')
    LOG.info("Starting Check For Existing CSARs")
    os.environ["FUNCTIONAL_USER_USERNAME"] = username
    os.environ["FUNCTIONAL_USER_PASSWORD"] = password
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
@username
@password
@csar_repo_option
@applications_to_check_option
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def download_existing_csar(csar_repo_url, applications_to_check, username, password, verbosity):
    """Download the officially built CSAR from the CSAR REPO."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='download_existing_csar')
    LOG.info("Starting Download of CSARs")
    os.environ["FUNCTIONAL_USER_USERNAME"] = username
    os.environ["FUNCTIONAL_USER_PASSWORD"] = password
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
@manifest_file
@images_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def combine_csar_build_info(manifest_file, images_file, verbosity):
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
@username
@password
@helmfile_path
@state_values_file
@chart_name
@chart_version
@helmfile_name
@helmfile_version
@helmfile_repo
@chart_cache_directory
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, too-many-locals
def compare_csar_and_helmfile_images(chart_name, chart_version, path_to_helmfile, state_values_file,
                                     helmfile_name, helmfile_version, helmfile_repo, chart_cache_directory,
                                     username, password, verbosity):
    """Compare images contained within a CSAR to those within a helmfile."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='examine_csar_images')
    LOG.info("Starting a comparison of the images contained within the CSAR and the helmfile template")
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
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
@username
@password
@artifact_url
@helmfile_name
@helmfile_version
@helmfile_repo
@helmfile_path
@state_values_file
@chart_name
@chart_cache_directory
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, too-many-locals
def download_and_compare_csar_build_info(artifact_url, helmfile_name, helmfile_version,
                                         helmfile_repo, path_to_helmfile, state_values_file,
                                         chart_name, chart_cache_directory,
                                         username, password, verbosity):
    """Download and extract the csar-build-info.txt file."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='generate_optionality_maximum')
    LOG.info('Downloading and comparing the csar-build-info.txt file')
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
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
