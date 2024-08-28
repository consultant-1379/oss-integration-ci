"""Module for CSAR related management."""
import logging
import os
import requests
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from requests.auth import HTTPBasicAuth

from . import utils
from . import helmfile
from . import optionality

LOG = logging.getLogger(__name__)
BUILD_CSAR_OUTPUT_FILE = "build_csar.properties"
CHECK_CSAR_OUTPUT_FILE = "csar_check.properties"
CSAR_REPOSITORY_URL = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars"


# pylint: disable=too-many-locals, too-many-branches, too-many-statements
def check_for_existing_csars_in_repo(artifactory_repo_url, applications_to_check_property_file):  # noqa: C901
    """
    Check for CSARs in remote repository and write properties files with availability and status.

    Input:
        artifactory_repo_url: Repository to check for CSARs
        applications_to_check_property_file: Property file that lists applications to check

    Output:
        Write to build_csar.properties with entries about availability about each application
        to check, and csar_check.properties with status for each application
    """
    # Read environment variables passed into container from docker run
    functional_user_username = os.environ.get('FUNCTIONAL_USER_USERNAME', None)
    functional_user_password = os.environ.get('FUNCTIONAL_USER_PASSWORD', None)

    # Remove output property files if they exist
    if os.path.exists(BUILD_CSAR_OUTPUT_FILE):
        os.remove(BUILD_CSAR_OUTPUT_FILE)
    if os.path.exists(CHECK_CSAR_OUTPUT_FILE):
        os.remove(CHECK_CSAR_OUTPUT_FILE)

    with open(applications_to_check_property_file, "r", encoding="utf-8") as application_file, \
         open(BUILD_CSAR_OUTPUT_FILE, "a+", encoding="utf-8") as build_csar_properties, \
         open(CHECK_CSAR_OUTPUT_FILE, "a+", encoding="utf-8") as csar_check_properties:
        for line in application_file:
            artifacts = []
            version_found = False
            csar_name = line.split("=")[0]
            csar_version = line.split("=")[1].rstrip('\n')
            LOG.info("Full CSAR Repo url for " + csar_name + " to be used:\n " + artifactory_repo_url + "/" + csar_name)
            try:
                # Send request to get CSAR versions available on CSAR repo
                artifactory_response = requests.get(artifactory_repo_url + "/" + csar_name,
                                                    auth=HTTPBasicAuth(functional_user_username,
                                                                       functional_user_password),
                                                    timeout=600)
                if artifactory_response.status_code == 200:
                    artifactory_response.raise_for_status()
                    artifactory_response_json = artifactory_response.json()
                    # Extract all artifact names into list (helmfile.tgz files)
                    for artifact in artifactory_response_json["children"]:
                        artifacts.append(artifact["uri"][1:])
                    LOG.info("Artifacts found in repo:\n %s", str(artifacts))
                if csar_version in artifacts:
                    LOG.info("-" * 119)
                    LOG.info("CSAR Version %s exists in CSAR repo, for %s: %s",
                             csar_version, csar_name, csar_version)
                    LOG.info("-" * 119)
                    version_found = True
                else:
                    LOG.info("-" * 119)
                    LOG.info("CSAR Version %s not found in CSAR repo, for %s: %s",
                             csar_version, csar_name, csar_version)
                    LOG.info("-" * 119)
            except HTTPError as http_err:
                LOG.info("HTTP error occurred: %s", http_err)
                raise
            except Exception as err:
                LOG.info("Other error occurred: %s", err)
                raise

            try:
                # Write decision whether CSAR is found or not to build_csar.properties
                LOG.debug("Writing update for CSAR %s to %s", csar_name, BUILD_CSAR_OUTPUT_FILE)
                build_csar_properties.write(csar_name + "_" + csar_version +
                                            "_csar_found=" + str(version_found) + "\n")
            except IOError as io_error:
                LOG.error("File write error, could not write to build_csar.properties: %s", io_error)
                raise

            try:
                # Write Information on CSAR to csar_check.properties
                LOG.debug("Writing update for CSAR %s to %s", csar_name, CHECK_CSAR_OUTPUT_FILE)
                if version_found:
                    csar_check_properties.write(csar_name + "__AVAILABLE=" +
                                                CSAR_REPOSITORY_URL + "/" + csar_name + "/" + csar_version + "\n")
                else:
                    csar_check_properties.write(csar_name + "__NOT_FOUND=" +
                                                CSAR_REPOSITORY_URL + "/" + csar_name + "/" + csar_version + "\n")
            except IOError as io_error:
                LOG.error("File write error, could not write to csar_check.properties: %s", io_error)
                raise


