"""Test for gerrit executor generate_gerrit_patch."""
import os

import pytest
from click.testing import CliRunner
from lib import containers
from bin.gerrit_executor import generate_gerrit_patch


@pytest.mark.parametrize("test_cli_args, expected", [
    # No image
    ("--message \"NO JIRA - Test\" --git-repo-local cloned_repo --gerrit-branch master "
     "--username name --password pswrd",
     {'output': "Error: Missing option \"--image\""}),
    # No message
    ("--image test.se --git-repo-local cloned_repo --gerrit-branch master "
     "--username name --password pswrd",
     {'output': "Error: Missing option \"--message\""}),
    # No username
    ("--image test.se --message \"NO JIRA - Test\" --git-repo-local cloned_repo --gerrit-branch master "
     "--password pswrd",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--message \"NO JIRA - Test\" --image test.se --git-repo-local cloned_repo --gerrit-branch master "
     "--username name",
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
def test_gerrit_create_patch_bad_args(test_cli_args, expected):
    """Test argument handling for gerrit_executor.gerrit-create-patch."""
    runner = CliRunner()
    result = runner.invoke(generate_gerrit_patch, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_run_gerrit_create_patch_success(monkeypatch):
    """Test successful patch creation."""
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-adp-release-auto:latest"
    git_message = "Hello World"
    git_repo_local = "bob/cloned_repo"
    gerrit_branch = "master"
    os.environ["GERRIT_USERNAME"] = "kevin"
    os.environ["GERRIT_PASSWORD"] = "who"

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(image, cmd_args, env_list):
        return ["Change is: https://gerrit-gamma.gic.ericsson.se/#/c/99999999"]
    monkeypatch.setattr(containers, "run_docker_command", execute_container)

    runner = CliRunner()
    result = runner.invoke(generate_gerrit_patch, args=[
                           "--image", image,
                           "--message", git_message, "--git-repo-local", git_repo_local,
                           "--gerrit-branch", gerrit_branch])

    assert os.path.exists(os.path.join(os.getcwd(), "gerrit_create_patch.properties")) is True
    with open(os.path.join(os.getcwd(), "gerrit_create_patch.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert "GERRIT_URL=https://gerrit-gamma.gic.ericsson.se/#/c/99999999" in text
    assert "GERRIT_CHANGE_NUMBER=99999999" in text
    assert "GERRIT_REFSPEC=refs/changes/99/99999999/1" in text
    assert "GERRIT_PATCHSET_NUMBER=1" in text
    assert "GERRIT_BRANCH=master" in text
    assert result.exit_code == 0


# pylint: disable=too-many-locals
def test_run_gerrit_create_patch_error(monkeypatch, caplog):
    """Test error patch creation."""
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/bob-adp-release-auto:latest"
    git_message = "Hello World"
    git_repo_local = "bob/cloned_repo"
    gerrit_branch = "master"
    os.environ["GERRIT_USERNAME"] = "kevin"
    os.environ["GERRIT_PASSWORD"] = "who"

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(image, cmd_args, env_list):
        raise Exception("The connectivity was lost to Docker.")
    monkeypatch.setattr(containers, "run_docker_command", execute_container)

    runner = CliRunner()
    result = runner.invoke(generate_gerrit_patch, args=[
                           "--image", image,
                           "--message", git_message, "--git-repo-local", git_repo_local,
                           "--gerrit-branch", gerrit_branch])
    assert "Unable to create a Gerrit patch set. Exception thrown:" in caplog.text
    assert result.exit_code == 1
