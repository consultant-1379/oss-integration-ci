"""This module contains a list of utility functions."""
# pylint: disable=too-many-lines
from datetime import datetime, timedelta
import json
import logging
import tarfile
import os
import sys
import subprocess
from pathlib import Path
from zipfile import ZipFile
import tempfile
import shutil
import re
from functools import reduce
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
import oyaml as yaml  # pip install oyaml

from . import errors

LOG = logging.getLogger(__name__)


def get_log_level_from_verbosity(verbosity):
    """
    Return a log level based on a given verbosity number.

    Input:
        verbosity: Verbosity number (0-4) that maps to a log-level property
    """
    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG
    }
    return log_levels.get(verbosity, "Invalid verbosity level")


def initialize_logging(verbosity, working_directory, logs_sub_directory, filename_postfix):
    """
    Initialize the logging to standard output and standard out at different verbosities.

    Returns
    -------
        Log file path relative to the working directory.

    """
    log_format = "[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s"
    absolute_log_directory = Path(working_directory) / Path(logs_sub_directory)
    absolute_log_directory.mkdir(parents=True, exist_ok=True)
    # pylint: disable=consider-using-f-string
    relative_log_file_path = str(Path(logs_sub_directory) / datetime.now().strftime(
        '%Y-%m-%dT%H_%M_%S%z_{0}.log'.format(filename_postfix))
                                 )
    absolute_log_file_path = str(Path(working_directory) / Path(relative_log_file_path))
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))
    stream_handler.setLevel(get_log_level_from_verbosity(verbosity))
    logging.basicConfig(filename=absolute_log_file_path, format=log_format, level=logging.DEBUG)
    logging.getLogger('').addHandler(stream_handler)
    logging.getLogger("kubernetes").setLevel(logging.INFO)
    return relative_log_file_path


def extract_tar_file(tar_file, directory):
    """
    Extract a given tar into a given directory.

    Input:
        tar_file: tar file to extract
        directory: directory to extract the tar file to
    """
    with tarfile.open(tar_file) as tar:
        tar.extractall(directory)


def get_content_of_tar_file(filename):
    """
    Get the content of the tar.

    Input:
      filename: Full file name

    Output:
      Content of the tarfile in a list format.
    """
    with tarfile.open(filename, "r:gz") as tar:
        return tar.getnames()


# pylint: disable=too-many-arguments
def download_file(url, filename, username, password, file_write_type, timeout_in_s=600, token=None):
    """
    Download a given file using the url.

    Input:
        url: This is the full url to the file
        filename: This will be used as the name of the file once downloaded
        username: username if the url requires it
        password: password if the url requires it
        file_write_type: parameter for the open file command to state how to write the file,
                         e.g. wb (Open file binary mode)
        token: identity token required to access the artifactory repo

    Output:
        File is downloaded
    """
    try:
        if token is not None:
            # Bearer token authentication to be used with supplied identity token.
            LOG.info("Downloading file using Bearer token")
            headers = {"Authorization": "Bearer " + token}
            response = requests.get(url, headers=headers, timeout=timeout_in_s)
        else:
            LOG.info("Downloading file using Basic Auth credential")
            response = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=timeout_in_s)
        LOG.debug(response.content)
        response.raise_for_status()
        # pylint: disable=unspecified-encoding
        with open(filename, file_write_type) as output_file:
            output_file.write(response.content)
    except requests.exceptions.Timeout as exception:
        LOG.error("Request timed out")
        raise exception
    except requests.exceptions.TooManyRedirects as exception:
        LOG.error("Is there an issue with the URL used. Please check URL.")
        raise exception
    except requests.exceptions.HTTPError as exception:
        LOG.error(str(response.content))
        raise exception
    except requests.exceptions.RequestException as exception:
        raise exception


def extract_tar_file_and_archive_base_directory(tar_file, directory, properties_file):
    """
    Extract the helmfile tar file.

    Input:
        tar_file: tar file to extract
        directory: directory where the tar file should be extracted to

    Output:
        tar_artifact.properties file that lists the base extracted directory
    """
    extract_tar_file(tar_file, directory)
    content_list = get_content_of_tar_file(tar_file)
    LOG.debug("Extracted Tar File Content")
    for file in content_list:
        LOG.debug(str(file))
    tar_file_base_dir = content_list[0]
    LOG.info("Tar File Base directory %s added to properties file %s", str(tar_file_base_dir), properties_file)
    with open(properties_file, "w", encoding="utf-8") as properties:
        properties.write('TAR_BASE_DIR=' + str(tar_file_base_dir) + "\n")
        properties.close()


