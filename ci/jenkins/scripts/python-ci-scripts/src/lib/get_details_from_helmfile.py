"""Module to build release details from helmfile."""
import logging
import os
import json
import tarfile
import shutil

from . import helmfile
from . import utils

LOG = logging.getLogger(__name__)

HELMFILE = "/usr/bin/helmfile"
HELM = "/usr/bin/helm"
CURRENT_WORKING_DIRECTORY = os.getcwd()
HELMFILE_BUILD_OUTPUT = CURRENT_WORKING_DIRECTORY + "/helmfile_build_output.txt"
HELMFILE_JSON = CURRENT_WORKING_DIRECTORY + "/helmfile_json_content.json"
CSAR_BUILD_PROPERTIES = CURRENT_WORKING_DIRECTORY + "/csar_build.properties"
RELEASES_ASSOCIATED_TO_CSARS_JSON = CURRENT_WORKING_DIRECTORY + "/releases_and_associated_csar.json"
CSARS_TO_BUILD = CURRENT_WORKING_DIRECTORY + "/csar_to_be_built.properties"
CSAR_HELM_CHART_MAPPING = CURRENT_WORKING_DIRECTORY + "/am_package_manager.properties"
METADATA_PATH = 'metadata.yaml'


def clean_up_files():
    """Ensure all created file are removed if not needed."""
    if os.path.exists(HELMFILE_BUILD_OUTPUT):
        os.remove(HELMFILE_BUILD_OUTPUT)
    if os.path.exists(HELMFILE_JSON):
        os.remove(HELMFILE_JSON)
    if os.path.exists(CURRENT_WORKING_DIRECTORY + "/compiledContent_crds-helmfile.yaml"):
        os.remove(CURRENT_WORKING_DIRECTORY + "/compiledContent_crds-helmfile.yaml")
    if os.path.exists(CURRENT_WORKING_DIRECTORY + "/compiledContent_helmfile.yaml"):
        os.remove(CURRENT_WORKING_DIRECTORY + "/compiledContent_helmfile.yaml")
    if os.path.exists(CSAR_BUILD_PROPERTIES):
        os.remove(CSAR_BUILD_PROPERTIES)
    if os.path.exists(RELEASES_ASSOCIATED_TO_CSARS_JSON):
        os.remove(RELEASES_ASSOCIATED_TO_CSARS_JSON)
    if os.path.exists(CSARS_TO_BUILD):
        os.remove(CSARS_TO_BUILD)
    if os.path.exists(CSAR_HELM_CHART_MAPPING):
        os.remove(CSAR_HELM_CHART_MAPPING)


# pylint: disable=too-many-locals too-many-arguments
def fetch_helmfile_charts(releases_dict,
                          csar_dict,
                          csar_list,
                          path_to_helmfile,
                          helmfile_csar_build=False):
    """
    Download the chart from the helmfile according to the site values inputted.

    Input:
        state_values_file: state values file (site-values.yaml)
        path_to_helmfile: path to the helmfile under test
        releases_dict: Dictionary Content of the helmfile according the state file inputted
        csar_dict: List of the CSAR to be created
        csar_list: A list of what CSAR the release should be added to
        helmfile_csar_build: Boolean set to true or false, if the Helmfile CSAR needs to be included

    Output:
        Required charts downloaded
        File created that can be used by the AM package manager to generate the CSARs using the downloaded charts
    """
    # Build up a file that can be used to pass the details to the am package manager.
    with open(CSAR_HELM_CHART_MAPPING, "w", encoding="utf-8") as am_package_manager_prop:
        for item in csar_list:
            csar_name = item.split(':')[0]
            csar_version = item.split(':')[1]
            csar_item_list = []
            for key, values in csar_dict.items():
                for value in values.split(','):
                    if value == csar_name:
                        version = releases_dict[key]['version']
                        csar_item_list.append(key + "-" + version + ".tgz")
            csar_content = ",".join(csar_item_list)
            am_package_manager_prop.write(str(csar_name) + "-" + str(csar_version) + "=" + str(csar_content) + "\n")
        if helmfile_csar_build:
            metadata_dict = utils.build_yaml(os.path.join(os.path.dirname(path_to_helmfile), 'metadata.yaml'))
            helmfile_name = metadata_dict['name']
            helmfile_version = metadata_dict['version']
            am_package_manager_prop.write(str(helmfile_name) + "-" + str(helmfile_version) + "="
                                          + str(helmfile_name) + "-"
                                          + str(helmfile_version) + ".tgz"
                                          + "\n"
                                          )


