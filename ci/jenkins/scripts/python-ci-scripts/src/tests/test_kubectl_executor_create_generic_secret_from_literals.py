"""Test for kubectl executor create_generic_secret_from_literals."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import create_generic_secret_from_literals

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--namespace testns --secret-name testsecret --from-literals \"username=username password=password\"",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--kubeconfig-file config --secret-name testsecret --from-literals \"username=username password=password\"",
     {'output': "Error: Missing option \"--namespace\""}),
    # No secret-name
    ("--kubeconfig-file config --namespace testns --from-literals \"username=username password=password\"",
     {'output': "Error: Missing option \"--secret-name\""}),
    # No from-literals
    ("--kubeconfig-file config --secret-name testsecret --namespace testns",
     {'output': "Error: Missing option \"--from-literals\""}),
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
def test_create_generic_secret_from_literals_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_generic_secret_from_literals."""
    runner = CliRunner()
    result = runner.invoke(create_generic_secret_from_literals, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_create_generic_secret_from_literals_success(monkeypatch, fp, caplog):
    """Test successful generic secret creation."""
    kubeconfig = "testconfig"
    secret_name = "testsecret"
    namespace = "testns"
    from_literals = "username=username password=password"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): secrets \"{secret_name}\" not found",
                        returncode=1)
        elif "label" in command_and_args_list:
            fp.register(command_and_args_list,
                        stdout="Successfully labeled the resource",
                        returncode=0)
        else:
            fp.register(command_and_args_list, stdout=f"secret/{secret_name} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_generic_secret_from_literals, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--secret-name", secret_name,
                           "--namespace", namespace,
                           "--from-literals", from_literals])
    assert f"Secret {secret_name} already exist for namespace for namespace {namespace}" not in caplog.text
    assert f"{secret_name} created successfully" in caplog.text
    assert "Successfully labeled the resource" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_generic_secret_from_literals_already_exists(monkeypatch, fp, caplog):
    """Test generic secret creation when it already exists."""
    kubeconfig = "testconfig"
    secret_name = "testsecret"
    namespace = "testns"
    from_literals = "username=username password=password"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stdout=f"NAME         TYPE     DATA   AGE\n{secret_name}   Opaque   2      3m33s")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_generic_secret_from_literals, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--secret-name", secret_name,
                           "--namespace", namespace,
                           "--from-literals", from_literals])
    assert f"Secret {secret_name} already exists in namespace {namespace}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_create_generic_secret_from_literals_failed(monkeypatch, fp, caplog):
    """Test failed generic secret creation."""
    kubeconfig = "testconfig"
    secret_name = "testsecret"
    namespace = "testns"
    from_literals = "username=username password=password"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): secrets \"{secret_name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list,
                        stderr=f"secret/{secret_name} creation failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_generic_secret_from_literals, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--secret-name", secret_name,
                           "--namespace", namespace,
                           "--from-literals", from_literals])
    assert f"Issue arose when creating secret {secret_name}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_create_generic_secret_from_literals_check_existing_failed(monkeypatch, fp, caplog):
    """Test failed generic secret creation on checking for existing secret."""
    kubeconfig = "testconfig"
    secret_name = "testsecret"
    namespace = "testns"
    from_literals = "username=username password=password"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stderr="Error", returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_generic_secret_from_literals, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--secret-name", secret_name,
                           "--namespace", namespace,
                           "--from-literals", from_literals])
    assert f"Issue arose when creating secret {secret_name}" in caplog.text
    assert result.exit_code == 1
