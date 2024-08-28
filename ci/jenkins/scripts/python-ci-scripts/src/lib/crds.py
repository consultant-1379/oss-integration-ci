"""Module to manage CRDs."""

import logging
import os
import re
import glob
import multiprocessing.pool
import functools
import oyaml as yaml  # pip install oyaml

from . import utils
from . import helmfile
from . import cihelm
from . import errors
from . import containers

LOG = logging.getLogger(__name__)
PROPERTIES_FILE = 'crd_details_artifact.properties'
CWD = os.getcwd()


# pylint: disable=too-many-arguments, too-many-locals, too-many-statements
def compile_crd_details_from_app_chart(path_to_helmfile, chart_name,
                                       chart_version, chart_repo, adp_crd_handler_image,
                                       repo_password=None,
                                       repo_username=None):
    """
    Retrieve CRD details from a chart and generate a new property file with chart details.

    Input:
        path_to_helmfile: Path to the helmfile to check against.
        chart_name: application chart name
        chart_version: application chart version
        chart_repo: application chart repo
        adp_crd_handler_image: The image point to adp-crd-handler
        repo_password: password to log into the application chart repo
        repo_username: username to log into the application chart repo

    Output:
        properties file with the new CHART details for delivery.
    """
    # Set the state values file here to the default build environments variable.
    # This ensures all tags are true, which ensure all details are returned from the helmfile build command
    state_values_file = os.path.dirname(path_to_helmfile) + "/build-environment/tags_true.yaml"
    LOG.debug('Inputted parameters')
    LOG.debug('path_to_helmfile: %s', path_to_helmfile)
    LOG.debug('chart_name: %s', chart_name)
    LOG.debug('chart_version: %s', chart_version)
    LOG.debug('chart_repo: %s', chart_repo)
    LOG.debug('Auto set variables')
    LOG.debug('state_values_file: %s', state_values_file)
    LOG.debug('PROPERTIES_FILE: %s', PROPERTIES_FILE)
    mask = []
    if 'GERRIT_PASSWORD' in os.environ:
        mask.append(os.environ['GERRIT_PASSWORD'])
    if 'GERRIT_USERNAME' in os.environ:
        mask.append(os.environ['GERRIT_USERNAME'])
    if repo_password is not None:
        mask.append(repo_password)
    if repo_username is not None:
        mask.append(repo_username)

    overall_chart_name = []
    overall_chart_version = []
    overall_chart_repo = []

    csar_dict = helmfile.fetch_csar_details_from_helmfile(state_values_file, path_to_helmfile)
    repo_associate_to_chart_dict = helmfile.associate_repo_details_to_charts(state_values_file, path_to_helmfile)
    netrc = helmfile.build_netrc_file_with_repo_credentials_from_helmfile(state_values_file, path_to_helmfile, CWD)

    # Generate a list of the details entered and strip the whitespace
    chart_name_list = chart_name.split(",")
    chart_name_list = [x.strip(' ') for x in chart_name_list]
    chart_version_list = chart_version.split(",")
    chart_version_list = [x.strip(' ') for x in chart_version_list]
    chart_repo_list = chart_repo.split(",")
    chart_repo_list = [x.strip(' ') for x in chart_repo_list]

    chart_list = zip(chart_name_list, chart_version_list, chart_repo_list)

    for app_name, app_version, app_repo in chart_list:
        deps = []
        deps.append((app_repo, app_version, app_name))
        LOG.info("Fetching details for %s, with version %s", app_name, app_version)
        # pylint: disable=no-member
        cihelm.fetch(deps, netrc, mask, CWD)

        utils.extract_tar_file(app_name + "-" + app_version + ".tgz", CWD)
        cmd_args = ["crd", "collect", "--chart", "/workdir/" + app_name, "--workspace",
                    "/workdir/CRD", "--debug", "--cleanup"]
        crd_files_list = get_crd_files_list(adp_crd_handler_image, cmd_args)

        LOG.info(crd_files_list)

        if not isinstance(crd_files_list, int):
            LOG.debug("CRDs extracted : %s", str(crd_files_list))
            overall_chart_name, overall_chart_version, overall_chart_repo = generate_crd_details_for_properties_file(
                    app_name, app_version, app_repo, repo_associate_to_chart_dict, csar_dict, crd_files_list,
                    overall_chart_name, overall_chart_version, overall_chart_repo)
        else:
            raise Exception("Error Receiving CRD Details")
    build_properties_file(overall_chart_name, overall_chart_version, overall_chart_repo)
    if os.path.exists(CWD + '/.netrc'):
        netrc.remove()


