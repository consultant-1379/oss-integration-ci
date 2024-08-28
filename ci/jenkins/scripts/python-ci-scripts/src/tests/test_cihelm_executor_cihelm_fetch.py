"""Test for CI Helm Executor for CIHelm Fetch"""
import os

from unittest import mock
import pytest

from click.testing import CliRunner
from lib import cmd_common
from bin.cihelm_executor import cihelm_fetch

USERNAME = "username"
PASSWORD = "password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --path-to-helmfile boolean
    ("--clean-up False",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
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
    """Test argument handling for cihelm_executor.cihelm_fetch"""
    runner = CliRunner()
    result = runner.invoke(cihelm_fetch, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
@mock.patch.dict(os.environ, {"GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_cihelm_fetch_failure(monkeypatch, caplog):
    """Test cihelm_fetch package functionality on failure"""
    path_to_helmfile = "/internal/ci-helmfile/eric-ci-helmfile/"
    clean_up = True
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(cihelm_fetch, args=[
        "--path-to-helmfile", path_to_helmfile,
        "--clean-up", clean_up])
    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text
