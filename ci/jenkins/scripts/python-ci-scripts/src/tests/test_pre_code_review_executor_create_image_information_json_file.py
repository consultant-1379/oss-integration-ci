"""Test for Pre Code Review Executor for Create Image Information Json File"""
import os
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import check_eric_product_info_images


SAMPLE_ERIC_PRODUCT_INFO = """
images:
  keycloakClient:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "keycloak-client"
    tag: "1.0.0-88"
"""

SAMPLE_ERIC_PRODUCT_INFO_2 = """
images:
  keycloakClient:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "keycloak-client"
    tag: "1.0.0-112"
"""

OUTPUT_FILE = "image_information_list.txt"
ERIC_PRODUCT_INFO_PATH = "eric-oss-integration-chart-chassis/eric-product-info.yaml"
ERIC_PRODUCT_INFO_HELMFILE_PATH = "helmfile/eric-product-info.yaml"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --chart-full-path
    ("",
     {'output': "Error: Missing option \"--chart-full-path\""}),
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
def test_check_eric_product_info_images_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.check_eric_product_info_images"""
    runner = CliRunner()
    result = runner.invoke(check_eric_product_info_images, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_check_eric_product_info_images_success(monkeypatch, caplog):
    """Test check_eric_product_info on chart for success"""
    chart_full_path = ".//.bob/__helmChartDockerImageName__"

    if not os.path.exists("eric-oss-integration-chart-chassis"):
        os.mkdir("eric-oss-integration-chart-chassis")

    with open(ERIC_PRODUCT_INFO_PATH, "a", encoding="utf-8") as chart_chassis_eric_product_info:
        chart_chassis_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO)

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(check_eric_product_info_images, args=[
        "--chart-full-path", chart_full_path])
    assert result.exit_code == 0
    assert os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "r", encoding="utf-8") as outdated_image_file:
        ticket_info = outdated_image_file.readlines()
    assert "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client:1.0.0-88" in ticket_info
    assert "Eric Product Info Images Check completed successfully" in caplog.text
    os.remove(OUTPUT_FILE)


# pylint: disable=too-many-locals
def test_check_eric_product_info_images_failure(monkeypatch, caplog):
    """Test check_eric_product_info on chart for failure"""
    chart_full_path = "./eric-oss-integration-chart-chassis"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(check_eric_product_info_images, args=[
        "--chart-full-path", chart_full_path])
    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text


# pylint: disable=too-many-locals
def test_check_eric_product_info_images_helmfile_success(monkeypatch, caplog):
    """Test check_eric_product_info on chart for success"""
    chart_full_path = "./helmfile"

    if not os.path.exists(chart_full_path):
        os.mkdir(chart_full_path)

    with open(ERIC_PRODUCT_INFO_HELMFILE_PATH, "a", encoding="utf-8") as helmfile:
        helmfile.writelines(SAMPLE_ERIC_PRODUCT_INFO_2)

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(check_eric_product_info_images, args=[
        "--chart-full-path", chart_full_path])
    assert result.exit_code == 0
    assert os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "r", encoding="utf-8") as outdated_image_file:
        ticket_info = outdated_image_file.readlines()
    assert "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client:1.0.0-112" in ticket_info
    assert "Eric Product Info Images Check completed successfully" in caplog.text
    os.remove(OUTPUT_FILE)
