"""Test for script executor schema tests"""
import os
import subprocess
import pytest
from click.testing import CliRunner
from bin.pre_code_review_executor import schema_tests

CHART_PATH = "./chart"
PATH_TO_FILES = "schematests/"
POSTIVIE_FILES_YAML_PATH = "schematests/positive/file.yaml"
NEGATIVE_FILES_YAML_PATH = "schematests/negative/file.yaml"
NEGATIVE_FILES_TEXT_PATH = "schematests/negative/file_expected_errors.txt"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No chart-full-path
    ("--directory-path \"path\"",
     {'output': "Error: Missing option \"--chart-full-path\""}),
    # No positive-and-negative-schema-files-full-path
    ("--chart-full-path \"chart.tgz\"",
     {'output': "Error: Missing option \"--directory-path\""}),
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
def test_static_tests_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.static_tests."""
    runner = CliRunner()
    result = runner.invoke(schema_tests, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_schema_tests_success(caplog, monkeypatch):
    """Test for successful schema tests"""
    os.makedirs(os.path.dirname(POSTIVIE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_TEXT_PATH), exist_ok=True)
    with open(POSTIVIE_FILES_YAML_PATH, "w", encoding="utf-8") as positive_yaml_file, \
            open(NEGATIVE_FILES_YAML_PATH, "w", encoding="utf-8") as negative_yaml_file, \
            open(NEGATIVE_FILES_TEXT_PATH, "w", encoding="utf-8") as negative_text_file:
        positive_yaml_file.writelines("key: value")
        negative_yaml_file.writelines("key: value")
        negative_text_file.writelines("There is an error with this template")

    # pylint: disable=unused-argument
    def mock_helm_template(command, **subprocess_run_options):
        return_code = 0
        if "/negative/" in command[3]:
            return_code = 1
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout='There is an error with this template'.encode('utf-8'),
                                           returncode=return_code)

    monkeypatch.setattr(subprocess, "run", mock_helm_template)

    runner = CliRunner()
    result = runner.invoke(schema_tests, args=[
        "--chart-full-path", CHART_PATH,
        "--directory-path", PATH_TO_FILES])

    assert "Testing file_expected_errors.txt (Expected Failure Output file file.yaml) pass" in caplog.text
    assert "Testing file.yaml (Expected Success) pass" in caplog.text
    assert "Number of passes - 2 Number of fails - 0" in caplog.text
    assert result.exit_code == 0


def test_schema_tests_fail_from_positive_file(caplog, monkeypatch):
    """Test for successful schema tests"""
    os.makedirs(os.path.dirname(POSTIVIE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_TEXT_PATH), exist_ok=True)
    with open(POSTIVIE_FILES_YAML_PATH, "w", encoding="utf-8") as positive_yaml_file, \
            open(NEGATIVE_FILES_YAML_PATH, "w", encoding="utf-8") as negative_yaml_file, \
            open(NEGATIVE_FILES_TEXT_PATH, "w", encoding="utf-8") as negative_text_file:
        positive_yaml_file.writelines("key: value")
        negative_yaml_file.writelines("key: value")
        negative_text_file.writelines("There is an error with this template")

    # pylint: disable=unused-argument
    def mock_helm_template(command, **subprocess_run_options):
        return_code = 1
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout='There is an error with this template'.encode('utf-8'),
                                           returncode=return_code)

    monkeypatch.setattr(subprocess, "run", mock_helm_template)

    runner = CliRunner()
    result = runner.invoke(schema_tests, args=[
        "--chart-full-path", CHART_PATH,
        "--directory-path", PATH_TO_FILES])

    assert "Testing file_expected_errors.txt (Expected Failure Output file file.yaml) pass" in caplog.text
    assert "fail (The output from file.yaml did not pass)" in caplog.text
    assert "Number of passes - 1 Number of fails - 1" in caplog.text
    assert "There were failures among the schema files" in caplog.text
    assert result.exit_code == 1


def test_schema_tests_fail_from_negative_file_successful_template(caplog, monkeypatch):
    """Test for successful schema tests"""
    os.makedirs(os.path.dirname(POSTIVIE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_TEXT_PATH), exist_ok=True)
    with open(POSTIVIE_FILES_YAML_PATH, "w", encoding="utf-8") as positive_yaml_file, \
            open(NEGATIVE_FILES_YAML_PATH, "w", encoding="utf-8") as negative_yaml_file, \
            open(NEGATIVE_FILES_TEXT_PATH, "w", encoding="utf-8") as negative_text_file:
        positive_yaml_file.writelines("key: value")
        negative_yaml_file.writelines("key: value")
        negative_text_file.writelines("There is an error with this template")

    # pylint: disable=unused-argument
    def mock_helm_template(command, **subprocess_run_options):
        return_code = 0
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout='There is an error with this template'.encode('utf-8'),
                                           returncode=return_code)

    monkeypatch.setattr(subprocess, "run", mock_helm_template)

    runner = CliRunner()
    result = runner.invoke(schema_tests, args=[
        "--chart-full-path", CHART_PATH,
        "--directory-path", PATH_TO_FILES])

    assert "Fail (the helm command was expected to fail but it didn't with file.yaml)" in caplog.text
    assert "Testing file.yaml (Expected Success) pass" in caplog.text
    assert "Number of passes - 1 Number of fails - 1" in caplog.text
    assert "There were failures among the schema files" in caplog.text
    assert result.exit_code == 1


def test_schema_tests_fail_from_negative_file_incorrect_output(caplog, monkeypatch):
    """Test for successful schema tests"""
    os.makedirs(os.path.dirname(POSTIVIE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_YAML_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(NEGATIVE_FILES_TEXT_PATH), exist_ok=True)
    with open(POSTIVIE_FILES_YAML_PATH, "w", encoding="utf-8") as positive_yaml_file, \
            open(NEGATIVE_FILES_YAML_PATH, "w", encoding="utf-8") as negative_yaml_file, \
            open(NEGATIVE_FILES_TEXT_PATH, "w", encoding="utf-8") as negative_text_file:
        positive_yaml_file.writelines("key: value")
        negative_yaml_file.writelines("key: value")
        negative_text_file.writelines("There is an error with this template")

    # pylint: disable=unused-argument
    def mock_helm_template(command, **subprocess_run_options):
        return_code = 0
        if "/negative/" in command[3]:
            return_code = 1
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout='There is a different error with this template'.encode('utf-8'),
                                           returncode=return_code)

    monkeypatch.setattr(subprocess, "run", mock_helm_template)

    runner = CliRunner()
    result = runner.invoke(schema_tests, args=[
        "--chart-full-path", CHART_PATH,
        "--directory-path", PATH_TO_FILES])

    assert "fail (the output from from file_expected_errors.txt using file.yaml did not match the helm template)" \
           in caplog.text
    assert "Testing file.yaml (Expected Success) pass" in caplog.text
    assert "Number of passes - 1 Number of fails - 1" in caplog.text
    assert "There were failures among the schema files" in caplog.text
    assert result.exit_code == 1
