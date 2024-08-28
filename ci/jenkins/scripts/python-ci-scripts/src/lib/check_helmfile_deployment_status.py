"""Module to check deployed releases vs. tag-enabled helmfile releases."""
import logging
import json
import re
import os
import time
import oyaml as yaml  # pip install oyaml


from . import utils
from . import helm
from . import helmfile
from . import errors

LOG = logging.getLogger(__name__)

# Global vars
OUTPUT_SITE_VALUES_FILE = "/ci-scripts/output-files/site-values-updated.yaml"


def write_skip_deletion_and_deployed_versions_to_artifact_properties(skip_deletion_flag, deployed_releases_yaml):
    """
    Write SKIP_DELETION status to artifact.properties and deployed release list (chart-version), if available.

    Input:
        skip_deletion_flag: True or False, whether or not to skip a deletion
        deployed_releases_yaml: Yaml from current deployed releases in target namespace

    Output:
        artifact.properties with SKIP_DELETION set along with deployed release list
    """
    with open("/ci-scripts/output-files/artifact.properties", "w", encoding="utf-8") as artifact_properties:
        if skip_deletion_flag:
            artifact_properties.write("SKIP_DELETION=true\n")
        else:
            artifact_properties.write("SKIP_DELETION=false\n")
        for release in deployed_releases_yaml:
            artifact_properties.write(release['chart'] + "\n")


def check_deployed_releases(helm_deployed_releases_yaml, namespace):
    """
    Check if there are any deployed releases in a target namespace.

    Input:
        helm_deployed_releases_yaml: Parsed yaml representing deployed releases to a namespace
        namespace: Target namespace for releases

    Output:
        artifact.properties with SKIP_DELETION set to false if no deployed releases are found

    Returns
    -------
        True if deployed releases exist, False otherwise

    """
    LOG.debug(helm_deployed_releases_yaml)
    number_of_deployed_releases = len(helm_deployed_releases_yaml)
    if number_of_deployed_releases == 0:
        # No deployed releases found - write to artifact properties to force an install
        LOG.info("*** No releases found in namespace %s - New deployment is required", namespace)
        write_skip_deletion_and_deployed_versions_to_artifact_properties(False, helm_deployed_releases_yaml)
        return False
    LOG.info("*** Releases found in namespace %s", namespace)
    return True


def log_all_releases(helm_all_releases_yaml, number_of_deployed_releases, namespace):
    """
    Log a list of chart releases to a namespace.

    Input:
        helm_all_releases_yaml: Parsed yaml representing all releases to a namespace
        number_of_deployed_releases: Count of deployed releases to a namespace
        namespace: Target namespace for releases

    Returns
    -------
        Log information about all releases to a namespace

    """
    number_of_all_releases = len(helm_all_releases_yaml)
    LOG.info("Current releases in namespace %s:", namespace)
    for release in helm_all_releases_yaml:
        LOG.info("%s (chart: %s)", release['name'], release['chart'])
    LOG.info("Number of successful releases in deployment: %s of %s",
             str(number_of_deployed_releases),
             str(number_of_all_releases))


def update_site_values_yaml_with_namespace_defaults(values):
    """
    Update a dictionary representing site-values yaml with helmfile namespace (app and crd) defaults.

    Input:
        values: Parsed site-values yaml

    Returns
    -------
        Updated dictionary with helmfile namespace (app and crd) defaults

    """
    if 'helmfile' not in values:
        values['helmfile'] = {}
    if 'app' not in values['helmfile']:
        values['helmfile']['app'] = {}
    if 'crd' not in values['helmfile']:
        values['helmfile']['crd'] = {}
    values['helmfile']['app']['namespace'] = "eric-app-ns"
    values['helmfile']['crd']['namespace'] = "eric-crd-ns"
    return values


def check_successful_releases(number_of_deployed_releases, number_of_all_releases, helm_deployed_releases_yaml):
    """
    Compare deployed vs. all releases.

    Input:
        number_of_deployed_releases: Count of deployed releases
        number_of_all_releases: Count of all releases
        helm_deployed_releases_yaml: Variable containing deployed releases Yaml data

    Returns
    -------
        Updated artifact.properties if deployed releases differs from all releases
        True if deployed releases matches all release count in namespace, False otherwise

    """
    if number_of_deployed_releases == number_of_all_releases:
        LOG.info("*** Number of successful releases matches number of total releases")
    else:
        LOG.info("*** Number of successful releases does not match number of total releases")
        write_skip_deletion_and_deployed_versions_to_artifact_properties(False, helm_deployed_releases_yaml)
        return False
    return True


