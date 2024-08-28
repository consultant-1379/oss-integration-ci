"""Tests for get_latest_helmfile_version in helmfile_executor.py."""
import os
from unittest import mock
import pytest
import requests
from click.testing import CliRunner
from mock_response import MockResponse
from bin.helmfile_executor import get_latest_helmfile_version


CHART_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"
HELMFILE_NAME = "eric-oss-common-base"
USERNAME = "username"
PASSWORD = "password"
REQUEST_PAYLOAD = 'items.find({"repo":{"$eq":"proj-eric-oss-drop-helm-local"},"path":{"$eq":"eric-oss-common-base"},' \
                  '"created": {"$gt": "2023-09-17T15:30:24.438674"}})'
AQL_RESULTS_JSON_CONTENT = """{
    "results": [
        {
            "repo": "proj-eric-oss-drop-helm-local",
            "path": "eric-oss-common-base",
            "name": "eric-oss-common-base-0.173.0.tgz",
            "type": "file",
            "size": 459398,
            "created": "2023-09-18T14:19:33.784+02:00",
            "created_by": "ossapps100",
            "modified": "2023-09-18T14:19:33.709+02:00",
            "modified_by": "ossapps100",
            "updated": "2023-09-18T14:19:33.785+02:00"
        },
        {
            "repo": "proj-eric-oss-drop-helm-local",
            "path": "eric-oss-common-base",
            "name": "eric-oss-common-base-0.174.0.tgz",
            "type": "file",
            "size": 458744,
            "created": "2023-09-18T14:32:04.218+02:00",
            "created_by": "ossapps100",
            "modified": "2023-09-18T14:32:04.157+02:00",
            "modified_by": "ossapps100",
            "updated": "2023-09-18T14:32:04.218+02:00"
        }],
    "range": {
        "start_pos": 0,
        "end_pos": 39,
        "total": 39
    }
}"""
API_STORAGE_RESULTS_JSON_CONTENT = '{"children" : [ {"uri" : "/eric-oss-common-base-0.1.0-999.tgz"}, \
                {"uri" : "/eric-oss-common-base-0.1.1-986.tgz"}],\
                "uri" : "https://arm.seli.gic.ericsson.se/artifactory/api/storage/\
                proj-eric-oss-drop-helm-local/eric-oss-common-base"}'
TIMEOUT_IN_S = 600


@pytest.mark.parametrize("test_cli_args, expected", [
    # No chart-repo
    ('',
     {'output': "Error: Missing option \"--chart-repo\"."}),
    # No helmfile-name
    ('--chart-repo https://repo',
     {'output': "Error: Missing option \"--helmfile-name\"."}),
    # Verbosity not an integer
    ('-v x',
     {'output': 'x is not a valid integer'}),
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
def test_get_latest_helmfile_version_invalid_args(test_cli_args, expected):
    """Test for get_latest_helmfile_version when arguments are invalid."""
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_missing_username(caplog):
    """Test for a missing username."""
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, args=[
        "--chart-repo", CHART_REPO,
        "--helmfile-name", HELMFILE_NAME])

    assert "Missing environment variable FUNCTIONAL_USER_USERNAME value" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME})
def test_missing_password(caplog):
    """Test for a missing password"""
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, args=[
        "--chart-repo", CHART_REPO,
        "--helmfile-name", HELMFILE_NAME])

    assert "Missing environment variable FUNCTIONAL_USER_USERNAME value" not in caplog.text
    assert "Missing environment variable FUNCTIONAL_USER_PASSWORD value" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_get_latest_helmfile_version_http_error(caplog):
    """Test for get_latest_helmfile_version when there is an http error."""
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, args=[
                           "--chart-repo", CHART_REPO,
                           "--helmfile-name", HELMFILE_NAME])
    assert result.exit_code == 1
    assert "HTTP error occurred: 401 Client Error" in caplog.text


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_get_latest_helmfile_version_other_error(monkeypatch, caplog):
    """Test for get_latest_helmfile_version when there is a non-http error."""
    # pylint: disable=too-many-arguments
    def get_response(post, artifactory_request_url, auth, data, timeout=600):
        raise Exception("Other Error")
    monkeypatch.setattr(requests, "request", get_response)
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, args=[
                           "--chart-repo", CHART_REPO,
                           "--helmfile-name", HELMFILE_NAME])
    assert result.exit_code == 1
    assert "Other error occurred: Other Error" in caplog.text


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_get_latest_helmfile_version_by_aql_query_success(monkeypatch):
    """Test for get_latest_helmfile_version when successful."""
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    def get_response(post, artifactory_request_url, auth, data, timeout=600):
        response = MockResponse(content=AQL_RESULTS_JSON_CONTENT)
        return response
    monkeypatch.setattr(requests, "request", get_response)
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, args=[
                           "--chart-repo", CHART_REPO,
                           "--helmfile-name", HELMFILE_NAME])
    assert result.exit_code == 0
    with open('artifact.properties', 'r', encoding="utf-8") as artifact_properties:
        assert "INT_CHART_VERSION:0.174.0" in artifact_properties.read()
    os.remove('artifact.properties')


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_get_latest_helmfile_version_by_api_storage_query_success(monkeypatch):
    """Test for get_latest_helmfile_version when successful."""
    # pylint: disable=unused-argument
    # pylint: disable=too-many-arguments
    def get_response(post, artifactory_request_url, auth, data, timeout=600):
        response = MockResponse(content=API_STORAGE_RESULTS_JSON_CONTENT)
        return response
    monkeypatch.setattr(requests, "request", get_response)
    runner = CliRunner()
    result = runner.invoke(get_latest_helmfile_version, args=[
                           "--chart-repo", CHART_REPO,
                           "--helmfile-name", HELMFILE_NAME])
    assert result.exit_code == 0
    with open('artifact.properties', 'r', encoding="utf-8") as artifact_properties:
        assert "INT_CHART_VERSION:0.1.1-986" in artifact_properties.read()
    os.remove('artifact.properties')
