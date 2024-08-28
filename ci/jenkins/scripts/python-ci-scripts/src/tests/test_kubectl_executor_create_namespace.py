"""Test for kubectl executor create_namespace."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import create_namespace

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--namespace testns --ignore-exists false",
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
def test_create_namespace_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_namespace."""
    runner = CliRunner()
    result = runner.invoke(create_namespace, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_namespace_creation_success(monkeypatch, fp, caplog):
    """Test successful namespace creation."""
    kubeconfig = "testconfig"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): namespaces \"{namespace}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"namespace/{namespace} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert f"Namespace {namespace} created successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_namespace_creation_failed(monkeypatch, fp, caplog):
    """Test failed namespace creation."""
    kubeconfig = "testconfig"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): namespaces \"{namespace}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"namespace/{namespace} creation failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert f"namespace/{namespace} creation failed" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_namespace_creation_ignore_exists_true(monkeypatch, fp, caplog):
    """Test successful check that namespace already exists."""
    kubeconfig = "testconfig"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stdout=f"NAME     STATUS   AGE\n{namespace}   Active   16h")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--ignore-exists", "true"])
    assert f"Namespace {namespace} already exists" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_namespace_creation_ignore_exists_false(monkeypatch, fp, caplog):
    """Test successful check that namespace already exists but ignore-exists is false."""
    kubeconfig = "testconfig"
    namespace = "testns"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stdout=f"NAME     STATUS   AGE\n{namespace}   Active   16h")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_namespace, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace,
                           "--ignore-exists", "false"])
    assert "Ensure the namespace has been cleaned down and deleted before continuing" in caplog.text
    assert result.exit_code == 1
