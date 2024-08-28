"""Test for csar executor download_existing_csar"""
import os
from unittest import mock
import pytest
import requests
from click.testing import CliRunner
from requests import HTTPError
from requests.auth import HTTPBasicAuth
from mock_response import MockResponse

from bin.csar_executor import download_existing_csar

USERNAME = "username"
PASSWORD = "password"
CSAR_NAME = "eric-cloud-native-base"
CSAR_VERSION = "87.8.0"
CSAR_REPO_URL = "test/url"
APPLICATIONS_TO_CHECK = "applications.properties"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No csar-repo-url
    ("--applications-to-check applications " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--csar-repo-url\""}),
    # No applications-to-check
    ("--csar-repo-url url " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--applications-to-check\""}),
    # No username
    ("--applications-to-check applications " +
     "--csar-repo-url url " +
     "--password password",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--applications-to-check applications " +
     "--csar-repo-url url " +
     "--username username",
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
def test_download_existing_csar_bad_args(test_cli_args, expected):
    """Test argument handling for csar_executor.download_existing_csars."""
    runner = CliRunner()
    result = runner.invoke(download_existing_csar, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_no_existing_csar_download(caplog):
    """Test for the CSAR values being set to false."""
    with open(APPLICATIONS_TO_CHECK, "w", encoding="utf-8") as applications_file:
        applications_file.write(f"{CSAR_NAME}_{CSAR_VERSION}_False")

    runner = CliRunner()
    result = runner.invoke(download_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", APPLICATIONS_TO_CHECK])

    assert f"CSAR for {CSAR_NAME}:{CSAR_VERSION} does not exist." in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_successful_csar_download_without_header(caplog, monkeypatch):
    """Test for a successful CSAR download."""
    with open(APPLICATIONS_TO_CHECK, "w", encoding="utf-8") as applications_file:
        applications_file.write(f"{CSAR_NAME}_{CSAR_VERSION}_True")

    # pylint: disable=unused-argument
    def get_response(full_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), stream=True,
                     timeout=600):
        content = str.encode(f"{CSAR_NAME}-{CSAR_VERSION}")
        response = MockResponse(content=content)
        return response

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(download_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", APPLICATIONS_TO_CHECK])

    assert os.path.isfile(f"{CSAR_NAME}-{CSAR_VERSION}.csar") is True
    with open(f"{CSAR_NAME}-{CSAR_VERSION}.csar", "r", encoding="utf-8") as generated_file:
        file_output = generated_file.readlines()
    assert [f"{CSAR_NAME}-{CSAR_VERSION}"] == file_output
    os.remove(f"{CSAR_NAME}-{CSAR_VERSION}.csar")
    assert f"Repo url for {CSAR_NAME}: {CSAR_REPO_URL}/" \
           f"{CSAR_NAME}/{CSAR_VERSION}/{CSAR_NAME}-{CSAR_VERSION}.csar" in caplog.text
    assert "Download of existing CSARs completed successfully" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_successful_csar_download_with_header(caplog, monkeypatch):
    """Test for a successful CSAR download."""
    with open(APPLICATIONS_TO_CHECK, "w", encoding="utf-8") as applications_file:
        applications_file.write(f"{CSAR_NAME}_{CSAR_VERSION}_True")

    # pylint: disable=unused-argument
    def get_response(full_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), stream=True,
                     timeout=600):
        content = str.encode(f"{CSAR_NAME}-{CSAR_VERSION}")
        headers = {"content-length": 5}
        response = MockResponse(content=content, headers=headers)
        return response

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(download_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", APPLICATIONS_TO_CHECK])

    assert os.path.isfile(f"{CSAR_NAME}-{CSAR_VERSION}.csar") is True
    with open(f"{CSAR_NAME}-{CSAR_VERSION}.csar", "r", encoding="utf-8") as generated_file:
        file_output = generated_file.readlines()
    assert [f"{CSAR_NAME}-{CSAR_VERSION}"] == file_output
    os.remove(f"{CSAR_NAME}-{CSAR_VERSION}.csar")
    assert f"Repo url for {CSAR_NAME}: {CSAR_REPO_URL}/" \
           f"{CSAR_NAME}/{CSAR_VERSION}/{CSAR_NAME}-{CSAR_VERSION}.csar" in caplog.text
    assert "Download of existing CSARs completed successfully" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_failed_csar_download_http_error(caplog, monkeypatch):
    """Test for a failed download because of a HTTP error."""
    with open(APPLICATIONS_TO_CHECK, "w", encoding="utf-8") as applications_file:
        applications_file.write(f"{CSAR_NAME}_{CSAR_VERSION}_True")

    # pylint: disable=unused-argument
    def get_response(full_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), stream=True,
                     timeout=600):
        raise HTTPError("Status 500 error")

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(download_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", APPLICATIONS_TO_CHECK])

    assert os.path.isfile(f"{CSAR_NAME}-{CSAR_VERSION}.csar") is False
    assert f"Repo url for {CSAR_NAME}: {CSAR_REPO_URL}/" \
           f"{CSAR_NAME}/{CSAR_VERSION}/{CSAR_NAME}-{CSAR_VERSION}.csar" in caplog.text
    assert "HTTP error occurred: Status 500 error" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_failed_csar_download_other_error(caplog, monkeypatch):
    """Test for a failed download because of a non-HTTP error."""
    with open(APPLICATIONS_TO_CHECK, "w", encoding="utf-8") as applications_file:
        applications_file.write(f"{CSAR_NAME}_{CSAR_VERSION}_True")

    # pylint: disable=unused-argument
    def get_response(full_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), stream=True,
                     timeout=600):
        raise Exception("A different error")

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(download_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", APPLICATIONS_TO_CHECK])

    assert os.path.isfile(f"{CSAR_NAME}-{CSAR_VERSION}.csar") is False
    assert f"Repo url for {CSAR_NAME}: {CSAR_REPO_URL}/" \
           f"{CSAR_NAME}/{CSAR_VERSION}/{CSAR_NAME}-{CSAR_VERSION}.csar" in caplog.text
    assert "Other error occurred: A different error" in caplog.text
    assert result.exit_code == 1
