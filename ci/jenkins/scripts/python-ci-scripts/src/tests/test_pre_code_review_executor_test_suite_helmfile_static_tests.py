"""Test for script executor check_for_existing_csar"""
import os
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import helmfile_static_tests

HELMFILE = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/eric-eiae-helmfile"
TEST_VALUES_FILE = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/test_values.yaml"
SPECIFIC_SKIP = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/specific_skip_list.json"
COMMON_SKIP = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/common_skip_list.json"
CHECK_SPECIFIC_CONTENT = "/ci-scripts/tests/testresources/helmfile_static_tests_testing/check_specific_content.json"
USERNAME = "username"
PASSWORD = "password"


# flake8: noqa: E501
# pylint: disable=line-too-long
@pytest.mark.parametrize("test_cli_args, expected", [
    # No common-skip-files
    ("--check-specific-content path --state-values-file site-values.yaml --helmfile-full-path path --specific-skip-file path --username joe --password bloggs",
     {'output': "Error: Missing option \"--common-skip-file\""}),
    # No specific-skip-files
    ("--check-specific-content path --state-values-file site-values.yaml --helmfile-full-path path --common-skip-file path --username joe --password bloggs",
     {'output': "Error: Missing option \"--specific-skip-file\""}),
    # No helmfile-full-path
    ("--check-specific-content path --state-values-file site-values.yaml --common-skip-file path --specific-skip-file path --username joe --password bloggs",
     {'output': "Error: Missing option \"--helmfile-full-path\""}),
    # No state-values-file
    ("--check-specific-content path --helmfile-full-path path --common-skip-file path --specific-skip-file path --username joe --password bloggs",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No check replica count path
    ("--state-values-file site-values.yaml --helmfile-full-path path --common-skip-file path --specific-skip-file path --username joe --password bloggs",
     {'output': "Error: Missing option \"--check-specific-content\""}),
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
def test_helmfile_static_tests_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.helmfile_static_tests."""
    runner = CliRunner()
    result = runner.invoke(helmfile_static_tests, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_helmfile_static_tests_success(monkeypatch, caplog):
    """Test get successful static tests."""
    state_values_file = TEST_VALUES_FILE
    helmfile_full_path = HELMFILE
    specific_skip_file = SPECIFIC_SKIP
    common_skip_file = COMMON_SKIP
    check_specific_content = CHECK_SPECIFIC_CONTENT
    test_folder = "/test-files"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(helmfile_static_tests, args=[
        "--state-values-file", state_values_file,
        "--helmfile-full-path", helmfile_full_path,
        "--specific-skip-file", specific_skip_file,
        "--common-skip-file", common_skip_file,
        "--check-specific-content", check_specific_content,
        "--username", USERNAME,
        "--password", PASSWORD])

    assert result.exit_code == 0
    assert os.path.exists(os.path.join(test_folder, "skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "common_skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "helmfile")) is True
    assert os.path.exists(os.path.join(test_folder, "site_values.yaml")) is True
    assert os.path.exists(os.path.join(test_folder, "check_specific_content.json")) is True
    assert "Execution completed successfully" in caplog.text

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']


# pylint: disable=too-many-locals
def test_helmfile_static_tests_error(monkeypatch, caplog):
    """Test get failed static tests."""
    state_values_file = TEST_VALUES_FILE
    helmfile_full_path = HELMFILE
    specific_skip_file = SPECIFIC_SKIP
    common_skip_file = COMMON_SKIP
    check_specific_content = CHECK_SPECIFIC_CONTENT
    test_folder = "/test-files"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(helmfile_static_tests, args=[
        "--state-values-file", state_values_file,
        "--helmfile-full-path", helmfile_full_path,
        "--specific-skip-file", specific_skip_file,
        "--common-skip-file", common_skip_file,
        "--check-specific-content", check_specific_content,
        "--username", USERNAME,
        "--password", PASSWORD])

    assert result.exit_code == 1
    assert os.path.exists(os.path.join(test_folder, "skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "common_skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "helmfile")) is True
    assert os.path.exists(os.path.join(test_folder, "site_values.yaml")) is True
    assert os.path.exists(os.path.join(test_folder, "check_specific_content.json")) is True
    assert "Execution failed with following errors" in caplog.text

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
