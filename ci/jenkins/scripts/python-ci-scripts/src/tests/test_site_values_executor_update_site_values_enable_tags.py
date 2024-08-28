"""Test for site_values_executor.update_site_values_file_enable_tags."""
import os
import pytest
import oyaml as yaml
from click.testing import CliRunner

from bin.site_values_executor import update_site_values_file_enable_tags
from lib import utils


@pytest.fixture(name="state_values_path")
def get_state_values_path(resource_path_root):
    """Fixture to generate path to the helmfile"""
    def _state_values_path():
        tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
        utils.extract_tar_file(tar_file=tarfile, directory=os.getcwd())
        return os.path.join(os.getcwd(), "eric-eo-helmfile", "templates", "site-values-template.yaml")
    return _state_values_path


@pytest.mark.parametrize("test_cli_args, expected", [
    # No base path
    ("--output-state-values-file /out/file --deployment-tags tags",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No override
    ("--state-values-file /stat-values --deployment-tags tags",
     {'output': "Error: Missing option \"--output-state-values-file\""}),
    # No ouput file
    ("--state-values-file /stat-values --output-state-values-file /out/file",
     {'output': "Error: Missing option \"--deployment-tags\""}),
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
def test_create_site_values_with_tags_bad_args(test_cli_args, expected):
    """Test arg handling for update_site_values_file_enable_tags"""
    runner = CliRunner()
    result = runner.invoke(update_site_values_file_enable_tags, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_create_site_values_with_tags_success(state_values_path, tmp_path):
    """Test for successful update to site-values file."""
    state_values_file = state_values_path()
    out_state_values_file = os.path.join(tmp_path, "state-values.yaml")
    tags = "eoEvnfm eoSo eoVmvnfm"
    optional_tags_list = ""
    runner = CliRunner()
    result = runner.invoke(update_site_values_file_enable_tags, args=[
                           "--state-values-file", state_values_file,
                           "--output-state-values-file", out_state_values_file,
                           "--deployment-tags", tags,
                           "--optional-tags", optional_tags_list])
    assert os.path.exists(out_state_values_file) is True
    assert result.exit_code == 0
    with open(out_state_values_file, "r", encoding='utf-8') as outfile:
        outyaml = yaml.safe_load(outfile)
    assert outyaml['tags']['eoEvnfm'] is True
    assert outyaml['tags']['eoSo'] is True
    assert outyaml['tags']['eoVmvnfm'] is True
    assert outyaml['tags']['eoCm'] is False


def test_output_not_writable(state_values_path, caplog):
    """Test for open file handling"""
    state_values_file = state_values_path()
    out_state_values_file = "/not/on/my/sytem.yaml"
    tags = "eoEvnfm eoSo eoVmvnfm"
    optional_tags_list = ""
    runner = CliRunner()
    result = runner.invoke(update_site_values_file_enable_tags, args=[
                           "--state-values-file", state_values_file,
                           "--output-state-values-file", out_state_values_file,
                           "--deployment-tags", tags,
                           "--optional-tags", optional_tags_list])
    assert result.exit_code == 1
    assert "Create Updated Site-values File failed with the following error" in caplog.text
    assert f"No such file or directory: '{out_state_values_file}'" in caplog.text


def test_state_values_not_readable(caplog, tmp_path):
    """Test handling of bad input file"""
    state_values_file = "/not/a/real/site-values.yaml"
    out_state_values_file = os.path.join(tmp_path, "state-values.yaml")
    tags = "eoEvnfm eoSo eoVmvnfm"
    optional_tags_list = ""
    runner = CliRunner()
    result = runner.invoke(update_site_values_file_enable_tags, args=[
                           "--state-values-file", state_values_file,
                           "--output-state-values-file", out_state_values_file,
                           "--deployment-tags", tags,
                           "--optional-tags", optional_tags_list])
    assert result.exit_code == 1
    assert "Create Updated Site-values File failed with the following error" in caplog.text
    assert f"No such file or directory: '{state_values_file}'" in caplog.text


def test_state_values_no_tags(tmp_path):
    """Test handling of site-values with no tags"""
    in_values = {
        "global": {
            "createClusterRoles": True
        },
        "eric-cloud-native-base": {
            "eric-ctrl-bro": {
                "persistence": {
                    "persistentVolumeClaim": {
                        "size": "20Gi"
                    }
                }
            }
        }
    }
    state_values_file = os.path.join(tmp_path, "site-values.yaml")
    out_state_values_file = os.path.join(tmp_path, "site-values-updated.yaml")
    tags = "eoEvnfm eoSo eoVmvnfm"
    optional_tags_list = ""
    with open(state_values_file, 'w', encoding='utf-8') as in_yaml:
        yaml.safe_dump(in_values, in_yaml, default_flow_style=False)
    runner = CliRunner()
    result = runner.invoke(update_site_values_file_enable_tags, args=[
                           "--state-values-file", state_values_file,
                           "--output-state-values-file", out_state_values_file,
                           "--deployment-tags", tags,
                           "--optional-tags", optional_tags_list])
    assert result.exit_code == 0
    with open(out_state_values_file, 'r', encoding='utf-8') as out_yaml:
        content = yaml.safe_load(out_yaml)
    assert 'tags' not in content
