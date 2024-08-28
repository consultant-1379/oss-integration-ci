"""Test for site_values_executor.create_site_values_file."""
import os
import pytest
import oyaml as yaml
from click.testing import CliRunner

from bin.site_values_executor import create_site_values_file


@pytest.mark.parametrize("test_cli_args, expected", [
    # No key/value list
    ("--path-output-yaml /out",
     {'output': "Error: Missing option \"--optional-key-value-list\""}),
    # No output file
    ("--optional-key-value-list list",
     {'output': "Error: Missing option \"--path-output-yaml\""}),
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
def test_create_site_values_file_bad_args(test_cli_args, expected):
    """Test arg handling for create_site_values_file."""
    runner = CliRunner()
    result = runner.invoke(create_site_values_file, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_create_site_values_file_success(tmp_path):
    """Test for successful creation of site-values file."""
    optional_key_value_list = ('eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,'
                               'eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false,'
                               'global.hosts.gm=host.hart102.ericsson.se')
    out_state_values_file = os.path.join(tmp_path, "state-values.yaml")
    runner = CliRunner()

    result = runner.invoke(create_site_values_file, args=[
                           "--optional-key-value-list", optional_key_value_list,
                           "--path-output-yaml", out_state_values_file])
    assert os.path.exists(out_state_values_file) is True
    assert result.exit_code == 0
    with open(out_state_values_file, "r", encoding='utf-8') as outfile:
        content = yaml.safe_load(outfile)
    assert content['eric-cloud-native-base']['eric-sec-access-mgmt']['accountManager']['enabled'] is True
    assert content['eric-oss-common-base']['eric-oss-ddc']['autoUpload']['enabled'] is False
    assert content['global']['hosts']['gm'] == 'host.hart102.ericsson.se'


def test_optional_key_value_list_bad_input(tmp_path):
    """Test handling of bad input string with no values"""
    optional_key_value_list = ('eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled,'
                               'eric-oss-common-base.eric-oss-ddc.autoUpload.enabled')
    out_state_values_file = os.path.join(tmp_path, "state-values.yaml")
    runner = CliRunner()
    result = runner.invoke(create_site_values_file, args=[
                            "--optional-key-value-list", optional_key_value_list,
                            "--path-output-yaml", out_state_values_file])
    assert result.exit_code == 0
    with open(out_state_values_file, 'r', encoding='utf-8') as out_yaml:
        content = yaml.safe_load(out_yaml)
    assert (content['eric-cloud-native-base']['eric-sec-access-mgmt']['accountManager']['enabled']
            == 'eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled')
    assert (content['eric-oss-common-base']['eric-oss-ddc']['autoUpload']['enabled']
            == 'eric-oss-common-base.eric-oss-ddc.autoUpload.enabled')


def test_create_site_values_path_output_yaml_invalid_path(tmp_path, caplog):
    """Test for Obfuscating Functional Password in state_values_file when state_values_file is an invalid path."""
    optional_key_value_list = ('eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,'
                               'eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false,'
                               'global.hosts.gm=host.hart102.ericsson.se')
    out_state_values_file = (tmp_path, "\\templates\\state-values.yaml")
    runner = CliRunner()

    result = runner.invoke(create_site_values_file, args=[
        "--optional-key-value-list", optional_key_value_list,
        "--path-output-yaml", out_state_values_file])
    assert "Please refer to the following log" in caplog.text
    assert result.exit_code == 1
