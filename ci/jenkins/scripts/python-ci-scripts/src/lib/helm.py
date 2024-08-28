"""Module for helm operations."""
import logging
import os
import subprocess
import time
import shutil
import yaml

from . import cmd_common
from . import utils
from . import cihelm
from . import errors
from . import helmfile

from .netrc_common import Netrc

LOG = logging.getLogger(__name__)
HELM = "/usr/bin/helm"
CWD = os.getcwd()


def run_helm_command(config_file_path, *helm_args):
    """
    Execute a helm command.

    Input:
        config_file_path: File path to cluster kube config (to set context for helm command)
        *helm_args: List of helm command arguments

    Returns
    -------
        Command object

    """
    command_and_args_list = [HELM, '--kubeconfig', config_file_path]
    command_and_args_list.extend(helm_args)
    command = utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command


def run_helm_command_with_retry(config_file_path, retry_count, retry_sleep_in_s, *helm_args):
    """
    Execute a helm command with a retry on error code returned.

    Input:
        config_file_path: File path to cluster kube config (to set context for helm command)
        retry_count: Number of times to retry a failed operation
        retry_sleep_in_s: Number of seconds to sleep in between retries
        *helm_args: List of helm command arguments

    Returns
    -------
        Command object

    """
    # Set defaults
    if isinstance(retry_count, int) is False or retry_count < 1:
        retry_count = 1
    if isinstance(retry_sleep_in_s, int) is False or retry_sleep_in_s < 1:
        retry_sleep_in_s = 1
    counter = 0
    new_args = []
    new_args.extend(helm_args)
    while counter < retry_count:
        LOG.debug("Helm command: %s", ' '.join(new_args))
        command = run_helm_command(config_file_path, *new_args)
        if command.returncode == 0:
            break
        time.sleep(retry_sleep_in_s)
        counter += 1
    return command


def removing_sep_release_from_namespace(namespace, kubeconfig_file):
    """
    Remove SEP Helm Release within a given Namespace.

    Input:
        namespace: Namespace where releases exist
        kubeconfig_file: Kube config file path to access target cluster

    Returns
    -------
        Remove SEP Helm Release from target namespace in cluster

    """
    helm_list_of_releases = run_helm_command(kubeconfig_file, 'ls', '--all', '--short', "--namespace", namespace)

    if helm_list_of_releases.returncode == 0:
        LOG.info('Removing release from target namespace: %s', namespace)
        LOG.info('Executing:')

        releases = helm_list_of_releases.stdout.decode('utf-8').split("\n")
        del releases[-1]

        LOG.info('Releases: %s', releases)

        if len(releases) > 1:
            LOG.warning("Multiple releases %s left in namespace %s", releases, namespace)

        if 'eric-storage-encryption-provider' in releases:
            release = 'eric-storage-encryption-provider'
            LOG.info("Deleting Release %s from namespace %s", release, namespace)
            uninstall_release = run_helm_command(kubeconfig_file, 'uninstall', '--no-hooks', release,
                                                 '--namespace', namespace, '--debug')
            if uninstall_release.returncode == 0:
                LOG.info('Removal of release %s from target namespace %s finished successfully', release, namespace)
            else:
                LOG.error(uninstall_release.stderr.decode('utf-8'))
                raise errors.RemovalOfHelmReleasesError(f"Issue deleting release from namespace: {namespace}")

            LOG.info('Removal of release from target namespace %s finished successfully', namespace)
        else:
            LOG.info("SEP Release is not installed on %s:", namespace)


