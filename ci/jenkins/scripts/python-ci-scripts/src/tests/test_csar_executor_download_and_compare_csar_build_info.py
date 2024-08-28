"""Test for csar executor download_and_compare_csar_build_info."""
import os
import subprocess
from unittest import mock
import pytest
from click.testing import CliRunner
from requests import RequestException
from bin.csar_executor import download_and_compare_csar_build_info
from lib import helmfile
from lib import utils
from lib import optionality

USERNAME = "username"
PASSWORD = "password"
CHART_NAME = "eric-oss-adc"
ARTIFACT_URL = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-generic-local/"
PATH_TO_HELMFILE = "eric-eiae-helmfile/helmfile.yaml"
STATE_VALUES_FILE = "site-values.yaml"
HELMFILE_NAME = "eric-eiae-helmfile"
HELMFILE_VERSION = "2.4.0-156"
HELMFILE_REPO = "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"
HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
MOCK_RESPONSE = """
# Source: eric-oss-adc/charts/deployment.yaml
image: "armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30"
image: "armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33"
image: "armdocker/test/path/eric-lm-hooklauncher:8.0.0-14"
image: "armdocker/test/path/stub-eric-pm-exporter:10.7.0-46"
---
# Source: eric-oss-common-base/charts/deployment.yaml
image: "armdocker/test/path/eric-cm-mediator:7.21.0-23"
image: "armdocker/test/path/eric-cm-key-init:7.21.0-23"
---
"""
FILENAME = "Files/images.txt"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No artifact-url
    ("--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--state-values-file $PWD/site-values.yaml " +
     "--chart-name eric-oss-adc " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--artifact-url\""}),
    # No helmfile-name
    ("--artifact-url url " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--state-values-file $PWD/site-values.yaml " +
     "--chart-name eric-oss-adc " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--helmfile-name\""}),
    # No helmfile-version
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--state-values-file $PWD/site-values.yaml " +
     "--chart-name eric-oss-adc " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--helmfile-version\""}),
    # No helmfile-repo
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--state-values-file $PWD/site-values.yaml " +
     "--chart-name eric-oss-adc " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--helmfile-repo\""}),
    # No path-to-helmfile
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--state-values-file $PWD/site-values.yaml " +
     "--chart-name eric-oss-adc " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No state-values-file
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--chart-name eric-oss-adc " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No chart-name
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--state-values-file $PWD/site-values.yaml " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No username
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--state-values-file $PWD/site-values.yaml " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--chart-name eric-oss-adc " +
     "--password password",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--artifact-url url " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--state-values-file $PWD/site-values.yaml " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--username username " +
     "--chart-name eric-oss-adc",
     {'output': "Error: Missing option \"--password\""}),
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
def test_compare_csar_and_helmfile_images_bad_args(test_cli_args, expected):
    """Test argument handling for csar_executor.compare_csar_and_helmfile_images."""
    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_no_csar_build_info_available(caplog, monkeypatch, fp):
    """Test for no csar-build-info file being present."""

    # pylint: disable=unused-argument, too-many-arguments
    def download_csar_build_info_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        raise RequestException

    monkeypatch.setattr(utils, "download_file", download_csar_build_info_file)

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", CHART_NAME])

    assert "Unable to find the csar_build_info file. The CSAR build will continue..." in caplog.text
    assert os.path.exists("csar-build-indicator-file.properties")
    with open("csar-build-indicator-file.properties", "r", encoding="utf-8") as csar_build_indicator_file:
        file_content = csar_build_indicator_file.read()
    assert "should_csar_be_built=True" in file_content
    os.remove("csar-build-indicator-file.properties")
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_successful_comparison_no_difference(caplog, monkeypatch, fp):
    """Test for a successful comparison with no difference."""

    # pylint: disable=unused-argument, too-many-arguments
    def download_csar_build_info_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        with open("downloaded_csar_build_info.txt", "w", encoding="utf-8") as csar_build_info_file:
            csar_build_info_file.write("Images: armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30, " +
                                       "armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33, " +
                                       "armdocker/test/path/eric-lm-hooklauncher:8.0.0-14, " +
                                       "armdocker/test/path/stub-eric-pm-exporter:10.7.0-46")

    # pylint: disable=unused-argument
    def donwload_helmfile(chart_name, chart_version, chart_repo, username, password):
        return True

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_RESPONSE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_csar_build_info_file)
    monkeypatch.setattr(helmfile, "download_helmfile", donwload_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", CHART_NAME])

    assert f"Assessing whether the csar_build_info.txt file is available at {ARTIFACT_URL}" in caplog.text
    assert "Download Successful. The images contained within this CSAR will be compared against the helmfile "\
           "to determine whether a CSAR rebuild is necessary..." in caplog.text
    assert "Found image: eric-sec-access-mgmt-image:13.1.0-30" in caplog.text
    assert "Found image: eric-fh-snmp-alarm-provider:7.1.0-33" in caplog.text
    assert "Found image: eric-lm-hooklauncher:8.0.0-14" in caplog.text
    assert "All images are contained in the CSAR" in caplog.text
    assert "There are no missing images between the csar-build-info.txt file and the helmfile. " \
           "The CSAR build will not proceed..." in caplog.text
    assert os.path.exists("csar-build-indicator-file.properties")
    with open("csar-build-indicator-file.properties", "r", encoding="utf-8") as csar_build_indicator_file:
        file_content = csar_build_indicator_file.read()
    assert "should_csar_be_built=False" in file_content
    os.remove("csar-build-indicator-file.properties")
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_successful_comparison_with_difference(caplog, monkeypatch, fp):
    """Test for a successful comparison with a difference."""

    # pylint: disable=unused-argument, too-many-arguments
    def download_csar_build_info_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        with open("downloaded_csar_build_info.txt", "w", encoding="utf-8") as csar_build_info_file:
            csar_build_info_file.write("Images: armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30, " +
                                       "armdocker/test/path/eric-lm-hooklauncher:8.0.0-14, " +
                                       "armdocker/test/path/stub-eric-pm-exporter:10.7.0-46")

    # pylint: disable=unused-argument
    def donwload_helmfile(chart_name, chart_version, chart_repo, username, password):
        return True

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_RESPONSE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_csar_build_info_file)
    monkeypatch.setattr(helmfile, "download_helmfile", donwload_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", CHART_NAME])

    assert f"Assessing whether the csar_build_info.txt file is available at {ARTIFACT_URL}" in caplog.text
    assert "Download Successful. The images contained within this CSAR will be compared against the helmfile " \
           "to determine whether a CSAR rebuild is necessary..." in caplog.text
    assert "Found image: eric-sec-access-mgmt-image:13.1.0-30" in caplog.text
    assert "Error: The image eric-fh-snmp-alarm-provider:7.1.0-33 is missing from the CSAR" in caplog.text
    assert "Found image: eric-lm-hooklauncher:8.0.0-14" in caplog.text
    assert "As images are missing from the csar-build-info.txt file, " \
           "the CSAR build will proceed" in caplog.text
    assert os.path.exists("csar-build-indicator-file.properties")
    with open("csar-build-indicator-file.properties", "r", encoding="utf-8") as csar_build_indicator_file:
        file_content = csar_build_indicator_file.read()
    assert "should_csar_be_built=True" in file_content
    os.remove("csar-build-indicator-file.properties")
    assert os.path.exists("templated-images.txt")
    with open("templated-images.txt", "r", encoding="utf-8") as templated_images_file:
        file_content = templated_images_file.read()
    assert "armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30," \
           "armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33," \
           "armdocker/test/path/eric-lm-hooklauncher:8.0.0-14" in file_content
    os.remove("templated-images.txt")
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_template_error(caplog, monkeypatch, fp):
    """Test for a template error."""

    # pylint: disable=unused-argument, too-many-arguments
    def download_csar_build_info_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        with open("downloaded_csar_build_info.txt", "w", encoding="utf-8") as csar_build_info_file:
            csar_build_info_file.write("Images: armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30, " +
                                       "armdocker/test/path/eric-lm-hooklauncher:8.0.0-14, " +
                                       "armdocker/test/path/stub-eric-pm-exporter:10.7.0-46")

    # pylint: disable=unused-argument
    def donwload_helmfile(chart_name, chart_version, chart_repo, username, password):
        return True

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_RESPONSE, stderr="Incompatible types",
                    returncode=1)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_csar_build_info_file)
    monkeypatch.setattr(helmfile, "download_helmfile", donwload_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", CHART_NAME])

    assert "Incompatible types" in caplog.text
    assert "Error: The helmfile template returned an error" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_no_images(caplog, monkeypatch, fp):
    """Test for no images being present."""

    # pylint: disable=unused-argument, too-many-arguments
    def download_csar_build_info_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        with open("downloaded_csar_build_info.txt", "w", encoding="utf-8") as csar_build_info_file:
            csar_build_info_file.write("Images: armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30, " +
                                       "armdocker/test/path/eric-lm-hooklauncher:8.0.0-14, " +
                                       "armdocker/test/path/stub-eric-pm-exporter:10.7.0-46")

    # pylint: disable=unused-argument
    def donwload_helmfile(chart_name, chart_version, chart_repo, username, password):
        return True

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_RESPONSE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_csar_build_info_file)
    monkeypatch.setattr(helmfile, "download_helmfile", donwload_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", "eric-cloud-native-base"])

    assert "Warning: The helmfile template returned no images" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_eric_eo_cm(caplog):
    """Test for no images being present."""

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", "eric-eo-cm"])

    assert "Exiting image comparison: Image comparison not conducted for eric-eo-cm or eric-eo-act-cna" in caplog.text
    assert os.path.exists("csar-build-indicator-file.properties")
    with open("csar-build-indicator-file.properties", "r", encoding="utf-8") as csar_build_indicator_file:
        file_content = csar_build_indicator_file.read()
    assert "should_csar_be_built=True" in file_content
    os.remove("csar-build-indicator-file.properties")
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_eric_eo_act_cna(caplog):
    """Test for no images being present."""

    runner = CliRunner()
    result = runner.invoke(download_and_compare_csar_build_info, args=[
        "--artifact-url", ARTIFACT_URL,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", "eric-eo-act-cna"])

    assert "Exiting image comparison: Image comparison not conducted for eric-eo-cm or eric-eo-act-cna" in caplog.text
    assert os.path.exists("csar-build-indicator-file.properties")
    with open("csar-build-indicator-file.properties", "r", encoding="utf-8") as csar_build_indicator_file:
        file_content = csar_build_indicator_file.read()
    assert "should_csar_be_built=True" in file_content
    os.remove("csar-build-indicator-file.properties")
    assert result.exit_code == 0
