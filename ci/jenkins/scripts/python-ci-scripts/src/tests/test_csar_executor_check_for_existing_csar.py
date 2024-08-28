"""Test for csar executor check_for_existing_csar"""
import os
from unittest import mock
import pytest
import requests
from click.testing import CliRunner
from requests.auth import HTTPBasicAuth
from mock_response import MockResponse

from bin.csar_executor import check_for_existing_csar

CSAR_REPO_URL = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/csars"
IMAGES = "applications.properties"
BUILD_CSAR_OUTPUT_FILE = "build_csar.properties"
CHECK_CSAR_OUTPUT_FILE = "csar_check.properties"
APPLICATIONS_FILE = "applications.properties"
CSAR_NAME = "eric-cloud-native-base"
CSAR_VERSION_1 = "73.10.0"
CSAR_VERSION_2 = "78.5.0"
CSAR_VERSION_3 = "84.3.0"
USERNAME = "username"
PASSWORD = "password"
TIMEOUT_IN_S = 600
JSON_CONTENT = '{"children": [{"uri": "v73.10.0"}, {"uri": "v78.5.0"}]}'


@pytest.mark.parametrize("test_cli_args, expected", [
    # No applications-to-check
    ("--csar-repo-url url --username username --password password",
     {'output': "Error: Missing option \"--applications-to-check\""}),
    # No csar-repo-url
    ("--applications-to-check applications --username username --password password",
     {'output': "Error: Missing option \"--csar-repo-url\""}),
    ("--csar-repo-url url --applications-to-check applications --password password",
     {'output': "Error: Missing option \"--username\""}),
    # No csar-repo-url
    ("--csar-repo-url url --applications-to-check applications --username username",
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
     {'output': 'Error: no such option: --unknown'})
])
def test_build_csars_from_properties_file_bad_args(test_cli_args, expected):
    """Test argument handling for csar_executor.get_app_version_from_helmfile."""
    runner = CliRunner()
    result = runner.invoke(check_for_existing_csar, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_files_removed():
    """Testing that the build and check csar files are removed from the directory."""
    # pylint: disable=unspecified-encoding
    with open(BUILD_CSAR_OUTPUT_FILE, "w+"), open(CHECK_CSAR_OUTPUT_FILE, "w+"):
        pass

    assert os.path.isfile(BUILD_CSAR_OUTPUT_FILE) is True
    assert os.path.isfile(CHECK_CSAR_OUTPUT_FILE) is True

    runner = CliRunner()
    runner.invoke(check_for_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", IMAGES])

    assert os.path.isfile(BUILD_CSAR_OUTPUT_FILE) is False
    assert os.path.isfile(CHECK_CSAR_OUTPUT_FILE) is False


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_successful_csar_found(monkeypatch, caplog):
    """Test a successful run with matching CSAR versions."""
    # pylint: disable=unspecified-encoding
    with open(APPLICATIONS_FILE, "w+") as applications_file:
        applications_file.write(f"{CSAR_NAME}={CSAR_VERSION_1}\n")

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=TIMEOUT_IN_S):
        response = MockResponse(content=JSON_CONTENT)
        return response

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(check_for_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", IMAGES])

    assert f"Artifacts found in repo:\n ['{CSAR_VERSION_1}', '{CSAR_VERSION_2}']\n" in caplog.text
    assert f"CSAR Version {CSAR_VERSION_1} exists in CSAR repo, for {CSAR_NAME}: {CSAR_VERSION_1}" in caplog.text
    assert os.path.isfile(BUILD_CSAR_OUTPUT_FILE) is True
    with open(BUILD_CSAR_OUTPUT_FILE, "r") as build_csar_output_file:
        file_content = build_csar_output_file.readlines()
    assert f"{CSAR_NAME}_{CSAR_VERSION_1}_csar_found=True\n" in file_content
    assert os.path.isfile(CHECK_CSAR_OUTPUT_FILE) is True
    with open(CHECK_CSAR_OUTPUT_FILE, "r") as check_csar_output_file:
        file_content = check_csar_output_file.readlines()
    assert f"{CSAR_NAME}__AVAILABLE={CSAR_REPO_URL}/{CSAR_NAME}/{CSAR_VERSION_1}\n" in file_content
    os.remove(BUILD_CSAR_OUTPUT_FILE)
    os.remove(CHECK_CSAR_OUTPUT_FILE)
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_successful_csar_not_found(monkeypatch, caplog):
    """Test a successful run with mismatched CSAR versions."""
    # pylint: disable=unspecified-encoding
    with open(APPLICATIONS_FILE, "w+") as applications_file:
        applications_file.write(f"{CSAR_NAME}={CSAR_VERSION_3}\n")

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=TIMEOUT_IN_S):
        response = MockResponse(content=JSON_CONTENT)
        return response

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(check_for_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", IMAGES])

    assert f"Artifacts found in repo:\n ['{CSAR_VERSION_1}', '{CSAR_VERSION_2}']\n" in caplog.text
    assert f"CSAR Version {CSAR_VERSION_3} not found in CSAR repo, for {CSAR_NAME}: {CSAR_VERSION_3}" in caplog.text
    assert os.path.isfile(BUILD_CSAR_OUTPUT_FILE) is True
    with open(BUILD_CSAR_OUTPUT_FILE, "r") as build_csar_output_file:
        file_content = build_csar_output_file.readlines()
    assert f"{CSAR_NAME}_{CSAR_VERSION_3}_csar_found=False\n" in file_content
    assert os.path.isfile(CHECK_CSAR_OUTPUT_FILE) is True
    with open(CHECK_CSAR_OUTPUT_FILE, "r") as check_csar_output_file:
        file_content = check_csar_output_file.readlines()
    assert f"{CSAR_NAME}__NOT_FOUND={CSAR_REPO_URL}/{CSAR_NAME}/{CSAR_VERSION_3}\n" in file_content
    os.remove(BUILD_CSAR_OUTPUT_FILE)
    os.remove(CHECK_CSAR_OUTPUT_FILE)
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_http_error(monkeypatch, caplog):
    """Test a HTTP error."""
    # pylint: disable=unspecified-encoding
    with open(APPLICATIONS_FILE, "w+") as applications_file:
        applications_file.write(f"{CSAR_NAME}={CSAR_VERSION_1}\n")

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=TIMEOUT_IN_S):
        raise requests.HTTPError("Error Code 401")

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(check_for_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", IMAGES])

    assert "HTTP error occurred: Error Code 401" in caplog.text
    assert os.path.isfile(BUILD_CSAR_OUTPUT_FILE) is True
    with open(BUILD_CSAR_OUTPUT_FILE, "r") as build_csar_output_file:
        file_content = build_csar_output_file.readlines()
    assert len(file_content) == 0
    assert os.path.isfile(CHECK_CSAR_OUTPUT_FILE) is True
    with open(CHECK_CSAR_OUTPUT_FILE, "r") as check_csar_output_file:
        file_content = check_csar_output_file.readlines()
    assert len(file_content) == 0
    os.remove(BUILD_CSAR_OUTPUT_FILE)
    os.remove(CHECK_CSAR_OUTPUT_FILE)
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_other_error(monkeypatch, caplog):
    """Test a non-HTTP error."""
    # pylint: disable=unspecified-encoding
    with open(APPLICATIONS_FILE, "w+") as applications_file:
        applications_file.write(f"{CSAR_NAME}={CSAR_VERSION_1}\n")

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=TIMEOUT_IN_S):
        raise Exception("Other Error")

    monkeypatch.setattr(requests, "get", get_response)

    runner = CliRunner()
    result = runner.invoke(check_for_existing_csar, args=[
        "--csar-repo-url", CSAR_REPO_URL,
        "--applications-to-check", IMAGES])

    assert "Other error occurred: Other Error" in caplog.text
    assert os.path.isfile(BUILD_CSAR_OUTPUT_FILE) is True
    with open(BUILD_CSAR_OUTPUT_FILE, "r") as build_csar_output_file:
        file_content = build_csar_output_file.readlines()
    assert len(file_content) == 0
    assert os.path.isfile(CHECK_CSAR_OUTPUT_FILE) is True
    with open(CHECK_CSAR_OUTPUT_FILE, "r") as check_csar_output_file:
        file_content = check_csar_output_file.readlines()
    assert len(file_content) == 0
    os.remove(BUILD_CSAR_OUTPUT_FILE)
    os.remove(CHECK_CSAR_OUTPUT_FILE)
    assert result.exit_code == 1