def generate_optionality_and_site_values_files(releases_dict,
                                               csar_dict,
                                               path_to_helmfile):
    """
    Take the content of the generated JSON and build up the variables for the CSAR build job.

    Input:
        releases_dict: Dictionary Content of the helmfile according the state file inputted
        csar_dict: List of the CSAR to be created
        state_values_file: state values file (site-values.yaml)
        path_to_helmfile: path to the helmfile under test

    Output:
        Required charts downloaded
        File created that can be used by the AM package manager to generate the CSARs using the downloaded charts
    """
    helmfile_dir = os.path.basename(os.path.dirname(path_to_helmfile))

    write_to_file("individual_App_SiteValues.txt", helmfile_dir + "/templates/site-values-template.yaml", helmfile_dir)
    write_to_file("individual_App_Optionality.txt", helmfile_dir + "/optionality.yaml", helmfile_dir)
    optionality_dicts = [utils.build_yaml(helmfile_dir + "/optionality.yaml")]
    # Get Content of site values and optionality file from helm charts
    for key in csar_dict:
        chart = releases_dict[key]['chart']
        chart_name = chart.split("/")[1]
        version = releases_dict[key]['version']

        with tarfile.open(chart_name + "-" + version + ".tgz") as chart_tar:
            if chart_name + "/site_values_template.yaml" in chart_tar.getnames():
                chart_tar.extract(chart_name + "/site_values_template.yaml", '.')
                write_to_file("individual_App_SiteValues.txt", chart_name + "/site_values_template.yaml",
                              chart_name + "-" + version + ".tgz")

            if chart_name + "/optionality.yaml" in chart_tar.getnames():
                chart_tar.extract(chart_name + "/optionality.yaml", '.')
                optionality_dicts.append(utils.build_yaml(chart_name + "/optionality.yaml"))
                write_to_file("individual_App_Optionality.txt", chart_name + "/optionality.yaml",
                              chart_name + "-" + version + ".tgz")
        if os.path.isdir(chart_name):
            shutil.rmtree(chart_name)

    merged_optionality_dicts = utils.logical_or_merge_optionality_dicts(optionality_dicts=optionality_dicts)
    utils.write_yaml(yaml_dict=merged_optionality_dicts, path_to_file="combined_optionality.yaml")


def write_to_file(output_file, input_file, chart_title):
    """
    Write the content of file to another.

    Input:
        output_file: File name to append the input_file contents to
        input_file: File to read to append to output_file
        chart_title: Chart title to be added to output_file

    Output:
        Writes an updated UTF-8 file
    """
    with open(output_file, "a", encoding="utf-8") as update_output_file:
        with open(input_file, "r", encoding="utf-8") as input_append_file:
            update_output_file.write(f"\n Chart Name :: {chart_title}\n")
            update_output_file.write("########################################################\n")
            update_output_file.write(input_append_file.read())


def get_metadata(path_to_helmfile, helmfile_url):
    """
    Fetch the content of metadata and prepare data be added to artifacts.

    Input:
           path_to_metadata: path to metadata.yaml
           helmfile_url: Helmfile Repo to download the helmfile from

    Output:
        dict with two keys:
            'csar_build_properties' - an array with metadata about helm file to be added to csar_build.properties
            'csar_to_be_built' - string with data to be added to csar_to_be_built.properties
    """
    metadata = {}
    metadata_yaml = utils.build_yaml(os.path.join(os.path.dirname(path_to_helmfile), METADATA_PATH))
    metadata['csar_build_properties'] = []
    helmfile_name = metadata_yaml['name']
    helmfile_version = metadata_yaml['version']
    helmfile_url = str(helmfile_url)
    keys = [helmfile_name + '_name', helmfile_name + '_version', helmfile_name + '_url']
    values = [helmfile_name, helmfile_version, helmfile_url]
    for index, key in enumerate(keys):
        metadata['csar_build_properties'].append(str(key) + "=" + str(values[index]) + "\n")
    metadata['csar_to_be_built'] = helmfile_name + ':' + helmfile_version
    return metadata