def get_charts_with_tag_dict_from_helmfile(path_to_helmfile, filter_tags=None):
    """
    Parse a helmfile and build a dictionary to map charts with tags defined in the helmfile.

    Input:
        path_to_helmfile: File path to helmfile.yaml
        filter_tags: List of tags to filter keys to include

    Returns
    -------
        Dictionary where keys are enabled-toggle tags in helmfile and values are
        chart names related to each found tag

    """
    charts_with_tag = {}
    chart_line = re.compile(r".*chart: .+/(.+)")
    tag_line = re.compile(r"get \"tags\.([-_a-zA-Z]+).*?\"")
    with open(path_to_helmfile, 'r', encoding="utf-8") as helmfile_input:
        tags_all = []
        chart = ""
        # pylint: disable=too-many-nested-blocks
        for line in helmfile_input.readlines():
            if chart_line.match(line):
                chart = chart_line.match(line).group(1)
                # Reset tag
                tags_all = []
            elif re.search(tag_line, line):
                tags_all = re.findall(tag_line, line)
            if tags_all and chart:
                for tag in tags_all:
                    if filter_tags:
                        if tag in filter_tags:
                            if tag in charts_with_tag:
                                charts_with_tag[tag].append(chart)
                            else:
                                charts_with_tag[tag] = [chart]
                    else:
                        if tag in charts_with_tag:
                            charts_with_tag[tag].append(chart)
                        else:
                            charts_with_tag[tag] = [chart]
                tags_all = []
    return charts_with_tag


def analyze_chart_tags(path_to_helmfile, deployed_applications, deployment_tag_list):
    """
    Parse tags tied to chart enables in helmfile and compare requested deployment tag list vs. deployed apps.

    Input:
        path_to_helmfile: File path to helmfile.yaml
        deployed_applications: List of deployed applications, where each entry uses the format:
                               "chart: <chart_name>-<chart_version>"
        deployment_tag_list: Space-separated list of tags enabled in the helmfile

    Returns
    -------
        True if tag-enabled applications matches deployed applications, False
        otherwise

    """
    enable_tags = deployment_tag_list.split(" ")
    charts_with_tag = get_charts_with_tag_dict_from_helmfile(path_to_helmfile)
    LOG.info("Found these tags tied to chart enablement in helmfile: %s", ', '.join(charts_with_tag.keys()))
    # Write to artifact.properties if an enabled app (tag) release is not deployed to the target namespace
    deployed_app_str = ','.join(deployed_applications)
    for tag in enable_tags:
        if tag is not None and tag.strip().upper() != "NONE":
            if tag not in charts_with_tag:
                raise errors.MissingHelmfileTag(f"Unable to find tag {tag} in helmfile chart enables")
            for chart in charts_with_tag[tag]:
                if chart not in deployed_app_str:
                    LOG.info("%s_DEPLOY=true but %s is not deployed on system", tag.upper(), chart)
                    return False
    for ref_tag in charts_with_tag:
        if ref_tag not in enable_tags:
            LOG.info("%s_DEPLOY=false", ref_tag.upper())
        else:
            LOG.info("%s_DEPLOY=true", ref_tag.upper())
    return True


def compare_apps(deployed_applications, helmfile_applications, specific=False):
    """
    Compare deployed vs. helmfile applications and log accordingly.

    Input:
        deployed_applications: List of chart-version entries representing deployed apps
        helmfile_applications: List of chart-version entries representing apps from helmfile
        specific: Customizes logging based on True/False for specific apps

    Returns
    -------
        True if lists match, False otherwise

    """
    LOG.info("*** Comparing")
    if specific:
        LOG.info("Deployed specific (check-tags) applications: %s", str(", ".join(deployed_applications)))
        LOG.info("Helmfile specific (check-tags) applications: %s", str(", ".join(helmfile_applications)))
    else:
        LOG.info("Deployed applications: %s", str(", ".join(deployed_applications)))
        LOG.info("Helmfile applications: %s", str(", ".join(helmfile_applications)))
    # Compare sorted lists of charts (and versions) between what is deployed and what is enabled in the helmfile
    if deployed_applications == helmfile_applications:
        LOG.info("*** Versions in helmfile are the same as deployed versions")
    else:
        LOG.error("*** Versions in helmfile are different to deployed versions")
        return False
    return True


