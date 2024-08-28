"""Module for executing Confluence commands."""
import logging
import time
import traceback
import sys
from datetime import timedelta
import os
import click

from lib import utils
from lib import confluence
from lib import get_all_microservices_from_helmfile

from lib.decorators import log_verbosity_option
from lib.decorators import space_key
from lib.decorators import url
from lib.decorators import parent_id
from lib.decorators import documents_path
from lib.decorators import helmfile_path
from lib.decorators import create_tickets
from lib.decorators import skip_list
from lib.decorators import microservice_skip_list

LOG = logging.getLogger(__name__)


def username(func):
    """Set a decorator for the username."""
    return click.option('--username', 'username', envvar='FUNCTIONAL_USER_USERNAME', required=True, type=str,
                        help='This is the username Jenkins uses for ARM Registry Credentials. This can also be set as '
                             'an environment variable, FUNCTIONAL_USER_USERNAME, if extra security is needed'
                        )(func)


def password(func):
    """Set a decorator for the password."""
    return click.option('--password', 'password', envvar='FUNCTIONAL_USER_PASSWORD', required=True, type=str,
                        help='This is the user password Jenkins uses for ARM Registry Credentials, This can also be '
                             'set as an environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for CI Confluence Executor."""


@cli.command()
@space_key
@url
@parent_id
@documents_path
@username
@password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def transfer_gerrit_documents(space_key, url, parent_id, documents_path, username, password, verbosity):
    """Transfer documents to Confluence."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='transfer_gerrit_documents')
    LOG.info('Creating confluence pages for each of the documents provided')
    os.environ["FUNCTIONAL_USER_USERNAME"] = username
    os.environ["FUNCTIONAL_USER_PASSWORD"] = password
    start_time = time.time()
    exit_code = 0
    try:
        confluence.transfer_gerrit_documents(space_key, url, parent_id, documents_path)
    except Exception as exception:
        LOG.error('The creation of Confluence pages failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('The creation of Confluence pages completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@helmfile_path
@create_tickets
@skip_list
@microservice_skip_list
@username
@password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_outdated_images_tickets(path_to_helmfile, create_tickets, skip_list, microservice_skip_list, username,
                                   password,  verbosity):
    """Create Jira tickets for each chart with outdated images."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_outdated_images_tickets')
    LOG.info('Creating Jira tickets for each chart with outdated images')
    os.environ["FUNCTIONAL_USER_USERNAME"] = username
    os.environ["FUNCTIONAL_USER_PASSWORD"] = password
    start_time = time.time()
    exit_code = 0
    try:
        get_all_microservices_from_helmfile.create_outdated_images_tickets(path_to_helmfile, create_tickets,
                                                                           skip_list, microservice_skip_list)
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
