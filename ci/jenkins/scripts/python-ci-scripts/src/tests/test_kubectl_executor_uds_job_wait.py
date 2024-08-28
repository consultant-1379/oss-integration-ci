"""Test for kubectl executor uds_backend_job_wait."""
import subprocess
import pytest
from click.testing import CliRunner

from bin.kubectl_executor import uds_backend_job_wait
from lib import utils
from lib import kubectl

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No path-to-helmfile
    ("--timeout 10 --namespace bob --kubeconfig-file /file/kube",
     {'output': "Error: Missing option \"--name\""}),
    # No chart_name
    ("--name job --timeout 10 --namespace bob",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No chart version
    ("--name job --timeout 10 --kubeconfig-file /file/kube",
     {'output': "Error: Missing option \"--namespace\""}),
    # No chart_repo
    ("--name job --namespace bob --kubeconfig-file /file/kube",
     {'output': "Error: Missing option \"--timeout\""}),
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
def test_uds_backend_job_wait_bad_args(test_cli_args, expected):
    """Test arg handling for kubectl_executor.uds_backend_job_wait."""
    runner = CliRunner()
    result = runner.invoke(uds_backend_job_wait, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_uds_backend_job_wait_success(monkeypatch, fp, caplog):
    """Test success in waiting for job completion."""
    kubeconfig = "testconfig"
    namespace = "testns"
    testjob = "test-job"
    successful_completion = f"job.batch \"{testjob}\" condition met"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_arg_list = [KUBECTL, "--kubeconfig", config_file_path]
        command_and_arg_list.extend(kubectl_args)
        if command_and_arg_list[3] == "get":
            fp.register(command_and_arg_list, stdout=f"NAME       COMPLETIONS   DURATION   AGE\n\
                                                      {testjob}   1/1           93s        34m", stderr="")
        else:
            fp.register(command_and_arg_list, stdout=successful_completion, stderr="")
        return utils.run_cli_command(command_and_arg_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(uds_backend_job_wait, args=[
                           "--name", testjob,
                           "--timeout", "30s",
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert successful_completion in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_uds_backup_job_wait_job_not_exist(monkeypatch, fp, caplog):
    """Test uds wait but job does not exist."""
    kubeconfig = "testconfig"
    namespace = "testns"
    testjob = "test-job"
    testjob_path = f"jobs/{testjob}"
    job_not_exist = f"Error from server (NotFound): jobs.batch \"{testjob}\" not found"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list,
                    stderr=job_not_exist,
                    stdout="",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(uds_backend_job_wait, args=[
                           "--name", testjob,
                           "--timeout", "30s",
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    # resource does not exist but does not cause a failure
    assert f"The indicated resource path {testjob_path}, does not exist" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_uds_backup_job_wait_timeout_error(monkeypatch, fp, caplog):
    """Test uds backup wait timeout error."""
    kubeconfig = "testconfig"
    namespace = "testns"
    testjob = "test-job"
    testjob_path = f"jobs/{testjob}"
    timeout_error = f"error: timed out waiting for the condition on {testjob_path}"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        if command_and_args_list[3] == "get":
            fp.register(command_and_args_list, stdout=f"NAME       COMPLETIONS   DURATION   AGE\n\
                                                      {testjob}   1/1           93s        34m", stderr="")
        else:
            fp.register(command_and_args_list, stderr=timeout_error, stdout="", returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(uds_backend_job_wait, args=[
                           "--name", testjob,
                           "--timeout", "30s",
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])
    assert timeout_error in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_uds_backup_job_wait_check_exist_failed(monkeypatch, fp, caplog):
    """Test uds backup job test exist failure."""
    kubeconfig = "testconfig"
    namespace = "testns"
    testjob = "test-job"
    testjob_path = f"jobs/{testjob}"

    # pylint: disable=unused-argument
    def kubectl_cmd(config_file_path, *kubectl_args):
        command_and_args_list = [KUBECTL, '--kubeconfig', config_file_path]
        command_and_args_list.extend(kubectl_args)
        fp.register(command_and_args_list, stderr="Error", returncode=1, stdout="")
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(kubectl, "run_kubectl_command", kubectl_cmd)

    runner = CliRunner()
    result = runner.invoke(uds_backend_job_wait, args=[
                           "--name", testjob,
                           "--timeout", "30s",
                           "--kubeconfig-file", kubeconfig,
                           "--namespace", namespace])

    assert f"Unable to determine if resource {testjob_path} exists" in caplog.text
    assert result.exit_code == 1