def chart_entry_exists_in_chart_list(chart_entry, chart_list):
    """
    Check if a chart from a formatted chart-version entry exists in a chart list (list of chart lists).

    Input:
        chart_entry: Format of entry string: "chart: <chart>-<version>"
        chart_list: List containing chart name values lists

    Returns
    -------
        True if chart is found in chart list, False otherwise

    """
    LOG.debug("chart_entry_exists_in_chart_list")
    LOG.debug("chart_entry: %s", chart_entry)
    LOG.debug("chart_list: %s", str(chart_list))
    if not isinstance(chart_list, list):
        raise Exception("Invalid chart_list parameter found")
    check_chart_and_version = re.compile(r"chart: (.+)-[0-9]+\.[\.0-9]+-*.*")
    if check_chart_and_version.match(chart_entry):
        chart_name = check_chart_and_version.match(chart_entry).group(1)
        if chart_name in chart_list:
            return True
    else:
        LOG.error("Unable to find chart name from entry %s", chart_entry)
    return False


def analyze_deployed_vs_helmfile_applications(path_to_helmfile, deployed_applications,
                                              helmfile_applications, check_tag_list=None):
    """
    Compare deployed vs. helmfile applications.

    Input:
        path_to_helmfile: File path to helmfile.yaml
        deployed_applications: Sorted list of deployed applications to target namespace
        helmfile_applications: Sorted list of (non-CRD) applications enabled in helmfile
        check_tag_list: Space-separated list of tags to specifically use for specific chart-version
                        checks

    Returns
    -------
        True if deployed applications match helmfile applications, False otherwise

    """
    # Use only specific check tags if they are defined
    if check_tag_list:
        LOG.info("*** Using specific check tags (%s) instead of default deployment tag list",
                 check_tag_list)
        check_tags = check_tag_list.split(' ')
        charts_with_check_tag = get_charts_with_tag_dict_from_helmfile(path_to_helmfile, check_tags)
        # Make sure the requested check tag exists in the helmfile toggles
        for check_tag in check_tags:
            if check_tag not in charts_with_check_tag:
                LOG.error("*** Requested check-tag %s does not exist in the helmfile-found tag list: %s",
                          check_tag, ', '.join(charts_with_check_tag.keys()))
                return False
        LOG.info("charts_with_check_tag:")
        LOG.info(charts_with_check_tag)
        tag_list_entries = []
        for chart_with_check_tag_entry in charts_with_check_tag.values():
            tag_list_entries.extend(chart_with_check_tag_entry)
        LOG.info("tag_list_entries: %s", tag_list_entries)
        specific_deployed_applications = list(filter(lambda app: chart_entry_exists_in_chart_list(app,
                                                                                                  tag_list_entries),
                                                     deployed_applications))
        specific_helmfile_applications = list(filter(lambda app: chart_entry_exists_in_chart_list(app,
                                                                                                  tag_list_entries),
                                                     helmfile_applications))
        specific_deployed_applications.sort()
        specific_helmfile_applications.sort()
        # Compare only specific check-tags apps by default
        return compare_apps(specific_deployed_applications, specific_helmfile_applications, True)

    # Compare all apps by default
    return compare_apps(deployed_applications, helmfile_applications, False)


def remove_extra_deployed_applications(helm_all_releases_yaml, all_installed_noncrd_releases_from_helmfile):
    """
    Remove extra deployed applications that are not defined within the Helmfile.

    Input:
        helm_all_releases_yaml: Parsed yaml representing all releases in a target namespace
        all_installed_noncrd_releases_from_helmfile: All Charts defined within the Helmfile

    Returns
    -------
        List of deployed applications with the removal of extra deployed applications

    """
    helmfile_chart_names_array = []
    for release in all_installed_noncrd_releases_from_helmfile:
        helmfile_chart_names_array.append(release['chart'].split('/')[-1])

    test_string = "internal-eric-test"

    # Remove check for applications that are not defined within the Helmfile
    for deployed_release in helm_all_releases_yaml:
        if test_string in deployed_release['name'] and deployed_release['name'] not in helmfile_chart_names_array:
            LOG.info("Removing release %s from Deployed Application List", deployed_release)
            helm_all_releases_yaml.remove(deployed_release)

    return helm_all_releases_yaml


