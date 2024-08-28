"""Module for handling helmfile."""
# pylint: disable=cyclic-import
import logging
import os
import io
import subprocess
import shutil
import json
import glob
from pathlib import Path
from functools import cache
import errno
import yaml

from .netrc_common import Netrc
from . import utils
from . import cmd_common
from . import helm
from . import cihelm


LOG = logging.getLogger(__name__)
HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
CWD = os.getcwd()
HELMFILE_BUILD_OUTPUT = CWD + "/helmfile_build_output.txt"
yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str
yaml.add_representer(str, utils.str_rep, Dumper=yaml.SafeDumper)


def run_helmfile_command(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
    """
    Execute a helmfile command.

    Input:
        helmfile_path: File path to helmfile
        site_values_file_path: File path to site-values Yaml to use for rendering helmfile templates
        config_file_path: Optional kube config file.  Set to None if not required (default context)
        *helmfile_args: List of arguments to pass to helmfile command

    Returns
    -------
        Helmfile command object (after running command)

    """
    if site_values_file_path:
        LOG.info("Running with Site values file : %s", site_values_file_path)
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
    else:
        LOG.info("Running without Site values file")
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path]
    command_and_args_list.extend(helmfile_args)

    if config_file_path:
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env={'KUBECONFIG': config_file_path})
    return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_helmfile_command_to_remove(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
    """
    Execute a helmfile command.

    Input:
        helmfile_path: File path to helmfile
        site_values_file_path: File path to site-values Yaml to use for rendering helmfile templates
        config_file_path: Optional kube config file.  Set to None if not required (default context)
        *helmfile_args: List of arguments to pass to helmfile command

    Returns
    -------
        Helmfile command object (after running command)

    """
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])
    command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                             '--file', helmfile_path,
                             '--state-values-file', site_values_file_path]
    command_and_args_list.extend(helmfile_args)
    cmd = ' '.join(map(str, command_and_args_list))
    if config_file_path:
        cmd = cmd + " --kubeconfig " + config_file_path
    response = cmd_common.execute_command(cmd, mask=mask, verbose=True)

    if response.returncode != 0:
        raise Exception("Helmfile Command failed")
    return response.stdout


# pylint: disable=too-many-arguments
def download_helmfile(chart_name, chart_version, chart_repo, username, password, token=None):
    """
    Download the project helmfile tar file given.

    Input:
        chart_name: name of the helmfile chart to download
        chart_version: version of the helmfile to download
        chart_repo: repository where the chart is stored
        username: username to access the repo
        password: password to access the repo
        token: identity token required to access the artifactory repo

    Output:
        Downloaded project helmfile tarball
    """
    full_chart_name = chart_name + "-" + chart_version + ".tgz"
    full_url = chart_repo + "/" + chart_name + "/" + full_chart_name
    LOG.info("Downloading: %s", str(full_url))
    utils.download_file(full_url, full_chart_name, username, password, 'wb', token=token)


def fetch_csar_details_from_helmfile(state_values_file, path_to_helmfile):
    """
    Gather all the csar details from the project helmfile tar file.

    Input:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml

    Output:
        csar_dict: dictionary which holds all the application details associated to a CSAR
    """
    csar_dict = {}
    for build_data in build(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile):
        for csar in build_data['releases']:
            if "csar" not in csar.get("labels", {}):
                continue
            csar_dict[csar["name"]] = csar["labels"]['csar']
    LOG.debug("CSAR dictionary returned %s", str(csar_dict))
    return csar_dict


