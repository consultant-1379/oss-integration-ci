"""Module to analyze helm charts to extract microservice chart details."""
import io
import logging
import os
import json
import tarfile
import pathlib
import yaml
import packaging
import requests
from requests.auth import HTTPBasicAuth
from packaging.version import InvalidVersion

from . import cihelm
from . import helmfile
from . import utils
from . import helm
from . import jira

LOG = logging.getLogger(__name__)

HELMFILE = "/usr/bin/helmfile"
HELM = "/usr/bin/helm"
CURRENT_WORKING_DIRECTORY = os.getcwd()
HELMFILE_BUILD_OUTPUT = CURRENT_WORKING_DIRECTORY + "/helmfile_build_output.txt"
HELMFILE_JSON = CURRENT_WORKING_DIRECTORY + "/helmfile_services_json_content.json"
HELMFILE_SHARED_SERVICES_JSON = CURRENT_WORKING_DIRECTORY + "/helmfile_shared_services_json_content.json"
HELMFILE_SHARED_IMAGES = CURRENT_WORKING_DIRECTORY + "/helmfile_shared_images.json"


def clean_up():
    """Ensure all created files are removed if not needed."""
    if os.path.exists(HELMFILE_BUILD_OUTPUT):
        os.remove(HELMFILE_BUILD_OUTPUT)
    if os.path.exists(HELMFILE_JSON):
        os.remove(HELMFILE_JSON)
    if os.path.exists(HELMFILE_SHARED_SERVICES_JSON):
        os.remove(HELMFILE_SHARED_SERVICES_JSON)
    if os.path.exists(CURRENT_WORKING_DIRECTORY + "/compiledContent_crds-helmfile.yaml"):
        os.remove(CURRENT_WORKING_DIRECTORY + "/compiledContent_crds-helmfile.yaml")
    if os.path.exists(CURRENT_WORKING_DIRECTORY + "/compiledContent_helmfile.yaml"):
        os.remove(CURRENT_WORKING_DIRECTORY + "/compiledContent_helmfile.yaml")
    if os.path.exists(CURRENT_WORKING_DIRECTORY + "/helmServicesContent.txt"):
        os.remove(CURRENT_WORKING_DIRECTORY + "/helmServicesContent.txt")


def execute_helmfile_with_build_command(state_values_file, path_to_helmfile):
    """
    Command to execute the helmfile using the build command.

    Input:
        state_values_file, state values file to use to pass into the helmfile to populate its details i.e. site values
        path_to_helmfile, Path to the helmfile to test against

    Output:
        File that contains all the build info for the helmfile
    """
    # /usr/bin/helmfile --environment build --state-values-file ./build-environment/tags_true.yaml
    # --file ./helmfile.yaml build > test.yaml
    helmfile_build_output = helmfile.run_helmfile_command(path_to_helmfile, state_values_file,
                                                          None, '--environment', 'build', 'build')
    helmfile_build_output = io.StringIO(helmfile_build_output.stdout.decode('utf-8'))

    # Write the output of the command to file
    with open(HELMFILE_BUILD_OUTPUT, "w", encoding="utf-8") as helmfile_build_file:
        for line in helmfile_build_output:
            helmfile_build_file.write(line)


def write_helm_service_content_file(name, version, product_number, file_name):
    """
    Write the applications or microservices details out to a file.

    Inputs:
        name: name of application or service
        version: version of the service
        product_number: product number of the service
        file_name: The file name to write the service content out to.
    """
    with open(file_name, 'a', encoding="utf-8") as helm_services_content_file:
        helm_services_content_file.write(name + ':' + version + ':' + product_number + '\n')


