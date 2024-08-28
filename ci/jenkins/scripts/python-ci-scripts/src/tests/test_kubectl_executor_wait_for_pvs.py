"""Test for kubectl executor wait_for_persistent_volumes_deletion."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import wait_for_persistent_volumes_deletion

KUBECTL = "/usr/bin/kubectl"
PV1 = "oss-deploy/data-eric-oss-jms-svc-amq-secondary-1"
PV2 = "kube-system/nfs-pvc-bc9a869b-de05-4e72-b691-c6747b2fccff"
PV3 = "kube-system/nfs-pvc-e0fb18d3-c927-44ef-b668-c0ef9a2f15cc"
NAMESPACE = "test-ns"
NAMESPACE2 = "oss-deploy"
NAMESPACE3 = "test-ns2"
KUBECONFIG_FILE = "test-file"
TIMEOUT_WAIT_FOR_PV = "10"
RETRY_WAIT_FOR_PV = 3


@pytest.mark.parametrize("test_cli_args, expected", [
    # No manifest-file
    ("--namespace test-ns",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No artifact-url
    # No force-rebuild
    ("--kubeconfig-file test-kubeconfig",
     {'output': "Error: Missing option \"--namespace\""}),
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
def test_wait_for_pvs_bad_arguments(test_cli_args, expected):
    """Test argument handling for kubectl_executor.wait_for_persistent_volumes_deletion."""
    runner = CliRunner()
    result = runner.invoke(wait_for_persistent_volumes_deletion, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_persistent_volumes_not_found_error(caplog, monkeypatch, fp):
    """Test for persistent volumes not being found."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path, "get", "pv"]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="not found",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(wait_for_persistent_volumes_deletion, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--timeout", TIMEOUT_WAIT_FOR_PV,
        "--retries", RETRY_WAIT_FOR_PV
    ])

    assert "Persistent Volumes do not exist on the specified namespace" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_failed_deletion_of_persistent_volumes(caplog, monkeypatch, fp):
    """Test for deletion of pvs failure as pv exists."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)

        fp.register(command_and_args_list,
                    stdout=f"{PV1} {PV2} {PV3}",
                    returncode=0)

        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(wait_for_persistent_volumes_deletion, args=[
        "--namespace", NAMESPACE2,
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--timeout", TIMEOUT_WAIT_FOR_PV,
        "--retries", RETRY_WAIT_FOR_PV
    ])

    assert "Waiting for Persistent Volumes Deletion failed with following errors" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_successful_deletion_of_persistent_volumes(caplog, monkeypatch, fp):
    """Test for successful deletion of PVs."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)

        fp.register(command_and_args_list,
                    stdout=f"{PV1} {PV2} {PV3}",
                    returncode=0)

        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(wait_for_persistent_volumes_deletion, args=[
        "--namespace", NAMESPACE3,
        "--kubeconfig-file", KUBECONFIG_FILE,
        "--timeout", TIMEOUT_WAIT_FOR_PV,
        "--retries", RETRY_WAIT_FOR_PV
    ])

    assert "Persistent Volumes Deleted successfully" in caplog.text
    assert result.exit_code == 0