# pylint: disable=too-many-arguments
def download_and_compare_csar_build_info(artifactory_url, helmfile_name, helmfile_version, helmfile_repo,
                                         helmfile_path, state_values_file_path, csar_name, chart_cache_directory):
    """
    Download and extract the images from the csar_build_info.txt file.

    Input:
        artifactory_url: The URL path to the csar_build_info.txt file
        helmfile_name: The name of the helmfile to be fetched
        helmfile_version: The version of the helmfile to be fetched
        helmfile_repo: The repository of the helmfile to be fetched
        helmfile_path: The path to the helmfile.yaml file
        state_values_file_path: The path to where the different site values files are located
        csar_name: The name of the CSAR

    Output:
        A text file containing the images of the existing CSAR and a text file
        indicating if the CSAR should be built
    """
    if csar_name in ["eric-eo-cm", "eric-eo-act-cna"]:
        LOG.info("Exiting image comparison: Image comparison not conducted for eric-eo-cm or eric-eo-act-cna")
        with open("csar-build-indicator-file.properties", "w", encoding="utf-8") as csar_build_indicator_file:
            csar_build_indicator_file.write("should_csar_be_built=True")
        return

    functional_user_username = os.environ.get('GERRIT_USERNAME', None)
    functional_user_password = os.environ.get('GERRIT_PASSWORD', None)

    should_csar_be_built = True

    try:
        LOG.info("Assessing whether the csar_build_info.txt file is available at %s", artifactory_url)
        utils.download_file(artifactory_url, "downloaded_csar_build_info.txt",
                            functional_user_username, functional_user_password, "wb")
        LOG.info("Download Successful. The images contained within this CSAR will be compared against the helmfile "
                 "to determine whether a CSAR rebuild is necessary...")
        with open("downloaded_csar_build_info.txt", "r", encoding="utf-8") as downloaded_info_file:
            for line in downloaded_info_file:
                if line.startswith("Images:"):
                    csar_build_info_images = [value.strip() for value in line.strip("Images:").split(",")]

        helmfile.download_helmfile(helmfile_name, helmfile_version, helmfile_repo,
                                   functional_user_username, functional_user_password)
        utils.extract_tar_file(helmfile_name + "-" + helmfile_version + ".tgz", "./")
        optionality.generate_optionality_maximum(state_values_file_path, f"{helmfile_name}/helmfile.yaml",
                                                 chart_cache_directory)
        template_images = get_template_images(csar_name, state_values_file_path, helmfile_path)

        try:
            helmfile_csar_image_list_comparison(csar_build_info_images, template_images)
            LOG.info("There are no missing images between the csar-build-info.txt file and "
                     "the helmfile. The CSAR build will not proceed...")
            should_csar_be_built = False

        # pylint: disable=broad-except
        except Exception:
            LOG.info("As images are missing from the csar-build-info.txt file, "
                     "the CSAR build will proceed")
            with open("templated-images.txt", "w", encoding="utf-8") as templated_images_file:
                templated_images_file.write(",".join(template_images))

    except RequestException:
        LOG.info("Unable to find the csar_build_info file. The CSAR build will continue...")

    finally:
        with open("csar-build-indicator-file.properties", "w", encoding="utf-8") as csar_build_indicator_file:
            csar_build_indicator_file.write(f"should_csar_be_built={str(should_csar_be_built)}")


def combine_csar_build_info(manifest_file_path, images_file_path):
    """
    Combine the TGZ and images information of a CSAR into a single file.

    Input:
        manifest_file_path: A path to the manifest.txt file
        images_file_path: A path to the images.txt file

    Output:
        A text file containing information about the TGZ files and images
        included within the CSAR
    """
    manifest_values = utils.get_file_contents(manifest_file_path)[0].split(" ")
    images_values = None
    if os.path.exists(images_file_path):
        images_values = utils.get_file_contents(images_file_path)
        images_values = [value.split("/")[-1] for value in images_values]
    with open("csar-build-info.txt", "w", encoding="utf-8") as csar_build_info:
        csar_build_info.write(f"TGZ files: {', '.join(manifest_values)}\n")
        if images_values:
            csar_build_info.write(f"Images: {', '.join(images_values)}")


