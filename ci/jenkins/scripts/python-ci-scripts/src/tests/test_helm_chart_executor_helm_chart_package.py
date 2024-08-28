"""Test for Pre Code Review Executor for Helm Lint"""
import os

from unittest import mock
import pytest

from click.testing import CliRunner
from lib import cmd_common
from lib import cihelm
from lib import helm
from bin.helm_chart_executor import helm_chart_package

USERNAME = "gerrit-username"
PASSWORD = "gerrit-password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --path-to-chart
    ("--directory-path /dummy/workspace"
     " --version 1.1.1"
     " --use-dependency-cache false"
     " --dependency-cache-directory /tmp/cache_dir"
     " --gerrit-username joe"
     " --gerrit-password bloggs",
     {'output': "Error: Missing option \"--path-to-chart\""}),
    # No --directory-path
    ("--path-to-chart /dummy/workspace/charts/dummy_chart"
     " --version 1.1.1"
     " --use-dependency-cache false"
     " --dependency-cache-directory /tmp/cache_dir"
     " --gerrit-username joe"
     " --gerrit-password bloggs",
     {'output': "Error: Missing option \"--directory-path\""}),
    # No --version
    ("--path-to-chart /dummy/workspace/charts/dummy_chart"
     " --directory-path /dummy/workspace"
     " --use-dependency-cache false"
     " --dependency-cache-directory /tmp/cache_dir"
     " --gerrit-username joe"
     " --gerrit-password bloggs",
     {'output': "Error: Missing option \"--version\""}),
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
    """Test argument handling for pre_code_review_executor.helm_lint"""
    runner = CliRunner()
    result = runner.invoke(helm_chart_package, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_helm_chart_package_use_cache_true_success(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart/"
    destination = "."
    version = "0.0.0"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def dependency_update(deps, netrc, mask, workspace, chart_cache_directory):
        return "/ci-scripts/tests/testresources/helm"

    monkeypatch.setattr(cihelm,
                        "dependency_update",
                        dependency_update)

    # pylint: disable=unused-argument too-many-arguments
    def package_chart_using_helm(path_to_chart, destination, version):
        return True

    monkeypatch.setattr(helm,
                        "package_chart_using_helm",
                        package_chart_using_helm)

    runner = CliRunner()
    result = runner.invoke(helm_chart_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version,
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD])
    assert result.exit_code == 0
    assert "Helm Chart package completed successfully" in caplog.text

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_helm_chart_package_use_cache_true_error(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart"
    destination = "."
    version = "0.0.0"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def dependency_update(deps, netrc, mask, workspace, chart_cache_directory):
        return "/ci-scripts/tests/testresources/helm"

    monkeypatch.setattr(cihelm,
                        "dependency_update",
                        dependency_update)

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Chart Package using Helm has failed", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(helm_chart_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version,
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD])

    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_helm_chart_package_use_cache_false_success(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart/"
    destination = "."
    version = "0.0.0"
    cache = "false"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def dependency_update(deps, netrc, mask, workspace, chart_cache_directory):
        return "/ci-scripts/tests/testresources/helm"

    monkeypatch.setattr(cihelm,
                        "dependency_update",
                        dependency_update)

    # pylint: disable=unused-argument too-many-arguments
    def package(path_to_chart, netrc, mask, workspace, destination, version):
        return True

    monkeypatch.setattr(cihelm,
                        "package",
                        package)

    runner = CliRunner()
    result = runner.invoke(helm_chart_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version,
        "--use-dependency-cache", cache,
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD])
    assert result.exit_code == 0
    assert "Helm Chart package completed successfully" in caplog.text

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_helm_chart_package_use_cache_false_error(monkeypatch, caplog):
    """Test cihelm package functionality on success"""
    path_to_chart = "/ci-scripts/tests/testresources/helm/chart/ci-helm-chart"
    destination = "."
    version = "0.0.0"
    cache = "false"
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def dependency_update(deps, netrc, mask, workspace, chart_cache_directory):
        return "/ci-scripts/tests/testresources/helm"

    monkeypatch.setattr(cihelm,
                        "dependency_update",
                        dependency_update)

    # pylint: disable=unused-argument too-many-arguments
    def package(path_to_chart, netrc, mask, workspace, destination, version):
        raise Exception('Some exception')

    monkeypatch.setattr(cihelm,
                        "package",
                        package)

    runner = CliRunner()
    result = runner.invoke(helm_chart_package, args=[
        "--path-to-chart", path_to_chart,
        "--directory-path", destination,
        "--version", version,
        "--use-dependency-cache", cache,
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD])

    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
