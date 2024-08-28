"""Test for helmfile executor cncs_optionality_checker."""
import os
import pytest

from click.testing import CliRunner

from bin.helm_chart_executor import cncs_optionality_checker
from lib import utils
from lib import helmfile

CNCS_NAME = "eric-cloud-native-base"
CNCS_VERSION = "87.12.0"
CB_NAME = "eric-oss-common-base"
CB_VERSION = "65.1.0"
HELMFILE_NAME = "eric-eiae-helmfile"
HELMFILE_VERSION = "2.8.0-20"
HELMFILE_FILENAME = "eric-eiae-helmfile/helmfile.yaml"
HELMFILE_OPTIONALITY_FILENAME = "helmfile/optionality.yaml"
CHART_FILENAME = "eric-cloud-native-base/Chart.yaml"
CB_OPTIONALITY_FILENAME = "eric-oss-common-base/optionality.yaml"
APP1 = "eric-cm-mediator"
APP2 = "eric-fh-snmp-alarm-provider"
APP3 = "eric-data-document-database-pg"
APP4 = "eric-fh-alarm-handler-db-pg"
APP5 = "eric-sec-access-mgmt-db-pg"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No helmfile name
    ("--helmfile-version version " +
     "--username username " +
     "--user-password password",
     {'output': "Error: Missing option \"--helmfile-name\""}),
    # No int chart version
    ("--helmfile-name name " +
     "--username username " +
     "--user-password password",
     {'output': "Error: Missing option \"--helmfile-version\""}),
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
def test_cncs_optionality_checker_bad_args(test_cli_args, expected):
    """Test argument handling for helmfile_executor.compare_csar_and_helmfile_images."""
    runner = CliRunner()
    result = runner.invoke(cncs_optionality_checker, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_no_cncs_found(caplog, monkeypatch):
    """Test for no CNCS value being found in the helmfile."""
    # pylint: disable=unused-argument
    def get_base_baseline(*args):
        with open("artifact.properties", "w", encoding="utf-8") as properties_file:
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_NAME=eric-oss-common-base\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_VERSION=1.1.1")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_REPO=repo_1")

    monkeypatch.setattr(helmfile, "get_base_baseline", get_base_baseline)

    runner = CliRunner()
    result = runner.invoke(cncs_optionality_checker, args=[
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--username", "username",
        "--user-password", "password"])

    assert "eric-cloud-native-base/eric-oss-common-base not found in the helmfile" in caplog.text
    assert result.exit_code == 1


def test_no_optionality_file(caplog, monkeypatch):
    """Test for no optionality file being found."""
    # pylint: disable=unused-argument
    def get_base_baseline(*args):
        with open("artifact.properties", "w", encoding="utf-8") as properties_file:
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_NAME=eric-oss-common-base, "
                                       "eric-cloud-native-base\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_VERSION=1.1.1, 2.2.2\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_REPO=repo_1, repo_2")

    # pylint: disable=too-many-arguments, unused-argument
    def download_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        os.makedirs(os.path.dirname(CHART_FILENAME), exist_ok=True)
        with open(CHART_FILENAME, "w", encoding="utf-8") as chart_file:
            chart_file.writelines("dependencies:\n")
            chart_file.writelines(f"  - name: {APP1}\n")
            chart_file.writelines(f"  - name: {APP2}\n")
            chart_file.writelines(f"  - name: {APP3}\n")
            chart_file.writelines(f"  - name: {APP4}\n")
            chart_file.writelines(f"  - name: {APP5}\n")

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_file)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "get_base_baseline", get_base_baseline)

    runner = CliRunner()
    result = runner.invoke(cncs_optionality_checker, args=[
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--username", "username",
        "--user-password", "password"])

    os.remove(CHART_FILENAME)
    assert f"No such file or directory: '{CB_OPTIONALITY_FILENAME}'" in caplog.text
    assert result.exit_code == 1


def test_no_cncs_chart(caplog, monkeypatch):
    """Test for no CNCS chart being found."""
    # pylint: disable=unused-argument
    def get_base_baseline(*args):
        with open("artifact.properties", "w", encoding="utf-8") as properties_file:
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_NAME=eric-oss-common-base, "
                                       "eric-cloud-native-base\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_VERSION=1.1.1, 2.2.2\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_REPO=repo_1, repo_2")

    # pylint: disable=too-many-arguments, unused-argument
    def download_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        return True

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_file)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "get_base_baseline", get_base_baseline)

    runner = CliRunner()
    result = runner.invoke(cncs_optionality_checker, args=[
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--username", "username",
        "--user-password", "password"])

    assert f"No such file or directory: '{CHART_FILENAME}'" in caplog.text
    assert result.exit_code == 1


