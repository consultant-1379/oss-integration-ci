"""Module for ADP Enabler cihelm."""

import json
import logging
import os
import subprocess
import shutil
from bs4 import BeautifulSoup
from lib import utils
from lib import cmd_common
from lib import helm


LOG = logging.getLogger(__name__)
TEST_FOLDER = "/test-files"
CURRENT_WORKING_DIRECTORY = os.getcwd()
IMAGE_INFORMATION_LIST = CURRENT_WORKING_DIRECTORY + "/image_information_list.json"
IMAGE_INFORMATION_STRING_LIST_FILE = CURRENT_WORKING_DIRECTORY + "/image_information_list.txt"


def helm_lint(chart, site_values_template):
    """
    Calls the helm lint against the application under test

    Input:
        chart: the chart that the tests should be executed against
        site_values_template: populated site values used with the chart
    """
    LOG.info("Parameters entered")
    LOG.info("Chart : %s", chart)
    LOG.info("Populated Site Values Template : %s", site_values_template)
    cmd = "helm lint " + chart + " --values " + site_values_template
    mask = []
    response = cmd_common.execute_command(cmd, mask, verbose=True)
    if int(response.get_return_code()) != 0:
        LOG.info(response.get_stdout())
        raise Exception("See failure(s) above")


def yaml_lint_application_chart(chart, site_values_template, yamllint_config, template_file, yamllint_log_file):
    """
    Performs yamllint against an application chart given a yamllint configuration file

    Input:
        chart: Chart that the tests should be executed against
        site_values_template: Populated site values used with the chart
        yamllint_config: Path to Yamllint Configuration File which extends rules when running the yamllint command
        template_file: Path where helm template output will be saved to
        yamllint_log_file: Path where yamllint output will be saved to
    """
    LOG.info("Parameters entered")
    LOG.info("Chart : %s", chart)
    LOG.info("Populated Site Values Template : %s", site_values_template)
    LOG.info("Yamllint Configuration File: %s", yamllint_config)
    LOG.info("Helm Template Output File: %s", template_file)
    LOG.info("Yamllint Output File: %s", yamllint_log_file)

    helm_template_cmd = "helm template " + chart + " -f " + site_values_template + " > " + template_file
    mask = []
    response_helm_template_cmd = cmd_common.execute_command(helm_template_cmd, mask, verbose=True)
    if int(response_helm_template_cmd.get_return_code()) != 0:
        LOG.info(response_helm_template_cmd.get_stdout())
        raise Exception("See failure(s) above")

    yamllint_cmd_output_to_log = "yamllint -c " + yamllint_config + " " + template_file + " > " + yamllint_log_file
    mask = []
    cmd_common.execute_command(yamllint_cmd_output_to_log, mask, verbose=True)

    yamllint_cmd_output_to_console = "yamllint -c " + yamllint_config + " " + template_file
    mask = []
    response_yamllint_cmd = cmd_common.execute_command(yamllint_cmd_output_to_console, mask, verbose=True)
    if int(response_yamllint_cmd.get_return_code()) != 0:
        LOG.info(response_yamllint_cmd.get_stdout())
        raise Exception("See failure(s) above")