def associate_repo_details_to_charts(state_values_file, path_to_helmfile):
    """
    Associate repo details to charts details from the project helmfile tar file.

    Input:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml

    Output:
        repo_associate_to_chart_dict: dictionary which holds all the chart and their associate repos
    """
    repo_associate_to_chart_dict = {}
    for build_data in build(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile):
        for charts in build_data['releases']:
            if "csar" not in charts.get("labels", {}):
                continue
            # Get the chart name and the repo name it is associated to
            chart_name = charts.get("name")
            repo_name = charts.get("chart").split('/')[0]
            repo_url = None
            for repositories in build_data['repositories']:
                if repositories["name"] == repo_name:
                    repo_url = repositories["url"]
                    break
            if repo_url:
                repo_associate_to_chart_dict[chart_name] = repo_url
            else:
                raise Exception(f"Unable to find repository reference for {chart_name}")
    LOG.debug("Repo Associate to Chart dictionary return %s", str(repo_associate_to_chart_dict))
    return repo_associate_to_chart_dict


def fetch_name_version_repo_details_from_helmfile(state_values_file, path_to_helmfile, only_enabled_releases=False):
    """
    Get the dependencies from a helm file.

    Inputs:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml
        only_enabled_releases: Set to True to filter out releases which would not be installed given the site values.

    Returns
    -------
        result: A list which holds all the Helmfile dependencies.
                Example of returned value:
                [('https://my.foo.se/artifactory/proj-my-repo/', '1.0.0+14', 'eric-my-gs')]

    """
    result = []

    if only_enabled_releases:
        release_list = helmfile_list(state_values_file, path_to_helmfile)
        # Detect what keys should be used when filtering out releases, depending on the helmfile version in use.
        # Older helmfile versions didn't have an 'installed' key in the helmfile list json output.
        if any('installed' in release for release in release_list):
            release_keys_to_filter_using = ['installed', 'enabled']
        else:
            release_keys_to_filter_using = ['enabled']
    else:
        release_list = []
        release_keys_to_filter_using = []

    for build_data in build(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile):
        repos = build_data['repositories']
        for release in build_data['releases']:
            release_should_be_filtered_out = False
            for release_key in release_keys_to_filter_using:
                if any(release_list_item['name'] == release['name'] and release_list_item[release_key] is not True
                       for release_list_item in release_list):
                    release_should_be_filtered_out = True
                    break

            if release_should_be_filtered_out:
                LOG.debug('Filtering out release %s as its not enabled given the site values provided',
                          release['name'])
            else:
                LOG.debug('Not filtering out release %s as its enabled given the site values provided',
                          release['name'])
                repo_key = release['chart'].split('/')[0]
                for repo in repos:
                    if repo['name'] == repo_key:
                        result.append((repo['url'], release['version'], release['name']))
                        break
    LOG.debug("Helmfile Dependencies Returned %s", str(result))
    return result


def build_netrc_file_with_repo_credentials_from_helmfile(state_values_file, path_to_helmfile, workspace=CWD):
    """
    Build a netrc file with the repo credentials.

    Inputs:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml
        workspace: Used to set the directory where to create the .netrc file, default current working directory.

    Output:
        File generated on the working directory ./.netrc with the repo credentials
    """
    netrc = Netrc(path=workspace)
    for build_data in build(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile):
        for repo in build_data['repositories']:
            if 'username' in repo:
                netrc.add_login(utils.get_remote_host(repo['url']),
                                repo['username'], repo['password'])
    return netrc


def clean_up_repositories_yaml_file(path_to_repositories_yaml_file):
    """
    Remove lines from repositories.yaml that are not json compatible.

    Inputs:
        path_to_repositories_yaml_file: location of the repositories.yaml file.

    Output:
        New repositories yaml file created that can be parsed using JSON.
    """
    try:
        with open(os.path.join(path_to_repositories_yaml_file, 'repositories.yaml'), "r", encoding="utf-8") as file:
            lines = file.readlines()
        with open(os.path.join(path_to_repositories_yaml_file, 'repositories_new.yaml'), "w", encoding="utf-8") as file:
            for line in lines:
                if "GERRIT" not in line.strip("\n"):
                    file.write(line)
    except FileNotFoundError as exception:
        LOG.error("Error: Unable to open repositories.yaml, within %s", path_to_repositories_yaml_file)
        raise exception


