"""Module for executing kubectl related scripts in CI image."""
# pylint: disable=too-many-lines
import logging
import time
import sys
from datetime import timedelta
import traceback
import click

from lib import kubectl
from lib import registry
from lib import utils

from lib.decorators import log_verbosity_option
from lib.decorators import namespace
from lib.decorators import kubeconfig_file
from lib.decorators import ignore_exists
from lib.decorators import name
from lib.decorators import release_name
from lib.decorators import secret_name
from lib.decorators import resource_name
from lib.decorators import resource_type
from lib.decorators import dockerconfig_file
from lib.decorators import file
from lib.decorators import cluster_role
from lib.decorators import service_account
from lib.decorators import from_literals
from lib.decorators import timeout
from lib.decorators import state_values_file
from lib.decorators import docker_auth_config
from lib.decorators import flow_area
from lib.decorators import cluster_name
from lib.decorators import retries
from lib.decorators import user_id
from lib.decorators import user_password
from lib.decorators import temp_secret
from lib.decorators import recreate_secret
from lib.decorators import search_string

LOG = logging.getLogger(__name__)


@click.group(context_settings=dict(terminal_width=220))
def cli():
    """Define the CLI for Kubernetes Commands."""


@cli.command()
@namespace
@kubeconfig_file
@ignore_exists
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def create_namespace(namespace, kubeconfig_file, ignore_exists, verbosity):
    """Create a namespace with a user-specified name if the namespace doesn't already exist."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_namespace')
    LOG.info('Create Namespace: Namespace to create is %s', namespace)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.check_and_create_namespace(namespace, kubeconfig_file, ignore_exists)
    except Exception as exception:
        LOG.error('Create Namespace: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Namespace completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@secret_name
@kubeconfig_file
@dockerconfig_file
@ignore_exists
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_namespace_secret(namespace, secret_name, kubeconfig_file, dockerconfig_file, ignore_exists, verbosity):
    """Create a secret on a specified namespace within a specified cluster using information provided by the user."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_namespace_secret')
    LOG.info('Create Namespace Secret: %s', secret_name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.check_and_create_namespace_secret(namespace, secret_name, kubeconfig_file,
                                                  dockerconfig_file, ignore_exists)
    except Exception as exception:
        LOG.error('Create Namespace Secret: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Namespace Secret completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def delete_namespace(namespace, kubeconfig_file, verbosity):
    """Delete a specified namespace on a cluster, will fail if the namespace does not exist."""
    log_file_path = utils.initialize_logging(verbosity=verbosity, working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_namespace')
    LOG.info('Delete Namespace: Namespace to delete is %s', namespace)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_namespace(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Delete Namespace: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Delete Namespace completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@name
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def create_service_account(name, namespace, kubeconfig_file, verbosity):
    """Create a service account resource within a specified namespace."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_service_account')
    LOG.info('Create Service Account: Creating resource with name %s', name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_service_account(name, namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Create Service Account: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Service Account completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@name
@release_name
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def create_privileged_policy_cluster_role(name, release_name, namespace, kubeconfig_file, verbosity):
    """Create a cluster role resource with a privileged policy."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_privileged_policy_cluster_role')
    LOG.info('Create Privileged Policy Cluster Role: Resource name to create is %s', name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_privileged_policy_cluster_role(name, release_name, namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Create Privileged Policy Cluster Role: failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Privileged Policy Cluster Role completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@secret_name
@from_literals
@temp_secret
@recreate_secret
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_generic_secret_from_literals(namespace, kubeconfig_file, secret_name, from_literals,
                                        temp_secret, recreate_secret, verbosity):
    """Set generic secret if none exists."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_generic_secret_from_literals')
    LOG.info("Creating the Generic Secret...")
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_generic_secret_from_literals(namespace, kubeconfig_file,
                                                    secret_name, from_literals,
                                                    temp_secret, recreate_secret)
    except Exception as exception:
        LOG.error('Create Generic Secret failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Generic Secret completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@name
@file
@resource_name
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_resource_with_yaml_file(namespace, kubeconfig_file, name, file, resource_name, verbosity):
    """Create a resource with a YAML file."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_resource_with_file')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_resource_with_yaml_file(namespace, kubeconfig_file, name, file, resource_name)
    except Exception as exception:
        LOG.error('Creating a resource with a YAML file failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Creating a resource with a YAML file completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@kubeconfig_file
@cluster_role
@service_account
@name
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_cluster_rolebinding(kubeconfig_file, name,
                               cluster_role, service_account, verbosity):
    """Create a cluster rolebinding."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='cleate_cluster_rolebinding')
    LOG.info("Creating Cluster Rolebinding %s", name)
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_cluster_rolebinding(kubeconfig_file,
                                           name, cluster_role,
                                           service_account)
    except Exception as exception:
        LOG.error('Create Cluster Rolebinding failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Cluster Rolebinding completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def remove_cluster_roles(namespace, kubeconfig_file, verbosity):
    """Delete Cluster roles."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_cluster_roles')
    LOG.info('Deleting cluster roles to completely clean the cluster')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_cluster_roles(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Deleting clusterroles failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Cluster roles deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def remove_cluster_role_bindings(namespace, kubeconfig_file, verbosity):
    """Delete Cluster rolebindings."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='delete_cluster_rolebindings')
    LOG.info('Deleting cluster rolebindings to completely clean the cluster')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.delete_cluster_role_bindings(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Deleting cluster rolebindings failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Cluster rolebindings deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@name
@timeout
@kubeconfig_file
@namespace
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def uds_backend_job_wait(name, timeout, kubeconfig_file, namespace, verbosity):
    """Wait for uds job to complete."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='uds_backend_job_wait')
    LOG.info('Waiting for UDS Backend Job to Complete ...')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.wait_for_condition("complete", f"jobs/{name}", timeout, kubeconfig_file, namespace)
    except Exception as exeception:
        LOG.error("Wait for uds backend job failure")
        LOG.info(traceback.format_exc())
        LOG.error(exeception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@state_values_file
@docker_auth_config
@flow_area
@cluster_name
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_common_resources(namespace, kubeconfig_file, state_values_file, docker_auth_config, flow_area,
                            cluster_name, verbosity):
    """Create common resources on a specified namespace used during deployment."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='create_common_resources')
    LOG.info('Creating the common secrets and configmap objects')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.create_testware_hostnames_configmap(namespace, kubeconfig_file, state_values_file)
        kubectl.create_global_testware_config_configmap(namespace, kubeconfig_file, docker_auth_config,
                                                        flow_area, cluster_name, state_values_file)
        kubectl.create_ddp_config_secret(namespace, kubeconfig_file, state_values_file)
    except Exception as exception:
        LOG.error('The creation of the common secrets and configmaps failed with the following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('The creation of the common secrets and configmaps completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@timeout
@retries
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except
def wait_for_persistent_volumes_deletion(namespace, kubeconfig_file, timeout, retries, verbosity):
    """Wait for Persistent Volumes Deletion."""
    log_file_path = utils.initialize_logging(verbosity=verbosity,
                                             working_directory='/ci-scripts/',
                                             logs_sub_directory='output-files/ci-script-executor-logs',
                                             filename_postfix='wait_for_persistent_volumes')
    LOG.info('Waiting for Persistent Volumes Deletion to complete')
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.wait_for_persistent_volumes_deletion(namespace, kubeconfig_file, timeout, retries)
    except Exception as exception:
        LOG.error('Waiting for Persistent Volumes Deletion failed with following errors')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Persistent Volumes Deleted successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@name
@user_id
@user_password
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def check_and_create_internal_registry_secret(namespace, kubeconfig_file, name,
                                              user_id, user_password, verbosity):
    """Set registry secret if none exists."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='check_and_create_internal_registry_secret')
    LOG.info("Creating the internal Registry for EVNFM Pre Deployment step")
    start_time = time.time()
    exit_code = 0
    try:
        registry.create_internal_registry_secret(namespace, kubeconfig_file, name,
                                                 user_id, user_password)
    except Exception as exception:
        LOG.error('Create Internal Registry failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Create Internal Registry completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def create_server_event_variables(namespace, kubeconfig_file, verbosity):
    """Create the server event variables."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='create_server_event_variables')
    LOG.info("Creating server event variables")
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.get_testware_server_event_variables(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Creating server event variables failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Creating server event variables completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@namespace
@kubeconfig_file
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def remove_kafka_topic_resources(namespace, kubeconfig_file, verbosity):
    """Remove kafkatopic resources."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='remove_kafka_topic_resources')
    LOG.info("Removing kafka topic resources")
    start_time = time.time()
    exit_code = 0
    try:
        kubectl.remove_kafka_topic_resources(namespace, kubeconfig_file)
    except Exception as exception:
        LOG.error('Removing kafka topic resources failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Removing kafka topic resources completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)


@cli.command()
@resource_name
@resource_type
@namespace
@kubeconfig_file
@search_string
@log_verbosity_option
# pylint: disable=redefined-outer-name, broad-except, too-many-arguments
def get_value_from_configmap_or_secret(resource_name, resource_type,
                                       namespace, kubeconfig_file,
                                       search_string,
                                       verbosity):
    """Search for string within kubectl resource, secret and configmap."""
    log_file_path = utils.initialize_logging(
        verbosity=verbosity,
        working_directory='/ci-scripts/',
        logs_sub_directory='output-files/ci-script-executor-logs',
        filename_postfix='get_value_from_configmap_or_secret')
    LOG.info("Search for string within kubectl resource")
    start_time = time.time()
    exit_code = 0
    try:
        value = kubectl.get_value_from_configmap_or_secret(
            resource_name,
            resource_type,
            namespace,
            kubeconfig_file,
            search_string
        )
        with open("artifact.properties", "w", encoding="utf-8") as properties:
            properties.write(search_string + '=' + value)
    except Exception as exception:
        LOG.error('Search for string within kubectl resource failed with the following error')
        LOG.debug(traceback.format_exc())
        LOG.error(exception)
        LOG.info('Please refer to the following log file for further output: %s', log_file_path)
        exit_code = 1
    else:
        LOG.info('Completed successfully')
    finally:
        end_time = time.time()
        time_taken = end_time - start_time
        LOG.info('Time Taken: %s', timedelta(seconds=round(time_taken)))
        sys.exit(exit_code)