def generate_csar_content(releases_dict, csar_dict, csar_list, metadata, helmfile_csar_build):
    """
    Take the content of the generated JSON and build up the variables for the CSAR build job.

    Input:
        releases_dict: Dictionary content of the helmfile according the state file input
        csar_dict: List of the CSAR to be created
        csar_list: A list of what CSAR the release should be added to

    Output:
        artifact.properties that will list the chart(s), chart version(s) and chart repo(s) for all the
        releases in the helmfile which should have a CSAR built
    """
    with open(CSAR_BUILD_PROPERTIES, "w", encoding="utf-8") as artifact_prop_file:
        if helmfile_csar_build:
            metadata_content = "".join(metadata)
            artifact_prop_file.write(metadata_content)
        for item in csar_list:
            item = item.split(':')[0]
            csar_item_list = []
            for key, values in csar_dict.items():
                for value in values.split(','):
                    if value == item and key != item:
                        csar_item_list.append(key)
            csar_item_list.insert(0, item)
            for entry in ['name', 'version', 'url']:
                item_list = []
                for csar_item in csar_item_list:
                    values = releases_dict.get(csar_item)
                    item_details = values.get(entry)
                    item_list.append(item_details)
                csar_content = ",".join(item_list)
                artifact_prop_file.write(str(item) + "_" + str(entry) + "=" + str(csar_content) + "\n")


# Note: this can be removed at a later stage, current date 17/02/2022
def check_csar_labels(releases_dict, csar_dict, get_all_images):
    """
    Check CSAR labels for helmfiles that don't have the CSAR label already defined.

    Input:
        releases_dict: Dictionary content of the helmfile according the state file input
        csar_dict: List of the CSAR to be created
        get_all_images: Set to true if all CSARs should be included even if they are not installed

    Output:
        Updates csar_dict with pre-defined release keys
    """
    if not csar_dict:
        csar_dict_temp = {}
        csar_dict_temp.update({
                'eric-tm-ingress-controller-cr-crd': 'eric-cloud-native-base',
                'eric-service-mesh-integration': 'eric-service-mesh-integration',
                'service-mesh-integration': 'service-mesh-integration',
                'eric-eo-so': 'eric-eo-so',
                'eric-oss-dmm': 'eric-oss-dmm',
                'eric-oss-adc': 'eric-oss-adc',
                'eric-oss-pf': 'eric-oss-pf',
                'eric-mesh-controller-crd': 'eric-cloud-native-base',
                'eric-cncs-oss-config': 'eric-cncs-oss-config',
                'eric-cloud-native-base': 'eric-cloud-native-base',
                'eric-oss-ericsson-adaptation': 'eric-oss-ericsson-adaptation',
                'eric-topology-handling': 'eric-topology-handling',
                'eric-oss-common-base': 'eric-oss-common-base',
                'eric-oss-app-mgr': 'eric-oss-app-mgr',
                'eric-oss-config-handling': 'eric-oss-config-handling',
                'eric-oss-uds': 'eric-oss-uds',
                })
        # Add a check to ensure all the items in the dictionary are in the releases dict. For older helmfiles
        # csar_dict = csar_dict_temp.copy()
        csar_dict.update(csar_dict_temp)
        for key in csar_dict_temp:
            if key not in releases_dict.keys():
                csar_dict.pop(key)

        if get_all_images == "false":
            tmp_csar_dict = csar_dict.copy()
            for key in csar_dict:
                name = releases_dict[key]['name']
                installed = releases_dict[key]['installed']
                condition = releases_dict[key]['condition']
                if not installed and (not condition or condition == "false"):
                    if name in csar_dict:
                        del tmp_csar_dict[name]
            csar_dict.clear()
            csar_dict.update(tmp_csar_dict)


