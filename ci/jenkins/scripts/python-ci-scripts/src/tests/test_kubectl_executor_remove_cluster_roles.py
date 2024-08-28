"""Test for kubectl executor remove_cluster_rolebindings."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import remove_cluster_roles

KUBECTL = "/usr/bin/kubectl"
CR_LIST = ["cr1", "cr2", "cr3"]
NAMESPACE = "test-ns"
KUBECONFIG_FILE = "test-file"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--namespace test-ns",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
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
def test_remove_cluster_roles_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.remove_cluster_roles."""
    runner = CliRunner()
    result = runner.invoke(remove_cluster_roles, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_cluster_roles_not_found_error(caplog, monkeypatch, fp):
    """Test for cluster roles not being found."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="not found",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_cluster_roles, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert "Cluster roles do not exist" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_cluster_roles_not_found_other_error(caplog, monkeypatch, fp):
    """Test for cluster roles not being found due to an error."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="Connection error",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_cluster_roles, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"removing cluster role with annotation for namespace {NAMESPACE}" in caplog.text
    assert "Connection error" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_no_cluster_role_components(caplog, monkeypatch, fp):
    """Test for no cluster role components being found."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] == "clusterrole":
            fp.register(command_and_args_list,
                        stdout=f"name ns\n{CR_LIST[0]} {NAMESPACE}\n{CR_LIST[1]} "
                               f"{NAMESPACE}\n{CR_LIST[2]} {NAMESPACE}\n",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout="namespace: ns\n",
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_cluster_roles, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert "cluster_role_components: []" in caplog.text
    assert "No cluster roles exist" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_failed_cluster_role_component_deletion(caplog, monkeypatch, fp):
    """Test for a failure in the deletion of the cluster role components."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] == "clusterrolebinding":
            fp.register(command_and_args_list,
                        stdout=f"name ns\n{CR_LIST[0]} {NAMESPACE}\n{CR_LIST[1]} "
                               f"{NAMESPACE}\n{CR_LIST[2]} {NAMESPACE}\n",
                        returncode=0)
        elif command_and_args_list[-1] == "-oyaml":
            fp.register(command_and_args_list,
                        stdout=f"meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout="Connection error\n",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_cluster_roles, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"removing cluster role with annotation for namespace {NAMESPACE}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_successful_cluster_role_component_deletion(caplog, monkeypatch, fp):
    """Test for a successful deletion of cluster role components."""
    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] == "clusterrole":
            fp.register(command_and_args_list,
                        stdout=f"name ns\n{CR_LIST[0]} {NAMESPACE}\n{CR_LIST[1]} "
                               f"{NAMESPACE}\n{CR_LIST[2]} {NAMESPACE}\n",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout=f"meta.helm.sh/release-namespace: {NAMESPACE}\n",
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_cluster_roles, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert f"cluster_role_components: ['{CR_LIST[0]}', '{CR_LIST[1]}', '{CR_LIST[2]}']" in caplog.text
    for cr in CR_LIST:
        assert f"Removal of cluster role_component {cr} has finished successfully" in caplog.text
    assert "Deleting cluster role_components has finished successfully" in caplog.text
    assert result.exit_code == 0