# pylint: disable=too-many-arguments, too-many-locals, too-many-branches
def compare_deployed_releases_to_helmfile_tags(path_to_helmfile, kubeconfig_file, helm_all_releases_yaml,
                                               deployment_tag_list, check_tag_list=None,
                                               check_full_version="false"):
    """
    Log details about deployed chart releases vs. enabled tags in helmfile.

    Input:
        path_to_helmfile: File path to helmfile.yaml
        kubeconfig_file: Config file tied to target cluster for helmfile commands
        helm_all_releases_yaml: Parsed yaml representing all releases in a target namespace
        deployment_tag_list: Space-separated list of tags enabled in the helmfile
        check_tag_list: Space-separated list of tags to specifically use for specific chart-version
                        checks
        check_full_version: True/false string to toggle full versions for chart deployment checks

    Returns
    -------
        True if no issues are found with chart-version analysis and if deployed chart
        releases matches the enabled helmfile application charts (via tags), and False
        otherwise

    """
    # Get chart names from helmfile list command, pull out chart name and version only if ENABLED is true
    # Filter out CRD
    all_releases_from_helmfile = helmfile.run_helmfile_command(path_to_helmfile, OUTPUT_SITE_VALUES_FILE,
                                                               kubeconfig_file, '--environment', 'build', 'list',
                                                               '--output', 'json')
    if all_releases_from_helmfile.returncode != 0:
        raise errors.HelmfileReleaseError("Unable to list charts from helmfile ",
                                          utils.join_command_stdout_and_stderr(all_releases_from_helmfile))
    all_releases_from_helmfile_json = json.loads(all_releases_from_helmfile.stdout)

    # Filter releases that are both enabled and have a non-empty version string
    all_installed_releases_from_helmfile = [release_item for release_item in
                                            all_releases_from_helmfile_json if
                                            release_item['installed']]
    LOG.debug(all_installed_releases_from_helmfile)
    all_installed_noncrd_releases_from_helmfile = [release_item for release_item in
                                                   all_installed_releases_from_helmfile if
                                                   release_item['namespace'] != 'eric-crd-ns']
    LOG.debug(all_installed_noncrd_releases_from_helmfile)

    LOG.info("---------- Charts in helmfile ----------")
    for release in all_installed_noncrd_releases_from_helmfile:
        LOG.info(release['chart'].split('/')[-1] + " " + release['version'])

    # Remove check for applications that are not defined within the Helmfile
    helm_all_releases_yaml = remove_extra_deployed_applications(helm_all_releases_yaml,
                                                                all_installed_noncrd_releases_from_helmfile)

    # Re-format and sort lists of deployed charts/versions vs. helmfile spec
    deployed_app_dict = {}
    check_chart_and_version = re.compile(r"(.+)-([0-9]+\.[\.0-9]+)-*.*")
    check_version = re.compile(r"([0-9]+\.[\.0-9]+)-*.*")
    # Determine if full-version or sprint-version should be used
    if check_full_version.lower() == "true":
        LOG.info("*** Using full chart version for comparisons")
        check_chart_and_version = re.compile(r"(.+)-([0-9]+\.[\.0-9]+-*.*)")
        check_version = re.compile(r"([0-9]+\.[\.0-9]+-*.*)")
    for release in helm_all_releases_yaml:
        LOG.debug("*** Checking deployed chart/version from %s", release['chart'])
        if check_chart_and_version.match(release['chart']):
            # Add key/value for chart/version for later defaulting of helmfile app version when needed
            chart_name = check_chart_and_version.match(release['chart']).group(1)
            LOG.debug("Found chart name: %s", chart_name)
            deployed_app_dict[chart_name] = check_chart_and_version.match(release['chart']).group(2)
        else:
            raise errors.HelmfileReleaseError("Unable to determine chart-version from " +
                                              f"deployed application: {release['chart']}")
    # Build-out deployed and helmfile application lists for comparisons
    deployed_applications = ["chart: " + key + "-" + value for key, value in deployed_app_dict.items()]
    deployed_applications.sort()
    helmfile_applications = []
    for release in all_installed_noncrd_releases_from_helmfile:
        chart_name = release['chart'].split('/')[-1]
        LOG.debug("*** Checking helmfile chart (version) from %s (%s)", chart_name, release['version'])
        if not release['version'] and chart_name in deployed_app_dict:
            # Default case -- just use deployed app version for consistency
            helmfile_applications.append("chart: " + chart_name + "-" +
                                         deployed_app_dict[chart_name])
        elif check_version.match(release['version']):
            helmfile_applications.append("chart: " + chart_name + "-" +
                                         check_version.match(release['version']).group(1))
        else:
            LOG.error("*** Unable to determine chart-version from helmfile application " +
                      "(likely no deployed release exists for this chart): " +
                      chart_name + "-" + release['version'])
            return False
    helmfile_applications.sort()

    # Compare and log lists of deployed vs. helmfile applications
    if not analyze_deployed_vs_helmfile_applications(path_to_helmfile, deployed_applications,
                                                     helmfile_applications, check_tag_list):
        return False

    # Compare successfully deployed applications to tags - use the general tag list here to
    # compare all enabled applications vs. deployed applications
    return analyze_chart_tags(path_to_helmfile, deployed_applications, deployment_tag_list)


