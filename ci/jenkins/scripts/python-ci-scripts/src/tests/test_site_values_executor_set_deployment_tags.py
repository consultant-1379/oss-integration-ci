"""Test for site values executor set_deployment_tags."""
import os
import shutil
import oyaml as yaml
import pytest
from click.testing import CliRunner

from bin.site_values_executor import set_deployment_tags

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state-values-file
    ("--deployment-tags \"th uds\"",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No deployment-tags
    ("--state-values-file testvaluesfile.yaml",
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
def test_set_deployment_tags_bad_args(test_cli_args, expected):
    """Test argument handling for site_values_executor.set_deployment_tags."""
    runner = CliRunner()
    result = runner.invoke(set_deployment_tags, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_set_deployment_tags_success(resource_path_root):
    """Test successful deployment tags update."""
    tags = "pf uds"
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-default.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(set_deployment_tags, args=[
                           "--deployment-tags", tags,
                           "--state-values-file", site_values_file])

    with open(site_values_file, 'r', encoding="utf-8") as yaml_file:
        parsed_yaml = yaml.safe_load(yaml_file)
    for check_tag in parsed_yaml['tags']:
        if check_tag in tags.split(' '):
            assert parsed_yaml['tags'][check_tag] is True
        else:
            assert parsed_yaml['tags'][check_tag] is False
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_set_deployment_tags_no_matching_tag(resource_path_root, caplog):
    """Test deployment tags set when no tag exists in yaml."""
    tags = "uds foo"
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-default.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(set_deployment_tags, args=[
                           "--deployment-tags", tags,
                           "--state-values-file", site_values_file])

    assert "There is no such tag \"foo\" in yaml file" in caplog.text
    with open(site_values_file, 'r', encoding="utf-8") as yaml_file:
        parsed_yaml = yaml.safe_load(yaml_file)
    for check_tag in parsed_yaml['tags']:
        assert parsed_yaml['tags'][check_tag] is False
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_set_deployment_tags_None_with_other_values(resource_path_root, caplog):
    """Test deployment tags set when None tag passed in with other values."""
    tags = "None ta"
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-default.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(set_deployment_tags, args=[
                           "--deployment-tags", tags,
                           "--state-values-file", site_values_file])

    assert "There should be no other tags if \"None\" is set" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_set_deployment_tags_with_None_tag(resource_path_root, caplog):
    """Test deployment tags set with None tag passed in."""
    tags = "None"
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-default.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(set_deployment_tags, args=[
                           "--deployment-tags", tags,
                           "--state-values-file", site_values_file])

    assert "No tags have been set. Only base applications will be installed.." in caplog.text
    assert result.exit_code == 0