def generate_dictionary_of_repositories_yaml_file(path_to_repositories_yaml_file):
    """
    Read the content of the repositories.yaml to a dictionary.

    Inputs:
        path_to_repositories_yaml_file: location of the repositories.yaml file.

    Output:
        repositories_dict: dictionary with the content of the repositories.yaml file.
    """
    with open(os.path.join(path_to_repositories_yaml_file, 'repositories_new.yaml'), "r", encoding="utf-8") as file:
        repositories_dict = yaml.load(file, Loader=yaml.CSafeLoader)
        LOG.debug("Content of Repositories.yaml")
        LOG.debug(str(repositories_dict))
    return repositories_dict


# pylint: disable=too-many-locals too-many-statements)
def get_base_baseline(path_to_helmfile,  # noqa: C901
                      execution_type,
                      project_file_name,
                      input_file,
                      output_file,
                      get_crds=True):
    """
    Add chart names and their version to the artifact.properties file.

    Inputs:
        path_to_helmfile: Path to the helmfile.yaml file.
        execution_type: to set the type of execution, options set_baseline or get_baseline
        project_file_name: This is the project file name to check if set within the helmfiles
        input_file: stores the content of the helm chart details to swap for current version if any is supplied.
        output_file: stores the output of the script execution
        get_crds: If set to true will gather all the CRD helmfile details also

    Outputs:
        output_file: generated with the details from the executed command.
    """
    LOG.info("INPUTTED COMMANDS")
    LOG.info("PATH TO HELMFILE: %s", path_to_helmfile)
    LOG.info("EXECUTION TYPE: %s", execution_type)
    LOG.info("INPUT FILE: %s", input_file)
    LOG.info("OUTPUT FILE: %s", output_file)
    LOG.info("GET CRDS: %s", get_crds)

    if not os.path.isfile(os.path.join(path_to_helmfile, "helmfile.yaml")):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                os.path.join(path_to_helmfile, "helmfile.yaml"))

    # Parse the input file and break the name version and repo into separate lists
    input_chart_name, input_chart_version, input_chart_repo = utils.parse_inca_chart_details_file(input_file,
                                                                                                  execution_type)

    # Execute, helmfile list against the helmfile
    helmfile_build_output = run_helmfile_command(os.path.join(path_to_helmfile, "helmfile.yaml"),
                                                 None,
                                                 None,
                                                 'list')
    helmfile_build_output = helmfile_build_output.stdout.decode('utf-8')
    LOG.debug("Helmfile list output %s", helmfile_build_output)
    if get_crds:
        crds_helmfile_build_output = run_helmfile_command(os.path.join(path_to_helmfile, "crds-helmfile.yaml"),
                                                          None,
                                                          None,
                                                          'list')
        crds_helmfile_build_output = crds_helmfile_build_output.stdout.decode('utf-8')
        # Concatenate two strings together
        helmfile_build_output = helmfile_build_output + crds_helmfile_build_output
    # Generate a list of the inputted strings
    helmfile_list_output = helmfile_build_output.strip().splitlines()
    # Remove lines from repositories.yaml that are not json compatible
    clean_up_repositories_yaml_file(path_to_helmfile)

    # Read the content of the repositories.yaml to a dictionary
    repositories_dict = generate_dictionary_of_repositories_yaml_file(path_to_helmfile)

    # Gather the chart details to write to a file
    charts = []
    baseline_chart_name = []
    baseline_chart_version = []
    baseline_chart_repo = []
    for line in helmfile_list_output:
        line = line.strip()
        chart_data = line.split()
        if "NAME" in chart_data:
            continue
        LOG.debug("Helm list output : %s", chart_data)
        chart_name = chart_data[0]
        # Check does the release have a project specific label attached
        if project_file_name and project_file_name != "None":
            if list(filter(lambda x: "project" in x, chart_data)):
                LOG.debug("Project label found")
                # Check the label to see if the project is listed if not skip
                # The project is not listed, so it is not a base component for the project.
                project_details = ''.join(list(filter(lambda x: project_file_name in x, chart_data)))
                if project_file_name not in project_details:
                    LOG.info("Skipping retrieval of %s for project %s", chart_name, project_file_name)
                    continue

        # If there were inputted chart details entered, these need to be swapped to generate a new baseline
        if chart_name in input_chart_name:
            LOG.debug("Found Inputted Chart Name: %s", chart_name)
            chart_name_index = input_chart_name.index(chart_name)
            chart_version = input_chart_version[chart_name_index]
            chart_repo = input_chart_repo[chart_name_index]
        else:
            chart_version = chart_data[-1]
            repo_search_string = chart_data[-2].split("/")[0]
            LOG.debug("Repo Search String : %s", repo_search_string)
            for item in repositories_dict["repositories"]:
                LOG.debug("Iterate over items in repositories.yaml : %s", item['name'])
                if item['name'] == repo_search_string:
                    LOG.debug("Found URL : %s", item['url'])
                    chart_repo = item['url']
                    break
            LOG.debug("Repo match Search String: %s", chart_repo)
        charts.append(chart_name + "_name" + "=" + chart_name)
        charts.append(chart_name + "_version" + "=" + chart_version)
        charts.append(chart_name + "_repo" + "=" + chart_repo)
        baseline_chart_name.append(chart_name)
        baseline_chart_version.append(chart_version)
        baseline_chart_repo.append(chart_repo)

    LOG.info("\n---------- Charts in helmfile ----------")
    with open(output_file, "a", encoding="utf-8") as artifacts_file:
        for chart in charts:
            LOG.info("Chart found: %s", chart)
            LOG.debug("Writing %s to %s\n", chart, output_file)
            artifacts_file.writelines(chart + "\n")
        artifacts_file.writelines("BASE_PLATFORM_BASELINE_CHART_NAME=" + (", ".join(baseline_chart_name)) + "\n")
        artifacts_file.writelines("BASE_PLATFORM_BASELINE_CHART_VERSION=" +
                                  (", ".join(baseline_chart_version)) +
                                  "\n")
        artifacts_file.writelines("BASE_PLATFORM_BASELINE_CHART_REPO=" + (", ".join(baseline_chart_repo)) + "\n")


