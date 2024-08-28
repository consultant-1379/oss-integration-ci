"""Test for Pre Code Review Executor for Yamllint on Helmfile"""
import os
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import yaml_lint_helmfile


@pytest.mark.parametrize("test_cli_args, expected", [
    # No helmfile full path
    ("--state-values-file path --yamllint-config path --template-output-file-path path --yamllint-log-file path",
     {'output': "Error: Missing option \"--helmfile-full-path\""}),
    # No state values file path
    ("--helmfile-full-path path --yamllint-config path --template-output-file-path path --yamllint-log-file path",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No yamllint config path
    ("--helmfile-full-path path --state-values-file path --template-output-file-path path --yamllint-log-file path",
     {'output': "Error: Missing option \"--yamllint-config\""}),
    # No template output file path
    ("--helmfile-full-path path --state-values-file path --yamllint-config path --yamllint-log-file path",
     {'output': "Error: Missing option \"--template-output-file-path\""}),
    # No template output file path
    ("--helmfile-full-path path --state-values-file path --yamllint-config path --template-output-file-path path",
     {'output': "Error: Missing option \"--yamllint-log-file\""}),
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
def test_yaml_lint_application_chart_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.yaml_lint_helmfile."""
    runner = CliRunner()
    result = runner.invoke(yaml_lint_helmfile, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_yaml_lint_helmfile_success(monkeypatch, caplog):
    """Test Yamllint successfully lint helmfile."""
    state_values_file = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/test_values.yaml"
    helmfile_full_path = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/eric-eiae-helmfile"
    yamllint_config = "/ci-scripts/tests/testresources/yamllint_config.yaml"
    yamllint_log_file = "yamllint_log_file.log"
    template_output_file = "helm_template_output_file.yaml"

    output_folder = "/output"
    template_output_file_path = output_folder + template_output_file
    yamllint_log_file_path = output_folder + yamllint_log_file

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(yaml_lint_helmfile, args=[
        "--state-values-file", state_values_file,
        "--helmfile-full-path", helmfile_full_path,
        "--yamllint-config", yamllint_config,
        "--yamllint-log-file", yamllint_log_file_path,
        "--template-output-file-path", template_output_file_path])
    assert result.exit_code == 0
    assert "Execution completed successfully" in caplog.text


# pylint: disable=too-many-locals
def test_yaml_lint_helmfile_failure(monkeypatch, caplog):
    """Test Yamllint failure when linting helmfile."""
    state_values_file = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/test_values.yaml"
    helmfile_full_path = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/eric-eiae-helmfile"
    yamllint_config = "/ci-scripts/tests/testresources/yamllint_config.yaml"
    yamllint_log_file = "yamllint_log_file.log"
    template_output_file = "helmfile_template_output_file.yaml"

    output_folder = "/output"
    template_output_file_path = output_folder + template_output_file
    yamllint_log_file_path = output_folder + yamllint_log_file

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(yaml_lint_helmfile, args=[
        "--state-values-file", state_values_file,
        "--helmfile-full-path", helmfile_full_path,
        "--yamllint-config", yamllint_config,
        "--yamllint-log-file", yamllint_log_file_path,
        "--template-output-file-path", template_output_file_path])
    assert result.exit_code == 1
    assert "See failure(s) above" in caplog.text
