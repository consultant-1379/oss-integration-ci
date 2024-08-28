"""Module for Pre Code review tests on a given chart/given helmfile."""
# pylint: disable=too-many-lines
import logging
import time
import sys
import os
from datetime import timedelta
import traceback
import click

from lib import utils
from lib import test_suite


LOG = logging.getLogger(__name__)


def log_verbosity_option(func):
    """Set a decorator for the log verbosity command line argument."""
    return click.option('-v', '--verbosity', type=click.IntRange(0, 4), default=3, show_default=True,
                        help='number for the log level verbosity, 0 lowest, 4 highest'
                        )(func)


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


def state_values_file(func):
    """Set a decorator for the path to the full values file."""
    return click.option('--state-values-file', 'state_values_file', required=True, type=str,
                        help='This is the full path to the state values file'
                        )(func)


def yamllint_config(func):
    """Set a decorator for the full path to the Yamllint Config file."""
    return click.option('--yamllint-config', 'yamllint_config', required=True, type=str,
                        help='Used to set the full path to the Yamllint Config File that is used during the Yaml Lint'
                        )(func)


def yamllint_log_file(func):
    """Set a decorator for the full path to the Yamllint Log file."""
    return click.option('--yamllint-log-file', 'yamllint_log_file', required=True, type=str,
                        help='Used to set the full path to save the output of the yamllint command'
                        )(func)


def template_output_file_path(func):
    """Set a decorator for the full path to the output of the helm/helmfile template command."""
    return click.option('--template-output-file-path', 'template_output_file_path', required=True, type=str,
                        help='Used to set the full path to the output of the helm/helmfile template command'
                        )(func)


def helmfile_full_path(func):
    """Set a decorator for the helmfile full path to the file."""
    return click.option('--helmfile-full-path', 'helmfile_full_path', required=True, type=str,
                        help='Used to set the full path to the helmfile'
                        )(func)


def chart_full_path(func):
    """Set a decorator for the helm chart full path to the file."""
    return click.option('--chart-full-path', 'chart_full_path', required=True, type=str,
                        help='Used to set the full path to the chart'
                        )(func)


def docker_file_full_path(func):
    """Set a decorator for the full path to the Docker file being used."""
    return click.option('--docker-file-full-path', 'docker_file_full_path', required=True, type=str,
                        help='Used to set the full path to the Docker file being used.'
                        )(func)


def specific_skip_file(func):
    """Set a decorator to be able to specify the path to the specific skip list for the test."""
    return click.option('--specific-skip-file', 'specific_skip_file', required=True, type=str,
                        help='Used to set the full path to the specific skip file for the app under test'
                        )(func)


def check_specific_content(func):
    """Set a decorator to be able to specify the path to check content file for the test."""
    return click.option('--check-specific-content', 'check_specific_content', required=True, type=str,
                        help='Used to set the full path to the check content file for the helmfile under test'
                        )(func)


def common_skip_file(func):
    """Set a decorator to be able to specify the path to the common skip list for the test."""
    return click.option('--common-skip-file', 'common_skip_file', required=True, type=str,
                        help='Used to set the full path to the common skip file for the app under test'
                        )(func)


def directory_path(func):
    """Set a decorator to be able to specify the path to a specific directory."""
    return click.option('--directory-path', 'directory_path', required=True, type=str,
                        help='Used to set the full path to a directory'
                        )(func)


def search_string(func):
    """Set a decorator to be able to specify a search string to search for."""
    return click.option('--search-string', 'search_string', default="yaml", show_default=True, required=False, type=str,
                        help='Used to set a search string to look for within a given directory'
                        )(func)


