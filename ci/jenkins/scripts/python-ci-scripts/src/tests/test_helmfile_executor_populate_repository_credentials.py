"""Test for helmfile executor populate_repository_credentials."""
import pytest
import yaml
from click.testing import CliRunner

from bin.helmfile_executor import populate_repository_credentials

REPOSITORY_FILE_NAME = "repositories.yaml"
USERNAME = "test_username"
PASSWORD = "test_password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No file
    ("--username username --user-password password",
     {'output': "Error: Missing option \"--file\""}),
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
     {'output': 'Error: no such option: --unknown'})
])
def test_populate_repository_credentials_bad_args(test_cli_args, expected):
    """Test argument handling for helmfile_executor.populate_repository_credentials."""
    runner = CliRunner()
    result = runner.invoke(populate_repository_credentials, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_no_repo_file(caplog):
    """Test for no repositories file being provided."""
    runner = CliRunner()
    result = runner.invoke(populate_repository_credentials, args=[
        "--file", REPOSITORY_FILE_NAME,
        "--username", USERNAME,
        "--user-password", PASSWORD])

    assert f"No such file or directory: '{REPOSITORY_FILE_NAME}'" in caplog.text
    assert result.exit_code == 1


def test_incorrect_repo_file(caplog):
    """Test for an incorrect repositories file being provided"""
    incorrect_data = {
        "key": "value"
    }
    with open(REPOSITORY_FILE_NAME, "w", encoding="utf-8") as repo_file:
        yaml.dump(incorrect_data, repo_file, default_flow_style=False)

    runner = CliRunner()
    result = runner.invoke(populate_repository_credentials, args=[
        "--file", REPOSITORY_FILE_NAME,
        "--username", USERNAME,
        "--user-password", PASSWORD])

    assert "Repositories entries not found in yaml file - no updates made" in caplog.text
    assert result.exit_code == 0


def test_successful_repo_file_change():
    """Test for a successful repositories file change."""
    repository_data = {
        "repositories": [
            {
                "name": "repo1",
                "url": "url/repo1",
                "username": "existing_username",
                "password": "existing_password"
            },
            {
                "name": "repo2",
                "url": "url/repo2"
            },
            {
                "name": "repo3",
                "url": "url/repo3"
            }
        ]
    }
    with open(REPOSITORY_FILE_NAME, "w", encoding="utf-8") as repo_file:
        yaml.dump(repository_data, repo_file, default_flow_style=False)

    runner = CliRunner()
    result = runner.invoke(populate_repository_credentials, args=[
        "--file", REPOSITORY_FILE_NAME,
        "--username", USERNAME,
        "--user-password", PASSWORD])

    with open(REPOSITORY_FILE_NAME, "r", encoding="utf-8") as repo_file:
        file_content = yaml.safe_load(repo_file)

    assert "existing_username" in file_content["repositories"][0]["username"]
    assert "existing_password" in file_content["repositories"][0]["password"]
    assert "test_username" in file_content["repositories"][1]["username"]
    assert "test_password" in file_content["repositories"][1]["password"]
    assert "test_username" in file_content["repositories"][2]["username"]
    assert "test_password" in file_content["repositories"][2]["password"]
    assert result.exit_code == 0