def test_successful_run_missing_images(caplog, monkeypatch):
    """Test for a successful comparison with missing images."""
    os.makedirs(os.path.dirname(HELMFILE_FILENAME), exist_ok=True)
    with open(HELMFILE_FILENAME, "w", encoding="utf-8") as helmfile_file:
        helmfile_file.writelines(f"name: {CB_NAME}\n")
        helmfile_file.writelines(f"version: {CB_VERSION}")
        helmfile_file.writelines(f"name: {CNCS_NAME}\n")
        helmfile_file.writelines(f"version: {CNCS_VERSION}")

    # pylint: disable=unused-argument
    def get_base_baseline(*args):
        with open("artifact.properties", "w", encoding="utf-8") as properties_file:
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_NAME=eric-oss-common-base, "
                                       "eric-cloud-native-base\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_VERSION=1.1.1, 2.2.2\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_REPO=repo_1, repo_2")

    # pylint: disable=too-many-arguments, unused-argument
    def download_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        os.makedirs(os.path.dirname(CHART_FILENAME), exist_ok=True)
        os.makedirs(os.path.dirname(CB_OPTIONALITY_FILENAME), exist_ok=True)
        with open(CHART_FILENAME, "w", encoding="utf-8") as chart_file, \
                open(CB_OPTIONALITY_FILENAME, "w", encoding="utf-8") as cb_optionality_file:
            chart_file.writelines("dependencies:\n")
            chart_file.writelines(f"  - name: {APP1}\n")
            chart_file.writelines(f"  - name: {APP2}\n")
            chart_file.writelines(f"  - name: {APP3}\n")
            chart_file.writelines(f"  - name: {APP4}\n")
            chart_file.writelines(f"  - name: {APP5}\n")
            cb_optionality_file.writelines("optionality:\n")
            cb_optionality_file.writelines(f"  {CNCS_NAME}:\n")
            cb_optionality_file.writelines(f"    {APP1}: value\n")
            cb_optionality_file.writelines(f"    {APP2}: value\n")

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    monkeypatch.setattr(utils, "download_file", download_file)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)
    monkeypatch.setattr(helmfile, "get_base_baseline", get_base_baseline)

    runner = CliRunner()
    result = runner.invoke(cncs_optionality_checker, args=[
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--username", "username",
        "--user-password", "password"])

    assert os.path.isfile("missingOptionalityValues.txt")
    with open("missingOptionalityValues.txt", "r", encoding="utf-8") as missing_optionality_values:
        file_content = missing_optionality_values.readlines()
    assert f"Helmfile name and version: {HELMFILE_NAME}-{HELMFILE_VERSION}\n" in file_content
    assert "CNCS optionality values that are missing from common-base:\n" in file_content
    assert APP4 + "\n" in file_content
    assert APP5 + "\n" in file_content
    os.remove("missingOptionalityValues.txt")
    assert f"{APP4} is not listed in the common-base optionality file" in caplog.text
    assert f"{APP5} is not listed in the common-base optionality file" in caplog.text
    assert result.exit_code == 1


def test_successful_run_no_missing_images(monkeypatch):
    """Test for a successful comparison with no missing images."""
    os.makedirs(os.path.dirname(HELMFILE_FILENAME), exist_ok=True)
    with open(HELMFILE_FILENAME, "w", encoding="utf-8") as helmfile_file:
        helmfile_file.writelines(f"name: {CB_NAME}\n")
        helmfile_file.writelines(f"version: {CB_VERSION}")
        helmfile_file.writelines(f"name: {CNCS_NAME}\n")
        helmfile_file.writelines(f"version: {CNCS_VERSION}")

    # pylint: disable=unused-argument
    def get_base_baseline(*args):
        with open("artifact.properties", "w", encoding="utf-8") as properties_file:
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_NAME=eric-oss-common-base, "
                                       "eric-cloud-native-base\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_VERSION=1.1.1, 2.2.2\n")
            properties_file.writelines("BASE_PLATFORM_BASELINE_CHART_REPO=repo_1, repo_2")

    # pylint: disable=too-many-arguments, unused-argument
    def download_file(url, filename, username, password, file_write_type, timeout_in_s=600):
        os.makedirs(os.path.dirname(CHART_FILENAME), exist_ok=True)
        os.makedirs(os.path.dirname(CB_OPTIONALITY_FILENAME), exist_ok=True)
        with open(CHART_FILENAME, "w", encoding="utf-8") as chart_file, \
                open(CB_OPTIONALITY_FILENAME, "w", encoding="utf-8") as cb_optionality_file:
            chart_file.writelines("dependencies:\n")
            chart_file.writelines(f"  - name: {APP1}\n")
            chart_file.writelines(f"  - name: {APP2}\n")
            chart_file.writelines(f"  - name: {APP3}\n")
            cb_optionality_file.writelines("optionality:\n")
            cb_optionality_file.writelines(f"  {CNCS_NAME}:\n")
            cb_optionality_file.writelines(f"    {APP1}: value\n")
            cb_optionality_file.writelines(f"    {APP2}: value\n")
            cb_optionality_file.writelines(f"    {APP3}: value\n")

    # pylint: disable=unused-argument
    def extract_tar_file(tar_file, directory):
        return True

    monkeypatch.setattr(helmfile, "get_base_baseline", get_base_baseline)
    monkeypatch.setattr(utils, "download_file", download_file)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)

    runner = CliRunner()
    result = runner.invoke(cncs_optionality_checker, args=[
        "--helmfile-name", HELMFILE_NAME,
        "--helmfile-version", HELMFILE_VERSION,
        "--username", "username",
        "--user-password", "password"])

    assert os.path.isfile("missingOptionalityValues.txt")
    with open("missingOptionalityValues.txt", "r", encoding="utf-8") as missing_optionality_values:
        file_content = missing_optionality_values.readlines()
    assert f"Helmfile name and version: {HELMFILE_NAME}-{HELMFILE_VERSION}\n" in file_content
    assert "All CNCS optionality files are contained in common-base" in file_content
    os.remove("missingOptionalityValues.txt")
    assert result.exit_code == 0
    os.remove(CHART_FILENAME)