def removing_helm_releases_from_namespace(namespace, kubeconfig_file):
    """
    Remove Helm Releases within a given Namespace.

    Input:
        namespace: Namespace where releases exist
        kubeconfig_file: Kube config file path to access target cluster

    Returns
    -------
        Remove Helm Releases from target namespace in cluster

    """
    helm_list_of_releases = run_helm_command(kubeconfig_file, 'ls', '--all', '--short', "--namespace", namespace)

    if helm_list_of_releases.returncode == 0:
        LOG.info('Removing releases from target namespace: %s', namespace)
        LOG.info('Executing:')

        releases = helm_list_of_releases.stdout.decode('utf-8').split("\n")
        del releases[-1]

        LOG.info('Releases: %s', releases)

        if len(releases) != 0:
            if 'eric-storage-encryption-provider' in releases:
                releases.remove('eric-storage-encryption-provider')

            for release in releases:
                LOG.info("Deleting Release %s from namespace %s", release, namespace)
                uninstall_release = run_helm_command(kubeconfig_file, 'uninstall', '--no-hooks', release,
                                                     '--namespace', namespace, '--debug')
                if uninstall_release.returncode == 0:
                    LOG.info('Removal of release %s from target namespace %s finished successfully', release, namespace)
                else:
                    LOG.error(uninstall_release.stderr.decode('utf-8'))
                    raise errors.RemovalOfHelmReleasesError(f"Issue arose deleting release from namespace: {namespace}")

            LOG.info('Removal of releases from target namespace %s finished successfully', namespace)
        else:
            LOG.info('No releases exist on namespace %s', namespace)
    else:
        if "not found" in helm_list_of_releases.stderr.decode('utf-8'):
            LOG.info('Helm Releases do not exist on the specified namespace %s', namespace)
        else:
            LOG.error(helm_list_of_releases.stderr.decode('utf-8'))
            raise errors.RemovalOfHelmReleasesError(f"Issue arose deleting release from namespace: {namespace}")


def repo_index(directory_to_index):
    """Index a helm repository.

    Input:
        directory_to_index: The path to the directory to create the index in.
    """
    LOG.info('Indexing directory "%s", to create local helm repository.', directory_to_index)
    command = run_helm_command('na', 'repo', 'index', directory_to_index)
    if command.returncode != 0:
        raise errors.HelmRepoIndexFailedError(utils.join_command_stdout_and_stderr(command))
    output = command.stdout.decode('utf-8').rstrip()
    LOG.debug("\n%s", output)


# pylint: disable=unused-variable
def get_image_info_from_helm_chart(helm_chart_path):
    """
    Obtain the images from a helm chart.

    Input:
        helm_chart_path: The path to the chart to retreive the images

    Returns
    -------
        A list containing the source, name, and version for each image
    """
    source_image_version_list = []
    for root, directory, file in os.walk(helm_chart_path):
        if "eric-product-info.yaml" in file:
            path_to_eric_product_info = os.path.join(root, "eric-product-info.yaml")
            with open(path_to_eric_product_info, "r", encoding="utf-8") as file:
                eric_product_info_dict = yaml.safe_load(file)
                LOG.info("Searching for images in the eric-product-info file for %s", root)
                if "images" in eric_product_info_dict.keys():
                    LOG.info("Retrieving images from %s", root)
                    for image in eric_product_info_dict["images"].keys():
                        version = eric_product_info_dict["images"][image]["tag"]
                        full_image_path = "/".join([eric_product_info_dict["images"][image]["registry"],
                                                    eric_product_info_dict["images"][image]["repoPath"],
                                                    eric_product_info_dict["images"][image]["name"]])
                        source_image_version_list.append(f"{root}:{full_image_path}:{version}")
                else:
                    LOG.info("No images found in the eric-product-info file for %s", root)
    return source_image_version_list


def package_chart(path_to_chart, destination=CWD, version='0.0.0',
                  use_chart_cache='true',
                  chart_cache_directory="/tmp/cachedir"
                  ):
    """
    Call ADP enabler cihelm to package a helm chart.

    Inputs:
        path_to_chart: This is the location of the chart.yaml file
        destination: Directory where the package will be stored, default current working directory
        version: version to apply to the chart during build
        use_chart_cache: Option to use the dependency cache functionality if required, default true
        chart_cache_directory: local cache directory to store the dependency, default /tmp/cachedir

    Output:
        helm chart is built
    """
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])
    LOG.debug('Inputted Parameters')
    LOG.debug('path_to_chart: %s', path_to_chart)
    LOG.debug('destination: %s', destination)
    LOG.debug('version: %s', version)
    LOG.debug('Use Cache: %s', use_chart_cache)
    LOG.debug('Chart Cache: %s\n', chart_cache_directory)
    netrc = build_netrc_file_with_repo_credentials_from_chart(path_to_chart, CWD)
    deps = fetch_dependencies_from_helm_chart(path_to_chart=path_to_chart)
    download_directory = cihelm.dependency_update(deps, netrc, mask, CWD, chart_cache_directory)
    if os.path.isdir(chart_cache_directory):
        LOG.info('Chart cache directory %s contents: %s', chart_cache_directory, os.listdir(chart_cache_directory))
    else:
        LOG.info('%s is not directory', chart_cache_directory)
    if use_chart_cache == 'true':
        LOG.info("Build Helm Chart Package using cache")
        copy_dependencies_to_chart(path_to_chart, download_directory)
        package_chart_using_helm(path_to_chart, destination, version)
    else:
        LOG.info("Build Helm Chart Package with ADP CIHelm")
        cihelm.package(path_to_chart, netrc, mask, CWD, destination, version)
    if os.path.exists(CWD + '/.netrc'):
        netrc.remove()


