"""Module for ADP Enabler cihelm."""
# pylint: disable=cyclic-import
import logging
import os
import tempfile
from pathlib import Path
import glob
import shutil
import yaml

from . import cmd_common
from . import helmfile
from . import helm
from . import utils
from .netrc_common import Netrc


LOG = logging.getLogger(__name__)
CWD = os.getcwd()


def cihelm_fetch(path_to_helmfile, clean_up=False):
    """
    Call ADP enabler cihelm to replace helm fetch command.

    Inputs:
        path_to_helmfile: To download the dependency for
        clean_up: Used to remove the downloaded charts

    Output:
        helm chart is downloaded
    """
    # Set the state values file here to the default build environments variable.
    # This ensures all tags are true, which ensure all details are returned from the helmfile build command
    state_values_file = os.path.dirname(path_to_helmfile) + "/build-environment/tags_true.yaml"
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])
    LOG.debug('Inputted Parameters')
    LOG.debug('path_to_helmfile: %s', path_to_helmfile)
    LOG.debug('clean_up: %s', str(clean_up))
    LOG.debug('Auto Set variables')
    LOG.debug('state_values_file: %s', state_values_file)

    deps = helmfile.fetch_name_version_repo_details_from_helmfile(state_values_file, path_to_helmfile)
    netrc = helmfile.build_netrc_file_with_repo_credentials_from_helmfile(state_values_file, path_to_helmfile, CWD)
    LOG.info("Downloading Dependencies from Helmfile")
    fetch(deps, netrc, mask, CWD, clean_up)
    if os.path.exists(CWD + '/.netrc'):
        netrc.remove()


def cihelm_fetch_single_chart(chart_name, chart_version, chart_repo):
    """
    Call ADP enabler cihelm to replace helm fetch, repo add and repo update command for a single chart.

    Inputs:
        chart_name: Name of the helm chart to be fetched
        chart_version: Version of the helm chart to be fetched
        chart_repo: Repo location of the helm chart to be fetched

    Output:
        helm chart is downloaded
    """
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])
    LOG.debug('Inputted Parameters')
    LOG.debug('chart_name: %s', chart_name)
    LOG.debug('chart_version: %s', chart_version)
    LOG.debug('chart_repo: %s', chart_repo)

    netrc = build_netrc_file_for_chart(chart_repo, CWD)
    LOG.info("Creating netrc file from chart repo and gerrit user creds")
    fetch_single_chart(chart_name, chart_version, chart_repo, netrc, mask, CWD)
    if os.path.exists(CWD + '/.netrc'):
        netrc.remove()


def fetch(deps, netrc, mask, workspace, clean_up=False):
    """
    ADP cihelm Enabler main fetch feature.

    Inputs:
        deps: List of dependencies to be fetched
        netrc: file which holds all the credentials to log onto the artifact repositories.
        mask: list of string items to be omitted from any print to screen commands
        workspace: Used to set the directory where to create the .netrc file, default current working directory.
        clean_up: boolean to state whether to keep the artifacts downloaded or not
    """
    netrc_arg = ''
    if os.path.exists(workspace + '/.netrc'):
        netrc_arg = '--netrc ' + workspace + '/.netrc'
    for repo, version, name in deps:
        cmd = f'cihelm {netrc_arg} fetch {name} {version} {repo}'
        if cmd_common.execute_command(cmd, mask=mask, verbose=True).returncode != 0:
            if os.path.exists(workspace + '/.netrc'):
                netrc.remove()
            clean_up_after_cihelm_fetch(name, version, mask)
            raise Exception("cihelm fetch update failed")
        if clean_up:
            clean_up_after_cihelm_fetch(name, version, mask)


