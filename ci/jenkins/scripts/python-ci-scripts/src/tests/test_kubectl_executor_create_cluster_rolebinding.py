"""Test for kubectl executor create_cluster_rolebinding."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import create_cluster_rolebinding

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--cluster-role testcr --service-account testsa --name testname",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No cluster-role
    ("--kubeconfig-file config --service-account testsa --name testname",
     {'output': "Error: Missing option \"--cluster-role\""}),
    # No service-account
    ("--kubeconfig-file config --cluster-role testcr --name testname",
     {'output': "Error: Missing option \"--service-account\""}),
    # No name
    ("--kubeconfig-file config --cluster-role testcr --service-account testsa",
     {'output': "Error: Missing option \"--name\""}),
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
def test_create_cluster_rolebinding_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_cluster_rolebinding."""
    runner = CliRunner()
    result = runner.invoke(create_cluster_rolebinding, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_create_cluster_rolebinding_success(monkeypatch, fp, caplog):
    """Test successful cluster rolebinding creation."""
    kubeconfig = "testconfig"
    name = "testname"
    cluster_role = "testrole"
    service_account = "testns:testsa"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr="Error from server (NotFound): "
                        f"clusterrolebindings.rbac.authorization.k8s.io \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"clusterrolebinding.rbac.authorization.k8s.io/{name} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_cluster_rolebinding, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--cluster-role", cluster_role,
                           "--service-account", service_account])
    assert f"{name} cluster rolebinding already created" not in caplog.text
    assert f"{name} created successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_cluster_rolebinding_already_exists(monkeypatch, fp, caplog):
    """Test cluster rolebinding creation when it already exists."""
    kubeconfig = "testconfig"
    name = "testname"
    cluster_role = "testrole"
    service_account = "testns:testsa"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stdout=f"NAME       ROLE                   AGE\n{name}   ClusterRole/{cluster_role}   15m")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_cluster_rolebinding, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--cluster-role", cluster_role,
                           "--service-account", service_account])
    assert f"{name} cluster rolebinding already created" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_cluster_rolebinding_failed(monkeypatch, fp, caplog):
    """Test failed cluster rolebinding creation."""
    kubeconfig = "testconfig"
    name = "testname"
    cluster_role = "testrole"
    service_account = "testns:testsa"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr="Error from server (NotFound): "
                        f"clusterrolebindings.rbac.authorization.k8s.io \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list,
                        stderr=f"clusterrolebinding.rbac.authorization.k8s.io/{name} creation failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_cluster_rolebinding, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--cluster-role", cluster_role,
                           "--service-account", service_account])
    assert f"Issue arose when creating cluster rolebinding {name}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_create_cluster_rolebinding_check_existing_failed(monkeypatch, fp, caplog):
    """Test failed cluster rolebinding creation on checking for existing rolebinding."""
    kubeconfig = "testconfig"
    name = "testname"
    cluster_role = "testrole"
    service_account = "testns:testsa"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stderr="Error", returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_cluster_rolebinding, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--cluster-role", cluster_role,
                           "--service-account", service_account])
    assert f"Issue arose when creating cluster rolebinding {name}" in caplog.text
    assert result.exit_code == 1
