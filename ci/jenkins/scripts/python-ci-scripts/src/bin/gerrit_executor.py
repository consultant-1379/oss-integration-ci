"""Module for executing gerrit related scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import os
import time
import sys
from datetime import timedelta
import traceback
import click

from lib import utils
from lib import containers

from lib.decorators import log_verbosity_option
from lib.decorators import image
from lib.decorators import message
from lib.decorators import git_repo_local
from lib.decorators import gerrit_branch
from lib.decorators import gerrit_change_number
from lib.decorators import timeout


LOG = logging.getLogger(__name__)


def username(func):
    """Set a decorator for the username."""
    return click.option('--username', 'username', envvar='GERRIT_USERNAME', required=True, type=str,
                        help='This is the username to log into Gerrit. This can also be set as an environment '
                             'variable, GERRIT_USERNAME, if extra security is needed'
                        )(func)


def password(func):
    """Set a decorator for the password."""
    return click.option('--password', 'password', envvar='GERRIT_PASSWORD', required=True, type=str,
                        help='This is the user password to log into Gerrit. This can also be set as an '
                             'environment variable, GERRIT_PASSWORD, if extra security is needed'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for CI Pre Code Review Executor."""


@cli.command()
@username
@password
@image
@message
@git_repo_local
@gerrit_branch
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def generate_gerrit_patch(image, message, git_repo_local, gerrit_branch, username, password, verbosity):
    """Generate Gerrit Review."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='generate_gerrit_patch')
    LOG.info('Generate a Gerrit Review for the inputted Repo')
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
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
@username
@password
@image
@timeout
@gerrit_change_number
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def check_gerrit_review_submittable(image, gerrit_change_number, username, password, timeout, verbosity):
    """Generate Gerrit Review."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='check_gerrit_review_submittable')
    LOG.info('Checking Gerrit Review to see if submittable')
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password
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
