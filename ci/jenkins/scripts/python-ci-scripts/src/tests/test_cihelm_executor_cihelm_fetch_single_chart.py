"""Test for CI Helm Executor for CIHelm Fetch Single Chart"""
import os

from unittest import mock
import pytest

from click.testing import CliRunner
from lib import cmd_common
from bin.cihelm_executor import cihelm_fetch_single_chart

USERNAME = "username"
PASSWORD = "password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No chart name
    ("--chart-version 1.0.1 --chart-repo url --username joe --password pass",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No chart version
    ("--chart-name chart --chart-repo url --username joe --password pass",
     {'output': "Error: Missing option \"--chart-version\""}),
    # No chart repo
    ("--chart-name chart --chart-version 1.0.1 --username joe --password pass",
     {'output': "Error: Missing option \"--chart-repo\""}),
    # No username
    ("--chart-name chart --chart-version 1.0.1 --chart-repo url --password pass",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--chart-name chart --chart-version 1.0.1 --chart-repo url --username joe",
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
def test_helm_lint_bad_args(test_cli_args, expected):
    """Test argument handling for cihelm_executor.cihelm_fetch_single_chart"""
    runner = CliRunner()
    result = runner.invoke(cihelm_fetch_single_chart, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_cihelm_fetch_single_chart_success(monkeypatch, caplog):
    """Test cihelm_fetch_single_chart package functionality on success"""
    chart_name = "eric-oss-oran-support"
    chart_version = "0.128.0"
    chart_repo = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(cihelm_fetch_single_chart, args=[
        "--chart-name", chart_name,
        "--chart-version", chart_version,
        "--chart-repo", chart_repo])
    assert result.exit_code == 0
    assert "Creating netrc file" in caplog.text
    assert "cihelm fetch for " + chart_name + "-" + chart_version + " completed successfully" in caplog.text


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_cihelm_fetch_single_chart_failure(monkeypatch, caplog):
    """Test cihelm_fetch_single_chart package functionality on failure"""
    chart_name = "eric-oss-oran-support"
    chart_version = "0.128.0"
    chart_repo = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(cihelm_fetch_single_chart, args=[
        "--chart-name", chart_name,
        "--chart-version", chart_version,
        "--chart-repo", chart_repo])
    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text
    assert ("cihelm fetch update for " + chart_name + "-" + chart_version +
            " failed with the following error" in caplog.text)
