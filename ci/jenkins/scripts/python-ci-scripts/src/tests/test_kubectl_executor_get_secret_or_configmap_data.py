"""Test for kubectl executor get_value_from_configmap_or_secret."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import get_value_from_configmap_or_secret

KUBECTL = "/usr/bin/kubectl"
OUTPUT_JSON = '''{
    "apiVersion": "v1",
    "data": {
        "api_url": "aHR0cDovL2FwaS5hcHAtc3RhZ2luZy1yZXBvcnQuZXdzLmdpYy5lcmljc3Nvbi5zZS9hcGk=",
        "database_url": "aHR0cDovL2FwaS5hcHAtc3RhZ2luZy1yZXBvcnQuZXdzLmdpYy5lcmljc3Nvbi5zZS9hcGk=",
        "gui_url": "aHR0cDovL2d1aS5hcHAtc3RhZ2luZy1yZXBvcnQuZXdzLmdpYy5lcmljc3Nvbi5zZS9zdGFnaW5nLXJlcG9ydHM="
    },
    "kind": "Secret",
    "metadata": {
        "creationTimestamp": "2024-03-11T17:51:11Z",
        "name": "testware-resources-secret",
        "namespace": "ci-test-flow-upgrade2",
        "resourceVersion": "704310404",
        "uid": "30154687-35fb-4f45-81ec-a2e7e68d6208"
    },
    "type": "Opaque"
}'''


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--resource-name test-resources --resource-type secret --namespace test --search-string gui_url",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--resource-name test-resources --resource-type secret --kubeconfig-file ./admin.conf --search-string gui_url",
     {'output': "Error: Missing option \"--namespace\""}),
    # No search-string
    ("--resource-name test-resources --resource-type secret --namespace test --kubeconfig-file ./admin.conf",
     {'output': "Error: Missing option \"--search-string\""}),
    # No resource-type
    ("--resource-name test-resources --namespace test --kubeconfig-file ./admin.conf --search-string gui_url",
     {'output': "Error: Missing option \"--resource-type\""}),
    # No resource-name
    ("--resource-type secret --namespace test --kubeconfig-file ./admin.conf --search-string gui_url",
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
def test_get_value_from_configmap_or_secret_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.get_value_from_configmap_or_secret."""
    runner = CliRunner()
    result = runner.invoke(get_value_from_configmap_or_secret, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_get_value_from_configmap_or_secret_not_found(monkeypatch, fp, caplog):
    """Test if search string not found."""
    resource_name = "test-resource"
    resource_type = "secret"
    kubeconfig = "testconfig"
    search_string = "key"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): {resource_type} \"{resource_name}\" not found",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(get_value_from_configmap_or_secret, args=[
                           "--resource-name", resource_name,
                           "--resource-type", resource_type,
                           "--kubeconfig-file", kubeconfig,
                           "--search-string", search_string,
                           "--namespace", namespace])
    assert f"The {resource_type} {resource_name} was not found in the cluster." in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_get_value_from_configmap_or_secret_found_but_key_not_found(monkeypatch, fp, caplog):
    """Test if search string not found."""
    resource_name = "test-resource"
    resource_type = "secret"
    kubeconfig = "testconfig"
    search_string = "key"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stdout=OUTPUT_JSON,
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(get_value_from_configmap_or_secret, args=[
                           "--resource-name", resource_name,
                           "--resource-type", resource_type,
                           "--kubeconfig-file", kubeconfig,
                           "--search-string", search_string,
                           "--namespace", namespace])
    assert f"{resource_type} {resource_name} found on the cluster. Checking for the key {search_string}" in caplog.text
    assert f"The key {search_string} was not in the {resource_type} {resource_name}"
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_get_value_from_configmap_or_secret_found(monkeypatch, fp, caplog):
    """Test if search string not found."""
    resource_name = "test-resource"
    resource_type = "secret"
    kubeconfig = "testconfig"
    search_string = "api_url"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stdout=OUTPUT_JSON,
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(get_value_from_configmap_or_secret, args=[
                           "--resource-name", resource_name,
                           "--resource-type", resource_type,
                           "--kubeconfig-file", kubeconfig,
                           "--search-string", search_string,
                           "--namespace", namespace])
    assert f"Found key {search_string} in {resource_type} {resource_name}" in caplog.text
    assert result.exit_code == 0
