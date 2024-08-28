"""Test for csar executor combine_csar_build_info."""
import os.path
import pytest
from click.testing import CliRunner
from bin.csar_executor import combine_csar_build_info

MANIFEST_FILE = "manifest.txt"
IMAGES_FILE = "images.txt"
TGZ_FILE = "csar-build-info.txt"
IMAGES = ["eric-oss-enm-fns:1.0.168-1", "eric-oss-ves-collector:0.0.2-24",
          "eric-oss-5gpmevt-filetx-proc:1.34.0-1", "eric-oss-helm-test:1.0.0-1",
          "eric-oss-3gpp-pm-xml-core-parser:1.23.0-1", "eric-oss-file-notification-enm-stub:1.0.40-1",
          "eric-oss-sftp-filetrans:1.43.0-1", "eric-oss-3gpp-pm-xml-ran-parser:1.63.0-1",
          "eric-csm-p:1.3.82-12"]


@pytest.mark.parametrize("test_cli_args, expected", [
    # No manifest-file
    ("--images-file file",
     {'output': "Error: Missing option \"--manifest-file\""}),
    # No images-file
    ("--manifest-file file",
     {'output': "Error: Missing option \"--images-file\""}),
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
def test_combine_csar_build_info_bad_args(test_cli_args, expected):
    """Test argument handling for csar_executor.combine_csar_build_info."""
    runner = CliRunner()
    result = runner.invoke(combine_csar_build_info, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_invalid_manifest_file_provided(caplog):
    """Test invalid manifest file being provided."""
    runner = CliRunner()
    result = runner.invoke(combine_csar_build_info, args=[
        "--manifest-file", MANIFEST_FILE,
        "--images-file", IMAGES_FILE])
    assert "No such file or directory: 'manifest.txt'" in caplog.text
    assert result.exit_code == 1


def test_successful_csar_build_info_generation_without_images(caplog):
    """Test successful csar-build-info.txt file creation without images."""
    with open(MANIFEST_FILE, "w", encoding="utf-8") as manifest_file:
        manifest_file.write(f"{TGZ_FILE}")
    runner = CliRunner()
    result = runner.invoke(combine_csar_build_info, args=[
        "--manifest-file", MANIFEST_FILE,
        "--images-file", IMAGES_FILE])
    assert os.path.exists("csar-build-info.txt")
    with open("csar-build-info.txt", "r", encoding="utf-8") as csar_build_info_file:
        file_content = csar_build_info_file.read()
    assert f"TGZ files: {TGZ_FILE}" in file_content
    os.remove(MANIFEST_FILE)
    assert "Combining the manifest.txt and images.txt files completed successfully" in caplog.text
    assert result.exit_code == 0


def test_successful_csar_build_info_generation_with_images(caplog):
    """Test successful csar-build-info.txt file creation with images."""
    with open(MANIFEST_FILE, "w", encoding="utf-8") as manifest_file,\
            open(IMAGES_FILE, "w", encoding="utf-8") as images_file:
        manifest_file.write(f"{TGZ_FILE}")
        for image in IMAGES:
            images_file.write(image + "\n")

    runner = CliRunner()
    result = runner.invoke(combine_csar_build_info, args=[
        "--manifest-file", MANIFEST_FILE,
        "--images-file", IMAGES_FILE])
    assert os.path.exists("csar-build-info.txt")
    with open("csar-build-info.txt", "r", encoding="utf-8") as csar_build_info_file:
        file_content = csar_build_info_file.read()
    assert f"TGZ files: {TGZ_FILE}" in file_content
    assert f"Images: {', '.join(IMAGES)}" in file_content
    os.remove(MANIFEST_FILE)
    os.remove(IMAGES_FILE)
    os.remove("csar-build-info.txt")
    assert "Combining the manifest.txt and images.txt files completed successfully" in caplog.text
    assert result.exit_code == 0