def get_repository_details_from_parent_chart(dir_name, service_name):
    """
    Use to get the repository details from service charts parent Chart.yaml.

    Inputs:
        dir_name : service chart directory to start the search from.
        service_name : the name of the service chart

    Output:
        A str referencing the repository details
    """
    repository = ""
    parent_directory = ""
    loop_continue = 1
    check_for_chart_yaml = dir_name
    while loop_continue > 0:
        check_for_chart_yaml = os.path.dirname(check_for_chart_yaml)
        LOG.info("Check directory for Chart.yaml : %s", check_for_chart_yaml)
        if os.path.isfile(os.path.join(check_for_chart_yaml, 'Chart.yaml')):
            parent_directory = check_for_chart_yaml
            loop_continue = 0
        if check_for_chart_yaml == '/':
            loop_continue = 0
    if parent_directory:
        LOG.debug("PARENT SERVICE CHART : %s", parent_directory)
        with open(os.path.join(parent_directory, 'Chart.yaml'), 'r', encoding="utf-8") as file:
            parent_chart_configuration = yaml.safe_load(file)
            LOG.debug("PARENT CHART DETAILS : %s", parent_chart_configuration)
        parent_dependencies = parent_chart_configuration['dependencies']
        for dependencies in parent_dependencies:
            LOG.debug("PARENT CHART DEPENDENCIES %s", dependencies)
            if service_name in dependencies.values():
                repository = dependencies['repository']
                break
    return repository


# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def parse_and_write_chart_dependencies_to_file(chart_root_dir, chart_repo, output_file):  # noqa: C901
    """
    Get the name, version, and directory for all chart dependencies.

    Input:
        chart_root_dir: Directory root for searching for Chart.yaml files
        chart_repo: This the repo the application chart was downloaded from.
        output_file: The file name to write the content of dependencies to.

    Output:
        Populates services dictionary
    """
    LOG.info("Analyzing Application Chart directory: %s", chart_root_dir)
    chart_files = list(pathlib.Path().glob(chart_root_dir + '/**/*Chart.yaml'))
    application_dict = {}
    for chart_file in chart_files:
        LOG.info("Checking Service Chart : %s", chart_file)
        product_number = ""
        version = ""
        # Set the service chart of the Chart.yaml file
        # eric-oss-pm-stats-calc-handling/charts/eric-data-engine-sk/Chart.yaml -->
        # eric-oss-pm-stats-calc-handling/charts/eric-data-engine-sk
        dir_name = os.path.dirname(chart_file)
        # Set the service name
        # eric-oss-pm-stats-calc-handling/charts/eric-data-engine-sk/ --> eric-data-engine-sk
        service_name = os.path.basename(dir_name)

        # Get details from services chart Chart.yaml
        with open(chart_file, 'r', encoding="utf-8") as file:
            chart_configuration = yaml.safe_load(file)
            LOG.debug("CHART_DETAILS : %s", chart_configuration)
        if 'version' in chart_configuration:
            version = chart_configuration["version"]

        # Get details from service chart eric-product-info.yaml
        with open(os.path.join(dir_name, 'eric-product-info.yaml'), 'r', encoding="utf-8") as file:
            eric_product_info_configuration = yaml.safe_load(file)
            LOG.debug("ERIC_PRODUCT_INFO_DETAILS : %s", eric_product_info_configuration)
        if 'productName' in eric_product_info_configuration:
            product_name = eric_product_info_configuration['productName']
            if service_name not in product_name:
                LOG.warning("Product name %s does not match chart name %s", product_name, service_name)
        if 'productNumber' in eric_product_info_configuration:
            product_number = eric_product_info_configuration["productNumber"]

        # Get Repository details from service chart parent Chart.yaml
        directory_list_length = len(dir_name.split('/'))
        if directory_list_length > 2:
            repository = get_repository_details_from_parent_chart(dir_name, service_name)
        else:
            repository = chart_repo

        # Set the list of keys that should be added to the dictionary
        dictionary_keys_list = dir_name.split('/')
        if 'charts' in dictionary_keys_list:
            dictionary_keys_list = [i for i in dictionary_keys_list if i != 'charts']

        # Extend the keys list for the additional keys to be added to the dictionary
        dictionary_keys_list_location = utils.existing_list_appended_with_extra_value(dictionary_keys_list, 'location')
        dictionary_keys_list_version = utils.existing_list_appended_with_extra_value(dictionary_keys_list, 'version')
        dictionary_keys_list_product_number = utils.existing_list_appended_with_extra_value(dictionary_keys_list,
                                                                                            'product_number')
        dictionary_keys_list_product_name = utils.existing_list_appended_with_extra_value(dictionary_keys_list,
                                                                                          'product_name')
        dictionary_keys_list_repository = utils.existing_list_appended_with_extra_value(dictionary_keys_list,
                                                                                        'url')

        # Create/update a dictionary with a value according to the keys entered as a list.
        service_dict = {}
        service_dict = utils.nested_dictionary_create_and_set_value(service_dict,
                                                                    dictionary_keys_list_location,
                                                                    dir_name)
        service_dict = utils.nested_dictionary_create_and_set_value(service_dict,
                                                                    dictionary_keys_list_version,
                                                                    version)
        service_dict = utils.nested_dictionary_create_and_set_value(service_dict,
                                                                    dictionary_keys_list_product_number,
                                                                    product_number)
        service_dict = utils.nested_dictionary_create_and_set_value(service_dict,
                                                                    dictionary_keys_list_product_name,
                                                                    product_name)
        service_dict = utils.nested_dictionary_create_and_set_value(service_dict,
                                                                    dictionary_keys_list_repository,
                                                                    repository)
        # Write service content to a file
        write_helm_service_content_file(service_name, version, product_number, output_file)
        # Merge the individual service dictionary on top of the application dictionary
        application_dict = dict(utils.merge_dicts(service_dict, application_dict))

    LOG.debug("Individual Application %s Dictionary : %s", chart_root_dir, application_dict)
    return application_dict


