"""Test for kubectl executor check_and_create_internal_registry_secret."""
import os
import shutil
import subprocess
import pytest
from click.testing import CliRunner

from lib import registry
from lib import kubectl
from lib import utils
from bin.kubectl_executor import check_and_create_internal_registry_secret

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No kubeconfig-file
    ("--name testname --namespace testns --user-id testid --user-password testpassword",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--name testname --kubeconfig-file config --user-id testid --user-password testpassword",
     {'output': "Error: Missing option \"--namespace\""}),
    # No user-id
    ("--name testname --kubeconfig-file config --namespace testns --user-password testpassword",
     {'output': "Error: Missing option \"--user-id\""}),
    # No name
    ("--kubeconfig-file config --namespace testns --user-id testid",
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
def test_check_and_create_internal_registry_secret_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.check_and_create_internal_registry_secret."""
    runner = CliRunner()
    result = runner.invoke(check_and_create_internal_registry_secret, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_check_and_create_internal_registry_secret_success(monkeypatch, fp, caplog, resource_path_root):
    """Test successful registry secret creation."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"
    user_id = "testid"
    user_password = "testpassword"

    # pylint: disable=unused-argument
    def create_htpasswd_cmd(username, user_password):
        return True
    monkeypatch.setattr(registry, "create_htpasswd", create_htpasswd_cmd)
    shutil.copyfile(os.path.join(resource_path_root, "htpasswd"),
                    os.path.join(os.getcwd(), "htpasswd"))

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): secrets \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list, stdout=f"secret/{name} created")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(check_and_create_internal_registry_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--user-id", user_id,
                           "--user-password", user_password])
    assert f"Internal registry secret {name} already exists for namespace {namespace}" not in caplog.text
    assert f"{name} created successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_check_and_create_internal_registry_secret_already_exists(monkeypatch, fp, caplog, resource_path_root):
    """Test internal registry secret creation when it already exists."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"
    user_id = "testid"
    user_password = "testpassword"

    # pylint: disable=unused-argument
    def create_htpasswd_cmd(username, user_password):
        return True
    monkeypatch.setattr(registry, "create_htpasswd", create_htpasswd_cmd)
    shutil.copyfile(os.path.join(resource_path_root, "htpasswd"),
                    os.path.join(os.getcwd(), "htpasswd"))

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stdout=f"NAME         TYPE     DATA   AGE\n{name}   Opaque   1      3m33s")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(check_and_create_internal_registry_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--user-id", user_id,
                           "--user-password", user_password])
    assert f"Internal registry secret {name} already exists for namespace {namespace}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_check_and_create_internal_registry_secret_failed(monkeypatch, fp, caplog, resource_path_root):
    """Test failed internal registry secret creation."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"
    user_id = "testid"
    user_password = "testpassword"

    # pylint: disable=unused-argument
    def create_htpasswd_cmd(username, user_password):
        return True
    monkeypatch.setattr(registry, "create_htpasswd", create_htpasswd_cmd)
    shutil.copyfile(os.path.join(resource_path_root, "htpasswd"),
                    os.path.join(os.getcwd(), "htpasswd"))

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list,
                        stderr=f"Error from server (NotFound): secrets \"{name}\" not found",
                        returncode=1)
        else:
            fp.register(command_and_args_list,
                        stderr=f"secret/{name} creation failed",
                        returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(check_and_create_internal_registry_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--user-id", user_id,
                           "--user-password", user_password])
    assert f"Issue arose when creating internal registry secret {name}" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_check_and_create_internal_registry_secret_check_existing_failed(monkeypatch, fp, caplog, resource_path_root):
    """Test failed internal registry secret creation on checking for existing secret."""
    kubeconfig = "testconfig"
    name = "testname"
    namespace = "testns"
    user_id = "testid"
    user_password = "testpassword"

    # pylint: disable=unused-argument
    def create_htpasswd_cmd(username, user_password):
        return True
    monkeypatch.setattr(registry, "create_htpasswd", create_htpasswd_cmd)
    shutil.copyfile(os.path.join(resource_path_root, "htpasswd"),
                    os.path.join(os.getcwd(), "htpasswd"))

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stderr="Error", returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(check_and_create_internal_registry_secret, args=[
                           "--kubeconfig-file", kubeconfig,
                           "--name", name,
                           "--namespace", namespace,
                           "--user-id", user_id,
                           "--user-password", user_password])
    assert f"Issue arose when creating internal registry secret {name}" in caplog.text
    assert result.exit_code == 1
