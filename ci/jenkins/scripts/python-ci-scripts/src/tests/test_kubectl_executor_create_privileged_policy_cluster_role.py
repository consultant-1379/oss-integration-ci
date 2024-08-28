"""Test for kubectl executor create_privileged_policy_cluster_role."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import create_privileged_policy_cluster_role

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--release-name testrelease --namespace testns --name testname",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--kubeconfig-file config --release-name testrelease --name testname",
     {'output': "Error: Missing option \"--namespace\""}),
    # No name
    ("--kubeconfig-file config --release-name testrelease --namespace testns",
     {'output': "Error: Missing option \"--name\""}),
    # No release-name
    ("--kubeconfig-file config --namespace testns --name testname",
     {'output': "Error: Missing option \"--release-name\""}),
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
def test_create_privileged_policy_cluster_role_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_privileged_policy_cluster_role."""
    runner = CliRunner()
    result = runner.invoke(create_privileged_policy_cluster_role, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_create_privileged_policy_cluster_role_success(monkeypatch, fp, caplog):
    """Test successful cluster role creation."""
    kubeconfig = "testconfig"
    name = "testname"
    release_name = "testrelease"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr="Error from server (NotFound): "
                        f"clusterroles.rbac.authorization.k8s.io \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"clusterrole.rbac.authorization.k8s.io/{name} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_privileged_policy_cluster_role, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--release-name", release_name])
    assert f"Cluster role {name} already exists" not in caplog.text
    assert f"Created cluster role {name} successfully" in caplog.text
    with open('./PrivilegedPolicyClusterRole.yaml', 'r', encoding="utf-8") as yaml_file:
        generated_yaml = yaml_file.read()
    assert f"meta.helm.sh/release-name: {release_name}-{namespace}" in generated_yaml
    assert f"meta.helm.sh/release-namespace: {namespace}" in generated_yaml
    assert "securitycontextconstraints" in generated_yaml
    assert "podsecuritypolicies" in generated_yaml
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_privileged_policy_cluster_role_already_exists(monkeypatch, fp, caplog):
    """Test cluster role creation when it already exists."""
    kubeconfig = "testconfig"
    name = "testname"
    release_name = "testrelease"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stdout=f"NAME       CREATED AT\n{name}   2022-11-11T15:04:54Z")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_privileged_policy_cluster_role, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--release-name", release_name])
    assert f"Cluster role {name} already exists" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_privileged_policy_cluster_role_failed(monkeypatch, fp, caplog):
    """Test failed cluster role creation."""
    kubeconfig = "testconfig"
    name = "testname"
    release_name = "testrelease"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr="Error from server (NotFound): "
                        f"clusterroles.rbac.authorization.k8s.io \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list,
                        stderr=f"clusterrole.rbac.authorization.k8s.io/{name} creation failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_privileged_policy_cluster_role, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--release-name", release_name])
    assert f"Failed to create cluster role {name}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_create_privileged_policy_cluster_role_check_existing_failed(monkeypatch, fp, caplog):
    """Test failed cluster role creation on checking for existing cluster role."""
    kubeconfig = "testconfig"
    name = "testname"
    release_name = "testrelease"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stderr="Error", returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_privileged_policy_cluster_role, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--release-name", release_name])
    assert f"Unable to determine if cluster role {name} exists" in caplog.text
    assert result.exit_code == 1
