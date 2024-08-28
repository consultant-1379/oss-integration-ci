"""Module for decorator related management."""
import click


def log_verbosity_option(func):
    """Set a decorator for the log verbosity command line argument."""
    return click.option('-v', '--verbosity', type=click.IntRange(0, 4), default=3, show_default=True,
                        help='number for the log level verbosity, 0 lowest, 4 highest'
                        )(func)


# pylint: disable=redefined-builtin
def dir(func):
    """Set a decorator to set a directory."""
    return click.option('--dir', 'dir', required=True, type=str,
                        help='Used to set the directory path'
                        )(func)


def csar_repo_option(func):
    """Set a decorator for the CSAR artifactory repo url."""
    return click.option('--csar-repo-url', 'csar_repo_url', required=True, type=str,
                        help='A URL, including the path to the directory in artifactory where CSARs \
                              are stored for a specific application.'
                        )(func)


def applications_to_check_option(func):
    """Set a decorator for the file that has the list of application to iterate over."""
    return click.option('--applications-to-check', 'applications_to_check', required=True, type=str,
                        help='This should be file with a list of all the application from the helmfile \
                              that a CSAR should be checked for.'
                        )(func)


def path_to_chart(func):
    """Set a decorator for the helm chart full path to the file."""
    return click.option('--path-to-chart', 'path_to_chart', required=True, type=str,
                        help='Used to set the path to the chart'
                        )(func)


def directory_path(func):
    """Set a decorator to be able to specify the path to a specific directory."""
    return click.option('--directory-path', 'directory_path', required=True, type=str,
                        help='Used to set the full path to a directory'
                        )(func)


def output_file(func):
    """Set a decorator for the path to the full values file for output."""
    return click.option('--output-file', 'output_file',
                        required=False, default="artifact.properties", type=str,
                        help='This is the full path to the output file'
                        )(func)


def input_file(func):
    """Set a decorator to set a file name."""
    return click.option('--input-file', 'input_file',
                        required=False, default="input.properties", type=str,
                        help='Used to pass a file into the script'
                        )(func)


def execution_type(func):
    """Set a decorator to set a execution type."""
    return click.option('--execution-type', 'execution_type',
                        required=True, type=str,
                        help='Used to pass a string identifier'
                        )(func)


def space_key(func):
    """Set the Confluence space key."""
    return click.option('--space-key', required=True, type=str, default=None,
                        help='This is the Confluence space key'
                        )(func)


def url(func):
    """Set the URL."""
    return click.option('--url', required=True, type=str, default=None,
                        help='This is the URL for the function'
                        )(func)


def parent_id(func):
    """Set the parent ID of the Confluence page."""
    return click.option('--parent-id', required=True, type=str, default=None,
                        help='This is the Confluence parent ID'
                        )(func)


def documents_path(func):
    """Set the path of the files to be moved to Confluence."""
    return click.option('--documents-path', required=True, type=str, default=None,
                        help='This is the page of documents for Confluence'
                        )(func)


def helmfile_path(func):
    """Set a decorator for the path to the helmfile under test."""
    return click.option('--path-to-helmfile', 'path_to_helmfile', required=True, type=str,
                        help='This is the full path to the helmfile under test'
                        )(func)


def helmfile_url(func):
    """Set a decorator for the path to the helmfile url under test."""
    return click.option('--helmfile-url', 'helmfile_url', required=True, type=str,
                        help='This is the full path to the helmfile url under test'
                        )(func)


def helmfile_name(func):
    """Set a decorator for the name of the helmfile under test."""
    return click.option('--helmfile-name', 'helmfile_name', required=True, type=str,
                        help='This is the name of the helmfile under test'
                        )(func)


def helmfile_version(func):
    """Set a decorator for the version of the helmfile under test."""
    return click.option('--helmfile-version', 'helmfile_version', required=True, type=str,
                        help='Used to set the version of the helmfile'
                        )(func)


def helmfile_repo(func):
    """Set a decorator to set an artifact properties file."""
    return click.option('--helmfile-repo', 'helmfile_repo', required=True, type=str,
                        help='Used to set the repo URL of the helmfile'
                        )(func)


