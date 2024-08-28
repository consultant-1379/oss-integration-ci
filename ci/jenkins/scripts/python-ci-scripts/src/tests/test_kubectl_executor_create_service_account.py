"""Test for kubectl executor create_service_account."""
import subprocess
import pytest
from click.testing import CliRunner
from lib import kubectl
from lib import utils
from bin.kubectl_executor import create_service_account

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--namespace testns --name testname",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--kubeconfig-file config --name testname",
     {'output': "Error: Missing option \"--namespace\""}),
    # No name
    ("--kubeconfig-file config --namespace testns",
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
def test_create_service_account_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_service_account."""
    runner = CliRunner()
    result = runner.invoke(create_service_account, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_create_service_account_success(monkeypatch, fp, caplog):
    """Test successful service account creation."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): serviceaccounts \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"serviceaccount/{name} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_service_account, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace])
    assert f"Service account {name} already exists" not in caplog.text
    assert f"Created service account {name} successfully" in caplog.text
    with open('./ServiceAccount.yaml', 'r', encoding="utf-8") as yaml_file:
        generated_yaml = yaml_file.read()
    assert f"name: {name}" in generated_yaml
    assert "automountServiceAccountToken: true" in generated_yaml
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_service_account_already_exists(monkeypatch, fp, caplog):
    """Test service account creation when it already exists."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stdout=f"NAME       SECRETS   AGE\n{name}   0         4m55s")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_service_account, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace])
    assert f"Service account {name} already exists" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_service_account_failed(monkeypatch, fp, caplog):
    """Test failed service account creation."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): serviceaccounts \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list,
                        stderr=f"serviceaccount/{name} creation failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_service_account, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace])
    assert f"Failed to create service account {name}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_create_service_account_check_existing_failed(monkeypatch, fp, caplog):
    """Test failed service account creation on checking for existing SA."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stderr="Error", returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_service_account, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace])
    assert f"Unable to determine if service account {name} exists" in caplog.text
    assert result.exit_code == 1
