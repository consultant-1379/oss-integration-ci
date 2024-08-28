"""Test for utils executor extract_tar_file"""
import os
import pytest
from click.testing import CliRunner

from bin.utils_executor import extract_tar_file


@pytest.mark.parametrize("test_cli_args, expected", [
    # No file name
    ("--dir /some/dir --properties-file /some/file.properties",
     {'output': "Error: Missing option \"--file\""}),
    # No directory name
    ("--file /some/file.tgz --properties-file /some/file.properties",
     {'output': "Error: Missing option \"--dir\""}),
    # No properites file
    ("--file /some/file.tgz --dir /some/dir",
     {'output': "Error: Missing option \"--properties-file\""}),
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
def test_extract_tar_file_bad_arguments(test_cli_args, expected):
    """Test extract tar with bad arguments."""
    runner = CliRunner()
    result = runner.invoke(extract_tar_file, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_extract_tar_file_positive(resource_path_root, tmp_path):
    """Test script executor extract_tar_file with positive result."""
    tar_file = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    properties_file = os.path.join(tmp_path, "artifact.properties")
    expected_output = "TAR_BASE_DIR=eric-eo-helmfile\n"

    runner = CliRunner()
    result = runner.invoke(extract_tar_file,
                           args=["--file", tar_file, "--dir", tmp_path, "--properties-file", properties_file])
    assert result.exit_code == 0
    assert os.path.exists(properties_file) is True
    with open(properties_file, 'r', encoding="utf-8") as props:
        data = props.read()
    assert expected_output == data


def test_extract_tar_file_corrupt_tar(resource_path_root, tmp_path, caplog):
    """Test attempt to untar corrupt tar file."""
    tar_file = os.path.join(resource_path_root, "corrupt.tgz.test")
    properties_file = os.path.join(tmp_path, "artifact.properties")
    runner = CliRunner()
    result = runner.invoke(extract_tar_file,
                           args=["--file", tar_file, "--dir", tmp_path, "--properties-file", properties_file])
    assert result.exit_code == 1
    assert "file could not be opened successfully" in caplog.text


def test_extract_tar_file_no_output_dir(resource_path_root, tmp_path, caplog):
    """Test extract tar cannot write to output directory."""
    tar_file = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    properties_file = "/some/unkknown/dir/artifact.properties"
    runner = CliRunner()
    result = runner.invoke(extract_tar_file,
                           args=["--file", tar_file, "--dir", tmp_path, "--properties-file", properties_file])
    assert result.exit_code == 1
    assert f"No such file or directory: '{properties_file}'" in caplog.text