def package_chart_using_helm(path_to_chart, destination, version):
    """
    Package the chart using helm package command.

    Inputs:
        path_to_chart: This is the location of the chart.yaml file
        destination: Directory where the package will be stored, default current working directory
        version: version to apply to the chart during build
    """
    LOG.debug("Executing package_chart_using_helm")
    mask = []
    cmd = "helm package " + str(path_to_chart) + " --destination " + str(destination) + " --version " + str(version)
    LOG.debug("Executing command, %s", cmd)
    if cmd_common.execute_command(cmd, mask=mask, verbose=True).returncode != 0:
        raise Exception("Chart Package using Helm has failed")


def copy_dependencies_to_chart(path_to_chart, download_directory):
    """
    Copy the dependencies to the chart directory of the helm chart to build.

    Inputs:
        path_to_chart: This is the location of the chart.yaml file
        download_directory: This is the location where the dependencies are stored
    """
    chart_dir = os.path.join(path_to_chart, 'charts')
    if not os.path.isdir(chart_dir):
        os.mkdir(chart_dir)
    for chart in os.listdir(download_directory):
        LOG.debug("Chart Found : %s", chart)
        source = os.path.join(download_directory, chart)
        destination = os.path.join(chart_dir, chart)
        LOG.debug("Cache source : %s", source)
        LOG.debug("Charts dependency directory : %s", destination)
        if os.path.isfile(source):
            LOG.debug('Copying %s to the dependencies chart directory', chart)
            shutil.copy(source, destination)


def build_netrc_file_with_repo_credentials_from_chart(path_to_chart, workspace=CWD):
    """
    Build a netrc file with the repo credentials.

    Inputs:
        path_to_chart: Path to the location of the Chart.yaml
        workspace: Used to set the directory where to create the .netrc file, default current working directory.

    Output:
        File generated on the working directory ./.netrc with the repo credentials
    """
    LOG.debug("Executing build_netrc_file_with_repo_credentials_from_chart")
    netrc = Netrc(path=workspace)
    chart_file = os.path.join(path_to_chart, 'Chart.yaml')
    with open(chart_file, encoding="utf-8") as chart_yaml_input:
        chart_yaml_data = yaml.safe_load(chart_yaml_input)
    LOG.debug(str(chart_yaml_data))
    if 'dependencies' in chart_yaml_data:
        for chart_data in chart_yaml_data['dependencies']:
            repo = chart_data['repository']
            LOG.debug("Adding Repo details %s to netrc", repo)
            netrc.add_login(utils.get_remote_host(repo),
                            os.environ['GERRIT_USERNAME'],
                            os.environ['GERRIT_PASSWORD'])
    return netrc


def fetch_dependencies_from_helm_chart(path_to_chart):
    """
    Fetch the dependencies from a given chart.

    Inputs:
        path_to_chart: Path to the location of the Chart.yaml

    Output:
        Returned list of the dependencies
    """
    result = []
    chart_file = os.path.join(path_to_chart, 'Chart.yaml')
    with open(chart_file, 'r', encoding="utf-8") as chart_yaml_input:
        chart_yaml_data = yaml.safe_load(chart_yaml_input)
    LOG.debug("List of Key from Chart.yaml - %s", list(chart_yaml_data))
    if 'dependencies' in chart_yaml_data:
        for chart_data in chart_yaml_data['dependencies']:
            result.append((chart_data['repository'], chart_data['version'], chart_data['name']))
    LOG.debug("Helm Chart Dependencies Returned %s", str(result))
    return result