def join_command_stdout_and_stderr(command):
    """
    Return a string joining the standard output and standard error strings from a command object.

    Input:
        command: Subprocess command object
    """
    returned_string = ''
    decoded_stdout = command.stdout.decode('utf-8')
    decoded_stderr = command.stderr.decode('utf-8')
    if decoded_stdout != "":
        returned_string += decoded_stdout
    if decoded_stdout != "" and decoded_stderr != "":
        returned_string += "\n"
    if decoded_stderr != "":
        returned_string += decoded_stderr
    return returned_string


def run_cli_command(command_and_args_list, **subprocess_run_options):
    """
    Run the given cli command and arguments through pythons subprocess run, with the given options.

    Input:
        command_and_args_list: List of commands to execute
        **subprocess_run_options: Optional key/value parameters for subprocess call
    """
    LOG.debug('Adding all environment variables from the image, to the subprocess.run env variables')
    if 'env' not in subprocess_run_options:
        subprocess_run_options['env'] = {}
    subprocess_run_options['env'] = {**subprocess_run_options['env'], **dict(os.environ.items())}
    LOG.debug('Running the following cli command: %s', ' '.join(command_and_args_list))
    # pylint: disable=subprocess-run-check
    return subprocess.run(command_and_args_list, **subprocess_run_options)


def update_new_site_values_with_tags(state_values_file, deployment_tag_list, optional_tag_list):
    """
    Update site-values yaml with passed-in tags.

    Input:
      state_values_file: Base site-values to read in
      deployment_tag_list: Space-separated list of tags to update in base site-values
      optional_tag_list: Space-separated list of optional tags to update in base site-values

    Returns
    -------
      updated yaml

    """
    with open(state_values_file, encoding="utf-8") as values_file:
        base = yaml.safe_load(values_file)

    enable_tags = deployment_tag_list.split(" ")
    optional_tags = optional_tag_list.split(" ")

    for key in base:
        if key == 'tags':
            for optional_tag in optional_tags:
                if optional_tag not in base[key]:
                    tag_dictionary = {optional_tag: 'false'}
                    base[key].update(tag_dictionary)

            for tag in base[key]:
                if tag in optional_tags:
                    base[key][tag] = True
            for tag in base[key]:
                if tag in enable_tags:
                    base[key][tag] = True
    return base


def write_new_site_values_file_with_tags(in_state_values_file, out_state_values_file, deployment_tag_list,
                                         optional_tag_list):
    """
    Write a site-values yaml after updating with passed-in tags.

    Input:
      in_state_values_file: Base site-values to read in
      deployment_tag_list: Space-separated list of tags to update in base site-values
      optional_tag_list: Space-separated list of optional tags to update in base site-values

    Output:
      out_state_values_file: Site-values with updated yaml to write
    """
    updated_values = update_new_site_values_with_tags(in_state_values_file, deployment_tag_list, optional_tag_list)
    with open(out_state_values_file, 'w', encoding="utf-8") as output_file:
        yaml.safe_dump(updated_values, output_file, default_flow_style=False)


# pylint: disable=too-many-arguments
def stream_download_binary_file(download_path, name, full_url, functional_user_username,
                                functional_user_password, timeout_in_s=600):
    """
    Stream a binary file download.

    Input:
        download_path: File path for downloaded CSAR file
        name: Name of the CSAR to download
        full_url: URL for CSAR file
        functional_user_username: Username for basic authentication to artifact repository
        functional_user_password: Password for basic authentication to artifact repository
        timeout_in_s: Request.get timeout, defaulted to 10 minutes
    """
    with open(download_path, "wb") as downloaded_file:
        LOG.info("Downloading %s", name)
        response = requests.get(full_url, auth=HTTPBasicAuth(functional_user_username,
                                functional_user_password), stream=True,
                                timeout=timeout_in_s)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            downloaded_file.write(response.content)
        else:
            increment = int(10)
            download_count = 0
            total_length = int(total_length)
            percentage = int(total_length / 10)
            percentage_to_add = percentage
            sys.stdout.write("\r[1%]")
            sys.stdout.flush()
            for data in response.iter_content(chunk_size=4096):
                download_count += len(data)
                downloaded_file.write(data)
                if download_count >= int(percentage):
                    sys.stdout.write("\r[" + str(increment) + "%]")
                    sys.stdout.flush()
                    increment += 10
                    percentage += percentage_to_add


def substitute_values_in_file(update_file, config_file):
    """
    Substitute placeholder variables contained in a config file into a file.

    Input:
        update_file: File to update with values substitutions
        config_file: File containing key-value pairs representing substitutions

    Output:
        Updates update_file with substitutions defined in config_file
    """
    with open(update_file, "r", encoding="utf-8") as sv_file:
        data = sv_file.read()
    with open(config_file, "r", encoding="utf-8") as config_to_check:
        for line in config_to_check:
            if "=" in line:
                placeholder = line.split("=")[0].strip()
                value = line.split("=")[1].strip()
                if placeholder in data:
                    if value in ["default", "none"]:
                        LOG.info('Skipping change for %s as it is set to %s', placeholder, value)
                        continue
                    LOG.info('Changing %s to %s in %s', placeholder, value, update_file)
                    data = data.replace(placeholder, value)
                else:
                    LOG.debug('%s not found', placeholder)
    with open(update_file, "w", encoding="utf-8") as updated_file:
        updated_file.write(data)