def fetch_helmfile_charts_and_find_microservices(releases_dict, path_to_helmfile):
    """
    Take the content of the generated JSON and download the associated charts.

    Input:
        releases_dict: Dictionary Content of the helmfile according the state file inputted
        path_to_helmfile: path to the helmfile under test

    Output:
        Required charts downloaded
    """
    LOG.info("Fetching charts using the helmfile information")
    # Fetching the charts using cihelm
    # pylint: disable=no-name-in-module, no-member
    cihelm.cihelm_fetch(path_to_helmfile)
    microservice_dict = {}
    LOG.info("Analyzing charts...")
    for key in releases_dict:
        if 'url' in releases_dict[key].keys():
            appname = releases_dict[key]['name']
            version = releases_dict[key]['version']
            repository = releases_dict[key]['url']
            # Extract the content of the Chart tar file
            with tarfile.open(appname + "-" + version + '.tgz', 'r') as chart_tarfile:
                chart_tarfile.extractall('.')
            services = \
                parse_and_write_chart_dependencies_to_file('./' + appname + '/',
                                                           repository,
                                                           output_file='helmServicesContent.txt')
            microservice_dict = dict(utils.merge_dicts(microservice_dict, services))
    return microservice_dict


# pylint: disable=too-many-branches
def get_shared_images(path_to_helmfile, microservice_skip_list=""):
    """
    Obtain the shared images between each chart in the helmfile.

    Input:
        path_to_helmfile: Path to the helmfile under test

    Output:
        File that contains the image information from the helmfile
    """
    # flake8: noqa: C901
    helmfile_releases = []
    helmfile_releases.append(f"{path_to_helmfile.split('/')[-2]}/")
    with open(path_to_helmfile, "r", encoding="utf-8") as helmfile_file:
        for line in helmfile_file.readlines():
            if "name:" in line:
                helmfile_releases.append(line.split("name:")[1].strip())
    image_info_list = []
    for release in helmfile_releases:
        if os.path.exists(release):
            image_info = helm.get_image_info_from_helm_chart(release)
            for image in image_info:
                image_info_list.append(image)

    shared_images_dict = {}
    for value in image_info_list:
        source, image, version = value.split(":")

        skip_microservice_found = False
        if microservice_skip_list:
            for microservice in microservice_skip_list.split(","):
                if microservice in source:
                    skip_microservice_found = True
        if skip_microservice_found:
            continue

        if image not in shared_images_dict:
            shared_images_dict[image] = {
                "Number of occurrences": 1,
                "Different versions and frequency": {version: 1},
                "Sources of occurrences": {source: version}
            }
        else:
            shared_images_dict[image]["Number of occurrences"] += 1

            if version in shared_images_dict[image]["Different versions and frequency"]:
                shared_images_dict[image]["Different versions and frequency"][version] += 1
            else:
                shared_images_dict[image]["Different versions and frequency"][version] = 1

            if source not in shared_images_dict[image]["Sources of occurrences"].keys():
                shared_images_dict[image]["Sources of occurrences"].update({source: version})

    shared_images_dict = dict(sorted(shared_images_dict.items(), key=lambda x: x[1]['Number of occurrences'],
                              reverse=True))
    LOG.info("Writing shared images JSON file: %s", HELMFILE_SHARED_IMAGES)
    with open(HELMFILE_SHARED_IMAGES, "w", encoding="utf-8") as shared_images_fh:
        json.dump(shared_images_dict, shared_images_fh, indent=4, sort_keys=False)

    generate_image_version_changes_file(shared_images_dict)


