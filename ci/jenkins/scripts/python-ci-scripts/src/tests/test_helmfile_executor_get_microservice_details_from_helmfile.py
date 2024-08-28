"""Test for helmfile executor get_microservice_details_from_helmfile."""
import os
import shutil
import logging
import json
import pytest
from click.testing import CliRunner

from bin.helmfile_executor import get_microservice_details_from_helmfile
from lib import cihelm
from lib import utils

LOGGER = logging.getLogger(__name__)
HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
SERVICE_OUTPUT_JSON = "helmfile_services_json_content.json"
SERVICE_OUTPUT_FLATFILE = "helmServicesContent.txt"
HELMFILE_BUILD_OUTPUT_FILE = "helmfile_build_output.txt"
HELMFILE_COMPILED_BUILD_OUTPUT_FILE = "compiledContent_helmfile.yaml"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state-values-file
    ("--path-to-helmfile path",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No path-to-helmfile
    ("--state-values-file path",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
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
     {'output': 'Error: no such option: --unknown'})
])
def test_get_microservice_details_from_helmfile_bad_args(test_cli_args, expected):
    """Test argument handling for helmfile_executor.get_microservice_details_from_helmfile."""
    runner = CliRunner()
    result = runner.invoke(get_microservice_details_from_helmfile, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_invalid_helmfile(caplog):
    """Testing an invalid helmfile being provided."""
    runner = CliRunner()
    result = runner.invoke(get_microservice_details_from_helmfile, args=[
        "--state-values-file", "site-values.yaml",
        "--path-to-helmfile", "helmfile.yaml"])

    assert "helmfile.yaml is not found" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name,too-many-locals
def test_get_microservice_details_from_helmfile_success(monkeypatch, resource_path_root, tmp_path, caplog):
    """Testing getting microservice details from helmfile."""
    chart_name_1 = "eric-cloud-native-base"
    chart_version_1 = "74.0.0"
    chart_name_2 = "eric-oss-dmm"
    chart_version_2 = "0.0.0-223"
    chart_name_3 = "eric-tm-ingress-controller-cr-crd"
    chart_version_3 = "11.0.0+29"
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile-reduced.tgz.test")
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    site_values_file = os.path.join(resource_path_root, "site-values-template.yaml")
    utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name_1}-{chart_version_1}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name_1}-{chart_version_1}.tgz"))
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name_2}-{chart_version_2}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name_2}-{chart_version_2}.tgz"))
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name_3}-{chart_version_3}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name_3}-{chart_version_3}.tgz"))

    # pylint: disable=unused-argument
    def download_chart(deps, netrc, mask, cwd, clean_up):
        return True
    monkeypatch.setattr(cihelm, "fetch", download_chart)

    runner = CliRunner()
    result = runner.invoke(get_microservice_details_from_helmfile, args=[
        "--state-values-file", site_values_file,
        "--path-to-helmfile", helmfile_path])
    LOGGER.info(os.listdir(os.getcwd()))
    assert "Fetching charts using the helmfile information" in caplog.text
    assert os.path.exists(os.path.join(os.getcwd(), HELMFILE_BUILD_OUTPUT_FILE)) is True
    assert os.path.exists(os.path.join(os.getcwd(), SERVICE_OUTPUT_FLATFILE)) is True
    assert os.path.exists(os.path.join(os.getcwd(), SERVICE_OUTPUT_JSON)) is True
    with open(os.path.join(os.getcwd(), SERVICE_OUTPUT_JSON), "r", encoding="utf-8") as json_data:
        input_json = json.loads(json_data.read())
        assert chart_name_1 in input_json
        assert "product_number" in input_json[chart_name_1]
        assert "version" in input_json[chart_name_1]
        assert "location" in input_json[chart_name_1]
        assert input_json[chart_name_1]["product_number"] == "CXD 101 001"
        assert input_json[chart_name_1]["version"] == "74.0.0"
        assert input_json[chart_name_1]["eric-tm-ingress-controller-cr"]["product_number"] == "CXC 201 2193"
    with open(os.path.join(os.getcwd(), "helmServicesContent.txt"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert f"{chart_name_1}:{chart_version_1}:CXD 101 001" in text
    assert "eric-data-document-database-pg:8.1.0+35:CXC 201 1475" in text
    assert result.exit_code == 0


# pylint: disable=invalid-name,too-many-locals
def test_cleanup_success(caplog):
    """Testing initial cleanup."""
    LOGGER.info(os.listdir(os.getcwd()))
    assert os.path.exists(os.path.join(os.getcwd(), HELMFILE_COMPILED_BUILD_OUTPUT_FILE)) is True

    runner = CliRunner()
    result = runner.invoke(get_microservice_details_from_helmfile, args=[
        "--state-values-file", "site-values.yaml",
        "--path-to-helmfile", "helmfile.yaml"])

    LOGGER.info(os.listdir(os.getcwd()))
    assert os.path.exists(os.path.join(os.getcwd(), HELMFILE_BUILD_OUTPUT_FILE)) is True
    assert os.path.exists(os.path.join(os.getcwd(), HELMFILE_COMPILED_BUILD_OUTPUT_FILE)) is False
    assert "helmfile.yaml is not found" in caplog.text
    assert result.exit_code == 1
