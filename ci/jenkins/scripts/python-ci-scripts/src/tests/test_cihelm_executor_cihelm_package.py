"""Test for CI Helm Executor for Helm Lint"""
import os

from unittest import mock
import pytest

from click.testing import CliRunner
from lib import cmd_common
from bin.cihelm_executor import cihelm_package

USERNAME = "username"
PASSWORD = "password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --state-values-file
    ("--path-to-chart path --version 0.0.0 --username joe --password blogs",
     {'output': "Error: Missing option \"--directory-path\""}),
    # No --chart-full-path
    ("--path-to-chart path --directory-path path --username joe --password blogs",
     {'output': "Error: Missing option \"--version\""}),
    # No --chart-full-path
    ("--version 0.0.0 --directory-path path --username joe --password blogs",
     {'output': "Error: Missing option \"--path-to-chart\""}),
    # No --username
    ("--path-to-chart path --version 0.0.0 --directory-path path --password blogs",
     {'output': "Error: Missing option \"--username\""}),
    # No --password
    ("--path-to-chart path --version 0.0.0 --directory-path path --username joe",
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
    """Test argument handling for cihelm_executor.cihelm_package"""
    runner = CliRunner()
    result = runner.invoke(cihelm_package, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_cihelm_package_success(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart"
    destination = "."
    version = "0.0.0"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(cihelm_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version])
    assert result.exit_code == 0
    assert "cihelm package completed successfully" in caplog.text


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_cihelm_package_success_with_path_to_chart_stripped(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart/"
    destination = "."
    version = "0.0.0"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(cihelm_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version])
    assert result.exit_code == 0
    assert "cihelm package completed successfully" in caplog.text


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_cihelm_package_error(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart"
    destination = "."
    version = "0.0.0"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(cihelm_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version])
    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text
