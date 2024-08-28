"""Test for utils executor convert_yaml_to_json"""
import os.path

import pytest
from click.testing import CliRunner

from bin.utils_executor import convert_yaml_to_json


VALID_YAML_FILE = "test_values_no_registry_password.yaml"
JSON_OUTPUT = "test_values.json"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No yaml file
    ("--yaml-file /some/yaml/file",
     {'output': "Error: Missing option \"--json-file\""}),
    ("--json-file /some/json/file",
     {'output': "Error: Missing option \"--yaml-file\""}),
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
def test_convert_yaml_to_json_bad_arguments(test_cli_args, expected):
    """Test convert_yaml_to_json with bad arguments."""
    runner = CliRunner()
    result = runner.invoke(convert_yaml_to_json, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_convert_yaml_to_json_success(resource_path_root):
    """Test script executor convert_yaml_to_json with positive result."""
    expected_output = '{"global": {"registry": {"user": "123"}}}'

    yaml_file = os.path.join(resource_path_root, VALID_YAML_FILE)
    json_file = os.path.join(resource_path_root, JSON_OUTPUT)

    runner = CliRunner()
    result = runner.invoke(convert_yaml_to_json,
                           args=["--yaml-file", yaml_file, "--json-file", json_file])
    assert result.exit_code == 0
    with open(json_file, 'r', encoding="utf-8") as json:
        data = json.read()
    os.remove(json_file)
    assert expected_output == data


def test_convert_yaml_to_json_no_such_yaml_file(resource_path_root, caplog):
    """Test script executor convert_yaml_to_json with no such yaml file result."""
    expected_output = 'No such file or directory'

    yaml_file = os.path.join(resource_path_root, "no_such_yaml_file.yaml")
    json_file = os.path.join(resource_path_root, JSON_OUTPUT)

    runner = CliRunner()
    result = runner.invoke(convert_yaml_to_json,
                           args=["--yaml-file", yaml_file, "--json-file", json_file])
    assert result.exit_code != 0
    assert expected_output in caplog.text
