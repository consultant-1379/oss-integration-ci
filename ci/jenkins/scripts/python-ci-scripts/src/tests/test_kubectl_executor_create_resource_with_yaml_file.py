"""Test for kubectl executor create_evnfm_predeploy_cluster_rolebinding."""
import subprocess
import pytest
from click.testing import CliRunner

from bin.kubectl_executor import create_resource_with_yaml_file
from lib import utils
from lib import kubectl

KUBECTL = "/usr/bin/kubectl"
KUBECONFIG_FILE = "test-config-file"
NAMESPACE = "test-ns"
NAME = "test-name"
FILE = "test-file"
RESOURCE_NAME = "pod"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No namespace
    ("--kubeconfig-file file --name name --file file --resource-name pod",
     {'output': "Error: Missing option \"--namespace\""}),
    # No kubeconfig file
    ("--namespace ns --name name --file file --resource-name pod",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No name
    ("--kubeconfig-file file --namespace ns --file file --resource-name pod",
     {'output': "Error: Missing option \"--name\""}),
    # No file
    ("--kubeconfig-file file --namespace ns --name name --resource-name pod",
     {'output': "Error: Missing option \"--file\""}),
    # No resource name
    ("--kubeconfig-file file --namespace ns --name name --file file",
     {'output': "Error: Missing option \"--resource-name\""}),
    # Verbosity not an integer
    ('-v x',
     {'output': "x is not a valid integer"}),
    # Verbosity too small
    ('-v -1',
     {'output': '-1 is not in the valid range of 0 to 4'}),
    # Verbosity too large
    ('-v 10',
     {'output': '10 is not in the valid range of 0 to 4'}),
    # Unknown argument
    ('--unknown a',
     {'output': 'Error: no such option: --unknown'}),
])
def test_create_cluster_role_binding_with_file_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_resource_with_yaml_file."""
    runner = CliRunner()
    result = runner.invoke(create_resource_with_yaml_file, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_missing_file(caplog, monkeypatch, fp):
    """Test for the namespace not being found."""

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr=f"Error from server (NotFound): namespaces \"{NAMESPACE}\" not found",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_resource_with_yaml_file, args=[
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--namespace", NAMESPACE,
        "--name", NAME,
        "--file", FILE,
        "--resource-name", RESOURCE_NAME])

    assert f"No such file or directory: '{FILE}'"
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_resource_already_exists(caplog, monkeypatch, fp):
    """Test for the resource already existing."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stdout=f"resource {NAME} found",
                    returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_resource_with_yaml_file, args=[
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--namespace", NAMESPACE,
        "--name", NAME,
        "--file", FILE,
        "--resource-name", RESOURCE_NAME])

    assert f"The {RESOURCE_NAME} {NAME} already exists" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_namespace_not_found(caplog, monkeypatch, fp):
    """Test for the namespace not being found."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr=f"Error from server (NotFound): namespaces \"{NAMESPACE}\" not found",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    with open(FILE, "w", encoding="utf-8"):
        pass

    runner = CliRunner()
    result = runner.invoke(create_resource_with_yaml_file, args=[
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--namespace", NAMESPACE,
        "--name", NAME,
        "--file", FILE,
        "--resource-name", RESOURCE_NAME])

    assert f"Error from server (NotFound): namespaces \"{NAMESPACE}\" not found" in caplog.text
    assert f"{RESOURCE_NAME} did not create correctly"
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_successful_resource_creation(caplog, monkeypatch, fp):
    """Test for the successful creation of the resource."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="not found",
                    returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    with open(FILE, "w", encoding="utf-8"):
        pass

    runner = CliRunner()
    result = runner.invoke(create_resource_with_yaml_file, args=[
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--namespace", NAMESPACE,
        "--name", NAME,
        "--file", FILE,
        "--resource-name", RESOURCE_NAME])

    assert f"The creation of {RESOURCE_NAME} {NAME} completed successfully" in caplog.text
    assert result.exit_code == 0