def yaml_lint_helmfile(helmfile_full_path, site_values_template, yamllint_config, template_file,
                       yamllint_log_file):
    """
    Performs yamllint against a helmfile given a yamllint configuration file

    Input:
        helmfile_full_path: Helmfile that the tests should be executed against
        site_values_template: Populated site values used with the helmfile
        yamllint_config: Path to Yamllint Configuration File which extends rules when running the yamllint command
        template_file: Path where helmfile template output will be saved to
        yamllint_log_file: Path where yamllint output will be saved to
    """
    LOG.info("Parameters entered")
    LOG.info("Helmfile Full Path : %s", helmfile_full_path)
    LOG.info("Populated Site Values Template : %s", site_values_template)
    LOG.info("Yamllint Configuration File: %s", yamllint_config)
    LOG.info("Helmfile Template Output File: %s", template_file)
    LOG.info("Yamllint Output File: %s", yamllint_log_file)

    command_part_1 = "helmfile --environment build --state-values-file " + site_values_template
    command_part_2 = " -f " + helmfile_full_path + " template > " + template_file

    helmfile_template_cmd = command_part_1 + command_part_2

    mask = []
    response_helmfile_template_cmd = cmd_common.execute_command(helmfile_template_cmd, mask, verbose=True)
    if int(response_helmfile_template_cmd.get_return_code()) != 0:
        LOG.info(response_helmfile_template_cmd.get_stdout())
        raise Exception("See failure(s) above")

    yamllint_cmd_output_to_log = "yamllint -c " + yamllint_config + " " + template_file + " > " + yamllint_log_file
    mask = []
    cmd_common.execute_command(yamllint_cmd_output_to_log, mask, verbose=True)

    yamllint_cmd = "yamllint -c " + yamllint_config + " " + template_file
    mask = []
    response_yamllint_cmd = cmd_common.execute_command(yamllint_cmd, mask, verbose=True)
    if int(response_yamllint_cmd.get_return_code()) != 0:
        LOG.info(response_yamllint_cmd.get_stdout())
        raise Exception("See failure(s) above")


def helmfile_static_tests(helmfile, site_values_template, common_skip_file, specific_skip_file, check_specific_content):
    """
    Calls the chart validate tests against the given helmfile.

    Input:
        helmfile: the helmfile that the tests should be executed against
        site_values_template: populated site values used with the chart
        common_skip_file: Full path to the common skip list
        specific_skip_file: Full path to the specific skip list for the project
        check_specific_content: Full path to the replica check list for the project

    Output:
        report.html: holds the results of the execution.
    """
    # Check is there a skip_list.json and a common_skip_list.json file
    LOG.info("Parameters entered")
    LOG.info("Helmfile : %s", helmfile)
    LOG.info("Populated Site Values Template : %s", site_values_template)
    LOG.info("Common Skip List : %s", common_skip_file)
    LOG.info("Specific Skip List : %s", specific_skip_file)
    LOG.info("Check Specific Content List : %s", check_specific_content)
    utils.copy_file(specific_skip_file,
                    os.path.join(TEST_FOLDER, "skip_list.json"),
                    "Issue with fetching the Specific skip list file")
    utils.copy_file(check_specific_content,
                    os.path.join(TEST_FOLDER, "check_specific_content.json"),
                    "Issue with fetching the Check Specific Content list file")
    utils.copy_file(common_skip_file,
                    os.path.join(TEST_FOLDER, "common_skip_list.json"),
                    "Issue with fetching the Common skip list")
    utils.copy_file(site_values_template,
                    os.path.join(TEST_FOLDER, "site_values.yaml"),
                    "Issue with fetching the Populated site values template")
    shutil.copytree(helmfile, os.path.join(TEST_FOLDER, "helmfile"))

    # execute the pytest
    cmd_report = "pytest -s --log-cli-level=INFO --html=report.html"
    cmd_location = " --self-contained-html /ci-scripts/etc/testsuite/helmfile-validator"
    cmd = cmd_report + cmd_location
    mask = []
    response = cmd_common.execute_command(cmd, mask, verbose=True)
    if int(response.get_return_code()) != 0:
        LOG.info(response.get_stderr())
        raise Exception("See failure(s) above")
    edit_html_file("report.html")


