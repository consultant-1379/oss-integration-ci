"""Test for kubectl executor remove_kafka_topic_resources."""
import subprocess
import pytest
from click.testing import CliRunner

from lib import kubectl
from lib import utils
from bin.kubectl_executor import remove_kafka_topic_resources

KUBECTL = "/usr/bin/kubectl"
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
def test_remove_kafka_topic_resources_bad_args(test_cli_args, expected):
    """Test argument handling for kubectl_executor.remove_kafka_topic_resources"""
    runner = CliRunner()
    result = runner.invoke(remove_kafka_topic_resources, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_no_kt_resources(caplog, monkeypatch, fp):
    """Test for no kafkatopic resources."""

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] == "name":
            fp.register(command_and_args_list,
                        stdout="No kafkatopic resources found",
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_kafka_topic_resources, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert "No kafkatopic resources found in the namespace" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_run_exception(caplog, monkeypatch, fp):
    """Test for an error during the run."""

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] == "name":
            raise Exception("Connectivity error")

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_kafka_topic_resources, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert "Removing kafka topic resources failed with the following error" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_successful_run(caplog, monkeypatch, fp):
    """Test for a successful run."""

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[-1] == "name":
            fp.register(command_and_args_list,
                        stdout="kafkatopic.kafka.strimzi.io/test1\nkafkatopic.kafka.strimzi.io/test2",
                        returncode=0)
        else:
            fp.register(command_and_args_list,
                        stdout="patch successful",
                        returncode=0)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(remove_kafka_topic_resources, args=[
        "--namespace", NAMESPACE,
        "--kubeconfig-file", KUBECONFIG_FILE
    ])

    assert "Successfully patched kafkatopic kafkatopic.kafka.strimzi.io/test1: patch successful" in caplog.text
    assert "Successfully patched kafkatopic kafkatopic.kafka.strimzi.io/test2: patch successful" in caplog.text
    assert result.exit_code == 0