def chart_name(func):
    """Set a decorator for the helm chart name."""
    return click.option('--chart-name', 'chart_name', required=True, type=str,
                        help='Used to set the helm chart name'
                        )(func)


def chart_version(func):
    """Set a decorator for the helm chart version."""
    return click.option('--chart-version', 'chart_version', required=True, type=str,
                        help='Used to set the helm chart version'
                        )(func)


def chart_cache_directory(func):
    """Set the destination path for dependencies to be cached to."""
    return click.option('--chart-cache-directory', required=False, type=str, default=None,
                        help='This is the path to the desired directory to cache dependencies to'
                        )(func)


def manifest_file(func):
    """Set a decorator used to set the path of the CSAR manifest file."""
    return click.option('--manifest-file', 'manifest_file', required=True, type=str,
                        help='Used to set the path of the CSAR manifest file'
                        )(func)


def images_file(func):
    """Set a decorator used to set the path of the CSAR images.txt file."""
    return click.option('--images-file', 'images_file', required=True, type=str,
                        help='Used to set the path of the CSAR images file'
                        )(func)


def chart_repo(func):
    """Set a decorator for the helm chart repository."""
    return click.option('--chart-repo', 'chart_repo', required=True, type=str,
                        help='Used to set the helm chart repo'
                        )(func)


def username(func):
    """Set a decorator for the username."""
    return click.option('--username', 'username', envvar='FUNCTIONAL_USER_USERNAME',
                        default=None, required=False, type=str,
                        help='This is the username Jenkins uses for ARM Registry Credentials. This can also be set as '
                             'an environment variable, FUNCTIONAL_USER_USERNAME, if extra security is needed'
                        )(func)


def user_id(func):
    """Set a decorator for the user id."""
    return click.option('--user-id', 'user_id', default=None, required=True, type=str,
                        help='Set to the user id or name to set'
                        )(func)


def user_password(func):
    """Set a decorator for the user password."""
    return click.option('--user-password', 'user_password', envvar='FUNCTIONAL_USER_PASSWORD',
                        default=None, required=False, type=str,
                        help='This is the user password Jenkins uses for ARM Registry Credentials, This can also be '
                             'set as an environment variable, FUNCTIONAL_USER_PASSWORD, if extra security is needed'
                        )(func)


def user_token(func):
    """Set a decorator for the user token."""
    return click.option('--user-token', 'user_token', envvar='FUNCTIONAL_USER_TOKEN',
                        default=None, required=False, type=str,
                        help='This is the user token Jenkins uses for ARM Registry Credentials, This can also'
                             'be set as an environment variable, FUNCTIONAL_USER_TOKEN, if extra security is needed'
                        )(func)


def artifactory_username(func):
    """Set a decorator for the username."""
    return click.option('--artifactory-username', 'artifactory_username', envvar='GERRIT_USERNAME',
                        default=None, required=True, type=str,
                        help='This is the username Jenkins uses for Artifactory Credentials. This can also '
                             'be set as an environment variable, GERRIT_USERNAME, if extra security is needed'
                        )(func)


def artifactory_password(func):
    """Set a decorator for the user password."""
    return click.option('--artifactory-password', 'artifactory_password', envvar='GERRIT_PASSWORD',
                        default=None, required=True, type=str,
                        help='This is the password Jenkins uses for Artifactory Credentials, This can also'
                             'be set as an environment variable, GERRIT_PASSWORD, if extra security is needed'
                        )(func)


def state_values_file(func):
    """Set a decorator for the path to the full values file."""
    return click.option('--state-values-file', 'state_values_file', required=True, type=str,
                        help='This is the full path to the state values file'
                        )(func)


def optional_key_value_list(func):
    """Set a decorator for the list of keys/value sets for a new state values file."""
    return click.option('--optional-key-value-list', 'optional_key_value_list', required=True, type=str,
                        help='This is a comma separated list of state values file key/value sets,'
                             'key levels are separated by \".\" and values by \"=\",'
                             'e.g. eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false'
                        )(func)


