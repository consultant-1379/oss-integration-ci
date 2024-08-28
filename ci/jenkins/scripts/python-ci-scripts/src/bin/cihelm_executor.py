"""Module for executing ADP enabler cihelm to fetch dependencies and build helm charts."""
# pylint: disable=too-many-lines
import logging
import time
import sys
from datetime import timedelta
import traceback
import os
import click

from lib import cihelm
from lib import utils

from lib.decorators import log_verbosity_option
from lib.decorators import helmfile_path
from lib.decorators import path_to_chart
from lib.decorators import clean_up
from lib.decorators import directory_path
from lib.decorators import version
from lib.decorators import chart_name
from lib.decorators import chart_version
from lib.decorators import chart_repo

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
    """Define the CLI for CI Pre Code Review Executor."""


@cli.command()
@helmfile_path
@clean_up
@username
@password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def cihelm_fetch(path_to_helmfile, username, password, clean_up, verbosity):
    """Run CI helm fetch Chart Dependency."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='cihelm_fetch')
    LOG.info("Starting To execute cihelm fetch update")
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
    start_time = time.time()
    exit_code = 0
    try:
        # pylint: disable=no-member
        cihelm.cihelm_fetch(path_to_helmfile, clean_up)
    except Exception as exception:
        LOG.error('cihelm Fetch update failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('cihelm Fetch completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@chart_name
@chart_version
@chart_repo
@username
@password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def cihelm_fetch_single_chart(chart_name, chart_version, chart_repo, username, password, verbosity):
    """Run CI helm fetch Chart Dependency."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='cihelm_fetch_single_chart')
    LOG.info("Starting To execute cihelm fetch update for %s-%s", chart_name, chart_version)
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
    start_time = time.time()
    exit_code = 0
    try:
        # pylint: disable=no-member
        cihelm.cihelm_fetch_single_chart(chart_name, chart_version, chart_repo)
    except Exception as exception:
        LOG.error('cihelm fetch update for %s-%s failed with the following error', chart_name, chart_version)
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('cihelm fetch for %s-%s completed successfully', chart_name, chart_version)
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@path_to_chart
@directory_path
@username
@password
@version
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def cihelm_package(path_to_chart, directory_path, version, username, password, verbosity):
    """Run CI helm Package Chart."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='cihelm_package_chart')
    LOG.info("Starting To execute cihelm package chart")
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
    start_time = time.time()
    exit_code = 0
    try:
        # Due to limitation in cihelm package on the destination directory can not have an ending "/"
        if path_to_chart[-1] == '/':
            path_to_chart_stripped = path_to_chart.rsplit('/', 1)[0]
        else:
            path_to_chart_stripped = path_to_chart
        cihelm.cihelm_package_chart(path_to_chart_stripped, directory_path, version)
    except Exception as exception:
        LOG.error('cihelm package failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('cihelm package completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
