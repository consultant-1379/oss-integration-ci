"""Test for csar executor compare_csar_and_helmfile_images."""
import os
import subprocess
from unittest import mock
import pytest
from click.testing import CliRunner

from bin.csar_executor import compare_csar_and_helmfile_images
from lib import helmfile
from lib import utils
from lib import optionality

USERNAME = "username"
PASSWORD = "password"
CHART_NAME = "eric-oss-adc"
CHART_VERSION = "0.0.2-538"
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
    # No chart-name
    ("--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--state-values-file $PWD/site-values.yaml "
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No chart-version
    ("--chart-name eric-oss-adc " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--state-values-file $PWD/site-values.yaml "
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--chart-version\""}),
    # No path-to-helmfile
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--state-values-file $PWD/site-values.yaml "
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No state-values-file
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml "
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No helmfile-name
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml "
     "--state-values-file $PWD/site-values.yaml " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--helmfile-name\""}),
    # No helmfile-version
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml "
     "--state-values-file $PWD/site-values.yaml " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--helmfile-version\""}),
    # No helmfile-repo
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml "
     "--state-values-file $PWD/site-values.yaml " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--username username " +
     "--password password",
     {'output': "Error: Missing option \"--helmfile-repo\""}),
    # No username
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml "
     "--state-values-file $PWD/site-values.yaml " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo repo " +
     "--password password",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--chart-name eric-oss-adc " +
     "--chart-version 0.0.2-538 " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml "
     "--state-values-file $PWD/site-values.yaml " +
     "--helmfile-name eric-eiae-helmfile " +
     "--helmfile-version 2.4.0-156 " +
     "--helmfile-repo repo " +
     "--username username",
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
    result = runner.invoke(compare_csar_and_helmfile_images, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_successful_comparison(caplog, monkeypatch, fp):
    """Test for a successful image comparison."""
    # pylint: disable=unused-argument
    def download_helmfile(chart_name, chart_version, chart_repo, username, password):
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
    def unzip_file(path_to_zipfile, target_path, file=None):
        os.makedirs(os.path.dirname(FILENAME), exist_ok=True)
        with open(FILENAME, "w", encoding="utf-8") as images_file:
            images_file.write("armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30\n")
            images_file.write("armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33\n")
            images_file.write("armdocker/test/path/eric-lm-hooklauncher:8.0.0-14\n")

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(helmfile, "download_helmfile", download_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(utils, "unzip_file", unzip_file)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(compare_csar_and_helmfile_images, args=[
        "--chart-name", CHART_NAME,
        "--chart-version", CHART_VERSION,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO])

    os.remove(FILENAME)
    assert "Found image: eric-sec-access-mgmt-image:13.1.0-30" in caplog.text
    assert "Found image: eric-fh-snmp-alarm-provider:7.1.0-33" in caplog.text
    assert "Found image: eric-lm-hooklauncher:8.0.0-14" in caplog.text
    assert "Found image: stub-eric-pm-exporter:10.7.0-46" not in caplog.text
    assert "Found image: eric-cm-mediator:7.21.0-23" not in caplog.text
    assert "Found image: eric-cm-key-init:7.21.0-23" not in caplog.text
    assert "All images are contained in the CSAR" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_comparison_with_missing_images(caplog, monkeypatch, fp):
    """Test for a comparison with a missing image."""
    # pylint: disable=unused-argument
    def download_helmfile(chart_name, chart_version, chart_repo, username, password):
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
    def unzip_file(path_to_zipfile, target_path, file=None):
        os.makedirs(os.path.dirname(FILENAME), exist_ok=True)
        with open(FILENAME, "w", encoding="utf-8") as images_file:
            images_file.write("armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30\n")
            images_file.write("armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33\n")

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(helmfile, "download_helmfile", download_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(utils, "unzip_file", unzip_file)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(compare_csar_and_helmfile_images, args=[
        "--chart-name", CHART_NAME,
        "--chart-version", CHART_VERSION,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO])

    os.remove(FILENAME)
    assert "Found image: eric-sec-access-mgmt-image:13.1.0-30" in caplog.text
    assert "Found image: eric-fh-snmp-alarm-provider:7.1.0-33" in caplog.text
    assert "Error: The image eric-lm-hooklauncher:8.0.0-14 is missing from the CSAR" in caplog.text
    assert "Found image: stub-eric-pm-exporter:10.7.0-46" not in caplog.text
    assert "Found image: eric-cm-mediator:7.21.0-23" not in caplog.text
    assert "Found image: eric-cm-key-init:7.21.0-23" not in caplog.text
    assert "Error: Image(s) are missing from the CSAR" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_comparison_with_no_template_images(caplog, monkeypatch, fp):
    """Test for a comparison with no template images."""
    # pylint: disable=unused-argument
    def download_helmfile(chart_name, chart_version, chart_repo, username, password):
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
    def unzip_file(path_to_zipfile, target_path, file=None):
        os.makedirs(os.path.dirname(FILENAME), exist_ok=True)
        with open(FILENAME, "w", encoding="utf-8") as images_file:
            images_file.write("armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30\n")
            images_file.write("armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33\n")

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(helmfile, "download_helmfile", download_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(utils, "unzip_file", unzip_file)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(compare_csar_and_helmfile_images, args=[
        "--chart-name", "eric-cloud-native-base",
        "--chart-version", CHART_VERSION,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO])

    os.remove(FILENAME)
    assert "Warning: The helmfile template returned no images" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_missing_file_error(caplog, monkeypatch, fp):
    """Test for a missing file error."""
    # pylint: disable=unused-argument
    def download_helmfile(chart_name, chart_version, chart_repo, username, password):
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
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(helmfile, "download_helmfile", download_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(compare_csar_and_helmfile_images, args=[
        "--chart-name", CHART_NAME,
        "--chart-version", CHART_VERSION,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO])

    assert f"No such file or directory: './{CHART_NAME}-{CHART_VERSION}.csar'" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_helmfile_template_error(caplog, monkeypatch, fp):
    """Test for a helmfile template error."""
    # pylint: disable=unused-argument
    def download_helmfile(chart_name, chart_version, chart_repo, username, password):
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
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(helmfile, "download_helmfile", download_helmfile)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    runner = CliRunner()
    result = runner.invoke(compare_csar_and_helmfile_images, args=[
        "--chart-name", CHART_NAME,
        "--chart-version", CHART_VERSION,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO])

    assert "Incompatible types" in caplog.text
    assert "Error: The helmfile template returned an error" in caplog.text
    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
# pylint: disable=invalid-name
def test_successful_comparison_with_existing_file(caplog, monkeypatch, fp):
    """Test for a successful image comparison with an existing template images file."""

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_RESPONSE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def unzip_file(path_to_zipfile, target_path, file=None):
        os.makedirs(os.path.dirname(FILENAME), exist_ok=True)
        with open(FILENAME, "w", encoding="utf-8") as images_file:
            images_file.write("armdocker/test/path/eric-sec-access-mgmt-image:13.1.0-30\n")
            images_file.write("armdocker/test/path/eric-fh-snmp-alarm-provider:7.1.0-33\n")
            images_file.write("armdocker/test/path/eric-lm-hooklauncher:8.0.0-14\n")

    # pylint: disable=unused-argument
    def get_optionality_max(state_values_file_path, helmfile_name, chart_cache_directory):
        return True

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)
    monkeypatch.setattr(utils, "unzip_file", unzip_file)
    monkeypatch.setattr(optionality, "generate_optionality_maximum", get_optionality_max)

    with open("templated-images.txt", "w", encoding="utf-8") as templated_images_file:
        templated_images_file.write("eric-sec-access-mgmt-image:13.1.0-30," +
                                    "eric-fh-snmp-alarm-provider:7.1.0-33," +
                                    "eric-lm-hooklauncher:8.0.0-14")

    runner = CliRunner()
    result = runner.invoke(compare_csar_and_helmfile_images, args=[
        "--chart-name", CHART_NAME,
        "--chart-version", CHART_VERSION,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--helmfile-repo", HELMFILE_REPO])

    os.remove("templated-images.txt")
    assert "Found image: eric-sec-access-mgmt-image:13.1.0-30" in caplog.text
    assert "Found image: eric-fh-snmp-alarm-provider:7.1.0-33" in caplog.text
    assert "Found image: eric-lm-hooklauncher:8.0.0-14" in caplog.text
    assert "Found image: stub-eric-pm-exporter:10.7.0-46" not in caplog.text
    assert "Found image: eric-cm-mediator:7.21.0-23" not in caplog.text
    assert "Found image: eric-cm-key-init:7.21.0-23" not in caplog.text
    assert "All images are contained in the CSAR" in caplog.text
    assert result.exit_code == 0
