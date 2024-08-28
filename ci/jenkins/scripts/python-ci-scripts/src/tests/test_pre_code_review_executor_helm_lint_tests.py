"""Test for Pre Code Review Executor for Helm Lint"""
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import helm_lint


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --state-values-file
    ("--chart-full-path path",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No --chart-full-path
    ("--state-values-file path",
     {'output': "Error: Missing option \"--chart-full-path\""}),
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
    result = runner.invoke(helm_lint, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_helm_lint_success(monkeypatch, caplog):
    """Test helm lint on chart and site value"""

    chart_full_path = "./eric-oss-common-base"
    directory_path = "testsuite/helm-chart-validator/site_value.yaml"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(helm_lint, args=[
        "--chart-full-path", chart_full_path,
        "--state-values-file", directory_path])
    assert result.exit_code == 0
    assert "Execution completed successfully" in caplog.text


# pylint: disable=too-many-locals
def test_helm_lint_error(monkeypatch, caplog):
    """Test helm lint failure on chart and site values"""

    chart_full_path = "./eric-oss-common-base"
    directory_path = "testsuite/helm-chart-validator/site_value.yaml"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(helm_lint, args=[
        "--chart-full-path", chart_full_path,
        "--state-values-file", directory_path])
    assert result.exit_code == 1
    assert "See failure(s) above" in caplog.text