def static_tests(chart, site_values_template, common_skip_file, specific_skip_file):
    """
    Calls the chart validate tests against the given helm chart.

    Input:
        chart: the chart that the tests should be executed against
        site_values_template: populated site values used with the chart
        common_skip_file: Full path to the common skip list
        specific_skip_file: Full path to the specific skip list for the project

    Output:
        report.html: holds the results of the execution.
    """
    # Check is there a skip_list.json and a common_skip_list.json file
    LOG.info("Parameters entered")
    LOG.info("Chart : %s", chart)
    LOG.info("Populated Site Values Template : %s", site_values_template)
    LOG.info("Common Skip List : %s", common_skip_file)
    LOG.info("Specific Skip List : %s", specific_skip_file)
    utils.copy_file(specific_skip_file,
                    os.path.join(TEST_FOLDER, "skip_list.json"),
                    "Issue with fetching the Specific skip list file")
    utils.copy_file(common_skip_file,
                    os.path.join(TEST_FOLDER, "common_skip_list.json"),
                    "Issue with fetching the Common skip list")
    utils.copy_file(site_values_template, os.path.join(TEST_FOLDER, "site_values_template.yaml"),
                    "Issue with fetching the Populated site values template")
    utils.copy_file(chart, os.path.join(TEST_FOLDER, "test_chart.tgz"),
                    "Issue with fetching Specified chart")

    # execute the pytest
    cmd = "pytest --html=report.html --self-contained-html /ci-scripts/etc/testsuite/helm-chart-validator"
    mask = []
    response = cmd_common.execute_command(cmd, mask, verbose=True)
    if int(response.get_return_code()) != 0:
        LOG.info(response.get_stderr())
        raise Exception("See failure(s) above")
    edit_html_file("report.html")


def edit_html_file(html_file_path):
    """
    Used to clarify that no resources were found during the pytest.

    Input:
        html_file_path: The path to the report.html file.

    Output:
        An edited report.html file with "No Resources" specified for certain tests.
    """
    if os.path.exists(html_file_path):
        LOG.info("Editing %s to clarify test cases where the resources under test were not found...", html_file_path)
        with open(html_file_path, "r+", encoding="utf-8") as file:
            lines = file.read()
            soup = BeautifulSoup(lines, 'html.parser')
            logs = soup.find_all('div', class_='log')
            for log in logs:
                if 'got empty parameter set' in log.get_text():
                    col_result = log.find_previous('td', class_='col-result')
                    if col_result:
                        col_result.string = "No Resources Found (Skipped)"
            file.write(soup.prettify())
    else:
        LOG.info("HTML file path not found: %s", html_file_path)


def validate_chart_against_schema_file_tests(chart, schema_file_directory, search_string, ignore_strings=None):
    """
    Calls the chart validate tests against the given helm chart.

    Input:
        chart: the chart that the tests should be executed against
        schema_file_directory: directory to search for the schema files to test against
        search_string: The string that is used to search for the files in the given directory
        ignore_strings: A comma separated list of strings to ignore if found with the search_string
    """
    template_failed = False
    if ignore_strings and ignore_strings != "None":
        ignore_string_list = ignore_strings.split(",")
    else:
        ignore_string_list = None
    LOG.info("Chart under test : %s", str(chart))
    LOG.info("Schema File Directory : %s", str(schema_file_directory))
    LOG.info("Search String : %s", str(search_string))
    LOG.info("Ignore List : %s", str(ignore_string_list))
    file_list = utils.search_for_file(schema_file_directory, search_string, ignore_string_list)
    # execute the pytest
    for file in file_list:
        cmd = "helm template " + chart + " -f " + file
        mask = []
        response = cmd_common.execute_command(cmd, mask)
        if int(response.get_return_code()) != 0:
            template_failed = True
    if template_failed is True:
        raise Exception("See failure(s) above")


