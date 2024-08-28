"""Module to manage internal registry."""
import logging
import subprocess
import sys

from . import kubectl
from . import errors

LOG = logging.getLogger(__name__)


def create_htpasswd(username, user_password):
    """
    Create an htpasswd file.

    Input:
        username: Username string for htpasswd
        user_password: User password for htpasswd

    Output:
        Writes htpasswd file to local directory
    """
    LOG.info('Creating a htpasswd file')
    try:
        htpasswd_cmd_str = 'htpasswd -cBb htpasswd %s %s', username, user_password
        subprocess.check_output(htpasswd_cmd_str, shell=True, text=True)
    except Exception:
        LOG.error("Issue executing the htpasswd command %s", sys.exc_info())
        raise


def create_registry_secret_from_htpasswd(namespace, kubeconfig_file, secret_name, htpasswd_file):
    """
    Create the secret for the internal registry using an htpasswd file.

    Input:
        namespace: Namespace for the registry secret
        kubeconfig_file: Kube config file path to access target cluster
        secret_name: Name for the registry secret
        htpasswd_file: File path for htpasswd file to use for secret

    Output:
        Writes registry secret to target namespace in cluster
    """
    LOG.info('Checking if the internal registry secret is already created...')
    LOG.info('Executing:')
    kubectl_get_secret = kubectl.run_kubectl_command(kubeconfig_file, 'get', 'secret',
                                                     secret_name, '--namespace', namespace)
    if kubectl_get_secret.returncode != 0 and "not found" in kubectl_get_secret.stderr.decode('utf-8'):
        LOG.info('%s has not been created', secret_name)
        LOG.info('Creating %s internal registry secret', secret_name)
        kubectl_create_secret = kubectl.run_kubectl_command(kubeconfig_file, 'create', 'secret', 'generic', secret_name,
                                                            f'--from-file=htpasswd={htpasswd_file}',
                                                            '--namespace', namespace)
        LOG.info("Command: %s", kubectl_create_secret.args)
        if kubectl_create_secret.returncode == 0:
            LOG.info('%s created successfully', secret_name)
        else:
            LOG.error(kubectl_create_secret.stderr.decode('utf-8'))
            raise errors.CreateSecretError(f"Issue arose when creating internal registry secret {secret_name}")
    else:
        if secret_name in kubectl_get_secret.stdout.decode('utf-8'):
            LOG.info('Internal registry secret %s already exists for'
                     ' namespace %s', secret_name, namespace)
        else:
            LOG.error(kubectl_get_secret.stderr.decode('utf-8'))
            raise errors.CreateSecretError(f"Issue arose when creating internal registry secret {secret_name}")


def create_internal_registry_secret(namespace, kubeconfig_file, name, username, user_password):
    """
    Create registry secret if none exists.

    Input:
        namespace: Namespace for the registry secret
        kubeconfig_file: Kube config file path to access target cluster
        name: Name for the registry secret
        username: Username string for htpasswd
        user_password: User password for htpasswd

    Output:
        Writes registry secret to target namespace in cluster from htpasswd file
    """
    LOG.info('Inputted parameters:')
    LOG.info('namespace: %s', namespace)
    LOG.info('kubeconfig_file: %s', kubeconfig_file)
    LOG.info('name: %s', name)
    LOG.info('username: %s', username)
    LOG.info('user_password: %s', user_password)

    create_htpasswd(username, user_password)
    create_registry_secret_from_htpasswd(namespace, kubeconfig_file, name, "./htpasswd")