def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            pool.close()
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator


@timeout(120.0)
def get_crd_files_list(adp_crd_handler_image, cmd_args):
    """
    Get the CRD files list.

    Input:
        adp_crd_handler_image: The image that points to the adp-crd-handler
        cmd_args: The arguments to pass to the docker image

    Returns
    -------
        A list containing the CRD files
    """
    env_list = ["--user $(id -u):$(id -g)"]
    try:
        containers.run_docker_command(adp_crd_handler_image, cmd_args, env_list)
        return glob.glob(CWD + "/CRD/*")
    # pylint: disable=broad-except
    except Exception as ex:
        LOG.info("An exception occurred in collecting the CRD files: %s", str(ex))
        return 1


def generate_crd_details_for_properties_file(chart_name, chart_version, chart_repo,
                                             repo_associate_to_chart_dict, csar_dict, crd_files_list,
                                             overall_chart_name, overall_chart_version, overall_chart_repo):
    """
    Generate the properties file details with the required CRD details.

    Inputs:
        chart_name: application chart name
        chart_version: application chart version
        chart_repo: application chart repo
        repo_dict: Dictionary of all the repositories gather from the helmfile build command
        csar_dict: Dictionary of the csar's associated to an application
    """
    # Set the initial values for chart_name, chart_version & chart_repo
    overall_chart_name.append(chart_name)
    overall_chart_version.append(chart_version)
    overall_chart_repo.append(chart_repo)

    for file in crd_files_list:
        if ('tgz' or 'crd') in file:
            # Iterate over all the CRDs found
            LOG.info("CRD File Found: %s", str(file))
            filename = os.path.basename(file)
            crd_chart_name = re.split(r'-[0-9]*\.[0-9]*\.[0-9]*', filename, maxsplit=1)[0]
            # Check does the CRD exist in the helmfile by checking does its repository exist
            if crd_chart_name not in repo_associate_to_chart_dict:
                LOG.warning("CRD %s has no reference to a repository in the repositories.yaml. Skipped its addition",
                            str(crd_chart_name))
                continue
            # Check does the CRD in the application chart map towards the application CSAR
            if crd_chart_name in csar_dict:
                csar_list = csar_dict[str(crd_chart_name)].split(',')
                if chart_name not in csar_list:
                    LOG.warning("CRD %s is not mapped towards this application CSAR. "
                                "Mapping(s) found %s. Skipped its addition",
                                str(crd_chart_name), str(" ".join(csar_list)))
                    continue
            overall_chart_name.append(crd_chart_name)
            LOG.debug("crd_chart_name: %s", str(crd_chart_name))

            crd_chart_version = re.split(crd_chart_name + '-', filename, maxsplit=1)[1].replace('.tgz', '')
            overall_chart_version.append(crd_chart_version)
            LOG.debug("crd_chart_version: %s", str(crd_chart_version))

            crd_chart_repo = repo_associate_to_chart_dict.get(crd_chart_name)

            overall_chart_repo.append(crd_chart_repo)
            LOG.debug("crd_chart_repo: %s", str(crd_chart_repo))
    return overall_chart_name, overall_chart_version, overall_chart_repo


def build_properties_file(overall_chart_name, overall_chart_version, overall_chart_repo):
    """
    Build the properties file using the global overall chart lists.

    Inputs:
        overall_chart_name, list of all the chart names for main chart and CRDs found
        overall_chart_version, list of all the chart version found for main chart and CRDs found
        overall_chart_repo, list of all the chart repos found for main chart and CRDs found
    """
    # Create a properties file of the chart details found
    overall_chart_names_string = ', '.join(overall_chart_name)
    overall_chart_versions_string = ', '.join(overall_chart_version)
    overall_chart_repos_string = ', '.join(overall_chart_repo)
    with open(PROPERTIES_FILE, "w", encoding="utf-8") as properties:
        properties.write('CHART_NAME=' + str(overall_chart_names_string) + "\n")
        properties.write('CHART_VERSION=' + str(overall_chart_versions_string) + "\n")
        properties.write('CHART_REPO=' + str(overall_chart_repos_string) + "\n")


