"""Test for script executor check_for_existing_csar"""
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import validate_chart_against_schema_file


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --directory-path
    ("--chart-full-path path",
     {'output': "Error: Missing option \"--directory-path\""}),
    # No ---chart-full-path
    ("--directory-path path",
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
def test_validate_chart_against_schema_file_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.static_tests."""
    runner = CliRunner()
    result = runner.invoke(validate_chart_against_schema_file, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_validate_chart_against_schema_file_success(monkeypatch, caplog):
    """Test Validate Chart Against site values file"""

    chart_full_path = "eric-oss-common-base-0.4.2-11.tgz"
    directory_path = "testsuite/helm-chart-validator"
    search_string = "yaml"
    ignore_stings = "global,ticketmaster"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(validate_chart_against_schema_file, args=[
        "--chart-full-path", chart_full_path,
        "--directory-path", directory_path,
        "--search-string", search_string,
        "--ignore-strings", ignore_stings])
    assert result.exit_code == 0
    assert "Execution completed successfully" in caplog.text


# pylint: disable=too-many-locals
def test_validate_chart_against_schema_file_error(monkeypatch, caplog):
    """Test Validate Chart Against site values file"""

    chart_full_path = "eric-oss-common-base-0.4.2-11.tgz"
    directory_path = "/ci-scripts/tests/testresources"
    search_string = "yaml"
    ignore_stings = "None"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(validate_chart_against_schema_file, args=[
        "--chart-full-path", chart_full_path,
        "--directory-path", directory_path,
        "--search-string", search_string,
        "--ignore-strings", ignore_stings])
    assert result.exit_code == 1
    assert "See failure(s) above" in caplog.text
