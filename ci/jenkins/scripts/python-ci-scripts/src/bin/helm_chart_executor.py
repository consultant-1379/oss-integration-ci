"""Module for executing ADP enabler cihelm to fetch dependencies and build helm charts."""
# pylint: disable=too-many-lines
import logging
import time
import sys
from datetime import timedelta
import traceback
import os
import click

from lib import get_all_microservices_from_helmfile
from lib import helm
from lib import utils

from lib.decorators import log_verbosity_option
from lib.decorators import path_to_chart
from lib.decorators import directory_path
from lib.decorators import helmfile_path
from lib.decorators import chart_name
from lib.decorators import chart_version
from lib.decorators import chart_repo
from lib.decorators import state_values_file
from lib.decorators import use_dependency_cache
from lib.decorators import dependency_cache_directory
from lib.decorators import version
from lib.decorators import kubeconfig_file
from lib.decorators import namespace
from lib.decorators import helmfile_name
from lib.decorators import helmfile_version
from lib.decorators import username
from lib.decorators import user_password


LOG = logging.getLogger(__name__)


def gerrit_username(func):
    """Set a decorator for the gerrit_username."""
    return click.option('--gerrit-username', 'gerrit_username',
                        envvar='GERRIT_USERNAME',
                        required=True,
                        type=str,
                        help='This is the username to log into Artifactory. This can also be set as an environment \
                              variable, GERRIT_USERNAME, if extra security is needed'
                        )(func)


def gerrit_password(func):
    """Set a decorator for the gerrit_password."""
    return click.option('--gerrit-password', 'gerrit_password',
                        envvar='GERRIT_PASSWORD',
                        required=True,
                        type=str,
                        help='This is the user password to log into Artifactory, This can also be set as an \
                              environment variable, GERRIT_PASSWORD, if extra security is needed'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for Helm Chart Management."""


@cli.command()
@path_to_chart
@directory_path
@version
@use_dependency_cache
@dependency_cache_directory
@gerrit_username
@gerrit_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def helm_chart_package(path_to_chart,
                       directory_path,
                       version,
                       use_dependency_cache,
                       dependency_cache_directory,
                       gerrit_username,
                       gerrit_password,
                       verbosity
                       ):
    """Run CI helm Package Chart."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='chart_package')
    LOG.info("Starting To execute Helm Chart package")
    os.environ["GERRIT_USERNAME"] = gerrit_username
    os.environ["GERRIT_PASSWORD"] = gerrit_password
    start_time = time.time()
    exit_code = 0
    try:
        # Due to limitation in cihelm package on the destination directory can not have an ending "/"
        if path_to_chart[-1] == '/':
            path_to_chart_stripped = path_to_chart.rsplit('/', 1)[0]
        else:
            path_to_chart_stripped = path_to_chart
        helm.package_chart(path_to_chart_stripped,
                           directory_path,
                           version,
                           use_dependency_cache,
                           dependency_cache_directory
                           )
    except Exception as exception:
        LOG.error('Helm Chart package failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Helm Chart package completed successfully')
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
def remove_releases(namespace, kubeconfig_file, verbosity):
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
@kubeconfig_file
@namespace
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def remove_sep_release(namespace, kubeconfig_file, verbosity):
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
@state_values_file
@helmfile_path
@chart_name
@chart_repo
@chart_version
@gerrit_username
@gerrit_password
@username
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments, too-many-locals
def compare_microservice_versions_from_application(state_values_file, path_to_helmfile, chart_name, chart_repo,
                                                   chart_version, gerrit_username, gerrit_password,
                                                   username, user_password, verbosity):
    """Compare Microservice versions from a chart to the latest versions in the relevant repo."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='compare_microservice_versions_from_application')
    LOG.info("Starting To compare Microservice versions from the Application")
    os.environ["GERRIT_USERNAME"] = gerrit_username
    os.environ["GERRIT_PASSWORD"] = gerrit_password
    os.environ["FUNCTIONAL_USER_USERNAME"] = username
    os.environ["FUNCTIONAL_USER_PASSWORD"] = user_password
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
@helmfile_name
@helmfile_version
@username
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def cncs_optionality_checker(helmfile_name, helmfile_version, username, user_password, verbosity):
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