# pylint: disable=too-many-locals
def extract_crds_from_template_dir(template_dir):  # noqa: C901
    """
    Extract and generate separate CRD template files from a directory of templates.

    Input:
        template_dir: Template (Yaml) directory

    Output:
        Directories by template version with any CRD template files
    """
    LOG.info("Checking directory for template Yaml files: %s", template_dir)
    versions_found = []
    for check_file in os.listdir(template_dir):
        full_check_file = os.path.join(template_dir, check_file)
        if os.path.isfile(full_check_file):
            ext = os.path.splitext(check_file)[-1].lower()
            if ext in ('.yaml', '.yml'):
                LOG.info("Checking Yaml file %s", full_check_file)
                with open(full_check_file, 'r', encoding="utf-8") as yaml_file:
                    yaml_docs = yaml.safe_load_all(yaml_file)
                    for yaml_doc in yaml_docs:
                        if yaml_doc and "kind" in yaml_doc:
                            if yaml_doc["kind"] == "CustomResourceDefinition":
                                basename = os.path.basename(check_file)
                                version = os.path.splitext(basename)[0]
                                if version not in versions_found:
                                    versions_found.append(version)
                                version_dir = os.path.join(template_dir, version)
                                if not os.path.exists(version_dir):
                                    os.makedirs(version_dir)
                                crd_kind = yaml_doc["spec"]["names"]["kind"]
                                crd_group = yaml_doc["spec"]["group"]
                                for version in yaml_doc["spec"]["versions"]:
                                    crd_version = version["name"]
                                    crd_file_name = f"{crd_group}-{crd_kind}-{crd_version}.yaml"
                                    output_crd_file = os.path.join(version_dir, crd_file_name)
                                    LOG.info("Writing output CRD Yaml file %s", output_crd_file)
                                    with open(output_crd_file, 'w', encoding="utf-8") as output_yaml_file:
                                        yaml.dump(yaml_doc, output_yaml_file)
    versions_found_file = os.path.join(template_dir, "versions_found")
    with open(versions_found_file, 'w', encoding="utf-8") as version_file:
        for version in versions_found:
            LOG.info("Found version: %s", version)
            version_file.write(f"{version}\n")


