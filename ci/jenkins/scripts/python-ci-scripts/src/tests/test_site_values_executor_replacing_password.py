"""Test for site values executor replacing_password"""
import os
import pytest
import oyaml as yaml
from click.testing import CliRunner

from bin.site_values_executor import replacing_password


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state-values-file
    ('',
     {'output': "Error: Missing option \"--state-values-file\"."}),
    # Verbosity not an integer
    ('-v x',
     {'output': 'x is not a valid integer'}),
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
def test_replacing_password_invalid_args(test_cli_args, expected):
    """Test for Obfuscating Functional Password in state_values_file when arguments are invalid."""
    runner = CliRunner()
    result = runner.invoke(replacing_password, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_replacing_password_invalid_path(resource_path_root):
    """Test for Obfuscating Functional Password in state_values_file when state_values_file is an invalid path."""
    state_values_file = os.path.join(resource_path_root, 'fake_test_values.yaml')
    runner = CliRunner()
    result = runner.invoke(replacing_password, args=["--state-values-file", state_values_file])
    assert result.exit_code == 1


def test_replacing_password_success(resource_path_root, caplog):
    """Test for Obfuscating Functional Password in state_values_file successfully."""
    state_values_file = os.path.join(resource_path_root, 'test_values.yaml')
    runner = CliRunner()
    result = runner.invoke(replacing_password, args=["--state-values-file", state_values_file])
    assert "Parsed yaml file" in caplog.text
    assert result.exit_code == 0
    with open(state_values_file, 'r', encoding="utf-8") as stream:
        parsed_yaml = yaml.safe_load(stream)
    assert parsed_yaml['global']['registry']['password'] == '******'


def test_replacing_password_failed_for_global_registry_password_not_existing(resource_path_root, caplog):
    """Test for Obfuscating Functional Password in state_values_file failed."""
    state_values_file = os.path.join(resource_path_root, 'test_values_no_registry_password.yaml')
    runner = CliRunner()
    result = runner.invoke(replacing_password, args=["--state-values-file", state_values_file])
    assert "No registry password to obfuscate" in caplog.text
    assert result.exit_code == 0