def get_remote_host(remote_url):
    """
    Get the server/host part from an url.

    Inputs:
        remote_url: URL to the transferred Example: https://user:passwd@my.server.se/repo -> my.server.se
    """
    tmp = remote_url.replace("https://", "")
    tmp = tmp.split('@')[-1]
    return tmp.split('/')[0]


def get_file_contents(path_to_file):
    """
    Get the contents of a file.

    Input
        path_to_file: The path to the file

    Returns
    -------
        A list containing the contents of a file

    """
    lines = []
    with open(path_to_file, encoding="utf-8") as file:
        for line in file:
            lines.append(line.strip())
    return lines


def populate_repository_credentials_in_file(repository_yaml_file, username, password):
    """
    Update non-templated repository yaml file with default registry credentials where none provided.

    Input:
        repository_yaml_file: Repository yaml file to update
        username: Registry username to use as default
        password: Registry password to use as default

    Output:
        Update yaml file with registry credentials for repository entries where no credentials
        are provided
    """
    with open(repository_yaml_file, encoding="utf-8") as repo_yaml_input:
        repo_yaml_data = yaml.safe_load(repo_yaml_input)
    if "repositories" not in repo_yaml_data:
        LOG.info("Repositories entries not found in yaml file - no updates made")
        return
    updated_repo_list = []
    for repo_entry in repo_yaml_data["repositories"]:
        if "username" not in repo_entry:
            repo_entry["username"] = username
        if "password" not in repo_entry:
            repo_entry["password"] = password
        updated_repo_list.append(repo_entry)
    repo_yaml_data["repositories"] = updated_repo_list
    with open(repository_yaml_file, 'w', encoding="utf-8") as output_file:
        yaml.safe_dump(repo_yaml_data, output_file, default_flow_style=False)


def unzip_file(path_to_zipfile, target_path, file=None):
    """
    Unzip a file.

    Input:
        path_to_zipfile: Path to the file to be unpacked
        target_path: The directory where the unpacked file(s) should be held
        file: The file to be unpacked

    Output:
        target_path: The directory where the unpacked Files/images.txt file should be held
    """
    if not file:
        with ZipFile(path_to_zipfile) as zip_obj:
            zip_obj.extractall(target_path)
    else:
        with ZipFile(path_to_zipfile) as zip_obj:
            zip_obj.extract(file, target_path)


def str_rep(dumper, content):
    """
    Parse multiline strings in yaml files.

    Input:
        dumper: Yaml Dumper instance
        content: Content in Dumper instance

    Output:
        Returns appropriate Dumper instance depending on content
    """
    if '\n' in content:
        return dumper.represent_scalar('tag:yaml.org,2002:str', content, style='|')
    return dumper.org_represent_str(content)


def get_dm_url_and_tag_details(image, image_details_file, properties_file):
    """
    Parse a given file for the deployment manager tag.

    Input:
        image: This is the full image and tag currently set
        image_details_file: this is the file to check for the versio within
        properties_file: This is the file to output the new URL to

    Output:
        Output the full url and the tag in the propertirs file given
    """
    try:
        url = image.split(':')[0]
        set_tag = image.split(':')[1]
        if set_tag == 'default' and os.path.exists(image_details_file):
            with open(image_details_file, 'r', encoding="utf-8") as stream:
                data_loaded = yaml.safe_load(stream)
            registry = data_loaded['images']['eric-oss-deployment-manager']['registry']
            repo_path = data_loaded['images']['eric-oss-deployment-manager']['repoPath']
            name = data_loaded['images']['eric-oss-deployment-manager']['name']
            url = registry + "/" + repo_path + "/" + name
            tag = data_loaded['images']['eric-oss-deployment-manager']['tag']
        else:
            if set_tag == 'default':
                tag = 'latest'
            else:
                tag = set_tag
        # Write the image details out to a file
        LOG.info("Deployment manager Set : %s:%s", url, tag)
        with open(properties_file, "w", encoding="utf-8") as details_file:
            details_file.write("IMAGE=" + url + ":" + tag)
        details_file.close()
    except Exception as ex:
        raise errors.DMVersionFetchError(f"Unable to fetch deployment manager version. Exception thrown: {ex}")