def artifact_url(func):
    """Set a decorator used to set the URL of the CSAR artifact."""
    return click.option('--artifact-url', 'artifact_url', required=True, type=str,
                        help='Used to set the URL of the CSAR artifact'
                        )(func)


def use_dependency_cache(func):
    """Set a decorator to decide to use the dependency cache or not."""
    return click.option('--use-dependency-cache', 'use_dependency_cache',
                        required=False,
                        default="true",
                        show_default=True, type=str,
                        help='Used to decide whether to use the dependency cache or not.'
                        )(func)


def dependency_cache_directory(func):
    """Set a decorator to be able to specify the path to the local dependency repo."""
    return click.option('--dependency-cache-directory', 'dependency_cache_directory',
                        required=False,
                        default="/tmp/cachedir",
                        show_default=True, type=str,
                        help='Used to set the directory where the local cache of dependencies are stored,'
                             ' default /tmp/cachedir'
                        )(func)


def version(func):
    """Set a decorator to set a version."""
    return click.option('--version', 'version', required=True, type=str,
                        help='Used to set a version'
                        )(func)


def get_all_images(func):
    """Set a decorator set a true/false boolean."""
    return click.option('--get-all-images', 'get_all_images', required=True, type=str,
                        help='Set a true or false boolean to state whether to gather all CSAR independent \
                              of state values file'
                        )(func)


def fetch_charts(func):
    """Set a decorator set a true/false boolean."""
    return click.option('--fetch-charts', 'fetch_charts', required=True, type=str,
                        help='Set a true or false boolean this tells the script to download the charts from \
                              the helmfile'
                        )(func)


def namespace(func):
    """Set a decorator for the kubenetes namespace."""
    return click.option('--namespace', 'namespace', required=True, type=str,
                        help='Set to the kubernetes namespace name'
                        )(func)


def name(func):
    """Set a decorator for a general resource name."""
    return click.option('--name', 'name', required=True, type=str,
                        help='Set to a general resource name'
                        )(func)


def release_name(func):
    """Set a decorator for a release name."""
    return click.option('--release-name', 'release_name', required=True, type=str,
                        help='Set to a release name'
                        )(func)


def ignore_exists(func):
    """Set a decorator for an ignore flag if a resource exists."""
    return click.option('--ignore-exists', 'ignore_exists', default="false", required=True, type=str,
                        help='This is used to set a flag for ignoring a check if a resource exists'
                        )(func)


def image(func):
    """Set a decorator for an image parameter."""
    return click.option('--image', 'image', required=True, type=str,
                        help='Set to the image to use'
                        )(func)


def kubeconfig_file(func):
    """Set a decorator for the kubeconfig path."""
    return click.option('--kubeconfig-file', 'kubeconfig_file', required=True, type=str,
                        help='Set to the kubernetes kube config path to log onto the kubernetes system'
                        )(func)


def dockerconfig_file(func):
    """Set a decorator for the docker config path."""
    return click.option('--dockerconfig-file', 'dockerconfig_file', required=True, type=str,
                        help='Set to the docker config path'
                        )(func)


def secret_name(func):
    """Set a decorator for secret name."""
    return click.option('--secret-name', 'secret_name', required=True, type=str,
                        help='Used to set the secret name'
                        )(func)


def resource_name(func):
    """Set the name of a resource."""
    return click.option("--resource-name", "resource_name", required=True, type=str,
                        help="used to specify a Kubernetes resource name"
                        )(func)


def resource_type(func):
    """Set the type of resource, e.g. secret, configmap etc."""
    return click.option("--resource-type", "resource_type", required=True, type=str,
                        help="used to specify a Kubernetes resource type, \"secret\", \"configmap\"."
                        )(func)


def path_base_yaml(func):
    """Set a decorator for the base file to use in the merge."""
    return click.option('--path-base-yaml', 'path_base_yaml', required=True, type=str,
                        help='This is the base file that will be used in the merge. This the main file'
                        )(func)


def path_override_yaml(func):
    """Set a decorator for the override file to use in the merge."""
    return click.option('--path-override-yaml', 'path_override_yaml', required=True, type=str,
                        help='This is the override file that will be used in the merge. This the file that \
                              will be merged to the path_base_yaml file'
                        )(func)