# pylint: disable=too-many-arguments
def fetch_single_chart(chart_name, chart_version, chart_repo, netrc, mask, workspace):
    """
    ADP cihelm Enabler main fetch feature for a single chart.

    Inputs:
        chart_name: Name of chart in repo to be fetched
        chart_version: Version of chart to be fetched
        chart_repo: Full repository url of the chart to be fetched
        netrc: file which holds all the credentials to log onto the artifact repositories.
        mask: list of string items to be omitted from any print to screen commands
        workspace: Used to set the directory where to create the .netrc file, default current working directory.
    """
    netrc_arg = ''
    if os.path.exists(workspace + '/.netrc'):
        netrc_arg = '--netrc ' + workspace + '/.netrc'
    cmd = f'cihelm {netrc_arg} fetch {chart_name} {chart_version} {chart_repo}'
    if cmd_common.execute_command(cmd, mask=mask, verbose=True).returncode != 0:
        if os.path.exists(workspace + '/.netrc'):
            netrc.remove()
        raise Exception("cihelm fetch update failed")


def cihelm_package_chart(path_to_chart, destination=CWD, version='0.0.0'):
    """
    Call ADP enabler cihelm to package a helm chart.

    Inputs:
        path_to_chart: This is the location of the chart.yaml file
        destination: Directory where the package will be stored, default current working directory
        version: version to apply to the chart during build

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
    netrc = helm.build_netrc_file_with_repo_credentials_from_chart(path_to_chart, CWD)

    LOG.info("Build Helm Chart Package")
    package(path_to_chart, netrc, mask, CWD, destination, version)
    if os.path.exists(CWD + '/.netrc'):
        netrc.remove()


# pylint: disable=too-many-arguments
def package(path_to_chart, netrc, mask, workspace, destination=CWD, version='0.0.0'):
    """
    ADP cihelm Enabler package feature.

    Inputs:
        path_to_chart: This is the location of the Chart.yaml file
        netrc: file which holds all the credentials to log onto the artifact repositories.
        mask: list of string items to be omitted from any print to screen commands
        workspace: Used to set the directory where to create the .netrc file, default current working directory.
        destination: Directory where the package will be stored, default current working directory
        version: version to apply to the chart during build
    """
    netrc_arg = ''
    if os.path.exists(workspace + '/.netrc'):
        netrc_arg = '--netrc ' + workspace + '/.netrc'

    cmd = f'cihelm {netrc_arg} package --destination {destination} --version {version} {path_to_chart}'
    if cmd_common.execute_command(cmd, mask=mask, verbose=True).returncode != 0:
        if os.path.exists(workspace + '/.netrc'):
            netrc.remove()
        raise Exception("cihelm package failed")


def dependency_update(deps, netrc, mask, workspace, chart_cache_directory):
    """
    ADP cihelm dependency update feature, wrapped with a cache directory that can be mounted into the workspace.

    Inputs:
        deps: List of dependencies to be downloaded
        netrc: file which holds all the credentials to log onto the artifact repositories.
        mask: list of string items to be omitted from any print to screen commands
        workspace: Used to set the directory where to create the .netrc file, default current working directory.
        chart_cache_directory: the path to where the downloaded packages should be cached to/from
    """
    LOG.debug("Started the cihelm dependency update procedure.")
    with tempfile.TemporaryDirectory() as directory_name:
        temporary_helm_chart_directory = directory_name
    with tempfile.TemporaryDirectory() as directory_name:
        final_dependencies_directory = directory_name
    if not chart_cache_directory:
        with tempfile.TemporaryDirectory() as directory_name:
            chart_cache_directory = directory_name

    LOG.debug('The helm chart cache is located in %s', chart_cache_directory)
    Path(temporary_helm_chart_directory).mkdir(parents=True, exist_ok=True)
    Path(chart_cache_directory).mkdir(parents=True, exist_ok=True)
    Path(final_dependencies_directory).mkdir(parents=True, exist_ok=True)

    local_chart_prefix = "file://"
    uncached_dependencies = []
    for repo, version, name in deps:
        cached_chart_file_path = Path(chart_cache_directory) / (name + '-' + version + '.tgz')
        if cached_chart_file_path.exists():
            LOG.debug('%s was already in the download cache, copying it into the resulting directory, %s',
                      cached_chart_file_path, final_dependencies_directory)
            shutil.copy(str(cached_chart_file_path), final_dependencies_directory)
        else:
            if repo.startswith(local_chart_prefix):
                LOG.debug('Skipping the cihelm download of local chart %s.', name)
                continue
            LOG.debug('%s was not already in the download cache, marking it for download by cihelm.',
                      cached_chart_file_path)
            uncached_dependencies.append({'name': name, 'repository': repo, 'version': version})

    if len(uncached_dependencies) > 0:
        _dependency_update(dependencies=uncached_dependencies, workspace=workspace, mask=mask, netrc=netrc,
                           temporary_helm_chart_directory=temporary_helm_chart_directory)
        LOG.debug("List of Charts Downloaded to the temp download directory, %s - %s",
                  temporary_helm_chart_directory,
                  os.listdir(os.path.join(temporary_helm_chart_directory, 'charts'))
                  )
        for chart in glob.glob(str(Path(temporary_helm_chart_directory) / 'charts' / '*.tgz')):
            LOG.debug('Copying %s into the cache and into the resulting directory.', chart)
            shutil.copy(chart, chart_cache_directory)
            shutil.copy(chart, final_dependencies_directory)
    LOG.debug("Completed the cihelm dependency update procedure.")
    return final_dependencies_directory


def _dependency_update(dependencies, netrc, mask, workspace, temporary_helm_chart_directory):
    """
    ADP cihelm dependency update feature, wrapped with creation of the dummy helm Chart.yaml.

    Inputs:
        dependencies: List of dependencies to be downloaded
        netrc: file which holds all the credentials to log onto the artifact repositories.
        mask: list of string items to be omitted from any print to screen commands
        workspace: Used to set the directory where to create the .netrc file, default current working directory.
        temporary_helm_chart_directory: the directory to generate the temporary helm chart used by cihelm
    """
    chart_yaml_object = {
        'apiVersion': 'v2',
        'name': 'temporary_chart_for_cihelm_dependency_update',
        'version': '0.0.1',
        'dependencies': dependencies
    }
    with open(Path(temporary_helm_chart_directory) / Path('Chart.yaml'), 'w', encoding='utf-8') as chart_yaml_file:
        yaml.dump(chart_yaml_object, chart_yaml_file)

    _cihelm_dependency_update(netrc=netrc, mask=mask, workspace=workspace,
                              temporary_helm_chart_directory=temporary_helm_chart_directory)


def _cihelm_dependency_update(netrc, mask, workspace, temporary_helm_chart_directory):
    """
    ADP cihelm dependency update feature.

    Inputs:
        dependencies: List of dependencies to be downloaded
        netrc: file which holds all the credentials to log onto the artifact repositories.
        mask: list of string items to be ommitted from any print to screen commands
        workspace: Used to set the directory where to create the .netrc file, default current working directory.
        temporary_helm_chart_directory: the directory to generate the temporary helm chart used by cihelm
    """
    netrc_arg = ''
    if os.path.exists(workspace + '/.netrc'):
        netrc_arg = '--netrc ' + workspace + '/.netrc'
    cmd = f'cihelm {netrc_arg} dependency update {temporary_helm_chart_directory}'
    if cmd_common.execute_command(cmd=cmd, mask=mask, verbose=True).returncode != 0:
        if os.path.exists(workspace + '/.netrc'):
            netrc.remove()
        raise Exception("cihelm dependency update failed")


def clean_up_after_cihelm_fetch(chart_name, chart_version, mask):
    """
    Clean-up after the cihelm_fetch if set.

    Inputs:
        chart_name: name of the chart to be deleted
        chart_version: version of the chart to be deleted
        mask: list of string items to be omitted from any print to screen commands
    """
    if cmd_common.execute_command(f'rm -f {chart_name}-{chart_version}.tgz', mask=mask,
                                  verbose=True).returncode > 0:
        raise Exception(f"Remove {chart_name}-{chart_version}.tgz failed")


def build_netrc_file_for_chart(chart_repo, workspace=CWD):
    """
    Build a netrc file with the repo credentials.

    Inputs:
        chart_repo: Full repository url of the chart to be fetched
        workspace: Used to set the directory where to create the .netrc file, default current working directory.

    Output:
        File generated on the working directory ./.netrc with the repo credentials
    """
    netrc = Netrc(path=workspace)
    netrc.add_login(utils.get_remote_host(chart_repo), os.environ['GERRIT_USERNAME'], os.environ['GERRIT_PASSWORD'])
    return netrc