def set_helm_deployed_releases_yaml(helm_deployed_releases_yaml, kubeconfig_file, namespace):
    """
    Populate variable with deployed releases Yaml data.

    Input:
        helm_deployed_releases_yaml: Variable to populate with parsed Yaml data
        kubeconfig_file: Config file for target cluster for helm operations
        namespace: Target namespace for existing deployed releases

    Returns
    -------
        Populate helm_deployed_releases_yaml if successful

    """
    deployed_releases_found = helm.run_helm_command_with_retry(kubeconfig_file, 3, 10,
                                                               'list', '--namespace',
                                                               namespace, '--deployed',
                                                               '--output', 'yaml')
    if deployed_releases_found.returncode != 0:
        # Fail the script instead of writing to properties if helm command fails
        LOG.error("Unable to list deployed releases: %s", utils.join_command_stdout_and_stderr(deployed_releases_found))
        raise errors.HelmCommandError("Unable to list deployed releases")
    # Check for deployed releases
    helm_deployed_releases_yaml.extend(yaml.safe_load(deployed_releases_found.stdout))
    LOG.debug("helm_deployed_releases_yaml: %s", str(helm_deployed_releases_yaml))


def set_and_log_helm_all_releases_yaml(helm_all_releases_yaml, helm_deployed_releases_yaml, kubeconfig_file, namespace):
    """
    Update helm_all_releases_yaml and logs number of deployed releases vs. all releases.

    Input:
        helm_all_releases_yaml: Variable to populate with all release Yaml data
        helm_deployed_releases_yaml: Variable containing Yaml data for deployed releases
        kubeconfig_file: Config file for target cluster for helm operations
        namespace: Target namespace for existing deployed releases

    Returns
    -------
        Populate helm_all_releases_yaml if successful

    """
    all_releases_found = helm.run_helm_command_with_retry(kubeconfig_file, 3, 10,
                                                          'list', '--namespace',
                                                          namespace, '--output', 'yaml')
    if all_releases_found.returncode != 0:
        # Fail the script instead of writing to properties if helm command fails
        LOG.error("Unable to list all releases: %s", utils.join_command_stdout_and_stderr(all_releases_found))
        raise errors.HelmCommandError("Unable to list all releases")
    LOG.info("*** All release data: %s\n", all_releases_found.stdout.decode('utf-8'))
    helm_all_releases_yaml.extend(yaml.safe_load(all_releases_found.stdout))
    LOG.debug("helm_all_releases_yaml: %s", str(helm_all_releases_yaml))
    log_all_releases(helm_all_releases_yaml, len(helm_deployed_releases_yaml), namespace)