def generate_image_version_changes_file(shared_images_dict):
    """
    Get the charts that are not using the latest version of an image.

    Input:
        shared_images_dict: A dictionary containing the shared images

    Output:
        All of the charts that need to have image versions updated
    """
    LOG.info("Collecting the charts that need to be updated...")

    # Get the latest version of each image
    images_and_latest_version_dict = get_images_and_latest_versions(shared_images_dict)

    # Find which charts are not using the latest version
    chart_and_images_to_be_updated_dict = get_charts_that_need_updated_images(shared_images_dict,
                                                                              images_and_latest_version_dict)

    with open("./outdated_images_per_chart.json", "w", encoding="utf-8") as json_file:
        json.dump(chart_and_images_to_be_updated_dict, json_file, indent=4, sort_keys=False)


def get_images_and_latest_versions(shared_images_dict):
    """
    Get the images and latest versions.

    Input:
        shared_images_dict: The dictionary containing the shared images

    Returns
    -------
        A dictionary with each image and the maximum version

    """
    LOG.info("Getting the latest versions of each image...")
    images_and_latest_version_dict = {}
    for image in shared_images_dict:
        if shared_images_dict[image]["Number of occurrences"] > 1:
            docker_registry = image.split("/")[0]
            image_repository = image.split(docker_registry + "/")[1]
            versions_list_raw = get_image_versions_from_docker_repo(docker_registry, image_repository)
            version_list_clean = []
            for version in versions_list_raw:
                try:
                    version_list_clean.append(packaging.version.parse(version))
                except InvalidVersion:
                    continue
            max_version = max(version_list_clean)
            images_and_latest_version_dict[image] = max_version
    return images_and_latest_version_dict


def get_image_versions_from_docker_repo(docker_registry, image_repository):
    """
    Get the versions of an image from a Docker repository.

    Input:
        docker_registry: The Docker registry (e.g., armdocker.rnd.ericsson.se)
        image_repository: The path to the Docker repository

    Returns
    -------
        A list of all of the specified image versions

    """
    username = os.environ.get('FUNCTIONAL_USER_USERNAME', None)
    password = os.environ.get('FUNCTIONAL_USER_PASSWORD', None)
    image_info = requests.get(f"https://{docker_registry}/v2/{image_repository}/tags/list",
                              auth=HTTPBasicAuth(username, password), timeout=600)
    return image_info.json()["tags"]


