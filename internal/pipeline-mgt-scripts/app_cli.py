"""This is the CLI for the pipeline management utilities."""
import logging
import click

import utils
import spin
import cert
import jenkins

LOG = logging.getLogger(__name__)


def log_verbosity_option(func):
    """Set a decorator for the log verbosity command line argument."""
    return click.option('-v', '--verbosity', type=click.IntRange(0, 4), default=3, show_default=True,
                        help='number for the log level verbosity, 0 lowest, 4 highest'
                        )(func)


def filename_option(func):
    """Set a decorator for a filename."""
    return click.option('--filename', 'filename', required=True, type=str,
                        help='A filename string.'
                        )(func)


def app_list(func):
    """Set a decorator for an application list."""
    return click.option('--app-list', 'app_list', required=True, type=str,
                        help='A space-separated list of applications.'
                        )(func)


def banner_text(func):
    """Set a decorator for a banner message."""
    return click.option('--banner-text', 'banner_text', required=True, type=str,
                        help='A banner text message.'
                        )(func)


def bg_color(func):
    """Set a decorator for a background color."""
    return click.option('--bg-color', 'bg_color', required=True, type=str,
                        help='A background color value.'
                        )(func)


def text_color(func):
    """Set a decorator for a text color."""
    return click.option('--text-color', 'text_color', required=True, type=str,
                        help='A text color value.'
                        )(func)


def enabled(func):
    """Set a decorator for an enabled flag."""
    return click.option('--enabled', 'enabled', required=True, type=str,
                        help='A flag for enabled.'
                        )(func)


def skip(func):
    """Set a decorator for a skip flag."""
    return click.option('--skip', 'skip', required=True, type=str,
                        help='A flag for skip.'
                        )(func)


def delete(func):
    """Set a decorator for a delete flag."""
    return click.option('--delete', 'delete', required=True, type=str,
                        help='A flag for delete.'
                        )(func)


def repo_path(func):
    """Set a decorator for a repo path string."""
    return click.option('--repo-path', 'repo_path', required=True, type=str,
                        help='A repo path string.'
                        )(func)


def warn_days(func):
    """Set a decorator for number of days to warn for expiry."""
    return click.option('--warn-days', 'warn_days', required=True, type=str,
                        help='Number of days for certificate expiry warning.'
                        )(func)


def report_name(func):
    """Set a decorator for a report name."""
    return click.option('--report-name', 'report_name', required=True, type=str,
                        help='A report name.'
                        )(func)


def filters(func):
    """Set a decorator for a CSV of path filter keywords."""
    return click.option('--filters', 'filters', required=True, type=str,
                        help='A CSV of filter keywords.'
                        )(func)


def excludes(func):
    """Set a decorator for a CSV of path excludes keywords."""
    return click.option('--excludes', 'excludes', required=True, type=str,
                        help='A CSV of excludes keywords.'
                        )(func)


@click.group(context_settings=dict(terminal_width=220))
def cli_main():
    """Provide an entry-point to the spin management tool."""


@cli_main.command()
@filename_option
@log_verbosity_option
# pylint: disable=redefined-outer-name
def spinnaker_update_banners_from_csv(filename, verbosity):
    """Update banners from CSV file."""
    utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/pipeline-mgt-scripts/',
        logs_sub_directory='output-files/pipeline-mgt-logs',
        filename_postfix='spinnaker_update_banners_from_csv')
    spin.sync_banner_csv(filename)


@cli_main.command()
@app_list
@banner_text
@bg_color
@text_color
@enabled
@skip
@delete
@log_verbosity_option
# pylint: disable=redefined-outer-name,too-many-arguments
def spinnaker_update_app_banner(app_list, banner_text, bg_color, text_color,
                                enabled, skip, delete, verbosity):
    """Update banners from CSV file."""
    utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/pipeline-mgt-scripts/',
        logs_sub_directory='output-files/pipeline-mgt-logs',
        filename_postfix='spinnaker_update_app_banner')
    spin.sync_app_banner_msg(app_list, banner_text, bg_color, text_color,
                             enabled, skip, delete)


@cli_main.command()
@repo_path
@warn_days
@report_name
@filters
@excludes
@log_verbosity_option
# pylint: disable=redefined-outer-name,too-many-arguments
def report_repo_certificates_for_expiry(repo_path, warn_days, report_name,
                                        filters, excludes, verbosity):
    """Report certificates in repository for expiry."""
    utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/pipeline-mgt-scripts/',
        logs_sub_directory='output-files/pipeline-mgt-logs',
        filename_postfix='report_repo_certificates_for_expiry')
    cert.report_certificate_expiry(repo_path, warn_days, report_name,
                                   filters, excludes)


@cli_main.command()
@log_verbosity_option
# pylint: disable=redefined-outer-name
def list_lockable_resources(verbosity):
    """Get list of lockable resources."""
    utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/pipeline-mgt-scripts/',
        logs_sub_directory='output-files/pipeline-mgt-logs',
        filename_postfix='list_lockable_resources')
    jenkins.get_lockable_resource_cluster_list()