def get_app_version_from_helmfile(state_values_file, path_to_helmfile, tags_set_to_true_only):
    """
    Add chart names and their version to the artifact.properties file.

    Inputs:
        state_values_file: Path to the site-values file
        path_to_helmfile: Path to the helmfile.yaml file
        tags_set_to_true_only: A boolean value to indicate whether only enabled charts
                               are added to the artifact.properties file
    """
    LOG.info("STATE_VALUES_FILE: %s", state_values_file)
    LOG.info("PATH_TO_HELMFILE: %s", path_to_helmfile)
    helmfile_build_output = run_helmfile_command(path_to_helmfile, state_values_file,
                                                 None, '--environment', 'build', 'list')
    helmfile_build_output = io.StringIO(helmfile_build_output.stdout.decode('utf-8'))
    skip_tags = ["false", "eric-crd-ns"]

    # These needed_number_of_values variables are used to indicate which charts should
    # be added to the artifact.properties file. Only charts with a version are added,
    # so any charts without this value (e.g., eric-cncs-oss-pre-config) are not added to
    # the artifact.properties file. Charts with all necessary values in the newer
    # helmfile (e.g., containing a "label" value) should have 6 values,
    # whereas the older helmfile has 5 values
    with open(path_to_helmfile, "r", encoding="utf-8") as helmfile:
        needed_number_of_values = 5
        for line in helmfile:
            if "labels" in line:
                needed_number_of_values = 7
                break

    charts = []
    for line in helmfile_build_output:
        chart_data = line.split()
        if "NAME" in chart_data:
            continue
        if len(chart_data) == needed_number_of_values:
            if tags_set_to_true_only == "true" and any(value in skip_tags for value in chart_data):
                continue
            charts.append(chart_data[0] + "=" + chart_data[-1])

    LOG.info("\n---------- Charts in helmfile ----------\n")

    for chart in charts:
        LOG.info("Chart found: %s", chart)
        LOG.info("Writing %s to artifact.properties...\n", chart)
        with open("artifact.properties", "a", encoding="utf-8") as artifacts_file:
            artifacts_file.writelines(chart + "\n")