def get_charts_that_need_updated_images(shared_images_dict, images_and_latest_version_dict):
    """
    Get each chart that contains an image that is not the most recent version.

    Input:
        shared_images_dict: The dictionary containing the shared images
        images_and_latest_version_dict: The dictionary with the images and maximum versions

    Returns
    -------
        A dictionary with each chart and the images that need to be updated

    """
    LOG.info("Adding the outdated chart info to JSON...")
    chart_and_images_to_be_updated_dict = {}
    for image in shared_images_dict:
        if image in images_and_latest_version_dict:
            for chart in shared_images_dict[image]["Sources of occurrences"]:
                image_version = shared_images_dict[image]["Sources of occurrences"][chart]
                image_version = packaging.version.parse(image_version)
                latest_version = images_and_latest_version_dict[image]
                if image_version != latest_version:
                    if image_version.post:
                        image_version = f"{image_version.base_version}-{image_version.post}"
                    if images_and_latest_version_dict[image].post:
                        latest_version = f"{latest_version.base_version}-{latest_version.post}"
                    image_name = image.split("/")[-1]
                    dict_input = {
                        image_name: {
                            "Repo": image,
                            "Current version": str(image_version),
                            "Latest version": str(latest_version)
                        }
                    }
                    subchart_list = chart.split("/charts/")
                    _combine_chart_info_to_json(chart_and_images_to_be_updated_dict, subchart_list, dict_input)
    return chart_and_images_to_be_updated_dict


def _combine_chart_info_to_json(chart_image_collection_dict, subchart_list, input_dict):
    """
    Combine the chart and image information into a JSON file.

    Input:
        chart_image_collection_dict: The dictionary that will contain all of the information
        subchart_list: A list of each chart and subchart that contains the image
        input_dict: A dictionary containing the image information

    Output:
        A dictionary containing all of the chart and image information
    """
    parent_chart = subchart_list[0]
    next_chart = subchart_list[1] if len(subchart_list) > 1 else None
    if parent_chart not in chart_image_collection_dict.keys():
        chart_image_collection_dict.update({parent_chart: {}})
    for key, value in chart_image_collection_dict.items():
        if parent_chart == key:
            if "charts" in value:
                if not next_chart:
                    value.update(input_dict)
                    break
                if next_chart not in value["charts"]:
                    chart_dict = {next_chart: {}}
                    value["charts"].update(chart_dict)
                subchart_list.pop(0)
                next_layer_in_dict = value["charts"]
                _combine_chart_info_to_json(next_layer_in_dict, subchart_list, input_dict)
            else:
                if next_chart:
                    charts_dict = {"charts": {}}
                    value.update(charts_dict)
                    chart_dict = {next_chart: {}}
                    value["charts"].update(chart_dict)
                    subchart_list.pop(0)
                    next_layer_in_dict = value["charts"]
                    _combine_chart_info_to_json(next_layer_in_dict, subchart_list, input_dict)
                else:
                    value.update(input_dict)


def create_outdated_images_tickets(path_to_helmfile, create_tickets, skip_list="", microservice_skip_list=""):
    """
    Create Jira tickets for each chart with outdated images.

    Input:
        path_to_helmfile: The path to the helmfile
        create_tickets: A boolean value to determine whether tickets should be created or not
        skip_list: A comma-separated list of applications to be skipped for ticket creation
        microservice_skip_list: A comma-separated list of microservices to be skipped for ticket creation

    Output:
        A jira ticket for every chart containing outdated images
    """
    # Read environment variables passed into container from docker run
    functional_user_username = os.environ.get('FUNCTIONAL_USER_USERNAME', None)
    functional_user_password = os.environ.get('FUNCTIONAL_USER_PASSWORD', None)

    cihelm.cihelm_fetch(path_to_helmfile)
    with open(path_to_helmfile, "r", encoding="utf-8") as helmfile_file:
        for line in helmfile_file.readlines():
            if "name:" in line:
                name = line.split("name:")[1].strip()
            if "version:" in line:
                version = line.split("version:")[1].strip()
                utils.extract_tar_file(f"{name}-{version}.tgz", '.')
    get_shared_images(path_to_helmfile, microservice_skip_list)

    with open("outdated_images_per_chart.json", "r", encoding="utf-8") as json_file:
        outdated_dict = json.load(json_file)
    _create_outdated_images_text_file(outdated_dict)

    if create_tickets.upper() == "TRUE":
        with open("outdated-ticket-file.txt", "r", encoding="utf-8") as ticket_file:
            _send_outdated_image_tickets(ticket_file.readlines(), skip_list,
                                         functional_user_username, functional_user_password)


