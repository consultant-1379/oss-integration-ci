"""Test for the Helmfile Executor get_shared_images."""
import json
import os.path
import pytest
import requests
import yaml
from click.testing import CliRunner
from mock_response import MockResponse

from bin.helmfile_executor import get_shared_images


FILENAME = "helmfile/helmfile.yaml"
SAMPLE_ERIC_PRODUCT_INFO = """
images:
  keycloakClient:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "keycloak-client"
    tag: "1.0.0-89"
"""
SAMPLE_ERIC_PRODUCT_INFO_2 = """
images:
  keycloakClient:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "keycloak-client"
    tag: "1.0.0-90"
  otherImage:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "other-image"
    tag: "1.0.0-11"
"""
SAMPLE_ERIC_PRODUCT_INFO_3 = """
images:
  burOrchestrator:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "bur-orchestrator"
    tag: "1.0.0-91"
  otherImage:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "other-image"
    tag: "1.0.0-8"
"""
SAMPLE_ERIC_PRODUCT_INFO_4 = """
images:
  burOrchestrator:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "bur-orchestrator"
    tag: "1.0.0-90"
  otherImage:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "other-image"
    tag: "1.0.0-4"
"""
LATEST_VERSIONS_JSON_KC = """{
    "tags": ["1.0.0-89", "1.0.0-90"]
}"""
LATEST_VERSIONS_JSON_OI = """{
    "tags": ["1.0.0-11", "1.0.0-8", "1.0.0-4"]
}"""
LATEST_VERSIONS_JSON_BO = """{
    "tags": ["1.0.0-91", "1.0.0-90"]
}"""
SHARED_IMAGES_FILE = os.getcwd() + "/helmfile_shared_images.json"
IMAGE_NAME = "armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client"
HELMFILE_IMAGES_TO_BE_UPDATED = "./outdated_images_per_chart.json"


@pytest.mark.parametrize("test_cli_args, expected", [
    ('', {'output': "Error: Missing option \"--path-to-helmfile\""}),
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
def test_get_shared_images_bad_args(test_cli_args, expected):
    """Test argument handling in helmfile_exector.get_shared_images"""
    runner = CliRunner()
    result = runner.invoke(get_shared_images, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_successful_run_chart_with_no_images(caplog):
    """Test for a successful run where the chart has no images."""
    with open(FILENAME, "w", encoding="utf-8") as helmfile:
        helmfile.writelines("name: eric-oss-common-base")
    if not os.path.exists("eric-oss-common-base"):
        os.mkdir("eric-oss-common-base")

    with open("eric-oss-common-base/eric-product-info.yaml", "w", encoding="utf-8") as common_base_eric_product_info:
        common_base_eric_product_info.writelines("test: value")

    runner = CliRunner()
    result = runner.invoke(get_shared_images, args=[
        "--path-to-helmfile", FILENAME])
    assert "Searching for images in the eric-product-info file for eric-oss-common-base" in caplog.text
    assert "No images found in the eric-product-info file for eric-oss-common-base" in caplog.text
    assert result.exit_code == 0


def test_successful_run_with_single_chart():
    """Test for a successful run with a single chart."""
    with open(FILENAME, "w", encoding="utf-8") as helmfile:
        helmfile.writelines("name: eric-oss-common-base")
    if not os.path.exists("eric-oss-common-base"):
        os.mkdir("eric-oss-common-base")

    with open("eric-oss-common-base/eric-product-info.yaml", "w", encoding="utf-8") as common_base_eric_product_info:
        common_base_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO)

    runner = CliRunner()
    result = runner.invoke(get_shared_images, args=[
        "--path-to-helmfile", FILENAME])
    assert os.path.exists(SHARED_IMAGES_FILE)
    with open(SHARED_IMAGES_FILE, "r", encoding="utf-8") as images_file:
        shared_images_dict = yaml.safe_load(images_file)
    assert shared_images_dict[IMAGE_NAME]["Number of occurrences"] == 1
    assert shared_images_dict[IMAGE_NAME]["Different versions and frequency"]["1.0.0-89"] == 1
    assert "eric-oss-common-base" in shared_images_dict[IMAGE_NAME]["Sources of occurrences"]
    os.remove("eric-oss-common-base/eric-product-info.yaml")
    os.remove(SHARED_IMAGES_FILE)
    assert result.exit_code == 0


def test_successful_run_with_multiple_charts(monkeypatch):
    """Test for a successful run with multiple charts."""
    with open(FILENAME, "w", encoding="utf-8") as helmfile:
        helmfile.writelines("name: eric-oss-common-base\n")
        helmfile.writelines("name: eric-cloud-native-base")
    if not os.path.exists("eric-oss-common-base"):
        os.mkdir("eric-oss-common-base")
    if not os.path.exists("eric-cloud-native-base"):
        os.mkdir("eric-cloud-native-base")

    with open("eric-oss-common-base/eric-product-info.yaml", "w", encoding="utf-8") as common_base_eric_product_info, \
            open("eric-cloud-native-base/eric-product-info.yaml", "w",
                 encoding="utf-8") as cloud_native_eric_product_info:
        common_base_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO)
        cloud_native_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO)

    # pylint: disable=unused-argument, too-many-arguments
    def get_request(url, auth, timeout):
        if "keycloak-client" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_KC)
        elif "other-image" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_OI)
        else:
            response = MockResponse(content=LATEST_VERSIONS_JSON_BO)
        return response

    monkeypatch.setattr(requests, "get", get_request)

    runner = CliRunner()
    result = runner.invoke(get_shared_images, args=[
        "--path-to-helmfile", FILENAME])
    assert os.path.exists(SHARED_IMAGES_FILE)
    with open(SHARED_IMAGES_FILE, "r", encoding="utf-8") as images_file:
        shared_images_dict = yaml.safe_load(images_file)
    assert shared_images_dict[IMAGE_NAME]["Number of occurrences"] == 2
    assert shared_images_dict[IMAGE_NAME]["Different versions and frequency"]["1.0.0-89"] == 2
    assert "eric-oss-common-base" in shared_images_dict[IMAGE_NAME]["Sources of occurrences"]
    assert "eric-cloud-native-base" in shared_images_dict[IMAGE_NAME]["Sources of occurrences"]
    os.remove("eric-oss-common-base/eric-product-info.yaml")
    os.remove("eric-cloud-native-base/eric-product-info.yaml")
    os.remove(SHARED_IMAGES_FILE)
    assert result.exit_code == 0