# pylint: disable=too-many-arguments
def check_helmfile_deployment(path_to_helmfile, kubeconfig_file, namespace,
                              deployment_tag_list, optional_tag_list, optional_key_value_list,
                              check_tag_list='', check_full_version='false'):
    """
    Verify helmfile deployment status using helmfile template site-values.

    Input:
        state_values_file: Site values file to use as a baseline for tag updates
        path_to_helmfile: Helmfile to use for generating release dict for deployment checks
        kubeconfig_file: Config file for target cluster for helm operations
        namespace: Target namespace for existing deployed releases
        deployment_tag_list: Space-separated list of tags to include in general deployment checks
        optional_key_value_list: Comma-separated list of optional key/value groups
        optional_tag_list: Space-separated list of optional tags to include in general deployment checks
        check_tag_list: Space-separated list of tags to specifically use for specific chart-version
                        checks
        check_full_version: True/false string to toggle full versions for chart deployment checks

    Output:
        artifact.properties with SKIP_DELETION set along with deployed release list

    Returns
    -------
        True if all checks pass, False otherwise

    """
    LOG.info('Inputted parameters:')
    LOG.info('path_to_helmfile: %s', path_to_helmfile)
    LOG.info('kubeconfig_file: %s', kubeconfig_file)
    LOG.info('namespace: %s', namespace)
    LOG.info('deployment_tag_list: %s', deployment_tag_list)
    LOG.info('optional_tag_list: %s', optional_tag_list)
    LOG.info('optional_key_value_list: %s', optional_key_value_list)
    LOG.info('check_tag_list: %s', check_tag_list)
    LOG.info('check_full_version: %s', check_full_version)

    # Reference the helmfile's own site-values-template.yaml for helmfile commands
    state_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")

    # Update a copy of site-values with passed-in tags to be used in helmfile commands
    updated_values = utils.update_new_site_values_with_tags(state_values_file,
                                                            deployment_tag_list, optional_tag_list)

    # Update a copy of site-values with passed-in key/values from label if they exist
    if optional_key_value_list.lower() != 'none':
        updated_values = utils.update_yaml_dict_with_key_value_list(updated_values, optional_key_value_list)

    # Pre-define the app and crd namespaces to ensure consistency when filtering
    updated_values = update_site_values_yaml_with_namespace_defaults(updated_values)

    # Output new site-values file with updated namespace defaults and enabled tags
    with open(OUTPUT_SITE_VALUES_FILE, 'w', encoding="utf-8") as site_values_output_file:
        yaml.safe_dump(updated_values, site_values_output_file, default_flow_style=False)

    # 2. Check if number of total releases matches number of successful releases, and
    #    compare successfully deployed applications to tags
    # Write artifact.properties with SKIP_DELETION set to false if deployed chart releases
    # do not match the list of enabled helmfile application charts (via tags).
    # Repeat check up to 3 times on failed check, to ensure output from helm command
    # is accurate vs. what is in helmfile
    counter = 0
    while True:
        # Check if there are any releases in the namespace
        helm_deployed_releases_yaml = []
        set_helm_deployed_releases_yaml(helm_deployed_releases_yaml, kubeconfig_file, namespace)
        if not check_deployed_releases(helm_deployed_releases_yaml, namespace):
            return False
        number_of_deployed_releases = len(helm_deployed_releases_yaml)

        # Get the number of releases in the deployment for a given namespace
        helm_all_releases_yaml = []
        set_and_log_helm_all_releases_yaml(helm_all_releases_yaml, helm_deployed_releases_yaml,
                                           kubeconfig_file, namespace)
        number_of_all_releases = len(helm_all_releases_yaml)

        # Compare deployed release count to total releases in the namespace,
        # return if the counts do not match
        if not check_successful_releases(number_of_deployed_releases, number_of_all_releases,
                                         helm_deployed_releases_yaml):
            return False

        # Break out of loop on successful check
        LOG.info("*** Comparing deployed releases to tags -- running check #%s", str(counter + 1))
        if compare_deployed_releases_to_helmfile_tags(path_to_helmfile, kubeconfig_file, helm_all_releases_yaml,
                                                      deployment_tag_list, check_tag_list, check_full_version):
            break
        counter += 1
        if counter == 3:
            # If checks are still unsuccessful after 3 attempts, write SKIP_DELETION
            # false to artifact properties and return
            write_skip_deletion_and_deployed_versions_to_artifact_properties(False, helm_deployed_releases_yaml)
            return False
        time.sleep(5)

    LOG.info("*** All checks passed, skipping deletion of system")
    write_skip_deletion_and_deployed_versions_to_artifact_properties(True, helm_deployed_releases_yaml)
    return True