def update_crd_helmfile(helmfile_path):
    """
    Update the crds-helmfile.yaml file.

    Input:
        helmfile_path: Path to the crds-helmfile.yaml file
    """
    with open(helmfile_path, "r", encoding='utf-8') as crds_helmfile:
        lines = crds_helmfile.readlines()
        # pylint: disable=consider-using-enumerate
        for index in range(0, len(lines)):
            if "tags" in lines[index]:
                lines[index] = "    installed: true\n"
    with open(helmfile_path, "w", encoding='utf-8') as crds_helmfile:
        crds_helmfile.writelines(lines)


def get_single_app_version_from_helmfile(path_to_helmfile, app_name):
    """
    Get the version of a specific application in a helmfile.

    Input:
        path_to_helmfile: The path to the helmfile
        app_name: The name of the application for the desired version

    Returns
    -------
        The version of the application (None returned if the application is not found)

    """
    app_version = None
    with open(path_to_helmfile, encoding="utf-8") as helmfile:
        app_found = False
        for line in helmfile:
            if "name: " + app_name in line:
                app_found = True
            if "version" in line and app_found:
                app_version = line.split(":")[-1].strip()
                break
    return app_version


def split_content_from_helmfile_build_file():
    """
    Split content of helmfile build into two files, one for CRD and one for the main helmfile.

    Input:
        HELMFILE_BUILD_OUTPUT, global paramater created within the execute_helmfile_with_build_command function

    Output:
        Two files:
           compiledContent_crds-helmfile.yaml
           compiledContent_helmfile.yaml
    """
    filename = ""
    start = 0
    with open(HELMFILE_BUILD_OUTPUT, "r", encoding="utf-8") as helmfile_build_output:
        for line in helmfile_build_output:
            if "Source" in line:
                filename = line.split('Source: ')[1].rstrip("\n")
                filename = filename.split("/")[-1]
                # pylint: disable=consider-using-with
                file_content = open("compiledContent_" + filename, "w", encoding="utf-8")
                start = 1
            elif '---' == line.strip():
                if start == 1:
                    file_content.close()
                start = 0
            elif start == 1:
                file_content.write(line)


def gather_release_and_repo_info(helmfile_build_file, releases_dict, csar_dict, get_all_images):  # noqa: C901
    """
    Read output of helmfile build and append the appropriate info into a dictionary.

    Input:
        helmfile_build_file: File that contains the helmfile build output for a given helmfile chart
        releases_dict: Empty Dictionary for gather all the associated chart details
        csar_dict: Empty dictionary for gathering the releases and there associated CSAR
        get_all_images: Used to check whether you want to include items that are set to false
                        accoding to the state value used

    Output:
        Dictionary of the release information
    """
    with open(helmfile_build_file, 'r', encoding="utf-8") as build_file:
        values_yaml = yaml.load(build_file, Loader=yaml.CSafeLoader)
    for item in values_yaml['releases']:
        name = item.get('name')
        version = item.get('version')
        chart = item.get('chart')
        namespace = item.get('namespace')
        values = item.get('values')
        installed = item.get('installed')
        condition = item.get('condition')
        # Use the content of the label to build a CSAR list of the files to be created
        labels = item.get('labels')
        if get_all_images == "true":
            if labels is not None:
                for key, value in labels.items():
                    if key == 'csar':
                        csar_dict[name] = value
        elif installed or condition \
                or (installed is None and condition is None):
            if labels is not None:
                for key, value in labels.items():
                    if key == 'csar':
                        csar_dict[name] = value

        releases_dict[name] = {}
        releases_dict[name]['name'] = name
        releases_dict[name]['version'] = version
        releases_dict[name]['chart'] = chart
        releases_dict[name]['labels'] = labels
        releases_dict[name]['installed'] = installed
        releases_dict[name]['condition'] = condition
        releases_dict[name]['namespace'] = namespace
        releases_dict[name]['values'] = values

    # Append the repository information for the release
    for release_name in releases_dict.keys():
        for repo in values_yaml['repositories']:
            release_chart = releases_dict[release_name]['chart']
            repo_name = repo.get('name')
            if repo_name in release_chart:
                repo_url = repo.get('url')
                releases_dict[release_name]['url'] = repo_url

    return releases_dict


