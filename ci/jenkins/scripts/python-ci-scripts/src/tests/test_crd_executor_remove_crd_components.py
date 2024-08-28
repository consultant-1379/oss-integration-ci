"""Test for crd executor remove_crd_components."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.crd_executor import remove_crd_components

KUBECTL = "/usr/bin/kubectl"
CRD1 = "crd1"
CRD2 = "crd2"
CRD3 = "crd3"
NAMESPACE = "test-ns"
KUBECONFIG_FILE = "test-file"


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
def test_remove_crd_components_bad_args(test_cli_args, expected):
    """Test argument handling for crd_executor.remove_crd_components."""
    runner = CliRunner()
    result = runner.invoke(remove_crd_components, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_failed_crd_acquisition_from_none_found(caplog, monkeypatch, fp):
    """Test for no crds being found."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="crd values not found",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_crd_components, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"CRD components do not exist on the specified namespace {NAMESPACE}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_failed_crd_acquisition_from_other_error(caplog, monkeypatch, fp):
    """Test for a failed crd acquisition for a reason other than no crds being found"""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="The connection was lost",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_crd_components, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"Issue arose deleting crd components from namespace: {NAMESPACE}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_no_crd_components_found(caplog, monkeypatch, fp):
    """Test for no crd components being found."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] != "-oyaml":
            fp.register(command_and_args_list,
                        stdout=f"name ns\n"
                               f"{CRD1} meta.helm.sh/release-namespace: {NAMESPACE}\n"
                               f"{CRD2} meta.helm.sh/release-namespace: {NAMESPACE}\n"
                               f"{CRD3} meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout="fake annotation",
                        returncode=0)

        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_crd_components, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert "crd_components: []" in caplog.text
    assert f"No CRD components exists on namespace {NAMESPACE}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_failed_crd_component_deletion(caplog, monkeypatch, fp):
    """Test for a failed crd component deletion."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "delete":
            fp.register(command_and_args_list,
                        stdout="The connection was lost",
                        returncode=1)
        elif command_and_args_list[-1] != "-oyaml":
            fp.register(command_and_args_list,
                        stdout=f"name ns\n"
                               f"{CRD1} meta.helm.sh/release-namespace: {NAMESPACE}\n"
                               f"{CRD2} meta.helm.sh/release-namespace: {NAMESPACE}\n"
                               f"{CRD3} meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout=f"meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_crd_components, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"Issue arose deleting crd from namespace: {NAMESPACE}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_successful_deletion(caplog, monkeypatch, fp):
    """Test for a successful deletion of crd components."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] != "-oyaml":
            fp.register(command_and_args_list,
                        stdout=f"name ns\n"
                               f"{CRD1} meta.helm.sh/release-namespace: {NAMESPACE}\n"
                               f"{CRD2} meta.helm.sh/release-namespace: {NAMESPACE}\n"
                               f"{CRD3} meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout=f"meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_crd_components, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"crd_components: ['{CRD1}', '{CRD2}', '{CRD3}']" in caplog.text
    assert f"Removal of crd_component {CRD1} from target namespace {NAMESPACE} finished successfully" in caplog.text
    assert f"Removal of crd_component {CRD2} from target namespace {NAMESPACE} finished successfully" in caplog.text
    assert f"Removal of crd_component {CRD3} from target namespace {NAMESPACE} finished successfully" in caplog.text
    assert f"Deleting crd_components from target namespace {NAMESPACE} finished successfully" in caplog.text
    assert "CRD components deleted successfully" in caplog.text
    assert result.exit_code == 0