# pylint: disable=too-many-locals
def validate_template_with_json_schemas(template_dir, check_dir, kubeconform_image):  # noqa: C901
    """
    Validate CRs against CRD schemas from a directory of templates.

    Input:
        template_dir: Template (Yaml) directory
        check_dir: Directory containining JSON schema files
        kubeconform_image: Image that contains kubeconform binary

    Output:
        Logs any CR non-conformance and returns number of non-conformed CRs
    """
    non_conformance_count = 0
    non_conformance_yaml_files = []
    non_conformance_logs = []
    dir_basename = os.path.basename(check_dir)
    for template_file in os.listdir(template_dir):
        full_template_file = os.path.join(template_dir, template_file)
        ext = os.path.splitext(template_file)[-1].lower()
        if not os.path.isfile(full_template_file) \
           or ext not in ('.yaml', '.yml'):
            continue
        LOG.info("Analyzing file %s for CRs...", full_template_file)
        basename = os.path.basename(template_file)
        version = os.path.splitext(basename)[0]
        resource_dir = os.path.join(template_dir, version)
        if version == dir_basename:
            if not os.path.exists(resource_dir):
                os.makedirs(resource_dir)
            with open(full_template_file, 'r', encoding="utf-8") as yaml_file:
                yaml_docs = yaml.safe_load_all(yaml_file)
                for yaml_doc in yaml_docs:
                    if yaml_doc and "kind" in yaml_doc:
                        if yaml_doc["kind"] != "CustomResourceDefinition":
                            kind = yaml_doc["kind"].lower()
                            api_version = yaml_doc["apiVersion"]
                            if len(api_version.split("/")) < 2:
                                continue
                            LOG.debug("Found api_version: %s", api_version)
                            group_full = api_version.split("/")[0]
                            group = group_full.split(".")[0].lower()
                            version = api_version.split("/")[1].lower()
                            resource_yaml_file = f"{group}-{kind}-{version}.yaml"
                            json_file = f"{group}-{kind}-{version}.json"
                            LOG.debug("Looking for CRD JSON schema: %s", json_file)
                            check_json_file = os.path.join(check_dir, json_file)
                            if os.path.exists(check_json_file):
                                resource_file = os.path.join(resource_dir, resource_yaml_file)
                                with open(resource_file, 'w', encoding="utf-8") as output_yaml_file:
                                    yaml.dump(yaml_doc, output_yaml_file)
                                schema_locations_str = "-schema-location default" \
                                                       f" -schema-location {check_json_file}"
                                LOG.info("Comparing CR %s with CRD schema %s", resource_file, check_json_file)
                                res = containers.run_kubeconform(kubeconform_image,
                                                                 "/bin/sh -c \"/kubeconform/kubeconform"
                                                                 f" {schema_locations_str}"
                                                                 f" {resource_file}\"")
                                output = res.decode('utf-8')
                                if output != "":
                                    non_conformance_yaml_files.append(resource_file)
                                    non_conformance_logs.append(output)
                                    non_conformance_count += 1
    # Summarize reported non-conformance instances
    if non_conformance_count > 0:
        LOG.info("*** CR non-conformance summary ***")
        for (resource_file, output_log) in zip(non_conformance_yaml_files, non_conformance_logs):
            with open(resource_file, 'r', encoding="utf-8") as yaml_file:
                LOG.info("Yaml doc for review with violation: %s", yaml_file.read())
            LOG.info("Related error log: %s", output_log)
    return non_conformance_count


# pylint: disable=too-many-nested-blocks
def check_crs_from_templates_dir(template_dir, kubeconform_image):
    """
    Test CRs against CRD schemas from a directory of templates.

    Input:
        template_dir: Template (Yaml) directory
        kubeconform_image: Image that contains kubeconform binary

    Output:
        Runs CR conformance checks against CRD schemas generated
    """
    LOG.info("Template directory: %s", template_dir)
    extract_crds_from_template_dir(template_dir)
    versions_found_file = os.path.join(template_dir, "versions_found")
    curr_cwd = os.getcwd()
    with open(versions_found_file, 'r', encoding="utf-8") as version_file:
        valid_versions = version_file.readlines()
        for valid_version in valid_versions:
            valid_version = valid_version.strip()
            LOG.info("Looking at version %s", valid_version)
            check_dir = os.path.join(template_dir, valid_version)
            if os.path.isdir(check_dir):
                LOG.info("Checking dir %s", check_dir)
                for check_file in os.listdir(check_dir):
                    full_check_file = os.path.join(check_dir, check_file)
                    LOG.info("Checking %s", full_check_file)
                    ext = os.path.splitext(check_file)[-1].lower()
                    if ext in ('.yaml', '.yml'):
                        os.chdir(check_dir)
                        try:
                            res = containers.run_kubeconform(kubeconform_image,
                                                             "/bin/sh -c \"export FILENAME_FORMAT="
                                                             "'{group}-{kind}-{version}' &&"
                                                             " /kubeconform/openapi2jsonschema.py"
                                                             f" {full_check_file}\"")
                            LOG.info("Result: %s", res.decode('utf-8'))
                        except Exception as exc:
                            LOG.error("An exception occurred while calling kubeconform via docker run")
                            raise exc
                        finally:
                            os.chdir(curr_cwd)
                result = validate_template_with_json_schemas(template_dir,
                                                             check_dir,
                                                             kubeconform_image)
                if result > 0:
                    raise errors.CRNonConformanceError("Number of CRs that do not conform"
                                                       f" for version {valid_version}: {result}")
    LOG.info("CR conformance checks completed with no errors found")