def extract_files_from_archive(archive_file_path, file_to_extract_path,
                               target_directory=None, target_filename=None):
    """
    Extract the given files from the archive into a target directory.

    Input:
        archive_file_path: The archive to extract.
        file_to_extract_path: The file pattern to extract from the archive file.
        target_directory: The optional target directory for the extracted files.
        target_filename: The optional target filename for the extracted files.

    Output:
        A list of extracted files is returned.
    """
    with tempfile.TemporaryDirectory() as directory_name:
        temporary_target_directory = directory_name

    if not target_directory:
        target_directory = temporary_target_directory

    LOG.debug("Extracting file pattern '%s' from '%s' to '%s'",
              file_to_extract_path,
              archive_file_path,
              target_directory)
    archive_file_path_object = Path(archive_file_path)
    if archive_file_path_object.suffix in ['.tgz', '.tar']:
        archive_option_function = tarfile.open
    else:
        archive_option_function = ZipFile

    if not Path(target_directory).exists():
        Path(target_directory).mkdir(parents=True, exist_ok=True)
    with archive_option_function(archive_file_path, 'r') as archive_file_object:
        if archive_file_path_object.suffix in ['.tgz', '.tar']:
            archive_file_name_list = archive_file_object.getnames()
        else:
            archive_file_name_list = archive_file_object.namelist()

        list_of_extracted_files = []
        for file_path_in_archive in archive_file_name_list:
            if re.search(file_to_extract_path, file_path_in_archive):
                LOG.debug("Extracting file '%s'", file_path_in_archive)
                archive_file_object.extract(file_path_in_archive, temporary_target_directory)
                original_extracted_file_path = Path(temporary_target_directory) / Path(file_path_in_archive)
                if target_filename:
                    final_extracted_file_path = shutil.move(original_extracted_file_path,
                                                            target_directory / target_filename)
                else:
                    final_extracted_file_path = original_extracted_file_path
                list_of_extracted_files.append(str(final_extracted_file_path))

    if len(list_of_extracted_files) == 0:
        raise FileNotFoundError("Could not find the file pattern '" + file_to_extract_path +
                                "' in the given archive '" + archive_file_path_object.name + "'")

    return list_of_extracted_files


def populate_artifacts_list(artifacts, artifactory_json_response, regex_expression):
    """
    Populate artifacts list with artifacts retrieved from repo.

    Input:
        artifacts: The empty list of artifacts provided
        artifactory_json_response: The JSON response from artifactory holding artifact information
        regex_expression: The provided regex to match the artifact to a version

    Output:
        The populated artifacts list
    """
    # Check if the response is from the AQL endpoint request, or the Storage endpoint request
    if "results" in artifactory_json_response:
        parent_key = "results"
        child_key = "name"
    else:
        parent_key = "children"
        child_key = "uri"

    for artifact in artifactory_json_response[parent_key]:
        regex = re.match(regex_expression, artifact[child_key].replace("/", ""))
        if regex:
            artifacts.append(artifact[child_key].replace("/", ""))

    return artifacts


def make_artifactory_request(artifactory_api_endpoint, method, functional_user_username, functional_user_password,
                             functional_user_token=None, data=None):
    """
    Send an API request to the Artifactory API.

    Input:
        artifactory_aql_endpoint: AQL API endpoint e.g. https://arm.seli.gic.ericsson.se/artifactory/api/search/aql
        method: The request method, get or post
        functional_user_username: The functional user username used for basic authentication
        functional_user_password: The functional user password used for basic authentication
        functional_user_token: Optional - The functional user token used for bearer authentication
        data: Plain text API request body

    Output:
        artifactory_json_response: The response returned in json format
    """
    try:
        headers = {}
        if use_bearer_token_authentication(functional_user_token):
            headers = {"Authorization": "Bearer " + functional_user_token}
            artifactory_response = requests.request(method, artifactory_api_endpoint, headers=headers, data=data,
                                                    timeout=600)
        else:
            auth = HTTPBasicAuth(functional_user_username, functional_user_password)
            artifactory_response = requests.request(method, artifactory_api_endpoint, auth=auth, data=data,
                                                    timeout=600)
        artifactory_response.raise_for_status()
        artifactory_json_response = artifactory_response.json()
        return artifactory_json_response
    except HTTPError as http_err:
        LOG.error('HTTP error occurred: %s', http_err)
        raise
    except Exception as err:
        LOG.error('Other error occurred: %s', err)
        raise


def use_bearer_token_authentication(functional_user_token):
    """
    Determine if Bearer Token Authentication is to be used.

    Input:
        functional_user_token: The bearer token

    Output:
        Boolean: True or False value to determine whether Bearer Token Authentication is to be used
    """
    if functional_user_token is not None and functional_user_token.strip().upper() != "NONE" \
            and functional_user_token.strip() != "":
        LOG.info("Using Bearer token for API request")
        return True
    LOG.info("Using Basic Auth for API request")
    return False


