"""Test for kubectl executor create_common_resources."""
import os
import shutil
import subprocess
import pytest
import yaml
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import create_common_resources

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No namespace
    ("--kubeconfig-file file --state-values-file file --docker-auth-config config "
     "--flow-area release --cluster-name hart123",
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
def test_create_common_resources_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.create_cluster_rolebinding."""
    runner = CliRunner()
    result = runner.invoke(create_common_resources, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_kubectl_error(resource_path_root, caplog, monkeypatch, fp):
    """Test a run with a failed kubectl apply command."""
    shutil.copyfile(os.path.join(resource_path_root, "site-values-default.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="There was an error with the server",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_common_resources, args=[
        "--namespace", "namespace",
        "--kubeconfig-file", "config.yaml",
        "--state-values-file", "site-values.yaml",
        "--docker-auth-config", "default-docker-auth-config",
        "--flow-area", "release",
        "--cluster-name", "hart111"])

    assert "There was an error in creating/updating ConfigMap testware-hostnames" in caplog.text
    assert "There was an error with the server" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_successful_run_no_ddp(resource_path_root, caplog, monkeypatch, fp):
    """Test successful run with the DDP information not included."""
    shutil.copyfile(os.path.join(resource_path_root, "common-resources-site-values.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="Successfully created resource",
                    returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_common_resources, args=[
        "--namespace", "namespace",
        "--kubeconfig-file", "config.yaml",
        "--state-values-file", "site-values.yaml",
        "--docker-auth-config", "default-docker-auth-config",
        "--flow-area", "release",
        "--cluster-name", "hart111"])

    assert "The ConfigMap testware-hostnames was created/updated successfully" in caplog.text
    assert os.path.exists("./testware-hostnames.yaml")
    testware_hostnames_dict = get_dict_from_file("./testware-hostnames.yaml")
    assert testware_hostnames_dict["data"]["adc"] == "adc.hart105.ews.gic.ericsson.se"
    assert testware_hostnames_dict["data"]["ingress"] == "10.156.119.129"
    assert testware_hostnames_dict["data"]["fh-snmp-alarm"] == "10.156.119.126"
    assert "The ConfigMap testware-global-config was created/updated successfully" in caplog.text
    assert os.path.exists("./testware-global-config.yaml")
    testware_global_config_dict = get_dict_from_file("./testware-global-config.yaml")
    assert testware_global_config_dict["data"]["docker-pull-secret"] == "default-docker-auth-config"
    assert testware_global_config_dict["data"]["cluster-name"] == "hart111"
    assert testware_global_config_dict["data"]["environment-label"] == "release"
    assert "All of the DDP values needed to create the ddp-config-secret are not available " \
           "- The secret will not be created" in caplog.text
    assert os.path.exists("./ddp-config-secret.yaml") is not True
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_successful_run_with_ddp(caplog, monkeypatch, fp):
    """Test successful run with the DDP information included."""
    ddp_dict = {
        "eric-oss-common-base": {
            "eric-oss-ddc": {
                "autoUpload": {
                    "enabled": True,
                    "ddpid": "test-ddpid",
                    "account": "test-account",
                    "password": "test-password"
                }
            }
        }
    }
    with open("site-values.yaml", "r", encoding="utf-8") as site_values_file:
        site_values_yaml = yaml.safe_load(site_values_file)
        site_values_yaml.update(ddp_dict)
    with open("site-values-ddp.yaml", "w", encoding="utf-8") as site_values_ddp_file:
        yaml.safe_dump(site_values_yaml, site_values_ddp_file)

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr="Successfully created resource",
                    returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(create_common_resources, args=[
        "--namespace", "namespace",
        "--kubeconfig-file", "config.yaml",
        "--state-values-file", "site-values-ddp.yaml",
        "--docker-auth-config", "default-docker-auth-config",
        "--flow-area", "release",
        "--cluster-name", "hart111"])

    assert "The ConfigMap testware-hostnames was created/updated successfully" in caplog.text
    assert os.path.exists("./testware-hostnames.yaml")
    assert "The ConfigMap testware-global-config was created/updated successfully" in caplog.text
    assert os.path.exists("./testware-global-config.yaml")
    assert "The Secret ddp-config-secret was created/updated successfully" in caplog.text
    assert os.path.exists("./ddp-config-secret.yaml")
    ddp_config_secret_dict = get_dict_from_file("./ddp-config-secret.yaml")
    assert ddp_config_secret_dict["data"]["auto-upload-enabled"] == b'VHJ1ZQ=='
    assert ddp_config_secret_dict["data"]["ddp-account"] == b'dGVzdC1hY2NvdW50'
    assert ddp_config_secret_dict["data"]["ddp-id"] == b'dGVzdC1kZHBpZA=='
    assert result.exit_code == 0


def get_dict_from_file(file):
    """Return a dict from a file."""
    with open(file, "r", encoding="utf-8") as open_file:
        return yaml.safe_load(open_file)