def ignore_strings(func):
    """Set a decorator to be able to specify the path to a specific directory."""
    return click.option('--ignore-strings', 'ignore_strings', default=None, show_default=True, required=False, type=str,
                        help='Used to set a comma separated list of stings to omit from the search '
                             'within a given directory'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for CI Pre Code Review Executor."""


@cli.command()
@state_values_file
@chart_full_path
@yamllint_config
@template_output_file_path
@yamllint_log_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def yaml_lint_application_chart(state_values_file, chart_full_path, yamllint_config, template_output_file_path,
                                yamllint_log_file, verbosity):
    """Execute the Yaml lint against a given helm chart."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='yaml_lint_application_chart')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Yaml Lint Execution')
    try:
        test_suite.yaml_lint_application_chart(site_values_template=state_values_file, chart=chart_full_path,
                                               yamllint_config=yamllint_config, template_file=template_output_file_path,
                                               yamllint_log_file=yamllint_log_file)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@helmfile_full_path
@yamllint_config
@template_output_file_path
@yamllint_log_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def yaml_lint_helmfile(helmfile_full_path, state_values_file, yamllint_config, template_output_file_path,
                       yamllint_log_file, verbosity):
    """Execute the Yaml lint against a given helm chart."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='yaml_lint_helmfile')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Yaml Lint Execution')
    try:
        test_suite.yaml_lint_helmfile(helmfile_full_path=helmfile_full_path, site_values_template=state_values_file,
                                      yamllint_config=yamllint_config, template_file=template_output_file_path,
                                      yamllint_log_file=yamllint_log_file)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@chart_full_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def helm_lint(state_values_file, chart_full_path, verbosity):
    """Execute the Helm lint against a given helm chart."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='helm_lint')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Helm Lint Execution')
    try:
        test_suite.helm_lint(chart=chart_full_path, site_values_template=state_values_file)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@check_specific_content
@state_values_file
@helmfile_full_path
@specific_skip_file
@common_skip_file
@username
@password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def helmfile_static_tests(state_values_file, helmfile_full_path, specific_skip_file,
                          common_skip_file, check_specific_content, username, password, verbosity):
    """Execute the Helmfile Static Tests against a given helmfile."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='helmfile_static_tests')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Helmfile Static Test Execution')
    os.environ["GERRIT_USERNAME"] = username
    os.environ["GERRIT_PASSWORD"] = password

    try:
        test_suite.helmfile_static_tests(helmfile=helmfile_full_path,
                                         site_values_template=state_values_file,
                                         common_skip_file=common_skip_file,
                                         specific_skip_file=specific_skip_file,
                                         check_specific_content=check_specific_content)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@state_values_file
@chart_full_path
@specific_skip_file
@common_skip_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def static_tests(state_values_file, chart_full_path, specific_skip_file, common_skip_file, verbosity):
    """Execute the Static Tests against a given helm chart."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='static_tests')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Static Test Execution')
    try:
        test_suite.static_tests(chart=chart_full_path,
                                site_values_template=state_values_file,
                                common_skip_file=common_skip_file,
                                specific_skip_file=specific_skip_file)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@chart_full_path
@directory_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def schema_tests(chart_full_path, directory_path, verbosity):
    """Execute the Schema Tests against a given helm chart."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='schema_tests')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Schema Test Execution')
    try:
        test_suite.schema_tests(chart_full_path, directory_path)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@chart_full_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def check_eric_product_info_images(chart_full_path, verbosity):
    """Collect images from the eric-product-info.yaml file of the chart & subcharts and ensures the images exist."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='check_eric_product_info_images')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Eric Product Info Images Check Execution')
    try:
        test_suite.check_eric_product_info_images(chart_full_path)
    except Exception as exception:
        LOG.error('Eric Product Info Images Check failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Eric Product Info Images Check completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@docker_file_full_path
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def add_experimental_permissions_for_docker_config_file(docker_file_full_path, verbosity):
    """Add experimental permissions to docker config file in order to check eric-product-info images."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='add_experimental_permissions_for_docker_config_file')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Addition of Experimental Permissions for Docker Config File Execution')
    try:
        test_suite.add_experimental_permissions_for_docker_config_file(docker_file_full_path)
    except Exception as exception:
        LOG.error('Addition of Experimental Permissions for Docker Config File failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Addition of Experimental Permissions for Docker Config File has completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@chart_full_path
@directory_path
@search_string
@ignore_strings
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def validate_chart_against_schema_file(chart_full_path, directory_path, search_string, ignore_strings, verbosity):
    """Execute the schema validation against a given helm chart."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='validate_chart_against_schema_file')
    start_time = time.time()
    exit_code = 0
    LOG.info('Starting Execution of chart validation against schema files')
    try:
        test_suite.validate_chart_against_schema_file_tests(chart=chart_full_path,
                                                            schema_file_directory=directory_path,
                                                            search_string=search_string,
                                                            ignore_strings=ignore_strings)
    except Exception as exception:
        LOG.error('Execution failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Execution completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
