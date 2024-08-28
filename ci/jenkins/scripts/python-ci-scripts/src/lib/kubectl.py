"""Module for kubectl operations."""
import logging
import subprocess
import time
import os
import base64
import ast
import oyaml as yaml  # pip install oyaml

from . import utils
from . import errors
from . import site_values

LOG = logging.getLogger(__name__)
KUBECTL = "/usr/bin/kubectl"


def run_kubectl_command(config_file_path, *kubectl_args):
    """
    Execute a kubectl command.

    Input:
        config_file_path: File path to cluster kube config (to set context for kubectl command)
        *kubectl_args: List of kubectl command arguments

    Returns
    -------
        Command object

    """
    command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
    command_and_args_list.extend(kubectl_args)
    command = utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return command


def run_kubectl_command_with_retry(config_file_path, retry_count, retry_sleep_in_s, *kubectl_args):
    """
    Execute a kubectl command with a retry on error code returned.

    Input:
        config_file_path: File path to cluster kube config (to set context for kubectl command)
        retry_count: Number of times to retry a failed operation
        retry_sleep_in_s: Number of seconds to sleep in between retries
        *kubectl_args: List of kubectl command arguments

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
    new_args.extend(kubectl_args)
    while counter < retry_count:
        LOG.debug("Helm command: %s", ' '.join(new_args))
        command = run_kubectl_command(config_file_path, *new_args)
        if command.returncode == 0:
            break
        time.sleep(retry_sleep_in_s)
        counter += 1
    return command


def check_and_create_namespace(namespace, kubeconfig_file, ignore_exists="false"):
    """
    Create namespace unless it already exists, otherwise fail unless ignore_exists is true.

    Input:
        namespace: Namespace to check and create
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)
        ignore_exists: If set to true, ignore if the namespace already exists, and throw an
                       exception otherwise

    Output:
        Created namespace
    """
    LOG.info("Checking to see if namespace %s exists", namespace)
    kubectl_get_ns = run_kubectl_command(kubeconfig_file, 'get', 'namespace', namespace)
    kubectl_get_ns_output = utils.join_command_stdout_and_stderr(kubectl_get_ns)
    LOG.info("Output: %s", kubectl_get_ns_output)
    if "NotFound" in kubectl_get_ns_output:
        # Namespace is not found, create it now
        kubectl_create_ns = run_kubectl_command(kubeconfig_file, 'create', 'namespace', namespace)
        LOG.info(kubectl_create_ns.stdout.decode('utf-8'))
        if kubectl_create_ns.returncode != 0:
            LOG.error(kubectl_get_ns.stderr.decode('utf-8'))
            raise errors.NamespaceCreationError(f"Namespace {namespace} creation failed")
        LOG.info("Namespace %s created successfully", namespace)
    else:
        if kubectl_get_ns.returncode == 0:
            # Namespace exists, check ignore flag
            if ignore_exists == "true":
                LOG.info("Namespace %s already exists", namespace)
            else:
                LOG.error("Namespace %s already exists", namespace)
                LOG.info("Ensure the namespace has been cleaned down and deleted before continuing")
                raise errors.NamespaceExistsError(f"Namespace {namespace} exists")
        else:
            raise errors.KubectlCommandError(f"Unable to determine if namespace {namespace} exists")


def check_and_create_namespace_secret(namespace, secret_name, kubeconfig_file,
                                      dockerconfig_file,  ignore_exists="false"):
    """
    Create namespace secret unless it already exists, otherwise fail unless ignore_exists is true.

    Input:
        namespace: Namespace to create secret against
        secret_name: Name of the secret to be created.
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)
        dockerconfig_file: File path to the docker config file used as the secret credentials
        ignore_exists: If set to true, ignore if the secret already exists, and throw an
                       exception otherwise

    Output:
        Created namespace secret using docker config file.
    """
    cwd = os.getcwd()
    LOG.info("Checking to see if namespace \"%s\" exists", namespace)
    kubectl_get_ns = run_kubectl_command(kubeconfig_file, 'get', 'namespace', namespace)
    kubectl_get_ns_output = utils.join_command_stdout_and_stderr(kubectl_get_ns)
    LOG.info("Output: %s", kubectl_get_ns_output)
    if "NotFound" in kubectl_get_ns_output:
        raise errors.NamespaceExistsError(f"Specified Namespace {namespace} does not exists")
    LOG.info('Checking if secret %s exists', secret_name)
    kubectl_get_secret = run_kubectl_command(kubeconfig_file, 'get', 'secret',
                                             secret_name, '--namespace', namespace)
    if kubectl_get_secret.returncode == 0:
        if ignore_exists == "false":
            LOG.info("Secret %s already exists and --ignore_exists set to %s", secret_name, ignore_exists)
            raise errors.DeleteSecretError(f"Secret {secret_name} exists")
        LOG.info("Secret already exists, %s, deleting it", secret_name)
        # Namespace exists, proceed to delete
        kubectl_delete_namespace_secret = run_kubectl_command(kubeconfig_file, 'delete',
                                                              'secret', secret_name,
                                                              '--ignore-not-found',
                                                              '--namespace', namespace)
        LOG.info(kubectl_delete_namespace_secret.stdout.decode('utf-8'))
        if kubectl_delete_namespace_secret.returncode != 0:
            LOG.error(kubectl_delete_namespace_secret.stderr.decode('utf-8'))
            raise errors.DeleteSecretError(f"Secret {secret_name} deletion failed from {namespace}")
        LOG.info("Secret %s deleted successfully", secret_name)
    LOG.info('Creating secret %s', secret_name)
    # Secret is not found, create it now
    from_file = f"--from-file=.dockerconfigjson={cwd}/{dockerconfig_file}"
    kubectl_create_namespace_secret = run_kubectl_command(kubeconfig_file, 'create', 'secret', 'generic', secret_name,
                                                          from_file,
                                                          '--type=kubernetes.io/dockerconfigjson',
                                                          '--namespace', namespace)
    LOG.info(kubectl_create_namespace_secret.stdout.decode('utf-8'))
    if kubectl_create_namespace_secret.returncode != 0:
        LOG.error(kubectl_create_namespace_secret.stderr.decode('utf-8'))
        raise errors.CreateSecretError(f"Secret {secret_name} creation failed in Namespace {namespace}")
    LOG.info("Secret %s created successfully", secret_name)
    add_label_to_resource(kubeconfig_file, "secret", secret_name, namespace,
                          [f"app.kubernetes.io/instance=norelease-{namespace}"])


def delete_namespace(namespace, kubeconfig_file):
    """
    Delete namespace.

    Input:
        namespace: Namespace to delete
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Deleted namespace
    """
    LOG.info("Checking to see if namespace %s exists", namespace)
    kubectl_get_ns = run_kubectl_command(kubeconfig_file, 'get', 'namespace', namespace)
    kubectl_get_ns_output = utils.join_command_stdout_and_stderr(kubectl_get_ns)
    LOG.info("Output: %s", kubectl_get_ns_output)

    if kubectl_get_ns.returncode == 0:
        # Namespace exists, proceed to delete
        kubectl_delete_ns = run_kubectl_command(kubeconfig_file, 'delete', 'namespace', namespace)
        LOG.info(kubectl_delete_ns.stdout.decode('utf-8'))
        if kubectl_delete_ns.returncode != 0:
            LOG.error(kubectl_delete_ns.stderr.decode('utf-8'))
            raise errors.NamespaceDeletionError(f"Namespace {namespace} deletion failed")
        LOG.info("Namespace %s deleted successfully", namespace)
    else:
        LOG.info("Unable to determine if namespace %s exists", namespace)


def create_service_account(name, namespace, kubeconfig_file):
    """
    Create a service account.

    Input:
        name: Service account name
        namespace: Namespace for service account context
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Created service account
    """
    LOG.info("Checking to see if service account %s exists in namespace %s", name, namespace)
    kubectl_get_sa = run_kubectl_command(kubeconfig_file, 'get', 'serviceaccount', name,
                                         '--namespace', namespace)
    kubectl_get_sa_output = utils.join_command_stdout_and_stderr(kubectl_get_sa)
    LOG.info("Output: %s", kubectl_get_sa_output)
    if "NotFound" in kubectl_get_sa_output:
        LOG.info("Creating service account %s", name)
        service_account_data = {
            "kind": "ServiceAccount",
            "apiVersion": "v1",
            "metadata": {
                "name": name
            },
            "automountServiceAccountToken": True
        }
        with open("./ServiceAccount.yaml", 'w', encoding="utf-8") as sa_yaml_file:
            yaml.safe_dump(service_account_data, sa_yaml_file, default_flow_style=False)
        LOG.info("Content of ServiceAccount.yaml to apply:")
        with open('./ServiceAccount.yaml', 'r', encoding="utf-8") as yaml_file:
            LOG.info(yaml_file.read())
        LOG.info("Applying the service account resource...")
        kubectl_create_sa = run_kubectl_command(kubeconfig_file,
                                                'create', '-f',
                                                './ServiceAccount.yaml',
                                                '--namespace', namespace)
        if kubectl_create_sa.returncode != 0:
            kubectl_create_sa_output = utils.join_command_stdout_and_stderr(kubectl_create_sa)
            LOG.error("Service account %s did not create correctly: %s", name, kubectl_create_sa_output)
            raise errors.ServiceAccountCreationError(f"Failed to create service account {name}")
        LOG.info("Created service account %s successfully", name)
    else:
        if kubectl_get_sa.returncode == 0:
            # Service account exists, do nothing
            LOG.info("Service account %s already exists", name)
        else:
            raise errors.KubectlCommandError(f"Unable to determine if service account {name} exists")


def create_privileged_policy_cluster_role(name, release_name, namespace, kubeconfig_file):
    """
    Create a privileged policy cluster role.

    Input:
        name: Cluster role resource name
        release_name: Metadata release-name to use for cluster role
        namespace: Namespace where the privileged policy cluster role will be created
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Applied cluster role resource to target cluster
    """
    LOG.info("Checking to see if cluster role %s exists", name)
    kubectl_get_clusterrole = run_kubectl_command(kubeconfig_file, 'get', 'clusterrole', name)
    kubectl_get_clusterrole_output = utils.join_command_stdout_and_stderr(kubectl_get_clusterrole)
    LOG.info("Output: %s", kubectl_get_clusterrole_output)
    if "NotFound" in kubectl_get_clusterrole_output:
        LOG.info("Creating cluster role %s", name)
        cluster_role_data = {
            "kind": "ClusterRole",
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "metadata": {
                "name": name,
                "annotations": {
                    "meta.helm.sh/release-name": f"{release_name}-{namespace}",
                    "meta.helm.sh/release-namespace": namespace,
                    "helm.sh/resource-policy": "keep"
                },
                "labels": {
                    "app.kubernetes.io/managed-by": "Helm"
                }
            },
            "rules": [
                {
                    "apiGroups": ["security.openshift.io"],
                    "resources": ["securitycontextconstraints"],
                    "resourceNames": ["privileged"],
                    "verbs": ["use"],
                },
                {
                    "apiGroups": ["policy"],
                    "resources": ["podsecuritypolicies"],
                    "resourceNames": ["privileged"],
                    "verbs": ["use"],
                }
            ]
        }
        with open("./PrivilegedPolicyClusterRole.yaml", 'w', encoding="utf-8") as cluster_role_yaml_file:
            yaml.safe_dump(cluster_role_data, cluster_role_yaml_file, default_flow_style=False)
        LOG.info("Content of PrivilegedPolicyClusterRole.yaml to apply:")
        with open('./PrivilegedPolicyClusterRole.yaml', 'r', encoding="utf-8") as yaml_file:
            LOG.info(yaml_file.read())
        LOG.info("Applying the privileged policy for cluster role...")
        kubectl_create_cluster_role = run_kubectl_command(kubeconfig_file,
                                                          'apply', '-f',
                                                          './PrivilegedPolicyClusterRole.yaml')
        if kubectl_create_cluster_role.returncode != 0:
            LOG.error("Cluster role %s did not create correctly", name)
            raise errors.ClusterRoleCreationError(f"Failed to create cluster role {name}")
        LOG.info("Created cluster role %s successfully", name)
    else:
        if kubectl_get_clusterrole.returncode == 0:
            # Cluster role exists, do nothing
            LOG.info("Cluster role %s already exists", name)
        else:
            raise errors.KubectlCommandError(f"Unable to determine if cluster role {name} exists")


# pylint: disable=too-many-arguments
def create_generic_secret_from_literals(namespace, kubeconfig_file, secret_name, from_literals,
                                        temp_secret=False,
                                        recreate_secret=False):
    """
    Create a generic secret using a CSV of literals.

    Input:
        namespace: Namespace for the secret
        kubeconfig_file: Kube config file path to access target cluster
        secret_name: Name for the secret
        from_literals: Space-separated string of literals to use for the secret
        temp_secret: Used to add extra parameters to the secret create job is set to true, e.g.
        "cleanup-post-deployment=true"
        recreate_secret: Used to recreate the secret if it already exists

    Output:
        Writes secret to target namespace in cluster
    """
    if recreate_secret:
        kubectl_delete_secret = run_kubectl_command(kubeconfig_file, 'delete', 'secret', secret_name,
                                                    '--ignore-not-found',
                                                    '--namespace', namespace)
        LOG.info("Command: %s", kubectl_delete_secret.args)

    LOG.info('Checking if secret %s exists', secret_name)
    kubectl_get_secret = run_kubectl_command(kubeconfig_file, 'get', 'secret',
                                             secret_name, '--namespace', namespace)

    if kubectl_get_secret.returncode != 0 and "not found" in kubectl_get_secret.stderr.decode('utf-8'):
        LOG.info('%s has not been created', secret_name)
        LOG.info('Creating %s secret', secret_name)
        formatted_from_literals_list = [f"--from-literal={literal}" for literal in from_literals.split(' ')]
        kubectl_create_secret = run_kubectl_command(kubeconfig_file, 'create', 'secret', 'generic', secret_name,
                                                    *formatted_from_literals_list,
                                                    '--namespace', namespace)
        LOG.info("Command: %s", kubectl_create_secret.args)
        if kubectl_create_secret.returncode == 0:
            LOG.info('%s created successfully', secret_name)
            if temp_secret:
                add_label_to_resource(kubeconfig_file, "secret", secret_name, namespace,
                                      ["cleanup-post-deployment=true"])
            else:
                add_label_to_resource(kubeconfig_file, "secret", secret_name, namespace,
                                      [f"app.kubernetes.io/instance=norelease-{namespace}"])
        else:
            LOG.error(kubectl_create_secret.stderr.decode('utf-8'))
            raise errors.CreateSecretError(f"Issue arose when creating secret {secret_name}")
    else:
        if secret_name in kubectl_get_secret.stdout.decode('utf-8'):
            LOG.info('Secret %s already exists in namespace %s', secret_name, namespace)
        else:
            LOG.error(kubectl_get_secret.stderr.decode('utf-8'))
            raise errors.CreateSecretError(f"Issue arose when creating secret {secret_name}")


def create_cluster_rolebinding(kubeconfig_file, name, cluster_role, service_account):
    """
    Create a cluster rolebinding.

    Input:
        kubeconfig_file: Kube config file path to access target cluster
        name: Name for the rolebinding
        cluster_role: Cluster role to use for rolebinding
        service_account: Service account to associate with rolebinding

    Output:
        Writes rolebinding to target cluster
    """
    LOG.info('Checking if the %s cluster rolebinding is already created...', name)
    LOG.info('Executing......')
    kubectl_get_rb = run_kubectl_command(kubeconfig_file, 'get', 'clusterrolebinding', name)

    if kubectl_get_rb.returncode != 0 and "not found" in kubectl_get_rb.stderr.decode('utf-8'):
        LOG.info('%s has not been created', name)
        LOG.info('Creating cluster rolebinding %s', name)
        kubectl_create_rb = run_kubectl_command(kubeconfig_file, 'create', 'clusterrolebinding', name,
                                                f'--clusterrole={cluster_role}',
                                                f'--serviceaccount={service_account}')
        if kubectl_create_rb.returncode == 0:
            LOG.info('%s created successfully', name)
        else:
            LOG.error(kubectl_create_rb.stderr.decode('utf-8'))
            raise errors.CreateClusterRolebindingError(f"Issue arose when creating cluster rolebinding {name}")
    else:
        if name in kubectl_get_rb.stdout.decode('utf-8'):
            LOG.info('%s cluster rolebinding already created', name)
        else:
            LOG.error(kubectl_get_rb.stderr.decode('utf-8'))
            raise errors.CreateClusterRolebindingError(f"Issue arose when creating cluster rolebinding {name}")


def delete_crds(namespace, kubeconfig_file):
    """
    Delete CRDs.

    Input:
        namespace: Namespace where CRDs are present that needs to be deleted
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Deleted CRDs
    """
    LOG.info('Checking if any CRDs exist on the namespace %s...', namespace)
    LOG.info('Executing:')
    kubectl_get_crds = run_kubectl_command(kubeconfig_file, 'get', 'crd', '--namespace', namespace)

    if kubectl_get_crds.returncode == 0:
        LOG.info('Removing CRD components from target namespace: %s', namespace)
        LOG.info('Executing:')

        crd_components = get_components_or_cluster_roles(kubectl_get_crds, kubeconfig_file, namespace)

        LOG.info('crd_components: %s', crd_components)

        if len(crd_components) != 0:
            for crd_component in crd_components:
                LOG.info("Deleting crd_component %s from namespace %s", crd_component, namespace)
                delete_crd_component = run_kubectl_command(kubeconfig_file,
                                                           'delete', 'crd', '--namespace',
                                                           namespace, crd_component)
                if delete_crd_component.returncode == 0:
                    LOG.info('Removal of crd_component %s from target namespace %s finished successfully',
                             crd_component, namespace)
                else:
                    LOG.error(delete_crd_component.stderr.decode('utf-8'))
                    raise errors.CRDComponentDeletionError(f"Issue arose deleting crd from namespace: {namespace}")
            LOG.info('Deleting crd_components from target namespace %s finished successfully', namespace)
        else:
            LOG.info('No CRD components exists on namespace %s', namespace)
    else:
        if "not found" in kubectl_get_crds.stderr.decode('utf-8'):
            LOG.info('CRD components do not exist on the specified namespace %s', namespace)
        else:
            LOG.error(kubectl_get_crds.stderr.decode('utf-8'))
            raise errors.CRDComponentDeletionError(f"Issue arose deleting crd components from namespace: {namespace}")


def wait_for_persistent_volumes_deletion(namespace, kubeconfig_file, timeout, retries):
    """
    Wait for Persistent Volume Deletion to be completed.

    Input:
        namespace: Namespace where PVs are present that needs to be deleted
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)
        timeout: Time which will elapse between each retry
        retries: Maximum number of retries to perform

    Output:
        If successful, all PVs (Persistent Volumes) related to the namespace are deleted
    """
    LOG.info('Checking if any PVs exist on the namespace %s...', namespace)
    kubectl_get_pvs = run_kubectl_command(kubeconfig_file, 'get', 'pv')

    if kubectl_get_pvs.returncode == 0:
        LOG.info('Waiting for Persistent Volumes to be removed from target namespace: %s', namespace)

        # Check for the retry amount to see if the PVs for the namespace have been deleted and return the result
        wait_result = wait_for_persistent_volumes_check_if_exists(kubeconfig_file, timeout, retries, namespace)

        # If the wait result is 0 (PVs have been cleaned down), otherwise if value 1 (PVs have not been cleaned down)
        if wait_result == 0:
            LOG.info('Persistent Volumes Deleted successfully for namespace %s', namespace)
        else:
            LOG.error('Persistent Volumes were unable to be cleaned down for namespace %s', namespace)
            raise errors.PersistentVolumeWaitError(f"Issue arose cleaning down PVs from namespace: {namespace}")
    else:
        if "not found" in kubectl_get_pvs.stderr.decode('utf-8'):
            LOG.info('Persistent Volumes do not exist on the specified namespace %s', namespace)
        else:
            LOG.error(kubectl_get_pvs.stderr.decode('utf-8'))
            raise errors.PersistentVolumeWaitError(f"Issue arose waiting for PVs to delete from namespace: {namespace}")


def wait_for_persistent_volumes_check_if_exists(config_file_path, timeout_string, retries, namespace):
    """
    Check if Persistent Volumes Exist on namespace.

    Input:
        config_file_path: File path to cluster kube config (to set context for kubectl command)
        timeout_string: Time which will elapse between each retry
        retries: Maximum number of retries to perform
        namespace: Namespace where PVs are present that needs to be deleted

    Output:
        If PVs exist and cannot be cleaned down - Fail, if PVs have been cleaned down from the namespace - Pass
    """
    # Convert timeout from string to int
    timeout = int(timeout_string)

    # Set defaults
    if isinstance(retries, int) is False or retries < 1:
        retries = 1
    if isinstance(timeout, int) is False or timeout < 1:
        timeout = 1
    counter = 0
    return_code = 1

    # While loop to check if PVs have been successfully deleted for the retry period
    while counter < retries:
        # Setting default values for while loop and set up command
        line_array = []
        kubectl_get_pvs = run_kubectl_command(config_file_path, 'get', 'pv')
        output_from_command = kubectl_get_pvs.stdout.decode('utf-8').replace(" +", " ").split(" ")

        # From the output of the 'kubectl_get_pvs' command gather the namespaces where PVs exist and output to file
        with open('output.txt', 'w', encoding="utf-8") as output_file:
            for line in output_from_command:
                if "/" in line:
                    split_line = line.split("/")[0]
                    output_file.write(split_line + '\n')

        # Read all namespaces from the file and add namespace to an array, if they are not already in the set
        with open('output.txt', "r", encoding="utf-8") as read_file:
            for line in read_file:
                namespace_gathered = line.split("\n")[0]
                if namespace_gathered not in line_array:
                    line_array.append(namespace_gathered)

        # Showcase the namespaces that are gathered from the array
        LOG.info("Persistent Volumes have been found on the following namespaces: ")
        LOG.info(line_array)

        # If the namespace is not found in the array, PVs are successfully cleaned down and break the while loop
        if namespace not in line_array:
            return_code = 0
            break

        # If the namespace is found in the array, PVs still exist and enter the next iteration of the while loop
        time.sleep(timeout)
        counter += 1
    # Return the code stating whether the clean down of PVs were successful, if retry count is exceeded, return false
    return return_code


def delete_cluster_roles(namespace, kubeconfig_file):
    """
    Delete Cluster roles.

    Input:
        namespace: Used to find the cluster roles with release namespace with the specified namespace
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Deleted cluster roles
    """
    LOG.info('Checking if any cluster roles exist....')
    LOG.info('Executing:')
    kubectl_get_cluster_roles = run_kubectl_command(kubeconfig_file, 'get', 'clusterrole')

    if kubectl_get_cluster_roles.returncode == 0:
        cluster_role_components = get_components_or_cluster_roles(kubectl_get_cluster_roles, kubeconfig_file, namespace)

        LOG.info('cluster_role_components: %s', cluster_role_components)

        if len(cluster_role_components) != 0:
            for cluster_role_component in cluster_role_components:
                LOG.info("Deleting cluster role_component %s", cluster_role_component)
                delete_cluster_role_component = run_kubectl_command(kubeconfig_file, 'delete',
                                                                    'clusterrole', cluster_role_component)
                if delete_cluster_role_component.returncode == 0:
                    LOG.info('Removal of cluster role_component %s has finished successfully',
                             cluster_role_component)
                else:
                    LOG.error(delete_cluster_role_component.stderr.decode('utf-8'))
                    raise errors.ClusterroleDeletionError(f"removing cluster role with annotation for "
                                                          f"namespace {namespace}")
            LOG.info('Deleting cluster role_components has finished successfully')
        else:
            LOG.info('No cluster roles exists')
    else:
        if "not found" in kubectl_get_cluster_roles.stderr.decode('utf-8'):
            LOG.info('Cluster roles do not exist')
        else:
            LOG.error(kubectl_get_cluster_roles.stderr.decode('utf-8'))
            raise errors.ClusterroleDeletionError(f"removing cluster role with annotation for "
                                                  f"namespace {namespace}")


def delete_cluster_role_bindings(namespace, kubeconfig_file):
    """
    Delete Cluster role bindings.

    Input:
        namespace: Used to find the cluster roles with release namespace with the specified namespace
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Deleted cluster role bindings
    """
    LOG.info('Checking if any cluster role bindings exist...')
    LOG.info('Executing:')
    kubectl_get_cluster_role_bindings = run_kubectl_command(kubeconfig_file, 'get', 'clusterrolebinding')

    if kubectl_get_cluster_role_bindings.returncode == 0:
        cluster_role_binding_components = get_cluster_role_bindings(kubectl_get_cluster_role_bindings,
                                                                    kubeconfig_file, namespace)

        LOG.info('cluster_role_binding_components: %s', cluster_role_binding_components)

        if len(cluster_role_binding_components) != 0:
            for cluster_role_binding_component in cluster_role_binding_components:
                LOG.info("Deleting cluster role binding_component %s:",
                         cluster_role_binding_component)
                delete_cluster_role_binding_component = run_kubectl_command(kubeconfig_file,
                                                                            'delete', 'clusterrolebinding',
                                                                            cluster_role_binding_component)
                if delete_cluster_role_binding_component.returncode == 0:
                    LOG.info('Removal of cluster_role binding_component %s finished successfully',
                             cluster_role_binding_component)
                else:
                    LOG.error(delete_cluster_role_binding_component.stderr.decode('utf-8'))
                    raise errors.ClusterrolebindingDeletionError(f"removing cluster role binding with annotation for "
                                                                 f"namespace {namespace}")
            LOG.info('Deleting cluster_role_binding_components has finished successfully')
        else:
            LOG.info('No cluster role bindings exist')
    else:
        if "not found" in kubectl_get_cluster_role_bindings.stderr.decode('utf-8'):
            LOG.info('Cluster role bindings do not exist')
        else:
            LOG.error(kubectl_get_cluster_role_bindings.stderr.decode('utf-8'))
            raise errors.ClusterrolebindingDeletionError(f"removing cluster role binding with annotation for"
                                                         f" namespace {namespace}")


def get_components_or_cluster_roles(kubectl_get_command, kubeconfig_file, namespace):
    """
    Find crd components/cluster roles that need to be deleted.

    Input:
        namespace: Used to find the crd components/cluster roles with the release namespace annotation with namespace
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Return a list of crd components/cluster roles that need to be deleted
    """
    components = kubectl_get_command.stdout.decode('utf-8').split("\n")
    del components[-1]
    del components[0]
    annotation_name = "meta.helm.sh/release-namespace: " + str(namespace)
    LOG.info('The Annotation name used here is: %s', annotation_name)
    LOG.info('Cluster Roles found: %s', components)

    found_components = []
    for component in components:
        found_component = component.split(' ')[0]

        if kubectl_get_command.args[4] == 'crd':
            kubectl_get_metadata = run_kubectl_command(kubeconfig_file, 'get', 'crd', '--namespace',
                                                       namespace, found_component, '-oyaml')
        elif kubectl_get_command.args[4] == 'clusterrole':
            kubectl_get_metadata = run_kubectl_command(kubeconfig_file, 'get', 'clusterrole',
                                                       found_component, '-oyaml')
        else:
            raise errors.AnnotationSearchError(f"Command not recognised for this function on namespace {namespace}")

        if kubectl_get_metadata.returncode == 0:
            metadata = kubectl_get_metadata.stdout.decode('utf-8')
            for annotation in metadata.split("\n"):
                if str(annotation_name) in annotation:
                    found_components.append(found_component)
                    break

    LOG.info('Found components with specified annotation: %s', found_components)
    return found_components


def get_cluster_role_bindings(kubectl_get_cluster_role_bindings, kubeconfig_file, namespace):
    """
    Find cluster role bindings that needs to be deleted.

    Input:
        namespace: Used to find the cluster role bindings with release namespace with the specified namespace
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)

    Output:
        Return a list of cluster role bindings that needs to be deleted
    """
    cluster_role_bindings = kubectl_get_cluster_role_bindings.stdout.decode('utf-8').split("\n")
    del cluster_role_bindings[-1]
    del cluster_role_bindings[0]
    namespace_name = "namespace: " + str(namespace)
    LOG.info('The namespace_name used here is: %s', namespace_name)
    LOG.info('Cluster Role Bindings found: %s', cluster_role_bindings)

    cluster_role_binding_components = []
    for cluster_role_binding in cluster_role_bindings:
        found_cluster_role_binding = cluster_role_binding.split(' ')[0]
        kubectl_get_cluster_role_binding_annotations = run_kubectl_command(kubeconfig_file,
                                                                           'get', 'clusterrolebinding',
                                                                           found_cluster_role_binding, '-oyaml')
        if kubectl_get_cluster_role_binding_annotations.returncode == 0:
            annotations_information = kubectl_get_cluster_role_binding_annotations.stdout.decode('utf-8')
            for annotation in annotations_information.split("\n"):
                if namespace_name in annotation:
                    cluster_role_binding_components.append(found_cluster_role_binding)
                    break

    LOG.info('Cluster Role Bindings found: %s', cluster_role_binding_components)
    return cluster_role_binding_components


def wait_for_condition(condition_value, resource_path, timeout, kubeconfig_file, namespace):
    """
    Wait for a resource to reach condition value with a given timeout.

    Input:
        condition_value: what condition the resource should reach (ready, complete, available etc.)
        resource_path: what resource is targeted (jobs/jobname, pods/podname etc.)
        timeout: how long to wait for the condition default=30s
        kubeconfig_file: File path to cluster kube config (to set context for kubectl command)
        namespace: File path to cluster kube config (to set context for kubectl command)

    Output:
        Return success if wait condition successful, raises exception otherwise
    """
    LOG.info("Waiting for %s to be in condition: %s", resource_path, condition_value)
    resource_query = run_kubectl_command(kubeconfig_file, "--namespace", namespace, "get", resource_path)
    if "NotFound" in resource_query.stderr.decode('utf-8'):
        LOG.info("The indicated resource path %s, does not exist, No need to wait.", resource_path)
    else:
        if resource_query.returncode == 0:
            kubectl_wait = run_kubectl_command(kubeconfig_file, "--namespace", namespace, "wait",
                                               f"--for=condition={condition_value}",
                                               "--timeout", timeout, resource_path)
            if kubectl_wait.returncode != 0:
                LOG.error("Wait condition %s for resource %s unsuccessful after %s",
                          condition_value,
                          resource_path,
                          timeout)
                raise errors.KubectlCommandError(kubectl_wait.stderr.decode("utf-8"))
            LOG.info(kubectl_wait.stdout.decode("utf-8"))
        else:
            LOG.error("Unable to determine if resource %s exists", resource_path)
            raise errors.KubectlCommandError(resource_query.stderr.decode('utf-8'))


def create_testware_hostnames_configmap(namespace, kubeconfig_file, site_values_path):
    """
    Create the ConfigMap object for the testware hostnames.

    Input:
        namespace: The namespace to create the ConfigMap
        kubeconfig_file: The path to the kube_config.yaml file to connect to the cluster
        site_values_path: The site values file containing the hostnames

    Output:
        A ConfigMap object is created on the cluster
    """
    with open(site_values_path, "r", encoding="utf-8") as site_values_file:
        yaml_dict = yaml.safe_load(site_values_file)
        testware_hostnames_data = {"domain": yaml_dict["global"]["hosts"]["iam"].split(".", 1)[-1]}
        for key in yaml_dict["global"]["hosts"]:
            testware_hostnames_data[key] = yaml_dict["global"]["hosts"][key]
        ingress = site_values.find_shared_nested_value(yaml_dict, "service-mesh-ingress-gateway", "loadBalancerIP")
        if ingress:
            testware_hostnames_data["ingress"] = ingress
        fh_snmp_alarm = site_values.find_shared_nested_value(yaml_dict, "eric-fh-snmp-alarm-provider", "loadBalancerIP")
        if fh_snmp_alarm:
            testware_hostnames_data["fh-snmp-alarm"] = fh_snmp_alarm
    testware_hostnames_configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": "testware-hostnames",
            "labels": {
                "app.kubernetes.io/instance": f"norelease-{namespace}"
            }
        },
        "data": testware_hostnames_data
    }
    with open("testware-hostnames.yaml", "w", encoding="utf-8") as write_yaml:
        yaml.safe_dump(testware_hostnames_configmap, write_yaml)
    create_resource_with_kubectl_apply(namespace, kubeconfig_file, "testware-hostnames",
                                       "testware-hostnames.yaml", "ConfigMap")


# pylint: disable=too-many-arguments
def create_global_testware_config_configmap(namespace, kubeconfig_file, docker_auth_config,
                                            flow_area, cluster_name, site_values_path):
    """
    Create the ConfigMap object for the global testware configuration.

    Input:
        namespace: The namespace to create the ConfigMap
        kubeconfig_file: The path to the kube_config.yaml file to connect to the cluster
        docker_auth_config: The name of the docker config file
        flow_area: The name of the flow area for the deployment (e.g., release)
        cluster_name: The name of the cluster for the deployment
        site_values_path: The site values file used for the deployment

    Output:
        A ConfigMap object is created on the cluster
    """
    flow_area = "Not specified" if flow_area == "default" else flow_area
    with open(site_values_path, "r", encoding="utf-8") as site_values_file:
        yaml_dict = yaml.safe_load(site_values_file)
        tls_enabled = site_values.find_shared_nested_value(yaml_dict["global"], "tls", "enabled") is True
        sef_enabled = site_values.find_shared_nested_value(yaml_dict, "tags", "sef") is True
    testware_global_config_configmap = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": "testware-global-config",
            "labels": {
                "app.kubernetes.io/instance": f"norelease-{namespace}"
            }
        },
        "data": {
            "docker-pull-secret": docker_auth_config,
            "cluster-name": cluster_name,
            "environment-label": flow_area,
            "tls-enabled": str(tls_enabled),
            "sef-enabled": str(sef_enabled)
        }
    }
    with open("testware-global-config.yaml", "w", encoding="utf-8") as write_yaml:
        yaml.safe_dump(testware_global_config_configmap, write_yaml)
    create_resource_with_kubectl_apply(namespace, kubeconfig_file, "testware-global-config",
                                       "testware-global-config.yaml", "ConfigMap")


def create_ddp_config_secret(namespace, kubeconfig_file, site_values_path):
    """
    Create the Secret object for the DDP configuration.

    Input:
        namespace: The namespace to create the ConfigMap
        kubeconfig_file: The path to the kube_config.yaml file to connect to the cluster
        site_values_path: The site values file containing the hostnames

    Output:
        A Secret object is created on the cluster
    """
    with open(site_values_path, "r", encoding="utf-8") as site_values_file:
        yaml_dict = yaml.safe_load(site_values_file)
    try:
        ddc_enabled = base64.b64encode(bytes(
            str(yaml_dict["eric-oss-common-base"]["eric-oss-ddc"]["autoUpload"]["enabled"]),
            encoding="utf-8"))
        ddp_id = base64.b64encode(bytes(
            str(yaml_dict["eric-oss-common-base"]["eric-oss-ddc"]["autoUpload"]["ddpid"]),
            encoding="utf-8"))
        ddp_account = base64.b64encode(bytes(
            str(yaml_dict["eric-oss-common-base"]["eric-oss-ddc"]["autoUpload"]["account"]),
            encoding="utf-8"))
        ddp_password = base64.b64encode(bytes(
            str(yaml_dict["eric-oss-common-base"]["eric-oss-ddc"]["autoUpload"]["password"]),
            encoding="utf-8"))
    except (KeyError, IndexError):
        LOG.info("All of the DDP values needed to create the ddp-config-secret are not available"
                 " - The secret will not be created")
        return
    ddp_secret_config = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": "ddp-config-secret",
            "labels": {
                "app.kubernetes.io/instance": f"norelease-{namespace}"
            }
        },
        "type": "Opaque",
        "data": {
            "auto-upload-enabled": ddc_enabled,
            "ddp-id": ddp_id,
            "ddp-account": ddp_account,
            "ddp-password": ddp_password
        }
    }
    with open("ddp-config-secret.yaml", "w", encoding="utf-8") as write_yaml:
        yaml.safe_dump(ddp_secret_config, write_yaml)
    create_resource_with_kubectl_apply(namespace, kubeconfig_file, "ddp-config-secret",
                                       "ddp-config-secret.yaml", "Secret")


def create_resource_with_kubectl_apply(namespace, kubeconfig_file, name, file, resource_name):
    """
    Create a Kubernetes resource with kubectl apply - this will update an existing resource or create a new one.

    Input:
        namespace: The namespace for the cluster role binding
        kubeconfig_file: The kubeconfig file to connect to the cluster
        name: The name given to the created resource
        file: The path to the YAML file containing the resource
        resource_name: The name of the resource (e.g., Secret)

    Output:
        The resource set up within the cluster.
    """
    LOG.info("Creating the %s %s using %s...", resource_name, name, file)
    creation_result = run_kubectl_command(kubeconfig_file, "apply", "-f", file, "--namespace", namespace)
    if creation_result.returncode == 0:
        LOG.info("The %s %s was created/updated successfully", resource_name, name)
    else:
        LOG.info("There was an error in creating/updating %s %s", resource_name, name)
        creation_result_output = utils.join_command_stdout_and_stderr(creation_result)
        LOG.info(creation_result_output)
        raise Exception


def create_resource_with_yaml_file(namespace, kubeconfig_file, name, file, resource_name):
    """
    Create a Kubernetes resource with a provided YAML file.

    Input:
        namespace: The namespace for the cluster role binding.
        kubeconfig_file: The kubeconfig file to connect to the cluster.
        name: Name of the resource that you want to create.
        file: The path to the YAML file containing the resource.
        resource_name: The resource type (e.g., clusterrolebinding, secret, pod etc.).

    Output:
        The resource set up within the cluster.
    """
    LOG.info("Checking to see if the %s of name %s exists", resource_name, name)
    LOG.info("Executing: kubectl get %s %s --namespace %s --kubeconfig %s",
             resource_name, name, namespace, kubeconfig_file)
    resource_exists = run_kubectl_command(kubeconfig_file, "get", resource_name,
                                          name, "--namespace", namespace)
    if "not found" in resource_exists.stderr.decode("utf-8"):
        LOG.info("Creating %s", resource_name)
        LOG.info("Content of %s", file)
        with open(file, "r", encoding="utf-8") as yaml_file:
            for line in yaml_file:
                LOG.info(line)
        LOG.info("Executing: kubectl create -f %s --kubeconfig %s", file, kubeconfig_file)
        run_kubectl_command(kubeconfig_file, "create", "-f", file)
        resource_exists = run_kubectl_command(kubeconfig_file, "get", resource_name,
                                              name, "--namespace", namespace)
        if resource_exists.returncode == 0:
            LOG.info("The creation of %s %s completed successfully", resource_name, name)
        else:
            LOG.info("Exiting")
            LOG.info(resource_exists.stderr.decode("utf-8"))
            raise Exception(f"{resource_name} did not create correctly")
    else:
        if name in resource_exists.stdout.decode("utf-8"):
            LOG.info("The %s %s already exists", resource_name, name)
        else:
            LOG.info(resource_exists.stderr.decode("utf-8"))
            raise Exception(f"An error occurred in determining whether {name} exists")


def get_value_from_configmap_or_secret(name, resource_name, namespace, kubeconfig_file, desired_value):
    """
    Get a value from a configmap or secret.

    Input:
        name: The name of the configmap or secret.
        resource_name: The name of the resource (e.g., configmap or secret).
        namespace: The namespace containing the secrets.
        kubeconfig_file: The kubeconfig file to connect to the cluster.
        desired_value: The key for which to retreive the value.

    Output:
        Return the value from the configmap or secret.
    """
    command_output = run_kubectl_command(kubeconfig_file, "get", resource_name, name, "--namespace",
                                         namespace, "--output", "json")
    if "not found" in command_output.stderr.decode("utf-8"):
        LOG.info("The %s %s was not found in the cluster.", resource_name, name)
        value = "not_found"
    else:
        LOG.info("%s %s found on the cluster. Checking for the key %s", resource_name, name, desired_value)
        resource_dict = ast.literal_eval(command_output.stdout.decode("utf-8"))
        if desired_value not in resource_dict["data"]:
            LOG.info("The key %s was not in the %s %s", desired_value, resource_name, name)
            value = "not_found"
        else:
            LOG.info("Found key %s in %s %s", desired_value, resource_name, name)
            value = resource_dict["data"][desired_value]
            if resource_name == "secret":
                value = base64.b64decode(value).decode()
    return value


def get_testware_server_event_variables(namespace, kubeconfig_file):
    """
    Get the testware server event variables.

    Input:
        namespace: The namespace containing the secrets.
        kubeconfig_file: The kubeconfig file to connect to the cluster.

    Output:
        The secret information is written to a local properties file.
    """
    testware_api_url = get_value_from_configmap_or_secret("testware-resources-secret", "secret", namespace,
                                                          kubeconfig_file, "api_url")
    testware_gui_url = get_value_from_configmap_or_secret("testware-resources-secret", "secret", namespace,
                                                          kubeconfig_file, "gui_url")
    helmfile_version_info = get_value_from_configmap_or_secret("eric-installed-applications", "configmap", namespace,
                                                               kubeconfig_file, "Installed")
    if helmfile_version_info != "not_found":
        helmfile_version_info = yaml.safe_load(helmfile_version_info)
        helmfile_version_info = helmfile_version_info["helmfile"]["release"]
    with open("server-event-info.properties", "a+", encoding="utf-8") as server_event_properties_file:
        server_event_properties_file.write(f"api_url={testware_api_url}\n")
        server_event_properties_file.write(f"gui_url={testware_gui_url}\n")
        server_event_properties_file.write(f"from_version={helmfile_version_info}\n")


# pylint: disable=too-many-lines
def remove_kafka_topic_resources(namespace, kubeconfig_file):
    """
    Remove kafka topic resources.

    Input:
        namespace: The namespace to remove the kafka topic resources from
        kubeconfig_file: The path to the kube_config.yaml file to connect to the cluster

    Output:
        The kafka topic resources being removed.
    """
    command_output = run_kubectl_command(kubeconfig_file, "get", "kafkatopic", "--namespace", namespace, "-o", "name")
    kafkatopic_resources = command_output.stdout.decode("utf-8").strip().split("\n")
    list_of_kt_resources_returned = all("kafkatopic.kafka.strimzi.io" in item for item in kafkatopic_resources)
    if list_of_kt_resources_returned:
        for kafkatopic in kafkatopic_resources:
            command_output = run_kubectl_command(kubeconfig_file,
                                                 "--namespace", namespace,
                                                 "patch", kafkatopic,
                                                 "--type=json", "-p=[{'op': 'remove', 'path': '/metadata/finalizers'}]")
            if command_output.returncode == 0:
                LOG.info("Successfully patched kafkatopic %s: %s", kafkatopic,
                         command_output.stdout.decode("utf-8"))
            else:
                LOG.info("There was an error with patching the kafkatopic %s: %s", kafkatopic,
                         command_output.stderr.decode('utf-8'))
    else:
        LOG.info("No kafkatopic resources found in the namespace:")
        kubectl_get_kt_output = utils.join_command_stdout_and_stderr(command_output)
        LOG.info(kubectl_get_kt_output)


def add_label_to_resource(kubeconfig_file, resource_type, resource_name, namespace, labels):
    """
    Add a label to a resource.

    Input:
        kubeconfig_file: The path to the kube_config.yaml file to connect to the cluster
        resource_type: The type of the resource, e.g., secret
        resource_name: The name of the resource, e.g., dg-base-configmap
        namespace: The namespace where the resource exists
        labels: A list of labels to be added to the resouce, e.g., ["app-name=app", "app-type=type"]

    Output:
        The resource being labeled.
    """
    for label in labels:
        LOG.info("Labelling %s %s with %s in namespace %s", resource_type, resource_name, label, namespace)
        kubectl_label_result = run_kubectl_command(kubeconfig_file, 'label', resource_type, resource_name,
                                                   "--namespace", namespace, label)
        LOG.info(kubectl_label_result.stdout.decode('utf-8'))
        if kubectl_label_result.returncode != 0:
            LOG.error(kubectl_label_result.stderr.decode('utf-8'))
            raise errors.KubectlCommandError(f"Failed to label {resource_type} {resource_name} "
                                             f"in namespace {namespace}")