def test_for_latest_image_comparison(monkeypatch):
    """Test for a successful run with a chart not using the latest image version."""
    with open(FILENAME, "w", encoding="utf-8") as helmfile:
        helmfile.writelines("name: eric-oss-common-base\n")
        helmfile.writelines("name: eric-cloud-native-base")
    if not os.path.exists("eric-cloud-native-base"):
        os.mkdir("eric-cloud-native-base")
    os.makedirs(os.path.dirname("eric-oss-common-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml"),
                exist_ok=True)
    os.makedirs(os.path.dirname("eric-oss-common-base/charts/log-shipper/eric-product-info.yaml"),
                exist_ok=True)
    os.makedirs(os.path.dirname("eric-cloud-native-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml"),
                exist_ok=True)

    with open("eric-oss-common-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml", "a", encoding="utf-8")\
            as common_base_subchart_eric_product_info_gr,\
         open("eric-oss-common-base/charts/log-shipper/eric-product-info.yaml", "a", encoding="utf-8")\
            as common_base_subchart_eric_product_info_log,\
         open("eric-cloud-native-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml", "a", encoding="utf-8")\
            as cloud_native_subchart_eric_product_info,\
         open("eric-oss-common-base/eric-product-info.yaml", "a", encoding="utf-8") as common_base_eric_product_info,\
         open("eric-cloud-native-base/eric-product-info.yaml", "a",
              encoding="utf-8") as cloud_native_eric_product_info:
        common_base_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO)
        common_base_subchart_eric_product_info_gr.writelines(SAMPLE_ERIC_PRODUCT_INFO)
        common_base_subchart_eric_product_info_gr.writelines(SAMPLE_ERIC_PRODUCT_INFO_3)
        common_base_subchart_eric_product_info_log.writelines(SAMPLE_ERIC_PRODUCT_INFO_4)
        cloud_native_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO_2)
        cloud_native_subchart_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO_4)

    # pylint: disable=unused-argument, too-many-arguments
    def get_request(url, auth, timeout):
        if "keycloak-client" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_KC)
        elif "other-image" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_OI)
        else:
            response = MockResponse(content=LATEST_VERSIONS_JSON_BO)
        return response

    monkeypatch.setattr(requests, "get", get_request)

    runner = CliRunner()
    result = runner.invoke(get_shared_images, args=[
        "--path-to-helmfile", FILENAME])
    assert os.path.exists(os.path.join(os.getcwd(), HELMFILE_IMAGES_TO_BE_UPDATED)) is True
    with open(os.path.join(os.getcwd(), HELMFILE_IMAGES_TO_BE_UPDATED), 'r', encoding='utf-8') as json_data:
        input_json = json.loads(json_data.read())
    assert "1.0.0-89" in input_json["eric-oss-common-base"]["keycloak-client"]["Current version"]
    assert "1.0.0-90" in input_json["eric-oss-common-base"]["keycloak-client"]["Latest version"]
    assert "1.0.0-90" in (input_json["eric-cloud-native-base"]["charts"]["eric-gr-bur-orchestrator"]
                                    ["bur-orchestrator"]["Current version"])
    assert "1.0.0-91" in (input_json["eric-cloud-native-base"]["charts"]["eric-gr-bur-orchestrator"]
                                    ["bur-orchestrator"]["Latest version"])
    os.remove("eric-oss-common-base/eric-product-info.yaml")
    os.remove("eric-cloud-native-base/eric-product-info.yaml")
    os.remove("eric-oss-common-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml")
    os.remove("eric-oss-common-base/charts/log-shipper/eric-product-info.yaml")
    os.remove("eric-cloud-native-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml")
    os.remove(HELMFILE_IMAGES_TO_BE_UPDATED)
    os.remove(FILENAME)
    assert result.exit_code == 0