# pylint: disable=too-many-arguments
def compare_csar_and_helmfile_images(csar_name, csar_version, helmfile_path, state_values_file_path,
                                     helmfile_name, helmfile_version, helmfile_repo, chart_cache_directory):
    """
    Retrieve the images from the CSAR and helmfile template and compare them.

    Input:
        csar_name: The name of the CSAR
        csar_version: The version of the CSAR
        helmfile_path: The path to the helmfile.yaml file
        state_values_file_path: The path to where the different site values files are located
        helmfile_name: The name of the helmfile to be fetched
        helmfile_version: The version of the helmfile to be fetched
        helmfile_repo: The repository of the helmfile to be fetched
    """
    if csar_name in ["eric-eo-cm", "eric-eo-act-cna"]:
        LOG.info("Exiting image comparison: Image comparison not conducted for eric-eo-cm or eric-eo-act-cna")
        return

    functional_user_username = os.environ.get('GERRIT_USERNAME', None)
    functional_user_password = os.environ.get('GERRIT_PASSWORD', None)

    if not os.path.exists("templated-images.txt"):
        helmfile.download_helmfile(helmfile_name, helmfile_version, helmfile_repo,
                                   functional_user_username, functional_user_password)
        utils.extract_tar_file(helmfile_name + "-" + helmfile_version + ".tgz", "./")
        optionality.generate_optionality_maximum(state_values_file_path, f"{helmfile_name}/helmfile.yaml",
                                                 chart_cache_directory)
        template_images = get_template_images(csar_name, state_values_file_path, helmfile_path)
    else:
        LOG.info("The helmfile has already been downloaded. The template values will be reused...")
        with open("templated-images.txt", "r", encoding="utf-8") as template_images_file:
            template_images = template_images_file.read().split(",")

    csar_name = csar_name.split(",")[0]
    csar_version = csar_version.split(",")[0]
    utils.unzip_file("./" + csar_name + "-" + csar_version + ".csar", "./", "Files/images.txt")
    csar_images = utils.get_file_contents("Files/images.txt")

    try:
        helmfile_csar_image_list_comparison(csar_images, template_images)
    # pylint: disable=broad-except
    except Exception as exc:
        with open("csar-build-status-file.properties", "w", encoding="utf-8") as csar_build_status_file:
            csar_build_status_file.write("csar_build_status=Failed")
        raise Exception("Error: Image(s) are missing from the CSAR") from exc


def helmfile_csar_image_list_comparison(csar_images, template_images):
    """
    Compare the images retrieved from the CSAR and the helmfile template command.

    Input:
        csar_images: A list containing all the images within the CSAR
        template_images: A list containing all the images for a specific CSAR within the helmfile template output
    """
    if len(template_images) == 0:
        LOG.warning("Warning: The helmfile template returned no images")
        return
    template_images_name_and_version = [value.split("/")[-1] for value in template_images]
    csar_images_name_and_version = [value.split("/")[-1] for value in csar_images]
    missing_value = False
    for image_name_and_version in template_images_name_and_version:
        if image_name_and_version in csar_images_name_and_version:
            LOG.info("Found image: %s", image_name_and_version)
        else:
            LOG.error("Error: The image %s is missing from the CSAR", image_name_and_version)
            missing_value = True
    if missing_value:
        raise Exception("Error: Image(s) are missing from the CSAR")
    LOG.info("All images are contained in the CSAR")


def get_template_images(csar_name, state_values_file_path, helmfile_path):
    """
    Retrieve the images from the helmfile template based on the CSAR name.

    Input:
        csar_name: The name of the CSAR for which images should be extracted
        state_values_file_path: The path to where the different site values files are located
        helmfile_path: The path to the helmfile.yaml file

    Returns
    -------
        A sorted list of the images for the CSAR within the helmfile template

    """
    template_output = helmfile.get_helmfile_template_output(state_values_file_path, helmfile_path)

    csar_name = csar_name.split(",")[0]
    images = []
    correct_chart = False
    for line in template_output:
        if line.startswith("# Source: " + csar_name + "/"):
            correct_chart = True
        elif "image:" in line and correct_chart:
            line = line.split("image:", 1)[-1]
            line = line.replace('"', '')
            line = line.replace(" ", "")
            line = line.strip()
            if line not in images and "stub" not in line and "proxyImage" not in line:
                images.append(line)
        elif line.startswith("---"):
            correct_chart = False
    return images