# pylint: disable=too-many-locals
def check_cncs_optionality(helmfile_name, helmfile_version, username, password):
    """
    Check that all CNCS values are contained within the helmfile.

    Input:
        helmfile_name: The name of the helmfile
        helmfile_version: The version of the helmfile
        username: The username to download the helmfile
        password: The password to download the helmfile
    """
    helmfile.get_base_baseline(helmfile_name, "get_baseline", "None",
                               "input.properties", "artifact.properties")
    with open("artifact.properties", "r", encoding="utf-8") as properties_file:
        lines = properties_file.readlines()
        for line in lines:
            if "BASE_PLATFORM_BASELINE_CHART_NAME" in line:
                chart_names = line.replace(" ", "").strip().split("=")[1].split(",")
            if "BASE_PLATFORM_BASELINE_CHART_VERSION" in line:
                chart_versions = line.replace(" ", "").strip().split("=")[1].split(",")
            if "BASE_PLATFORM_BASELINE_CHART_REPO" in line:
                chart_repos = line.replace(" ", "").strip().split("=")[1].split(",")
    if "eric-oss-common-base" not in chart_names or "eric-cloud-native-base" not in chart_names:
        raise errors.MissingHelmfileValueError("eric-cloud-native-base/eric-oss-common-base not found in the helmfile")
    for chart_name, chart_version, chart_repo in zip(chart_names, chart_versions, chart_repos):
        if chart_name in ["eric-oss-common-base", "eric-cloud-native-base"]:
            utils.download_file(f"{chart_repo}/{chart_name}/{chart_name}-{chart_version}.tgz",
                                f"{chart_name}-{chart_version}.tgz", username, password, "wb")
            utils.extract_tar_file(f"{chart_name}-{chart_version}.tgz", '.')

    missing_optionality_values = []
    with open("eric-cloud-native-base/Chart.yaml", "r", encoding="utf-8") as chart_file, \
            open("eric-oss-common-base/optionality.yaml", "r", encoding="utf-8") as cb_optionality_file:
        cb_optionality_yaml = yaml.safe_load(cb_optionality_file)
        chart_yaml = yaml.safe_load(chart_file)
        cb_helmfile_optionality_values = cb_optionality_yaml["optionality"]["eric-cloud-native-base"].keys()
        cncs_chart_values = [item["name"] for item in chart_yaml["dependencies"]]
        for item in cncs_chart_values:
            if item not in cb_helmfile_optionality_values:
                missing_optionality_values.append(item)
                LOG.warning("-------------------------")
                LOG.warning("%s is not listed in the common-base optionality file", item)
                LOG.warning("-------------------------")

    write_missing_optionality_values_to_file(missing_optionality_values, helmfile_name, helmfile_version)


def write_missing_optionality_values_to_file(missing_optionality_values, helmfile_name, helmfile_version):
    """
    Write the missing optionality values to file.

    Input:
        missing_optionality_values: A list containing any missing optionality values
        helmfile_name: The name of the helmfile
        helmfile_version: The version of the helmfile
    """
    cb_version = helmfile.get_single_app_version_from_helmfile(f"{helmfile_name}/helmfile.yaml", "eric-oss-common-base")
    cncs_version = helmfile.get_single_app_version_from_helmfile(f"{helmfile_name}/helmfile.yaml",
                                                                 "eric-cloud-native-base")
    with open("missingOptionalityValues.txt", "w", encoding="utf-8") as artifacts_file:
        artifacts_file.writelines("------------------------------\n")
        artifacts_file.writelines(f"Helmfile name and version: {helmfile_name}-{helmfile_version}\n")
        artifacts_file.writelines(f"eric-oss-common-base version: {cb_version}\n")
        artifacts_file.writelines(f"eric-cloud-native-base version: {cncs_version}\n")
        artifacts_file.writelines("------------------------------\n")
        if len(missing_optionality_values) == 0:
            artifacts_file.writelines("All CNCS optionality files are contained in common-base")
            return
        artifacts_file.writelines("CNCS optionality values that are missing from common-base:\n")
        for item in missing_optionality_values:
            artifacts_file.writelines(item + "\n")
        raise errors.MissingOptionalityValueError("There are CNCS optionality values missing from common-base")
