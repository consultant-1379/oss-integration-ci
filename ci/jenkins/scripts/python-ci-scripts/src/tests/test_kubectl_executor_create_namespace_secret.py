"""Test for kubectl executor create_namespace."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils

from bin.kubectl_executor import create_namespace_secret

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--namespace testns --secret-name k8-secret --dockerconfig-file config.json --ignore-exists false",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--kubeconfig-file config --secret-name k8-secret --dockerconfig-file config.json --ignore-exists false",
     {'output': "Error: Missing option \"--namespace\""}),
    # No Docker config
    ("--namespace testns --kubeconfig-file config --secret-name k8-secret --ignore-exists false",
     {'output': "Error: Missing option \"--dockerconfig-file\""}),
    # No secret name
    ("--namespace testns --kubeconfig-file config --dockerconfig-file config.json --ignore-exists false",
     {'output': "Error: Missing option \"--secret-name\""}),
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
def test_create_namespace_secret_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_namespace."""
    runner = CliRunner()
    result = runner.invoke(create_namespace_secret, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_namespace_secret_creation_success(monkeypatch, fp, caplog):
    """Test successful namespace secret creation."""
    kubeconfig = "testconfig"
    namespace = "testns"
    dockerconfig = "testdockconfig"
    secret = "k8s-registry-secret"
    ignore = "true"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stdout=f"secret/{secret} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--dockerconfig-file", dockerconfig,
                           "--secret-name", secret,
                           "--ignore-exists", ignore])
    assert f"Secret {secret} created successfully" in caplog.text
    assert result.exit_code == 0


def test_namespace_secret_fail_if_namesapce_does_not_exist(monkeypatch, fp, caplog):
    """Test successful namespace secret creation."""
    kubeconfig = "testconfig"
    namespace = "testns"
    dockerconfig = "testdockconfig"
    secret = "k8s-registry-secret"
    ignore = "true"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr=f"Error from server (NotFound): secret \"{secret}\" not found",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--dockerconfig-file", dockerconfig,
                           "--secret-name", secret,
                           "--ignore-exists", ignore])
    assert "Error from server (NotFound)" in caplog.text
    assert result.exit_code == 1


def test_namespace_secret_fails_if_secret_created_and_ignore_exist_false(monkeypatch, fp, caplog):
    """Test successful namespace secret creation."""
    kubeconfig = "testconfig"
    namespace = "testns"
    dockerconfig = "testdockconfig"
    secret = "k8s-registry-secret"
    ignore = "false"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get" and command_and_args_list[4] == "secret":
            fp.register(command_and_args_list,
                        stderr=f"Checking if secret {secret} exists")
        else:
            fp.register(command_and_args_list, stdout=f"secret/{secret} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--dockerconfig-file", dockerconfig,
                           "--secret-name", secret,
                           "--ignore-exists", ignore])
    assert "already exists and --ignore_exists set to" in caplog.text
    assert result.exit_code == 1


def test_namespace_secret_fails_during_secret_delete(monkeypatch, fp, caplog):
    """Test successful namespace secret creation."""
    kubeconfig = "testconfig"
    namespace = "testns"
    dockerconfig = "testdockconfig"
    secret = "k8s-registry-secret"
    ignore = "true"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "delete":
            fp.register(command_and_args_list,
                        stderr=f"Checking if secret {secret} exists",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"secret/{secret} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--dockerconfig-file", dockerconfig,
                           "--secret-name", secret,
                           "--ignore-exists", ignore])
    assert f"Secret {secret} deletion failed from {namespace}" in caplog.text
    assert result.exit_code == 1


def test_namespace_secret_fails_during_secret_creation(monkeypatch, fp, caplog):
    """Test successful namespace secret creation."""
    kubeconfig = "testconfig"
    namespace = "testns"
    dockerconfig = "testdockconfig"
    secret = "k8s-registry-secret"
    ignore = "true"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "create":
            fp.register(command_and_args_list,
                        stderr=f"Creating secret {secret}",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"secret/{secret} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--dockerconfig-file", dockerconfig,
                           "--secret-name", secret,
                           "--ignore-exists", ignore])
    assert f"Secret {secret} creation failed in Namespace {namespace}" in caplog.text
    assert result.exit_code == 1