# pylint: disable=too-many-locals, too-many-statements
def get_latest_artifact_version_from_repo(artifact_repo_url, artifact_name, filter_by_days_past=14,
                                          adp_component=False):
    """
    Write latest artifact version to artifact.properties.

    Input:
        artifact_repo_url: Chart repository URL for artifact
        artifact_name: Name of the artifact to check
        filter_by_days_past: Filter Artifactory response between now and the provided number of days gone past
        adp_component: Boolean to set regex to only check for adp components ('+' in version) if value is True

    Output:
        Writes latest artifact version found to artifact.properties file
    """
    artifacts = []

    LOG.info("Input parameters:")
    LOG.info("artifact_repo_url: %s", artifact_repo_url)
    LOG.info("artifact_name: %s", artifact_name)

    # Read environment variables passed into container from docker run
    functional_user_username = os.environ.get('FUNCTIONAL_USER_USERNAME', None)
    functional_user_password = os.environ.get('FUNCTIONAL_USER_PASSWORD', None)
    functional_user_token = os.environ.get('FUNCTIONAL_USER_TOKEN', None)

    # Fail script if any of the above are empty
    if functional_user_username is None and functional_user_token is None:
        raise Exception("Missing environment variable FUNCTIONAL_USER_USERNAME value")
    if functional_user_password is None and functional_user_token is None:
        raise Exception("Missing environment variable FUNCTIONAL_USER_PASSWORD value")

    # Format helmfile repo url with appropriate endpoint
    artifact_repo_substring = "artifactory/"
    additional_artifactory_api_path = "api/search/aql"
    index_of_substring_end = artifact_repo_url.index(artifact_repo_substring) + len(artifact_repo_substring)

    # The repository to search for the artifact, isolated from the provided artifactory_repo_url
    repo_isolated = artifact_repo_url[index_of_substring_end:].replace("/", "")
    LOG.info("Isolated repo: %s", repo_isolated)

    # The url to send the api request body to
    artifactory_request_url = artifact_repo_url[:index_of_substring_end] + additional_artifactory_api_path
    LOG.info("Artifactory request url: %s", artifactory_request_url)

    # ISO formatted date, generated based on the number of days ago provided from now.
    date_number_of_days_ago = (datetime.now() - timedelta(days=filter_by_days_past)).isoformat()
    LOG.info("%s days ago: %s", filter_by_days_past, date_number_of_days_ago)

    # The aql (Artifactory Query Language) api request
    # JSON part of the body
    json_body = json.dumps({"repo": {"$eq": repo_isolated}, "path": {"$eq": artifact_name}, "created":
                            {"$gt": date_number_of_days_ago}})
    # The full aql plain text payload
    aql_payload = f"items.find({json_body})"
    LOG.info("AQL api request body: %s", aql_payload)

    artifactory_json_response = make_artifactory_request(artifactory_request_url, 'post', functional_user_username,
                                                         functional_user_password, functional_user_token,
                                                         aql_payload)

    # If the previous request came back with nothing, make a request to the storage api and return all artifacts
    if "results" not in artifactory_json_response or len(artifactory_json_response["results"]) == 0:
        additional_artifactory_api_path = "api/storage/"
        artifactory_request_url = artifact_repo_url[:index_of_substring_end] \
            + additional_artifactory_api_path + artifact_repo_url[index_of_substring_end:] + "/" + artifact_name
        LOG.info("Artifactory request url: %s", artifactory_request_url)
        artifactory_json_response = make_artifactory_request(artifactory_request_url, 'get',
                                                             functional_user_username,
                                                             functional_user_password, functional_user_token)
    LOG.info("Response: %s", artifactory_json_response)

    # Extract all artifact names into list (helmfile.tgz files)
    # Only match with components that have a '+' in the version if component is an ADP component
    if adp_component:
        regex_expression = fr"{artifact_name}-(\d*\.\d*\.\d*(\+\d*))\.tgz"
    else:
        regex_expression = fr"{artifact_name}-(\d*\.\d*\.\d*([\+-]\d*)?)\.tgz"

    # Populate the artifacts list
    populate_artifacts_list(artifacts, artifactory_json_response, regex_expression)

    LOG.info("Artifacts found in repo:\n%s", artifacts)
    # Sort to get helmfile artifact with the latest version
    artifacts.sort(key=get_artifact_keys, reverse=True)

    LOG.info("-" * 85)
    LOG.info("Latest artifact version from artifactory is %s", artifacts[0])
    LOG.info("-" * 85)
    # Separate the version number to be written to artifact.properties
    version_number = re.search(fr'{artifact_name}[\+-](.*?).tgz', artifacts[0]).group(1)

    try:
        # Write version to artifact.properties
        with open("artifact.properties", "w", encoding="utf-8") as artifact_properties:
            artifact_properties.write(f"INT_CHART_VERSION:{version_number}")
    except IOError as io_error:
        LOG.error('File write error, could not write to artifact.properties: %s', io_error)
        raise

    return version_number


