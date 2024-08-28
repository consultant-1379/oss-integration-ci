"""Tests for helmfile_executor.py generate_optionality_maximum command."""
from pathlib import Path
import logging
import pytest
import yaml
from click.testing import CliRunner

from bin.helmfile_executor import generate_optionality_maximum
from lib import optionality
from lib import utils
from lib import cihelm


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state values file
    ("--path-to-helmfile path --artifactory-username joe --artifactory-password pass",
     {'output': 'Error: Missing option "--state-values-file"'}),
    # No helmfile path
    ("--state-values-file file --artifactory-username joe --artifactory-password pass",
     {'output': 'Error: Missing option "--path-to-helmfile\"'}),
    # No artifactory username
    ("--state-values-file file --path-to-helmfile path --artifactory-password pass",
     {'output': 'Error: Missing option "--artifactory-username\"'}),
    # No artifactory password
    ("--state-values-file file --path-to-helmfile path --artifactory-username joe",
     {'output': 'Error: Missing option "--artifactory-password\"'}),
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
def test_generate_optionality_maximum_bad_args(test_cli_args, expected):
    """Test argument handling in script_executer.generate_optionality_maximum."""
    runner = CliRunner()
    result = runner.invoke(generate_optionality_maximum, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_generate_optionality_maximum_when_exception_thrown(monkeypatch, caplog):
    """Test handling of exceptions from the optionality.generate_optionality_maximum function."""

    def mock_optionality_generate_optionality_maximum(state_values_file, path_to_helmfile, chart_cache_directory):
        raise Exception('Some exception')
    monkeypatch.setattr(optionality, "generate_optionality_maximum", mock_optionality_generate_optionality_maximum)
    runner = CliRunner()

    result = runner.invoke(generate_optionality_maximum, ["--state-values-file", 'dummy',
                                                          "--path-to-helmfile", 'dummy',
                                                          "--artifactory-username", "username",
                                                          "--artifactory-password", "password"])
    assert result.exit_code == 1
    assert "Generating the optionality_maximum.yaml file failed with following errors" in caplog.text
    assert "Some exception" in caplog.text


# pylint: disable=too-many-locals
def test_generate_optionality_maximum_success(monkeypatch, resource_path_root, tmp_path, caplog):
    """Test positive scenario of script_executer.generate_optionality_maximum."""

    state_values_file = str(Path(resource_path_root) / 'test_values_with_some_tags_enabled.yaml')
    helmfile_tar = str(Path(resource_path_root) / "eric-eo-helmfile.tgz.test")
    helmfile_path = str(Path(tmp_path) / "eric-eo-helmfile" / "helmfile.yaml")
    cachedir = str(Path(tmp_path) / "test_cachedir")
    existing_cached_file = str(Path(cachedir) / 'eric-eo-evnfm-2.23.0-925.tgz')
    simulated_downloaded_file1 = 'eric-oss-uds-5.8.0-6.tgz'
    simulated_downloaded_file2 = 'eric-oss-pf-2.14.0-8.tgz'
    destination_optionality_maximum_file = str(Path(tmp_path) / "eric-eo-helmfile" / "build-environment" /
                                               "optionality_maximum.yaml")
    test_optionality_file1_path = str(Path(tmp_path) / 'test_optionality_file1.yaml')
    test_optionality_file2_path = str(Path(tmp_path) / 'test_optionality_file2.yaml')
    test_optionality_file1_contents = """
    optionality:
        eric-cloud-native-base:
            eric-data-coordinator-zk:
                enabled: true
            eric-fh-alarm-handler:
                enabled: false
            eric-sec-access-mgmt:
                enabled: false
        dummy1: true
        dummy2: false
        dummy3: false
    """
    test_optionality_file2_contents = """
    optionality:
        eric-cloud-native-base:
            eric-data-coordinator-zk:
                enabled: false
            eric-fh-alarm-handler:
                enabled: true
            eric-sec-access-mgmt:
                enabled: false
        dummy1: false
        dummy2: true
        dummy3: false
        dummy4: false
    """
    Path(cachedir).mkdir()
    Path(existing_cached_file).touch()
    utils.extract_tar_file(tar_file=helmfile_tar, directory=tmp_path)

    with open(test_optionality_file1_path, 'w', encoding='utf-8') as optionality_file:
        optionality_file.write(test_optionality_file1_contents)

    with open(test_optionality_file2_path, 'w', encoding='utf-8') as optionality_file:
        optionality_file.write(test_optionality_file2_contents)

    runner = CliRunner()

    # pylint: disable=unused-argument
    def mock_cihelm_dependency_update(netrc, mask, workspace, temporary_helm_chart_directory):
        Path(Path(temporary_helm_chart_directory) / 'charts').mkdir()
        Path(Path(temporary_helm_chart_directory) / 'charts' / simulated_downloaded_file1).touch()
        Path(Path(temporary_helm_chart_directory) / 'charts' / simulated_downloaded_file2).touch()

    # pylint: disable=unused-argument
    def mock_utils_extract_files_from_archive(archive_file_path, file_to_extract_path,
                                              target_directory=None, target_filename=None):
        if simulated_downloaded_file1 in archive_file_path:
            return [test_optionality_file1_path]
        if simulated_downloaded_file2 in archive_file_path:
            return [test_optionality_file2_path]
        raise FileNotFoundError('Not found')
    monkeypatch.setattr(cihelm, "_cihelm_dependency_update", mock_cihelm_dependency_update)
    monkeypatch.setattr(utils, "extract_files_from_archive", mock_utils_extract_files_from_archive)

    with caplog.at_level(logging.DEBUG):
        result = runner.invoke(generate_optionality_maximum, ["--state-values-file", state_values_file,
                                                              "--path-to-helmfile", helmfile_path,
                                                              '--chart-cache-directory', cachedir,
                                                              '--artifactory-username', "username",
                                                              '--artifactory-password', "password"])
    assert result.exit_code == 0
    assert 'Filtering out release eric-eo-so as its not enabled given the site values provided' in caplog.text
    assert 'Not filtering out release eric-oss-uds as its enabled given the site values provided' in caplog.text
    assert 'test_cachedir/eric-oss-uds-5.8.0-6.tgz was not already in the download cache, marking it for download' in \
           caplog.text
    assert 'test_cachedir/eric-eo-evnfm-2.23.0-925.tgz was already in the download cache, copying it' in \
           caplog.text

    with open(destination_optionality_maximum_file, encoding='utf-8') as yaml_file:
        resulting_optionality_maximum_object = yaml.load(yaml_file, Loader=yaml.CSafeLoader)
    optionality_result = resulting_optionality_maximum_object['optionality']
    assert optionality_result['eric-cloud-native-base']['eric-data-coordinator-zk']['enabled']
    assert optionality_result['eric-cloud-native-base']['eric-fh-alarm-handler']['enabled']
    assert not optionality_result['eric-cloud-native-base']['eric-sec-access-mgmt']['enabled']
    assert optionality_result['eric-cloud-native-base']['eric-sec-sip-tls']['enabled']
    assert optionality_result['dummy1']
    assert optionality_result['dummy2']
    assert not optionality_result['dummy3']
    assert not optionality_result['dummy4']

    with open(str(Path(tmp_path) / "eric-eo-helmfile" / "repositories.yaml"), encoding='utf-8') as yaml_file:
        resulting_repositories_object = yaml.load(yaml_file, Loader=yaml.CSafeLoader)
    assert {'name': 'eric-cloud-native-base', 'url': 'file://' + cachedir} in \
           resulting_repositories_object['repositories']
