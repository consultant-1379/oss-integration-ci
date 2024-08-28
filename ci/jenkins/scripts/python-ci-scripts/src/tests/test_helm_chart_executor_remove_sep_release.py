"""Test for helm chart executor remove_sep_release."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import helm
from lib import utils
from bin.helm_chart_executor import remove_sep_release

HELM = "/usr/bin/helm"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--namespace testns",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--kubeconfig-file config",
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
def test_remove_sep_release_bad_args(test_cli_args, expected):
    """Test argument handling for helm_chart_executor.remove_sep_release."""
    runner = CliRunner()
    result = runner.invoke(remove_sep_release, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_remove_sep_release_success(monkeypatch, fp, caplog):
    """Test successful sep release deletion from namespace."""
    kubeconfig = "testconfig"
    namespace = "testns"
    release = "eric-storage-encryption-provider"

    # pylint: disable=unused-argument
    def run_helm_command(config_file_path, *helm_args):
        command_and_args_list = [HELM, '--kubeconfig', config_file_path]
        command_and_args_list.extend(helm_args)
        if command_and_args_list[3] == "ls":
            fp.register(command_and_args_list, stdout=f"{release}\n")
        else:
            fp.register(command_and_args_list, stdout=f"{release} uninstalled")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helm, "run_helm_command", run_helm_command)

    runner = CliRunner()
    result = runner.invoke(remove_sep_release, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert f"Removal of release {release} from target namespace {namespace} finished successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_remove_sep_release_does_not_exist(monkeypatch, fp, caplog):
    """Test release deletion when namespace or release does not exist."""
    kubeconfig = "testconfig"
    namespace = "testns"

    # pylint: disable=unused-argument
    def run_helm_command(config_file_path, *helm_args):
        command_and_args_list = [HELM, '--kubeconfig', config_file_path]
        command_and_args_list.extend(helm_args)
        fp.register(command_and_args_list, stdout="")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helm, "run_helm_command", run_helm_command)

    runner = CliRunner()
    result = runner.invoke(remove_sep_release, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert f"SEP Release is not installed on {namespace}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_remove_sep_release_failed(monkeypatch, fp, caplog):
    """Test failed release deletion."""
    kubeconfig = "testconfig"
    namespace = "testns"
    release = "eric-storage-encryption-provider"

    # pylint: disable=unused-argument
    def run_helm_command(config_file_path, *helm_args):
        command_and_args_list = [HELM, '--kubeconfig', config_file_path]
        command_and_args_list.extend(helm_args)
        if command_and_args_list[3] == "ls":
            fp.register(command_and_args_list, stdout=f"{release}\n")
        else:
            fp.register(command_and_args_list, stdout=f"{release} deletion failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helm, "run_helm_command", run_helm_command)

    runner = CliRunner()
    result = runner.invoke(remove_sep_release, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert f"Issue deleting release from namespace: {namespace}" in caplog.text
    assert result.exit_code == 1
