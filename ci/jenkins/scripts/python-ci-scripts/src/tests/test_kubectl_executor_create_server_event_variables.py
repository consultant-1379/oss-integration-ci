"""Test for kubectl executor create_server_event_variables."""
import os.path
import subprocess
import pytest
from click.testing import CliRunner

from bin.kubectl_executor import create_server_event_variables
from lib import utils
from lib import kubectl

KUBECTL = "/usr/bin/kubectl"
KUBECONFIG_FILE = "test-config-file"
NAMESPACE = "test-ns"
TESTWARE_RESOURCES_SECRET = """
{
    "apiVersion": "v1",
    "data": {
        "api_url": "dGVzdDE=",
        "gui_url": "dGVzdDI="
    },
    "kind": "Secret",
    "metadata": {
        "creationTimestamp": "2024-03-05T15:16:59Z",
        "name": "testware-resources-secret",
        "namespace": "oss-deploy",
        "resourceVersion": "696849094",
        "uid": "bd1cd4c6-038a-4689-8f41-38d7c2bc0f34"
    },
    "type": "Opaque"
}
"""
EIC_INSTALLED_APPLICATIONS = """
{
    "apiVersion": "v1",
    "data": {
        "Installed": "helmfile:\\n  name: eric-eiae-helmfile\\n  release: 2.2566.1-1-h3ef8fef"
    },
    "kind": "ConfigMap",
    "metadata": {
        "creationTimestamp": "2024-03-05T15:33:09Z",
        "name": "eric-installed-applications",
        "namespace": "oss-deploy",
        "resourceVersion": "696871121",
        "uid": "fb6686fc-9654-4141-a2da-1bd090ba2156"
    }
}
"""


@pytest.mark.parametrize("test_cli_args, expected", [
    # No namespace
    ("--kubeconfig-file file",
     {'output': "Error: Missing option \"--namespace\""}),
    # No kubeconfig file
    ("--namespace ns",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
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
    """Test argument handling for kubectl_executor.create_server_event_variables."""
    runner = CliRunner()
    result = runner.invoke(create_server_event_variables, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_successful_run_without_secret_variables(caplog, monkeypatch, fp):
    """Test a successful run without the secret variables."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if "secret" in command_and_args_list:
            fp.register(command_and_args_list, stderr="Secret not found")
        else:
            fp.register(command_and_args_list, stdout=EIC_INSTALLED_APPLICATIONS)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_server_event_variables, args=[
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--namespace", NAMESPACE])
    assert os.path.exists("./server-event-info.properties")
    with open("./server-event-info.properties", "r", encoding="utf-8") as server_event_info:
        data = server_event_info.readlines()
        assert "api_url=not_found\n" in data
        assert "gui_url=not_found\n" in data
        assert "from_version=2.2566.1-1-h3ef8fef\n" in data
    assert "Creating server event variables completed successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_successful_run_with_all_variables(caplog, monkeypatch, fp):
    """Test a successful run with all of the variables."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if "secret" in command_and_args_list:
            fp.register(command_and_args_list, stdout=TESTWARE_RESOURCES_SECRET)
        else:
            fp.register(command_and_args_list, stdout=EIC_INSTALLED_APPLICATIONS)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_server_event_variables, args=[
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--namespace", NAMESPACE])
    assert os.path.exists("./server-event-info.properties")
    with open("./server-event-info.properties", "r", encoding="utf-8") as server_event_info:
        data = server_event_info.readlines()
        assert "api_url=test1\n" in data
        assert "gui_url=test2\n" in data
        assert "from_version=2.2566.1-1-h3ef8fef\n" in data
    assert "Creating server event variables completed successfully" in caplog.text
    assert result.exit_code == 0
