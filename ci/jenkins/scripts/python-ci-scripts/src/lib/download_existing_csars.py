"""Module to manage CSAR downloads."""

import logging
import os
import requests
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth

from . import utils
from . import errors

LOG = logging.getLogger(__name__)
CWD = os.getcwd()


def download_existing_csars_from_repo(artifactory_repo_url, applications_to_check):
    """Download CSAR files based on a list of CSAR name-version entries in property file.

    Input:
        artifactory_repo_url: URL for Artifactory service to download CSAR files
        applications_to_check: Property file containing entries using this format:
                               csar_name + "_" + csar_version + "_csar_found=True/False

    Throws:
        InvalidArgumentValueError, MissingCSARError, HTTPError
    """
    # Read environment variables passed into container from docker run
    functional_user_username = os.environ.get('FUNCTIONAL_USER_USERNAME', None)
    functional_user_password = os.environ.get('FUNCTIONAL_USER_PASSWORD', None)

    # Fail script if any of the above are empty
    if not artifactory_repo_url or not applications_to_check:
        err_msg = "One or more mandatory environment variables not set"
        LOG.error(err_msg)
        raise errors.InvalidArgumentValueError(err_msg)

    with open(applications_to_check, "r", encoding="utf-8") as application_file:
        for line in application_file:
            csar_name = line.split("_")[0]
            csar_version = line.split("_")[1]
            # Throw an error if any CSAR is missing (based on properties)
            if "False" in line:
                LOG.error("-" * 119)
                err_msg = "CSAR for " + csar_name + ":" + csar_version + " does not exist."
                LOG.error("%s  Please ensure the CSAR are available in the ", err_msg)
                LOG.error("Repo, " + artifactory_repo_url + "/" + csar_name)
                LOG.error("-" * 119)
                raise errors.MissingCSARError(err_msg)
            full_csar_name = csar_name + "-" + csar_version + ".csar"
            full_url = artifactory_repo_url + "/" + csar_name + "/" + csar_version + "/" + full_csar_name
            LOG.info("-" * 119)
            LOG.info("Repo url for " + csar_name + ": " + full_url)
            try:
                requests.get(full_url, auth=HTTPBasicAuth(functional_user_username, functional_user_password),
                             stream=True,
                             timeout=600)
                download_path = os.path.join(CWD, full_csar_name)
                utils.stream_download_binary_file(
                    download_path, full_csar_name, full_url, functional_user_username, functional_user_password)
            except HTTPError as http_err:
                LOG.info('HTTP error occurred: %s', http_err)
                raise
            except Exception as err:
                LOG.info('Other error occurred: %s', err)
                raise
            LOG.info("-" * 119)