# pylint: disable=unused-variable
def _create_outdated_images_text_file(outdated_dict, parent_chart=""):
    """
    Create a text file for charts with outdated images.

    Input:
        outdated_dict: The dictionary containing the outdated tickets information
        parent_chart: An optional parameter for the parent chart of the chart bein processed

    Output:
        A text file of information relating to charts and their outdated images
    """
    for chart in outdated_dict:
        for key, value in outdated_dict[chart].items():
            if key != "charts":
                chart_path = f"{parent_chart}/{chart}"[1:]
                text_input = (f"Chart: {chart_path}, Image: {outdated_dict[chart][key]['Repo']}, "
                              f"Latest version: {outdated_dict[chart][key]['Latest version']}, "
                              f"Current version: {outdated_dict[chart][key]['Current version']}")
                with open("outdated-ticket-file.txt", "a", encoding="utf-8") as ticket_file:
                    ticket_file.writelines(f"{text_input}\n")
        if "charts" in outdated_dict[chart]:
            subcharts = outdated_dict[chart]["charts"]
            _create_outdated_images_text_file(subcharts, parent_chart + "/" + chart)


# pylint: disable=consider-using-dict-items
def _send_outdated_image_tickets(ticket_info, skip_list, username, password):
    """
    Send the Jira tickets based on the information provided.

    Input:
        ticket_info: A list containing outdated image information
        skip_list: A comma-separated list of applications to be skipped for ticket creation
        username: The username to connect to Jira
        password: The password to connect to Jira

    Output:
        A number of Jira tickets based on the information provided
    """
    skip_list = skip_list.split(",")
    ticket_info_dict = {}
    for value in ticket_info:
        base_chart = value.split(",")[0].split(" ")[1].split("/")[0]
        if base_chart not in ticket_info_dict:
            ticket_info_dict[base_chart] = [value.strip()]
        else:
            ticket_info_dict[base_chart].append(value.strip())
    ticket_info_dict = jira.remove_duplicate_charts_from_tickets_dict(ticket_info_dict, username, password)
    if len(ticket_info_dict) < 1:
        LOG.info("There are no new tickets to be created. Exiting gracefully...")
        return
    LOG.info("Creating tickets for the following charts: %s", ", ".join(value for value in ticket_info_dict))
    for chart in ticket_info_dict:
        if chart in skip_list:
            LOG.info("Skipping the creation of a ticket for %s due to the skip list", chart)
            continue
        summary = f"Ticket raised for outdated images within {chart}"
        description = "The following charts/subcharts contained outdated images that need to be updated:\n\n"
        for value in ticket_info_dict[chart]:
            description += f"{value}\n\n"
        extra_values = {
            "customfield_24317": {"id": "478958"}
        }
        jira.create_jira(project="IDUN", issue_type="Support", summary=summary,
                         description=description, team_id="479994", labels=["OUTDATED_IMAGE_TICKET"],
                         priority="Major", username=username, password=password,
                         extra_values_dict=extra_values)


