"""Test for site values executor substitute_values."""
import os
import shutil
import oyaml as yaml
import pytest
from click.testing import CliRunner

from bin.site_values_executor import substitute_values

KUBECTL = "/usr/bin/kubectl"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state-values-file
    ("--file testfile",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No file
    ("--state-values-file testvaluesfile.yaml",
     {'output': "Error: Missing option \"--file\""}),
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
def test_substitute_values_bad_args(test_cli_args, expected):
    """Test argument handling for site_values_executor.substitute_values."""
    runner = CliRunner()
    result = runner.invoke(substitute_values, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_substitute_values_single_update_success(resource_path_root, caplog):
    """Test successful file update."""
    testfile = os.path.join(os.getcwd(), "testfile")
    with open(testfile, "w", encoding="utf-8") as file_with_updates:
        file_with_updates.write("DOCKER_REGISTRY_REPLACE=testregistry\n")
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-template.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(substitute_values, args=[
                           "--file", testfile,
                           "--state-values-file", site_values_file])

    assert f"Changing DOCKER_REGISTRY_REPLACE to testregistry in {site_values_file}" in caplog.text
    with open(site_values_file, 'r', encoding="utf-8") as yaml_file:
        parsed_yaml = yaml.safe_load(yaml_file)
    assert 'global' in parsed_yaml
    assert 'registry' in parsed_yaml['global']
    assert 'url' in parsed_yaml['global']['registry']
    assert parsed_yaml['global']['registry']['url'] == "testregistry"
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_substitute_values_multiple_update_success(resource_path_root, caplog):
    """Test successful file update with multiple matches."""
    testfile = os.path.join(os.getcwd(), "testfile")
    with open(testfile, "w", encoding="utf-8") as file_with_updates:
        file_with_updates.write("DOCKER_REGISTRY_REPLACE = testregistry\n"
                                "IPV6_ENABLE_REPLACE = true\n"
                                "FOO=bar\n"
                                "FOO2:bar2\n")
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-template.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(substitute_values, args=[
                           "--file", testfile,
                           "--state-values-file", site_values_file])

    assert f"Changing DOCKER_REGISTRY_REPLACE to testregistry in {site_values_file}" in caplog.text
    assert f"Changing IPV6_ENABLE_REPLACE to true in {site_values_file}" in caplog.text
    assert f"Changing FOO to true in {site_values_file}" not in caplog.text
    assert f"Changing FOO2 to true in {site_values_file}" not in caplog.text
    with open(site_values_file, 'r', encoding="utf-8") as yaml_file:
        parsed_yaml = yaml.safe_load(yaml_file)
    assert 'global' in parsed_yaml
    assert 'registry' in parsed_yaml['global']
    assert 'url' in parsed_yaml['global']['registry']
    assert parsed_yaml['global']['registry']['url'] == "testregistry"
    assert 'support' in parsed_yaml['global']
    assert 'ipv6' in parsed_yaml['global']['support']
    assert 'enabled' in parsed_yaml['global']['support']['ipv6']
    assert parsed_yaml['global']['support']['ipv6']['enabled'] is True
    assert 'eric-cloud-native-base' in parsed_yaml
    assert 'eric-data-search-engine' in parsed_yaml['eric-cloud-native-base']
    assert 'service' in parsed_yaml['eric-cloud-native-base']['eric-data-search-engine']
    assert 'network' in parsed_yaml['eric-cloud-native-base']['eric-data-search-engine']['service']
    assert 'protocol' in parsed_yaml['eric-cloud-native-base']['eric-data-search-engine']['service']['network']
    assert 'IPv6' in \
        parsed_yaml['eric-cloud-native-base']['eric-data-search-engine']['service']['network']['protocol']
    assert parsed_yaml['eric-cloud-native-base']['eric-data-search-engine']['service']['network']['protocol']['IPv6'] \
        is True
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_substitute_values_no_matches(resource_path_root, caplog):
    """Test file update when no matches are found."""
    testfile = os.path.join(os.getcwd(), "testfile")
    with open(testfile, "w", encoding="utf-8") as file_with_updates:
        file_with_updates.write("docker_registry_replace=testregistry\n")
    site_values_file = os.path.join(os.getcwd(), "site-values.yaml")
    shutil.copyfile(os.path.join(resource_path_root, "site-values-template.yaml"),
                    os.path.join(os.getcwd(), "site-values.yaml"))

    runner = CliRunner()
    result = runner.invoke(substitute_values, args=[
                           "--file", testfile,
                           "--state-values-file", site_values_file])

    assert f"Changing docker_registry_replace to testregistry in {site_values_file}" not in caplog.text
    with open(site_values_file, 'r', encoding="utf-8") as yaml_file:
        parsed_yaml = yaml.safe_load(yaml_file)
    assert 'global' in parsed_yaml
    assert 'registry' in parsed_yaml['global']
    assert 'url' in parsed_yaml['global']['registry']
    assert parsed_yaml['global']['registry']['url'] == "DOCKER_REGISTRY_REPLACE"
    assert result.exit_code == 0