def run_negative_schema_tests(chart_full_path, negative_files_dictionary):
    """
    Runs schema tests for the negative test files.

    Input:
        chart_full_path: The path to the helm chart
        negative_files: A dictionary containing the paths to the negative schema YAML and text files

    Returns
    -------
        The number of passed and failed tests
    """
    number_of_fails, number_of_passes = 0, 0
    for yaml_file, output_file in negative_files_dictionary.items():
        helm_template_output = subprocess.run(['helm', 'template', "-f", yaml_file, chart_full_path],
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        with open(output_file, "r", encoding="utf-8") as sample_output_file:
            sample_output = sample_output_file.read().strip().splitlines()
        # Get the sample output as a sorted list
        sample_output.sort()
        LOG.debug("Sample List Output : %s", str(sample_output))
        # Get command returned output as a sorted list
        returned_output = helm_template_output.stdout.decode("utf-8").strip().splitlines()
        returned_output.sort()
        LOG.debug("Command List Returned Output : %s", str(returned_output))
        if helm_template_output.returncode == 0:
            LOG.info("Fail (the helm command was expected to fail but it didn't with %s)", yaml_file.split("/")[-1])
            number_of_fails += 1
            continue
        if sample_output != returned_output:
            LOG.info("fail (the output from from %s using %s did not match the helm template)",
                     output_file.split("/")[-1], yaml_file.split("/")[-1])
            LOG.info("Output Received")
            LOG.info(str(helm_template_output.stdout.decode("utf-8").strip()))
            number_of_fails += 1
            continue
        number_of_passes += 1
        LOG.info("Testing %s (Expected Failure Output file %s) pass",
                 output_file.split("/")[-1], yaml_file.split("/")[-1])
    return number_of_passes, number_of_fails


def run_positive_schema_tests(chart_full_path, positive_files):
    """
    Runs schema tests for the positive test files.

    Input:
        chart_full_path: The path to the helm chart
        positive_files: A list containing the paths to the positive schema files

    Returns
    -------
        The number of passed and failed tests
    """
    number_of_fails, number_of_passes = 0, 0
    for file in positive_files:
        helm_template_output = subprocess.run(['helm', 'template', "-f", file, chart_full_path],
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if helm_template_output.returncode != 0:
            LOG.info("fail (The output from %s did not pass)", file.split("/")[-1])
            number_of_fails += 1
            continue
        LOG.info("Testing %s (Expected Success) pass", file.split("/")[-1])
        number_of_passes += 1
    return number_of_passes, number_of_fails


# pylint: disable=too-many-locals
def schema_tests(chart_full_path, positive_and_negative_schema_files_full_path):
    """
    Runs schema tests against the given helm chart.

    Input:
        chart_full_path: The path to the helm chart
        positive_and_negative_schema_files_full_path: The path to the positive and negative testing files
    """
    number_of_negative_passes, number_of_negative_fails = 0, 0
    path_to_negative_files = os.path.join(str(positive_and_negative_schema_files_full_path), "negative")
    if os.path.exists(path_to_negative_files):
        negative_files = [os.path.join(path_to_negative_files, file) for file in os.listdir(path_to_negative_files)]
        yaml_output_files_dictionary = {}
        for yaml_file in [file for file in negative_files if file.endswith(".yaml")]:
            for output_file in [file for file in negative_files if file.endswith(".txt")]:
                if output_file.split("/")[-1].replace("_expected_errors.txt", "") == \
                        yaml_file.split("/")[-1].replace(".yaml", ""):
                    yaml_output_files_dictionary[yaml_file] = output_file
        number_of_negative_passes, number_of_negative_fails = \
            run_negative_schema_tests(chart_full_path, yaml_output_files_dictionary)

    number_of_positive_passes, number_of_positive_fails = 0, 0
    path_to_positive_files = os.path.join(str(positive_and_negative_schema_files_full_path), "positive")
    if os.path.exists(path_to_positive_files):
        positive_files = [os.path.join(path_to_positive_files, file) for file in os.listdir(path_to_positive_files)]
        number_of_positive_passes, number_of_positive_fails = \
            run_positive_schema_tests(chart_full_path, positive_files)

    total_number_of_passes = number_of_negative_passes + number_of_positive_passes
    total_number_of_fails = number_of_negative_fails + number_of_positive_fails
    LOG.info("Number of passes - %s Number of fails - %s", total_number_of_passes, total_number_of_fails)
    if total_number_of_fails != 0:
        raise Exception("There were failures among the schema files")


def add_experimental_permissions_for_docker_config_file(docker_file_full_path):
    """
    Write experimental permissions to the docker config file and returns the new docker config file.

    Input:
        chart_path: Path to the chart that is used to gather the docker config file path
    -------
    Returns a Docker Config json file with experimental enabled
    """
    if os.path.exists(docker_file_full_path):
        with open(docker_file_full_path, 'r+', encoding="utf-8") as docker_config_file:
            docker_config_file_values = json.load(docker_config_file)
            docker_config_file_values['experimental'] = "enabled"

            docker_config_file.seek(0, 0)
            json.dump(docker_config_file_values, docker_config_file)
            docker_config_file.truncate()
    else:
        raise Exception("Docker Config File Path given does not exist")


def check_eric_product_info_images(chart_path):
    """
    Write all image information found within the eric-product-info.yaml files to a json file

    Input:
        chart_path: The path to the helm chart
    -------
    """
    # Getting the chart to point to the local chart
    if "helmfile" in chart_path:
        chart_full_path = chart_path
        chart_name = "helmfile"
        LOG.info("Chart Path: %s", chart_full_path)
    else:
        workdir_path = chart_path.split('.bob')[0]
        chart_name = chart_path.split('/')[-1]
        chart_full_path = ""

        if chart_name == "__helmChartDockerImageName__":
            chart_name = "eric-oss-integration-chart-chassis"

        chart_full_path = workdir_path + chart_name
        LOG.info("Chart Path: %s", chart_full_path)

    if os.path.exists(chart_full_path):
        # Declare Lists that are needed to get image information from integration chart
        integration_chart_image_list = []
        integration_chart_list_of_image_info = []

        # Declare Dictionary that will include all image information from integration chart and subcharts
        chart_dictionary = {}

        # Gather chart name and images from the Integration Chart Eric Product Info File
        integration_chart_image_list.append(helm.get_image_info_from_helm_chart(chart_full_path))
        integration_chart_list_of_image_info = get_image_info_list(integration_chart_image_list)
        chart_dictionary[chart_name] = integration_chart_list_of_image_info

        with open(IMAGE_INFORMATION_LIST, "w", encoding="utf-8") as image_information_list_json_file:
            json.dump(chart_dictionary, image_information_list_json_file, indent=4, sort_keys=False)
    else:
        raise Exception("Chart Path given does not exist")


def get_image_info_list(image_list):
    """
    Return a list of image information of dictionaries of image information based on image list provided

    Input:
        image_list: List of images within the eric-product-info file
    -------
    Return a list of dictionaries which contain image information on each image in the chart
    """
    # Declare Image Information List
    image_information_list = []

    # Get inner list of images within the image_list
    image_list_split = image_list[0]

    # Keep track of images added to the dictionary
    image_tracker_list = []

    # For each image given within the information list, gather image information
    for image in image_list_split:
        # Declare Dictionary Specific to this image
        specific_image_information_dictionary = {}

        # Image Information Gathered From the Full Path
        image_information_gathered_from_full_path = image.split(':')

        # Find specific values (Image Registry, Image Repo Path, Image Name, Image Version)
        image_path = image_information_gathered_from_full_path[1]
        image_version = image_information_gathered_from_full_path[2]
        image_name = image_path.split("/")[-1]

        full_image_path = image_path + ":" + image_version

        if full_image_path not in image_tracker_list:
            image_tracker_list.append(full_image_path)
            specific_image_information_dictionary[image_name] = full_image_path

            # Add the Image Information Dictionary to the Image Information List which will be added to the dictionary
            image_information_list.append(specific_image_information_dictionary)

    convert_list_to_string = "\n".join(image_tracker_list)

    with open(IMAGE_INFORMATION_STRING_LIST_FILE, "w", encoding="utf-8") as image_information_list_text_file:
        image_information_list_text_file.write(convert_list_to_string)

    return image_information_list