def fetch_shared_microservices_from_helmfile():
    """Read through the content of the generated HELMFILE json file and write out the shared microservices."""
    # To hold the name of the shared microservice and its number of occurrences.
    microservice_count_dict = {}

    with open(HELMFILE_JSON, encoding="utf-8") as apps:

        applications = json.load(apps)

        # Iterate over the applications
        for application in applications:

            microservices = applications.get(application)

            # Iterate over the microservices that make up the selected application and increment its count value
            for microservice in microservices:

                microservice_count_dict[microservice] = microservice_count_dict.get(microservice, 0) + 1

    shared_ms = {key: value for key, value in microservice_count_dict.items() if value > 1}

    LOG.info("Writing shared services JSON file: %s", HELMFILE_SHARED_SERVICES_JSON)
    with open(HELMFILE_SHARED_SERVICES_JSON, "w", encoding="utf-8") as shared_ms_fh:
        json.dump(shared_ms, shared_ms_fh, indent=4, sort_keys=True)


def fetch_microservice_details(state_values_file, path_to_helmfile):
    """
    Fetch microservice details from helmfile.

    Input:
        state_values_file: Yaml file with site-values for helmfile rendering
        path_to_helmfile: Full path to helmfile to analyze

    Output:
        Writes JSON file representing dictionary of microservice dependency information
    """
    LOG.info('Inputted Parameters')
    LOG.info('state_values_file: %s', state_values_file)
    LOG.info('path_to_helmfile: %s', path_to_helmfile)

    clean_up()
    execute_helmfile_with_build_command(state_values_file, path_to_helmfile)
    helmfile.split_content_from_helmfile_build_file()
    # Generate empty dictionaries
    releases_dict = {}
    # Empty csar dict for use with common function gather_release_and_repo_info
    csar_dict = {}
    # Iterate over all the compiledContent_* files and generate a release Dictionary that holds
    # the chart, version, repo etc. info for all the releases within the Helmfiles
    for filename in os.listdir(CURRENT_WORKING_DIRECTORY):
        if filename.startswith("compiledContent_"):
            helmfile.gather_release_and_repo_info(filename, releases_dict, csar_dict, "true")

    # Fetch the charts
    microservice_dict = fetch_helmfile_charts_and_find_microservices(releases_dict, path_to_helmfile)

    app_json = json.dumps(microservice_dict, indent=4, sort_keys=True)
    # Output full Helmfile JSON to a file for later use
    LOG.info("Writing JSON file %s", HELMFILE_JSON)
    with open(HELMFILE_JSON, "w", encoding="utf-8") as full_json_file:
        full_json_file.write(app_json)

    # Fetch shared microservices
    fetch_shared_microservices_from_helmfile()


def compare_microservice_versions_in_application(state_values_file, path_to_helmfile, chart_name, chart_repo,
                                                 chart_version):
    """
    Compare Microservice versions in an Application to the latest from the relevant repository.

    Input:
        state_values_file: Yaml file with site-values for building the netrc file from the helmfile
        path_to_helmfile: Full path to helmfile for building the netrc file from the helmfile
        chart_name: Name of the application chart
        chart_repo: Repository where the application chart is stored
        chart_version: Version of the application chart to download

    Output:
        Two files
            component_name_repo_version.csv: Contains name, url, current and latest versions of microservice
            component_version_mismatch.txt: Outlines the microservices with a version mismatch
    """
    # List of strings to be masked by on-screen prints
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])

    # Download the chart
    deps = [(chart_repo, chart_version, chart_name)]
    cwd = os.getcwd()
    netrc = helmfile.build_netrc_file_with_repo_credentials_from_helmfile(state_values_file, path_to_helmfile,
                                                                          workspace=cwd)
    # pylint: disable=no-member
    cihelm.fetch(deps, netrc, mask, cwd, False)

    # Extract the content of the Chart tar file
    utils.extract_tar_file(chart_name + "-" + chart_version + '.tgz', '.')
    # Populate the services dict with the Microservice information for the given chart name
    microservice_dict = \
        parse_and_write_chart_dependencies_to_file('./' + chart_name + '/',
                                                   chart_repo,
                                                   output_file='helmServicesContent.txt')
    utils.compare_included_version_against_latest_version(microservice_dict)
