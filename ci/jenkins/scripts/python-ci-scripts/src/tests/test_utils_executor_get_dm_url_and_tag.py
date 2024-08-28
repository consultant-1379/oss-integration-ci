"""Test for utils_executor.get_dm_url_and_tag."""
import os
import pytest
from click.testing import CliRunner

from bin.utils_executor import get_dm_url_and_tag

DM_IMAGE_DEFAULT = "armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:default"
DM_IMAGE_LATEST = "armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:latest"
DM_IMAGE_VERSION = "armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:1.1.1"
DM_IMAGE_ERROR = "armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager"

DM_VERSION_FILE = """
    productName: "Deployment Manager"
    images:
      eric-oss-deployment-manager:
        productName: "Deployment Manager"
        registry: "armdocker.rnd.ericsson.se"
        repoPath: "proj-eric-oss-drop"
        name: "eric-oss-deployment-manager"
        tag: "0.1.30"
"""


@pytest.fixture(name="dm_version_file_path")
def dm_file(tmp_path):
    """Fixture to create and return path to dm versio file"""
    def _get_dm_version_file(content, filename="dm_version.yaml"):
        dm_version_file = os.path.join(tmp_path, filename)
        with open(dm_version_file, "w", encoding="utf-8") as output_file:
            output_file.write(content)
        return dm_version_file
    return _get_dm_version_file


@pytest.mark.parametrize("test_cli_args, expected", [
    # No base path
    ("--image test.se/proj/deployment-manager:default --file eric-eo-helmfile/dm_version.yaml",
     {'output': "Error: Missing option \"--properties-file\""}),
    # No override
    ("--image test.se/proj/deployment-manager:default --properties-file IMAGE_DETAILS.txt",
     {'output': "Error: Missing option \"--file\""}),
    # No ouput file
    ("--file eric-eo-helmfile/dm_version.yaml --properties-file IMAGE_DETAILS.txt",
     {'output': "Error: Missing option \"--image\""}),
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
def test_get_dm_url_and_tag_bad_args(test_cli_args, expected):
    """Test arg handling for get_dm_url_and_tag"""
    runner = CliRunner()
    result = runner.invoke(get_dm_url_and_tag, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_setting_version_from_dm_version_file_success(dm_version_file_path, tmp_path):
    """Test successful setting from dm_version_file"""
    dm_version_file = dm_version_file_path(DM_VERSION_FILE)
    output_file = os.path.join(tmp_path, "IMAGE_DETAILS.txt")
    runner = CliRunner()
    result = runner.invoke(get_dm_url_and_tag, args=[
                           "--image", DM_IMAGE_DEFAULT,
                           "--file", dm_version_file,
                           "--properties-file", output_file])
    assert result.exit_code == 0
    assert os.path.exists(output_file) is True
    with open(output_file, "r", encoding="utf-8") as output_data:
        file_content = output_data.readlines()
    assert ["IMAGE=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:0.1.30"] == file_content


def test_setting_latest_when_dm_version_file_does_not_exist_success(tmp_path):
    """Test successful setting from dm_version_file"""
    dm_version_file = os.path.join(tmp_path, "not_existing_file.yaml")
    output_file = os.path.join(tmp_path, "IMAGE_DETAILS.txt")
    runner = CliRunner()
    result = runner.invoke(get_dm_url_and_tag, args=[
                           "--image", DM_IMAGE_DEFAULT,
                           "--file", dm_version_file,
                           "--properties-file", output_file])
    assert result.exit_code == 0
    assert os.path.exists(output_file) is True
    with open(output_file, "r", encoding="utf-8") as output_data:
        file_content = output_data.readlines()
    assert ["IMAGE=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:latest"] == file_content


def test_setting_version_when_latest_is_inputted_success(dm_version_file_path, tmp_path):
    """Test successful setting from dm_version_file"""
    dm_version_file = dm_version_file_path(DM_VERSION_FILE)
    output_file = os.path.join(tmp_path, "IMAGE_DETAILS.txt")
    runner = CliRunner()
    result = runner.invoke(get_dm_url_and_tag, args=[
                           "--image", DM_IMAGE_LATEST,
                           "--file", dm_version_file,
                           "--properties-file", output_file])
    assert result.exit_code == 0
    assert os.path.exists(output_file) is True
    with open(output_file, "r", encoding="utf-8") as output_data:
        file_content = output_data.readlines()
    assert ["IMAGE=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:latest"] == file_content


def test_setting_version_when_version_is_inputted_success(dm_version_file_path, tmp_path):
    """Test successful setting from dm_version_file"""
    dm_version_file = dm_version_file_path(DM_VERSION_FILE)
    output_file = os.path.join(tmp_path, "IMAGE_DETAILS.txt")
    runner = CliRunner()
    result = runner.invoke(get_dm_url_and_tag, args=[
                           "--image", DM_IMAGE_VERSION,
                           "--file", dm_version_file,
                           "--properties-file", output_file])
    assert result.exit_code == 0
    assert os.path.exists(output_file) is True
    with open(output_file, "r", encoding="utf-8") as output_data:
        file_content = output_data.readlines()
    assert ["IMAGE=armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-deployment-manager:1.1.1"] == file_content


def test_setting_version_when_exception_thrown_error(dm_version_file_path, tmp_path, caplog):
    """Test successful setting from dm_version_file"""
    dm_version_file = dm_version_file_path(DM_VERSION_FILE)
    output_file = os.path.join(tmp_path, "IMAGE_DETAILS.txt")
    runner = CliRunner()
    result = runner.invoke(get_dm_url_and_tag, args=[
                           "--image", DM_IMAGE_ERROR,
                           "--file", dm_version_file,
                           "--properties-file", output_file])
    assert result.exit_code == 1
    assert "Unable to fetch deployment manager version. Exception thrown:" in caplog.text