def convert_to_int_if_number(text):
    """
    Cast a string to an int if it represents a number.

    Input:
        text: String to potentially convert

    Returns
    -------
        An integer variable representing the string number, or the string otherwise

    """
    return int(text) if text.isdigit() else text


def get_artifact_keys(text):
    """
    Sort and get artifact with the latest version.

    Input:
        text: Key to convert to int if possible

    Returns
    -------
        List of converted version keys

    """
    return [convert_to_int_if_number(x) for x in re.split(r'(\d+)', text)]


def compare_included_version_against_latest_version(components_dict):
    """
    Compare component versions in an Application/Helmfile to the latest from the relevant repository.

    Input:
        components_dict: Dictionary containing the name, url and current version of a component

    Output:
        Two files
            component_name_repo_version.csv: Contains name, url, current and latest versions of component
            component_version_mismatch.txt: Outlines the components with a version mismatch
    """
    # Lines to be included in archived files
    version_mismatch_lines = ""
    csv_lines = "Component,Current Version,Latest Version,Repo\n"
    LOG.info("Check against releases dict: %s", json.dumps(components_dict))
    dictionary_list = keys_in_nested_dict(components_dict)
    dictionary_key_list = key_in_nested_dict_removing_last_key(dictionary_list)
    for item in dictionary_key_list:
        # Append Version to the list
        appname = item[-1]
        # Add version key to the dictionary list to get the version
        dictionary_keys_list_version = existing_list_appended_with_extra_value(item, 'version')
        # Retrieve the version from the dictionary using a dictionary and a list of keys
        version = nested_dictionary_read(components_dict, dictionary_keys_list_version)
        dictionary_keys_list_repository = existing_list_appended_with_extra_value(item, 'url')
        repository = nested_dictionary_read(components_dict, dictionary_keys_list_repository)

        if repository:
            if repository is not None and repository.startswith("http"):
                try:
                    # Check if Application/Microservice is an ADP component, indicated by '+' in the version
                    if '+' in version:
                        get_latest_artifact_version_from_repo(repository, appname, True)
                    else:
                        get_latest_artifact_version_from_repo(repository, appname)
                    with open("artifact.properties", "r", encoding="utf-8") as artifact_properties:
                        version_details_line = artifact_properties.readline()
                        latest_version = version_details_line.split(":")[1]
                        LOG.info("App Latest Version: %s", latest_version)
                except HTTPError as http_err:
                    latest_version = "Not Found"
                    LOG.warning("App Latest Version: %s", latest_version)
                    LOG.exception(http_err)
            else:
                LOG.info("No URL for: %s", str(appname))
                latest_version = "Not Found"
                repository = "Not Found"

            csv_lines += appname + "," + version + "," + latest_version + "," + repository + "\n"

            LOG.info("App Name: %s", appname)
            LOG.info("App URL: %s", repository)
            LOG.info("App Version: %s", version)

            # Compare the current version to the latest version
            if version != latest_version:
                LOG.warning("Version Mismatch - Current version: %s New Version: %s", version, latest_version)
                version_mismatch_lines += "Version mismatch: " + appname + "\n"
                version_mismatch_lines += "Current version: " + version + "\n"
                version_mismatch_lines += "Latest version: " + latest_version + "\n\n"

        else:
            LOG.warning("URL not in component list for Appname: %s", appname)
    # Write the details to the files
    with open("component_version_mismatch.txt", "w", encoding="utf-8") as file:
        file.writelines(version_mismatch_lines)
    with open("component_name_repo_version.csv", "w", encoding="utf-8") as file:
        file.writelines(csv_lines)


def copy_file(source, dest, comment):
    """
    Use  to populate the test folder with the appropriate files.

    Input:
        source: directory to send the files to
        dest: this is the file to be moved to the test area.
        comment: a comment to set if an exception is thrown
    """
    try:
        shutil.copy(source, dest)
    except FileNotFoundError as exc:
        raise FileNotFoundError(comment) from exc


# pylint: disable=too-many-nested-blocks,unused-variable
def search_for_file(path, search_string, ignore_string_list=None):
    """
    Use to search for a string in a given patch and return a list.

    Inputs:
        path: directory to search within
        search_string: string to search for
        ignore_string_list: A list of files that should be ignore if found with the search_string.
    Output:
        list with all the found files with the given string
    """
    file_list = []
    for subdir, dirs, files in os.walk(path):
        for file in files:
            if search_string in file:
                skip = False
                if ignore_string_list is not None:
                    for ignore_string in ignore_string_list:
                        if ignore_string in file:
                            skip = True
                if not skip:
                    LOG.info(os.path.join(subdir, file))
                    file_list.append(os.path.join(subdir, file))
    return file_list


def build_yaml(yaml_file):
    """
    Return a dictionary of the yaml passed to it.

    Inputs:
        yaml_file: full path to a file that holds the yaml
    Output:
        dictionary of the yaml file
    """
    try:
        with open(yaml_file, "r", encoding="utf-8") as yaml_file_content:
            return yaml.safe_load(yaml_file_content)
    except FileNotFoundError:
        return {}


