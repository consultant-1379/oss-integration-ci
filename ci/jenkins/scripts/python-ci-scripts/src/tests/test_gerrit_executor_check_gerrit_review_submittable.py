"""Test for gerrit executor generate_gerrit_patch."""
import os
from unittest import mock
import pytest
from click.testing import CliRunner

from lib import containers
from bin.gerrit_executor import check_gerrit_review_submittable

USERNAME = "username"
PASSWORD = "password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No image
    ("--gerrit-change-number 1234567 --timeout 1800 --username name --password pswrd",
     {'output': "Error: Missing option \"--image\""}),
    # No Gerrit Change Number
    ("--image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest "
     "--timeout 1800 --username name --password pswrd",
     {'output': "Error: Missing option \"--gerrit-change-number\""}),
    # No Timeout Set
    ("--image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest "
     "--gerrit-change-number 1234567 --username name --password pswrd",
     {'output': "Error: Missing option \"--timeout\""}),
    # No username
    ("--image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest "
     "--gerrit-change-number 1234567 --timeout 1800 --password pswrd",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--image armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest "
     "--gerrit-change-number 1234567 --timeout 1800 --username name",
     {'output': "Error: Missing option \"--password\""}),
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
def test_check_gerrit_review_submittable_bad_args(test_cli_args, expected):
    """Test argument handling for gerrit_executor.check_gerrit_review_submittable."""
    runner = CliRunner()
    result = runner.invoke(check_gerrit_review_submittable, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
# pylint: disable=too-many-locals
def test_run_check_gerrit_review_submittable_success(monkeypatch, caplog):
    """Test successful patch creation."""
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest"
    gerrit_change_number = "1234567"
    timeout = 15
    os.environ["GERRIT_USERNAME"] = "kevin"
    os.environ["GERRIT_PASSWORD"] = "bob"

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(image, cmd_args, env_list):
        return ["2023-02-01 14:08:38,256 [gerrit] [INFO] Submittable"]
    monkeypatch.setattr(containers, "run_docker_command", execute_container)

    runner = CliRunner()
    result = runner.invoke(check_gerrit_review_submittable, args=[
                           "--image", image,
                           "--gerrit-change-number", gerrit_change_number, "--timeout", timeout])
    assert "Gerrit Review submittable check completed successfully" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_run_check_gerrit_review_submittable_failure(monkeypatch, caplog):
    """Test successful patch creation."""
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest"
    gerrit_change_number = "1234567"
    timeout = 15
    os.environ["GERRIT_USERNAME"] = "kevin"
    os.environ["GERRIT_PASSWORD"] = "bob"

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(image, cmd_args, env_list):
        return ["2023-02-01 14:08:38,256 [gerrit] [WARNING] Not submittable"]
    monkeypatch.setattr(containers, "run_docker_command", execute_container)

    runner = CliRunner()
    result = runner.invoke(check_gerrit_review_submittable, args=[
                           "--image", image,
                           "--gerrit-change-number", gerrit_change_number, "--timeout", timeout])
    assert "The review has not become submittable in the timeout set." in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_run_check_gerrit_review_submittable_error(monkeypatch, caplog):
    """Test successful patch creation."""
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-int-helm-chart-auto:latest"
    gerrit_change_number = "1234567"
    timeout = 15
    os.environ["GERRIT_USERNAME"] = "kevin"
    os.environ["GERRIT_PASSWORD"] = "bob"

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(image, cmd_args, env_list):
        raise Exception("The connectivity was lost to Docker.")
    monkeypatch.setattr(containers, "run_docker_command", execute_container)

    runner = CliRunner()
    result = runner.invoke(check_gerrit_review_submittable, args=[
                           "--image", image,
                           "--gerrit-change-number", gerrit_change_number, "--timeout", timeout])
    assert "Issue with execution of submittable check. Exception thrown:" in caplog.text
    assert result.exit_code == 1