# pylint: disable=too-many-arguments, too-many-locals
def fetch_helmfile_details(state_values_file,
                           path_to_helmfile,
                           get_all_images,
                           fetch_charts,
                           helmfile_url,
                           chart_cache_directory):
    """
    Fetch helmfile details (CSAR description and releases).

    Input:
        state_values_file: Site values yaml file
        path_to_helmfile: File path to helmfile to load
        get_all_images: Toggles whether or not to include all CSARs tied to helmfile
                        (not just installed ones)
        fetch_charts: Set to true if charts should be downloaded
        helmfile_url: url to helmfile repo
        chart_cache_directory: The path to the helm chart cache

    Output:
        Writes several files to describe CSAR and releases from helmfile
    """
    LOG.info('Inputted Parameters')
    LOG.info('state_values_file: %s', state_values_file)
    LOG.info('path_to_helmfile: %s', path_to_helmfile)
    LOG.info('get_all_images: %s', get_all_images)
    LOG.info('fetch_charts: %s', fetch_charts)
    LOG.info('path_to_helmfile_repo: %s', helmfile_url)
    clean_up_files()
    helmfile.execute_helmfile_with_build_command(state_values_file, path_to_helmfile)
    helmfile.split_content_from_helmfile_build_file()
    # Generate empty dictionaries
    releases_dict = {}
    csar_dict = {}
    # Generate empty list
    csar_list = []
    # Iterate over all the compiledContent_* files and generate a release Dictionary that holds
    # the chart, version, repo etc. info for all the releases within the Helmfiles
    for filename in os.listdir(CURRENT_WORKING_DIRECTORY):
        if filename.startswith("compiledContent_"):
            helmfile.gather_release_and_repo_info(filename, releases_dict, csar_dict, get_all_images)

    # Temporary fix used for helmfiles that don't have the CSAR Label already defined
    # This can be removed at a later stage
    check_csar_labels(releases_dict, csar_dict, get_all_images)

    # Print info to the screen
    LOG.debug("JSON Final Dict")
    app_json = json.dumps(releases_dict, indent=4, sort_keys=True)
    LOG.debug(str(app_json))
    LOG.info("CSAR's to be built")
    for values in csar_dict.values():
        for value in values.split(','):
            if value in csar_dict:
                if not any(value in string for string in csar_list):
                    version = releases_dict[value]['version']
                    csar_list.append(value + ":" + version)
                    LOG.info(value + ":" + version)

    # Writing the Full Helmfile JSON to a file for later use
    with open(HELMFILE_JSON, "w", encoding="utf-8") as full_json_file:
        full_json_file.write(app_json)

    # releases_and_associated_csar_json = json.dumps(csar_dict)
    # Writing the associated CSAR's to releases to a file for later use
    with open(RELEASES_ASSOCIATED_TO_CSARS_JSON, "w", encoding="utf-8") as releases_and_associated_csar_json_file:
        releases_and_associated_csar_json_file.write(json.dumps(csar_dict, indent=4, sort_keys=True))

    # Get metadata about helmfile
    metadata = get_metadata(path_to_helmfile, helmfile_url)

    # Check if the CSAR Should be built for a Helmfile
    helmfile_csar_build = False
    if os.path.exists(os.path.join(os.path.dirname(path_to_helmfile), 'csar')):
        helmfile_csar_build = True

    # Write the CSAR's to be created to a file for later use
    with open(CSARS_TO_BUILD, 'w', encoding="utf-8") as csar_to_be_built:
        if helmfile_csar_build:
            csar_to_be_built.write(metadata['csar_to_be_built'] + "\n")
        file_content = "\n".join(csar_list)
        csar_to_be_built.write(file_content)

    # Generate the CSAR build artifact.properties
    generate_csar_content(releases_dict, csar_dict, csar_list, metadata=metadata['csar_build_properties'],
                          helmfile_csar_build=helmfile_csar_build)

    # Fetch the charts
    if fetch_charts == 'true':
        helmfile.download_dependencies(path_to_helmfile=path_to_helmfile,
                                       state_values_file=state_values_file,
                                       chart_cache_directory=chart_cache_directory,
                                       only_enabled_releases=False,
                                       copy_to_current_directory=True)
        fetch_helmfile_charts(releases_dict,
                              csar_dict,
                              csar_list,
                              path_to_helmfile,
                              helmfile_csar_build)
        generate_optionality_and_site_values_files(releases_dict, csar_dict, path_to_helmfile)