def write_yaml(yaml_dict, path_to_file):
    """
    Write a yaml dictionary to a given file.

    Inputs:
        yaml_dict : yaml dictionary to be parsed
        path_to_file : file to write the content to
    Outputs:
        File created with the content of yaml_dict
    """
    LOG.info("Creating %s", path_to_file)
    with open(path_to_file, 'w', encoding="utf-8") as yaml_file:
        yaml.dump(yaml_dict, yaml_file)
    with open(path_to_file, "r", encoding="utf-8") as yaml_file:
        LOG.debug(yaml_file.read())


def logical_or_merge_optionality_dicts(optionality_dicts):
    """
    Merge the optionality dicts doing a logical or on the enabled key values.

    Inputs:
        optionality_dicts : Dictionary of all the optionality files
    Output:
        Optionality files all merged together
    """
    merged_optionality_dict = {}
    for optionality_dict in optionality_dicts:
        logical_or_extend_dict(merged_optionality_dict, optionality_dict)
    return merged_optionality_dict


def logical_or_extend_dict(extend_me, extend_by):
    """
    Merge the contents of a dictionary into an existing dictionary, recursively.

    Inputs:
        extend_me: this is a dictionary that will be merged with extend_by
        extend_by: this is a dictionary of the content to be added to extend_me
    Output:
        optionality file with all the services that are set to true in the charts added to the overall optionality file
    """
    if isinstance(extend_me, dict):
        for key, value in extend_by.items():
            if key in extend_me:
                if value is True:
                    extend_me[key] = value
                else:
                    logical_or_extend_dict(extend_me[key], value)
            else:
                extend_me[key] = value
    else:
        extend_me += extend_by


def log_string_to_a_file_as_variable(directory, filename, message):
    """
    Log a string to a file for later reference as a variable.

    Inputs:
        directory: the working directory to add the file to
        filename: name of the file to create.
        message: message to be logged
    Output:
        output of a file with the message string set as a value.
    """
    log_file = os.path.join(directory, filename)
    # Regular expression ensures that all is on one line and remove multiple blank spaces with an _
    message_stripped = re.sub(r'\s+', '_', str(message).replace("\n", "\t"))
    with open(log_file, "w", encoding="utf-8") as new_file:
        new_file.write("MESSAGE=" + str(message_stripped))


def replace_content_after_string(line, search_string, replacement):
    """
    Replace a section of the line after a certain string.

    Inputs:
        line: the line to search
        search_string: What to search for
        replacement: what to replace after the search string

    Output
        string returned with the replaced line
    """
    pattern = re.compile(f"({search_string}).*")
    replaced_line = re.sub(pattern, f"\\1 {replacement}", line)
    return replaced_line


def parse_inca_chart_details_file(chart_details_file, execution_type):
    """
    Parse an input file that is in the structure INCA can read.

    Inputs:
        chart_details_file: stores the content of the helm chart details that INCA can read.
        execution_type: used to decide if values should be read from an input file, i.e. set_baseline a new baseline

    Output:
        Content of the file in 3 lists, giving chart name version and repo
    """
    input_chart_name = []
    input_chart_version = []
    input_chart_repo = []
    LOG.debug("Content of Input file")
    if execution_type == "set_baseline":
        try:
            with open(chart_details_file, 'r', encoding="utf-8") as file:
                data = file.readlines()
                LOG.debug(data)
                for line in data:
                    if "CHART_NAME" in line:
                        input_chart_name = [item.strip() for item in line.split("=", 1)[1].split(",")]
                        LOG.debug("INPUT_CHART_NAME List: %s", input_chart_name)
                    if "CHART_VERSION" in line:
                        input_chart_version = [item.strip() for item in line.split("=", 1)[1].split(",")]
                        LOG.debug("INPUT_CHART_VERSION List: %s", input_chart_version)
                    if "CHART_REPO" in line:
                        input_chart_repo = [item.strip() for item in line.split("=", 1)[1].split(",")]
                        LOG.debug("INPUT_CHART_REPO List: %s", input_chart_repo)
        except FileNotFoundError as exception:
            LOG.error("Error: Unable to open %s", chart_details_file)
            raise exception
    return input_chart_name, input_chart_version, input_chart_repo


