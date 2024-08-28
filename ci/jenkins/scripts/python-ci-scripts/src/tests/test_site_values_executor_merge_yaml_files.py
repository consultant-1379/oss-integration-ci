"""Test for site_values_executor.py merge-yaml-files"""
import os
import oyaml as yaml
import pytest
from click.testing import CliRunner

from lib import utils
from bin.site_values_executor import merge_yaml_files


SITEVALUES_OVERRIDE_NEW_KEY = {
    'newKey': {
        'newValue': True
    }
}

SITEVALUES_OVERRIDE_SERVICE_MESH = {
    'global': {
        'serviceMesh': {
            'enabled': True
        }
    }
}

SITEVALUES_OVERRIDE_TAGS = {
    'tags': {
        'eoPf': True
    }
}

SITEVALUES_OVERRIDE_LIST = ['one', 'two', 'three']


@pytest.fixture(name="site_values_path")
def site_values_template(tmp_path, resource_path_root):
    """Fixture to generate path to sitevalues template"""
    def _get_template_file():
        tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
        utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
        return os.path.join(tmp_path, "eric-eo-helmfile", "templates", "site-values-template.yaml")
    return _get_template_file


@pytest.fixture(name="site_values_override_path")
def site_values_override_file(tmp_path):
    """Fixture to create and return path to override site values file"""
    def _get_override_file(content, filename="site-values-override.yaml"):
        override_values_file = os.path.join(tmp_path, filename)
        with open(override_values_file, "w", encoding="utf-8") as over_file:
            yaml.dump(content, over_file)
        return override_values_file
    return _get_override_file


@pytest.mark.parametrize("test_cli_args, expected", [
    # No base path
    ("--path-override-yaml /override --path-output-yaml /out --check-values-only true",
     {'output': "Error: Missing option \"--path-base-yaml\""}),
    # No override
    ("--path-base-yaml /base  --path-output-yaml /out --check-values-only true",
     {'output': "Error: Missing option \"--path-override-yaml\""}),
    # No ouput file
    ("--path-base-yaml /base --path-override-yaml /override --check-values-only true",
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
def test_merge_yaml_files_bad_args(test_cli_args, expected):
    """Test argument handling in site_values_exector.merge_yaml_files"""
    runner = CliRunner()
    result = runner.invoke(merge_yaml_files, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_merge_yaml_files_success(site_values_path, site_values_override_path, tmp_path):
    """Test successful merge of site values yaml"""
    site_values_file = site_values_path()
    override_values_file = site_values_override_path(SITEVALUES_OVERRIDE_SERVICE_MESH)
    output_yaml_file = os.path.join(tmp_path, "site_values_merged.yaml")
    with open(site_values_file, "r", encoding="utf-8") as site_values_data:
        input_yaml = yaml.safe_load(site_values_data)
        assert input_yaml["global"]["serviceMesh"]["enabled"] is False
    runner = CliRunner()
    result = runner.invoke(merge_yaml_files, args=[
                           "--path-base-yaml", site_values_file,
                           "--path-override-yaml", override_values_file,
                           "--path-output-yaml", output_yaml_file])
    assert result.exit_code == 0
    assert os.path.exists(output_yaml_file) is True
    with open(output_yaml_file, "r", encoding="utf-8") as output_data:
        output_yaml = yaml.safe_load(output_data)
        assert output_yaml["global"]["serviceMesh"]["enabled"] is True


def test_merge_yaml_files_checkvalues_true(site_values_path, site_values_override_path, tmp_path, caplog):
    """Test to see handling of key not in base yaml"""
    site_values_file = site_values_path()
    override_values_file = site_values_override_path(SITEVALUES_OVERRIDE_NEW_KEY)
    output_yaml_file = os.path.join(tmp_path, "site_values_merged.yaml")
    runner = CliRunner()
    result = runner.invoke(merge_yaml_files, args=[
                           "--path-base-yaml", site_values_file,
                           "--path-override-yaml", override_values_file,
                           "--path-output-yaml", output_yaml_file,
                           "--check-values-only", "true"])
    assert result.exit_code == 1
    assert "Exiting deployment due to missing variables in the CI site values" in caplog.text


def test_merge_yaml_files_checkvalues_false(site_values_path, site_values_override_path, tmp_path):
    """Test to see if new key is ignored"""
    site_values_file = site_values_path()
    override_values_file = site_values_override_path(SITEVALUES_OVERRIDE_NEW_KEY)
    output_yaml_file = os.path.join(tmp_path, "site_values_merged.yaml")
    runner = CliRunner()
    result = runner.invoke(merge_yaml_files, args=[
                           "--path-base-yaml", site_values_file,
                           "--path-override-yaml", override_values_file,
                           "--path-output-yaml", output_yaml_file,
                           "--check-values-only", "false"])
    assert result.exit_code == 0
    with open(output_yaml_file, "r", encoding="utf-8") as output_data:
        output_yaml = yaml.safe_load(output_data)
        assert output_yaml["newKey"]["newValue"] is True


def test_merge_yaml_files_different_format_error(site_values_path, site_values_override_path, tmp_path, caplog):
    """Test merging yaml in wrong format"""
    site_values_file = site_values_path()
    output_yaml_file = os.path.join(tmp_path, "site_values_merged.yaml")
    override_values_file = site_values_override_path(SITEVALUES_OVERRIDE_LIST)
    runner = CliRunner()
    result = runner.invoke(merge_yaml_files, args=[
                           "--path-base-yaml", site_values_file,
                           "--path-override-yaml", override_values_file,
                           "--path-output-yaml", output_yaml_file,
                           "--check-values-only", "false"])
    assert result.exit_code == 1
    assert "'base.yaml' and 'override.yaml' have different structure" in caplog.text


def test_merge_yaml_files_multiple_overrides(site_values_path, site_values_override_path, tmp_path):
    """Test handling of override yaml as a list"""
    site_values_file = site_values_path()
    output_yaml_file = os.path.join(tmp_path, "site_values_merged.yaml")
    override_yaml_one = site_values_override_path(SITEVALUES_OVERRIDE_SERVICE_MESH, "override-one.yaml")
    override_yaml_two = site_values_override_path(SITEVALUES_OVERRIDE_TAGS, "override-two.yaml")
    runner = CliRunner()
    result = runner.invoke(merge_yaml_files, args=[
                           "--path-base-yaml", site_values_file,
                           "--path-override-yaml", f"{override_yaml_one},{override_yaml_two}",
                           "--path-output-yaml", output_yaml_file,
                           "--check-values-only", "false"])
    assert result.exit_code == 0
    with open(output_yaml_file, "r", encoding="utf-8") as output_data:
        output_yaml = yaml.safe_load(output_data)
        assert output_yaml["global"]["serviceMesh"]["enabled"] is True
        assert output_yaml["tags"]["eoPf"] is True