def path_output_yaml(func):
    """Set a decorator for the output file to use in the merge."""
    return click.option('--path-output-yaml', 'path_output_yaml', required=True, type=str,
                        help='This is the output file that will be used in the merge.'
                        )(func)


def check_values_only(func):
    """Set a decorator to set the parameter for merging values only for the site values file."""
    return click.option('--check-values-only', 'check_values_only', default="false", required=True, type=str,
                        help='This is used to set the parameter for merging values parameter only for the \
                              site values file'
                        )(func)


def file(func):
    """Set a decorator to set a file name."""
    return click.option('--file', 'file', required=True, type=str,
                        help='Used to set the file name'
                        )(func)


def from_literals(func):
    """Set a decorator used to set a space-separated list of literal values with key=value format."""
    return click.option('--from-literals', 'from_literals', required=True, type=str,
                        help='Used to set a space-separate list of literal values'
                        )(func)


def cluster_role(func):
    """Set a decorator used to set a cluster role."""
    return click.option('--cluster-role', 'cluster_role', required=True, type=str,
                        help='Used to set a cluster role'
                        )(func)


def service_account(func):
    """Set a decorator used to set a service account."""
    return click.option('--service-account', 'service_account', required=True, type=str,
                        help='Used to set a service account'
                        )(func)


def message(func):
    """Set a decorator used to set a message string."""
    return click.option('--message', 'message', required=True, type=str,
                        help='Used to set a message string'
                        )(func)


def git_repo_local(func):
    """Set a decorator used to set the directory where the repo is cloned to."""
    return click.option('--git-repo-local', 'git_repo_local', required=True, type=str,
                        default=".bob/cloned_repo",
                        help='Used to set the local directory where the repo is cloned to, default .bob/cloned_repo'
                        )(func)


def gerrit_branch(func):
    """Set a decorator used to a message string."""
    return click.option('--gerrit-branch', 'gerrit_branch', required=True, type=str,
                        default="master",
                        help='Used to set the Gerrit branch the review will be created on, default master'
                        )(func)


def gerrit_change_number(func):
    """Set a decorator used to set the review change number."""
    return click.option('--gerrit-change-number', 'gerrit_change_number', required=True, type=str,
                        help='Used to set the Gerrit change number of the review'
                        )(func)


def timeout(func):
    """Set timeout for any process."""
    return click.option("--timeout", "timeout", required=True, type=str,
                        help="used to set a timeout on a process that has that ability"
                        )(func)


def docker_auth_config(func):
    """Set a decorator to specify the docker config file name."""
    return click.option('--docker-auth-config', required=True, type=str,
                        help='Used to specify the docker config file name during a deployment'
                        )(func)


def flow_area(func):
    """Set a decorator to specify the flow area."""
    return click.option('--flow-area', required=True, type=str,
                        help='Used to specify the flow area during a deployment'
                        )(func)


def cluster_name(func):
    """Set a decorator to specify the cluster name."""
    return click.option('--cluster-name', required=True, type=str,
                        help='Used to specify the cluster name during a deployment'
                        )(func)


def retries(func):
    """Set retries for any process."""
    return click.option("--retries", "retries", required=True, type=int, default=10,
                        help="used to set a number of retries on a process that has that ability"
                        )(func)


def output_state_values_file(func):
    """Set a decorator for the path to the full values file for output."""
    return click.option('--output-state-values-file', 'output_state_values_file', required=True, type=str,
                        help='This is the full path to the output state values file'
                        )(func)


def deployment_tag_list(func):
    """Set a decorator for the list of tags for the application to iterate over."""
    return click.option('--deployment-tags', 'deployment_tag_list', required=True, type=str,
                        help='This should be a list of the deployment tags which are set to true'
                        )(func)


def optional_tag_list(func):
    """Set a decorator for the list of tags for the application to iterate over."""
    return click.option('--optional-tags', 'optional_tag_list', required=True, type=str,
                        help='This should be a list of the optional deployment tags which are set to true'
                        )(func)