def compare_application_versions_in_helmfile(state_values_file, path_to_helmfile):
    """
    Compare Application versions in the Helmfile to the latest from the relevant repository.

    Input:
        state_values_file: Yaml file with site-values for helmfile rendering
        path_to_helmfile: Full path to helmfile to analyze

    Output:
        Two files
           component_name_repo_version.csv: Contains name, url, current and latest versions of application
           component_version_mismatch.txt: Outlines the applications with a version mismatch
    """
    LOG.info("Starting to compare Application versions in the Helmfile")

    # Output the helmfile build info to a file
    execute_helmfile_with_build_command(state_values_file, path_to_helmfile)
    # Split the crd content from the regular content and output to two different files
    split_content_from_helmfile_build_file()

    # Generate empty dictionaries
    releases_dict = {}
    csar_dict = {}

    # Iterate over all the compiledContent_* files and generate a release Dictionary that holds
    # the chart, version, repo etc. info for all the releases within the Helmfiles
    for filename in os.listdir(CWD):
        if filename.startswith("compiledContent_"):
            releases_dict = gather_release_and_repo_info(filename, releases_dict, csar_dict, "true")

    # Compare the versions from the dictionary with the latest versions
    utils.compare_included_version_against_latest_version(releases_dict)


def execute_helmfile_with_build_command(state_values_file, path_to_helmfile):
    """
    Execute the helmfile using the build command.

    Input:
        state_values_file: State values file to use to pass into the helmfile to populate its details i.e. site values
        path_to_helmfile: Path to the helmfile to test against

    Output:
        File that contains all the build info for the helmfile
    """
    helmfile_build_output = run_helmfile_command(path_to_helmfile, state_values_file,
                                                 None, '--environment', 'build', 'build')

    if helmfile_build_output.returncode != 0:
        LOG.info(helmfile_build_output.stderr.decode('utf-8'))
        raise Exception("The helmfile build returned an error")

    helmfile_build_output = io.StringIO(helmfile_build_output.stdout.decode('utf-8'))

    # Write the output of the command to file
    with open(HELMFILE_BUILD_OUTPUT, "w", encoding="utf-8") as helmfile_build_file:
        for line in helmfile_build_output:
            helmfile_build_file.writelines(line)