def merge_dicts(data_dict1, data_dict2):
    """
    Merge two dictionary content together, used mainly for nested dictionaries.

    Inputs:
        data_dict1 : Dictionary to be updated.
        data_dict2 : Dictionary whose content will be added on top of dictionary 1.

    Output:
        Dictionary with the inputted dictionaries merged together.
    """
    for key in set(data_dict1.keys()).union(data_dict2.keys()):
        if key in data_dict1 and key in data_dict2:
            if isinstance(data_dict1[key], dict) and isinstance(data_dict2[key], dict):
                yield (key, dict(merge_dicts(data_dict1[key], data_dict2[key])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and move on.
                yield (key, data_dict2[key])
        elif key in data_dict1:
            yield (key, data_dict1[key])
        else:
            yield (key, data_dict2[key])


def nested_dictionary_create_and_set_value(data_dict, keys, value, create_missing=True):
    """
    Create a nested dictionary and add the associated values using a list of keys.

    Inputs:
        data_dict : This is the dictionary to apply the values to.
        Keys : this is a list of keys where the values should be added to,
        i.e. [x, y, z] maps to { x: { y: { z: None }} in the dictionary.
        value : value to be added to last key in the "keys" list above, i.e. { x: { y: { z: value }}}
        create_missing : set to true by default, will create the key and value if missing from the dictionary.
    """
    copy_dic = data_dict
    for key in keys[:-1]:
        if key in copy_dic:
            copy_dic = copy_dic[key]
        elif create_missing:
            copy_dic = copy_dic.setdefault(key, {})
        else:
            return data_dict
    if keys[-1] in copy_dic or create_missing:
        copy_dic[keys[-1]] = value
    return data_dict


def nested_dictionary_read(data_dict, map_list):
    """
    Use to get a value from a nested dictionary using a set of keys in a list.

    Inputs:
        data_dict : the dictionary to iterate over
        map_list : The key to search in for the value in a list format

    Output:
        A value from the dictionary according to he keys inputted
    """
    if keys_exists(data_dict, map_list):
        for key in map_list:
            data_dict = data_dict[key]
        return data_dict
    return ""


def keys_exists(data_dict, map_list):
    """
    Use this to ensure the key existed in the nested dictionary.

    Inputs:
        data_dict : the dictionary to iterate over
        map_list : The key to search in for the value in a list format

    Output:
        true if the key is found or false if not found.
    """
    nested_dict = data_dict

    for key in map_list:
        try:
            nested_dict = nested_dict[key]
        except KeyError:
            return False
    return True


# pylint: disable=dangerous-default-value
def keys_in_nested_dict(data_dict, parent=[]):
    """
    Use to get all the keys in the dictionary into a list format.

    Input:
        data_dict : the dictionary to iterate over
        parent : A list of keys to append to, defaults to an empty list

    Output
        A list with all the keys from the dictionary in their nested form
    """
    if not isinstance(data_dict, dict):
        return [tuple(parent)]
    return reduce(list.__add__, [keys_in_nested_dict(v, parent+[k]) for k, v in data_dict.items()], [])


def key_in_nested_dict_removing_last_key(dictionary_list):
    """
    Use to remove the last key from the list of dictionary keys.

    Input:
        dictionary_list : List of dictionary keys.

    Output:
        New List with the last key removed and the list unique
    """
    dictionary_key_list = []
    for item in dictionary_list:
        # Transfer to a list
        new_list = list(item)
        # Remove last entry from list
        del new_list[-1]
        dictionary_key_list.append(new_list)
    return [list(x) for x in set(tuple(x) for x in dictionary_key_list)]


def existing_list_appended_with_extra_value(created_list, appended_with):
    """
    Extend a list with an iputted string, the string will be appended to the end of the list.

    Inputs:
        created_list : This is the list to tbe extended.
        appended_with : A single string to be appended to the end of the list.

    Output:
        new list with the string appended.
    """
    new_list = created_list.copy()
    new_list.append(appended_with)
    return new_list


def convert_yaml_to_json(yaml_file, json_file):
    """
    Convert a yaml file to a given json file.

    Inputs:
        yaml_file : the yaml file to convert to json
        json_file : the outputted json file
    Outputs:
        JSON file created with the content of the converted yaml_file
    """
    LOG.info("Creating %s", json_file)
    with open(yaml_file, 'r', encoding="utf-8") as file:
        configuration = yaml.safe_load(file)

    with open(json_file, 'w', encoding="utf-8") as file:
        json.dump(configuration, file)


def update_yaml_dict_with_key_value_list(yaml_dict, key_value_list):
    """
    Update a dictionary representing site-values yaml with a key/value list.

    Input:
        yaml_dict: Parsed site-values yaml
        key_value_list: Comma separated key/value list

    Returns
    -------
        Updated dictionary with key/value label list
    """
    key_list = key_value_list.split(",")
    for key in key_list:
        branch = yaml_dict
        key_value = key.split("=")
        parts = key_value[0].split(".")
        for part in parts[:-1]:
            branch = branch.setdefault(part, {})
        if key_value[-1].lower() == 'true':
            branch[parts[-1]] = True
        elif key_value[-1].lower() == 'false':
            branch[parts[-1]] = False
        else:
            branch[parts[-1]] = key_value[-1]
    return yaml_dict