def check_tag_list(func):
    """Set a decorator for the list of tags for application checks to iterate over."""
    return click.option('--check-tags', 'check_tag_list', required=True, type=str,
                        help='This should be a list of the deployment tags to use for deployment checks'
                        )(func)


def check_full_version(func):
    """Set a decorator for true/false to enable full versions for application checks."""
    return click.option('--check-full-version', 'check_full_version', required=True, type=str,
                        help='This should be true/false to enable full versions for application checks'
                        )(func)


def tags_set_to_true_only(func):
    """Set a decorator to set a boolean flag to only download CSARs with tags set to true."""
    return click.option('--tags-set-to-true-only', 'tags_set_to_true_only', required=True, type=str,
                        help='Used to indicate whether only charts with tags set to true are \
                              processed by the get_app_version_from_helmfile command'
                        )(func)


def filter_by_days_past(func):
    """Set a decorator to filter Artifactory responses between now and the provided number of days gone past."""
    return click.option('--filter-by-days-past', required=False, type=int, default=14,
                        help='Used to filter Artifactory responses between the current day and the provided number of \
                              days gone past'
                        )(func)


def properties_file(func):
    """Set a decorator to set an artifact properties file."""
    return click.option('--properties-file', 'properties_file', required=True, type=str,
                        help='Used to set the artifact properties file name to use to store details'
                        )(func)


def include_images(func):
    """Set a decorator set a true/false boolean for including images."""
    return click.option('--include-images', 'include_images', required=True, type=str,
                        help='Set a true or false boolean to state whether to include images'
                        )(func)


def force_rebuild(func):
    """Set a decorator used to set a boolean flag for a forced rebuild during a CSAR build."""
    return click.option('--force-rebuild', 'force_rebuild', required=True, type=str,
                        help='Used to set a boolean flag for a forced rebuild during a CSAR build'
                        )(func)


def create_tickets(func):
    """Set a decorator to create tickets for the outdated image ticket generator."""
    return click.option('--create-tickets', required=True, type=str,
                        help='Used to create tickets for the outdated image ticket generator'
                        )(func)


def skip_list(func):
    """Set a decorator to specify a list of objects to be skipped."""
    return click.option('--skip-list', required=False, type=str,
                        help='Used to specify a list of objects to be skipped'
                        )(func)


def microservice_skip_list(func):
    """Set a decorator to specify a list of microservice to be skipped."""
    return click.option('--microservice-skip-list', required=False, type=str,
                        help='Used to specify a list of microservices to be skipped'
                        )(func)


def project_file_name(func):
    """Set a decorator to specify a project file name i.e eric-eiae-helmfile."""
    return click.option('--project-file-name', required=False, type=str, default=None,
                        help='Used to specify a project to execute for'
                        )(func)


def yaml_file(func):
    """Set a decorator to specify a yaml file."""
    return click.option('--yaml-file', required=True, type=str,
                        help='Used to specify the full path to a yaml file'
                        )(func)


def json_file(func):
    """Set a decorator to specify a json file."""
    return click.option('--json-file', required=True, type=str,
                        help='Used to specify the full path to a json file'
                        )(func)


def clean_up(func):
    """Set a decorator to set a boolean flag to clean-up after the command."""
    return click.option('--clean-up', 'clean_up', default=False, type=str,
                        help='Used to set a boolean flag to clean-up after the command'
                        )(func)


def temp_secret(func):
    """Set a decorator to set a boolean flag to create a temporary secret."""
    return click.option('--temp-secret', "temp_secret", is_flag=True, flag_value=True, default=False,
                        help='Used to set a boolean flag to create a temporary secret'
                        )(func)


def recreate_secret(func):
    """Set a decorator to set a boolean flag to recreate a secret."""
    return click.option('--recreate-secret', "recreate_secret", is_flag=True, flag_value=True, default=False,
                        help='Used to set a boolean flag to recreate a secret if it already exists'
                        )(func)


def search_string(func):
    """Set a decorator to set a search string."""
    return click.option('--search-string', 'search_string', required=True, type=str,
                        help='Used to set a search string'
                        )(func)
