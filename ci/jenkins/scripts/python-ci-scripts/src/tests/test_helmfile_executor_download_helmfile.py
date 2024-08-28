"""Tests for helmfile_executor.py download_helmfile command."""
import os
import pytest
import requests
from requests.auth import HTTPBasicAuth
from click.testing import CliRunner
from mock_response import MockResponse

from bin.helmfile_executor import download_helmfile


@pytest.mark.parametrize("test_cli_args, expected", [
    # No chart_name
    ("--chart-version 1.0.0 --chart-repo https://repo",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No chart version
    ("--chart-name oss-chart --chart-repo https://repo",
     {'output': "Error: Missing option \"--chart-version\""}),
    # No chart_repo
    ("--chart-name oss-chart --chart-version 1.0.0",
     {'output': "Error: Missing option \"--chart-repo\""}),
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
def test_download_helmfile_bad_args(test_cli_args, expected):
    """Test argument handling in helmfile_executor.download_helmfile."""
    runner = CliRunner()
    result = runner.invoke(download_helmfile, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_download_helmfile_success(monkeypatch, resource_path_root, caplog):
    """Test successful download of helmfile."""
    chart_name = "eric-eo-helmfile"
    chart_version = "1.0.0"
    full_chart_name = chart_name + "-" + chart_version + ".tgz"
    chart_repo = "https://my/artifactory"
    username = "me"
    password = "admin123"
    timeout_in_s = 600
    with open(os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test"), "rb") as file_content:
        content = file_content.read()
        content_size = len(content)

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(username, password), timeout=timeout_in_s):
        response = MockResponse(content=content)
        return response
    monkeypatch.setattr(requests, "get", get_response)
    runner = CliRunner()
    result = runner.invoke(download_helmfile,
                           args=["--chart-name", chart_name, "--chart-version", chart_version,
                                 "--chart-repo", chart_repo])
    assert f"Downloading: {chart_repo}/{chart_name}/{chart_name}-{chart_version}.tgz" in caplog.text
    assert result.exit_code == 0
    assert os.path.exists(full_chart_name) is True
    assert os.path.getsize(full_chart_name) == content_size
    assert "Download of the Helmfile completed successfully" in caplog.text


def test_download_helmfile_http_error(monkeypatch, caplog):
    """Test handling of 404 file not found."""
    chart_name = "eric-eo-helmfile"
    chart_version = "1.0.0"
    chart_repo = "https://my/artifactory"
    username = "me"
    password = "admin123"
    timeout_in_s = 600
    status_code = 404

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(username, password), timeout=timeout_in_s):
        response = MockResponse(status_code=status_code)
        return response
    monkeypatch.setattr(requests, "get", get_response)
    runner = CliRunner()
    result = runner.invoke(download_helmfile,
                           args=["--chart-name", chart_name, "--chart-version", chart_version,
                                 "--chart-repo", chart_repo])
    assert result.exit_code == 1
    assert f"Status: HTTPError - Error Code {status_code}" in caplog.text


def test_download_helmfile_timeout_error(monkeypatch, caplog):
    """Test download_helm handling timeout error."""
    chart_name = "eric-eo-helmfile"
    chart_version = "1.0.0"
    chart_repo = "https://my/artifactory"
    username = "me"
    password = "admin123"
    timeout_in_s = 600

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(username, password), timeout=timeout_in_s):
        response = MockResponse(timeout=True)
        return response
    monkeypatch.setattr(requests, "get", get_response)
    runner = CliRunner()
    result = runner.invoke(download_helmfile,
                           args=["--chart-name", chart_name, "--chart-version", chart_version,
                                 "--chart-repo", chart_repo])
    assert 'Download of the Helmfile failed with the following error' in caplog.text
    assert "Request timed out" in caplog.text
    assert result.exit_code == 1


def test_download_helmfile_redirect_error(monkeypatch, caplog):
    """Test download_helmfile handling TooManyRedircets error."""
    chart_name = "eric-eo-helmfile"
    chart_version = "1.0.0"
    chart_repo = "https://my/artifactory"
    username = "me"
    password = "admin123"
    timeout_in_s = 600

    # pylint: disable=unused-argument
    def get_response(url, auth=HTTPBasicAuth(username, password), timeout=timeout_in_s):
        response = MockResponse(redirects=True)
        return response
    monkeypatch.setattr(requests, "get", get_response)
    runner = CliRunner()
    result = runner.invoke(download_helmfile,
                           args=["--chart-name", chart_name, "--chart-version", chart_version,
                                 "--chart-repo", chart_repo])
    assert 'Download of the Helmfile failed with the following error' in caplog.text
    assert "Too Many Redirects" in caplog.text
    assert result.exit_code == 1
    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