def download_dependencies(path_to_helmfile, state_values_file, chart_cache_directory=None, only_enabled_releases=True,
                          copy_to_current_directory=False):
    """
    Download the dependencies of the given helmfile, using of whatever tags etc are set in the given state values file.

    Inputs:
        path_to_helmfile: Path to the helmfile.yaml
        state_values_file: Site values file to use when determining the repo details from the helmfile
        chart_cache_directory: An optional directory to cache downloaded dependencies to
        only_enabled_releases: Only pull the charts enabled by the site values file
        copy_to_current_directory: Copy the files from the cache to the current working directory

    Output:
        The path to the directory containing the downloaded dependencies is returned.
    """
    LOG.info('Started downloading the helmfiles dependencies.')
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    elif 'FUNCTIONAL_USER_PASSWORD' in os.environ:
        mask.append(os.environ['FUNCTIONAL_USER_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])
    elif 'FUNCTIONAL_USER_USERNAME' in os.environ:
        mask.append(os.environ['FUNCTIONAL_USER_USERNAME'])
    LOG.debug('Inputted Parameters')
    LOG.debug('path_to_helmfile: %s', path_to_helmfile)
    LOG.debug('Auto Set variables')
    LOG.debug('state_values_file: %s', state_values_file)
    __backup_repositories_yaml(path_to_helmfile=path_to_helmfile)
    deps = fetch_name_version_repo_details_from_helmfile(state_values_file=state_values_file,
                                                         path_to_helmfile=path_to_helmfile,
                                                         only_enabled_releases=only_enabled_releases)
    netrc = build_netrc_file_with_repo_credentials_from_helmfile(state_values_file=state_values_file,
                                                                 path_to_helmfile=path_to_helmfile, workspace=CWD)
    # pylint: disable=no-member
    download_directory = cihelm.dependency_update(deps, netrc, mask, CWD, chart_cache_directory)
    if os.path.exists(CWD + '/.netrc'):
        netrc.remove()
    helm.repo_index(directory_to_index=chart_cache_directory)
    __create_repositories_yaml(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile,
                               chart_cache_directory=chart_cache_directory)
    LOG.info('Completed downloading the helmfiles dependencies to %s.', download_directory)
    if copy_to_current_directory:
        for helm_chart in glob.glob(str(download_directory / Path('*.tgz'))):
            if helm_chart not in os.listdir():
                shutil.copy(helm_chart, os.getcwd())
    return download_directory


@cache
def build(state_values_file, path_to_helmfile):
    """
    Execute the "helmfile build" command against the helmfile.

    Input:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml

    Returns
    -------
        A list of objects that contain all the build info for the helmfile

    """
    LOG.debug("Calling helmfile build")
    helmfile_build_output = run_helmfile_command_to_remove(path_to_helmfile, state_values_file, None, '--environment',
                                                           'build', 'build')
    LOG.debug("Output from helmfile command: %s", helmfile_build_output)
    return list(yaml.load_all(helmfile_build_output, Loader=yaml.CSafeLoader))


@cache
def helmfile_list(state_values_file, path_to_helmfile):
    """
    Execute the "helmfile list" command against the helmfile.

    Input:
        state_values_file: Site values file to use when determining the repo details from the helmfile
        path_to_helmfile: Path to the helmfile.yaml

    Returns
    -------
        A list of objects that contain all the release info for the helmfile

    """
    LOG.debug("Calling helmfile list")
    helmfile_list_output = run_helmfile_command_to_remove(path_to_helmfile, state_values_file,
                                                          None, 'list', '--output', 'json')
    LOG.debug("Output from helmfile command: %s", helmfile_list_output)
    return json.loads(helmfile_list_output)


def __backup_repositories_yaml(path_to_helmfile):
    """
    Backup / restore the repositories.yaml to allow reruns of functions without errors.

    Input:
        path_to_helmfile: Path to the helmfile.yaml

    Output:
        Writes the repositories.yaml and repositories.yaml.backup files.
    """
    if (Path(path_to_helmfile).parent / 'repositories.yaml.backup').exists():
        LOG.debug("Restoring repositories.yaml from the backup repositories.yaml.backup")
        shutil.copy(str(Path(path_to_helmfile).parent / 'repositories.yaml.backup'),
                    str(Path(path_to_helmfile).parent / 'repositories.yaml'))
    else:
        LOG.debug("Backing up the repositories.yaml to the the backup repositories.yaml.backup")
        shutil.copy(str(Path(path_to_helmfile).parent / 'repositories.yaml'),
                    str(Path(path_to_helmfile).parent / 'repositories.yaml.backup'))


def __create_repositories_yaml(path_to_helmfile, state_values_file, chart_cache_directory):
    """
    Update the repositories.yaml file, with references to the chart cache directory.

    Input:
        path_to_helmfile: Path to the helmfile.yaml
        state_values_file: Site values file to use when determining the repo details from the helmfile
        chart_cache_directory: An optional directory to cache downloaded dependencies to

    Output:
        Calculates and overwrites the repositories.yaml with references to the local cache directory.
    """
    local_helm_repo_url = f'file://{chart_cache_directory}'
    repositories = []
    for build_data in build(state_values_file=state_values_file, path_to_helmfile=path_to_helmfile):
        for repository in build_data['repositories']:
            if not any(repository['name'] == repo['name'] for repo in repositories):
                repositories.append({'name': repository['name'], 'url': local_helm_repo_url})
    repositories_yaml_object = {'repositories': repositories}
    write_repositories_yaml(path_to_helmfile=path_to_helmfile, yaml_dict=repositories_yaml_object)


def write_repositories_yaml(path_to_helmfile, yaml_dict):
    """
    Write a dict into repositories.yaml.

    Input:
        path_to_helmfile: Path to the helmfile.yaml
        yaml_dict: The dictionary to be written to the repositories.yaml file.

    Output:
        Overwrites the repositories.yaml.
    """
    path_to_repositories_yaml_file = Path(path_to_helmfile).parent / 'repositories.yaml'
    with path_to_repositories_yaml_file.open('w', encoding='utf-8') as yaml_file:
        yaml.dump(yaml_dict, yaml_file)


def get_helmfile_template_output(state_values_file_path, helmfile_path):
    """
    Get the output of a helmfile template command.

    Input:
        state_values_file_path: The path to where the different site values files are located
        helmfile_path: The path to the helmfile.yaml file

    Returns
    -------
        The output of a helmfile template command
    """
    LOG.info("Running command: %s", "/usr/bin/helmfile --helm-binary /usr/bin/helm"
             + " --state-values-file " + state_values_file_path + " --file " + helmfile_path
             + " --environment build template")
    template_output = run_helmfile_command(helmfile_path, state_values_file_path,
                                           None, "--environment", "build", "template")
    if template_output.returncode != 0:
        LOG.info(template_output.stderr.decode('utf-8'))
        raise Exception("Error: The helmfile template returned an error")
    template_output = io.StringIO(template_output.stdout.decode('utf-8'))
    return template_output


# pylint: disable=unnecessary-dict-index-lookup
def check_helmfile_versions_for_snapshot_build(state_values_file_path, helmfile_path, chart_name, chart_version):
    """
    Check the chart versions in the helmfile against the versions provided.

    Input:
        state_values_file_path: The path to where the different site values files are located
        helmfile_path: The path to the helmfile.yaml file
        chart_name: A comma-separated list of chart names
        chart_version: A comma-separated list of chart versions

    Returns
    -------
        Creates a properties file to indicate if there were differences in the chart versions
    """
    # Create a dictionary from the chart(s) being changed
    charts_being_changed_dict = {}
    chart_list = chart_name.replace(" ", "").split(",")
    version_list = chart_version.replace(" ", "").split(",")
    for chart, version in zip(chart_list, version_list):
        charts_being_changed_dict[chart] = version
    LOG.info("Chart names and versions to be changed in the helmfile: %s", charts_being_changed_dict)

    # Create a dictionary from each release in the helmfile
    helmfile_release_dict = {}
    helmfile_list_output = helmfile_list(state_values_file_path, helmfile_path)
    for release in helmfile_list_output:
        helmfile_release_dict[release["name"]] = release["version"]
    LOG.info("Chart names and versions in the helmfile: %s", helmfile_release_dict)

    # Compare both dictionaries
    all_versions_are_the_same = charts_being_changed_dict.items() <= helmfile_release_dict.items()
    if all_versions_are_the_same:
        LOG.info("WARNING: Each of the chart versions in the CHART_VERSION parameter are already in the helmfile: %s",
                 charts_being_changed_dict)
    else:
        charts_changing = list(charts_being_changed_dict.items() - helmfile_release_dict.items())
        LOG.info("The following chart versions are being changed in the helmfile: %s", charts_changing)
    with open("helmfile-version-check.properties", "w", encoding="utf-8") as artifacts_file:
        artifacts_file.writelines(f"NO_CHART_VERSION_CHANGES={all_versions_are_the_same}\n")
