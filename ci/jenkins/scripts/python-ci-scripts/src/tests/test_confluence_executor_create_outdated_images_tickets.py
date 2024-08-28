"""Test for the Confluence Executor create_outdated_images_tickets."""
import os.path

import pytest
import requests
from click.testing import CliRunner
from mock_response import MockResponse

from bin.confluence_executor import create_outdated_images_tickets
from lib import jira
from lib import cihelm
from lib import utils

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
    tag: "1.0.0-90"
  otherImage:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "other-image"
    tag: "1.0.0-9"
"""
SAMPLE_ERIC_PRODUCT_INFO_3 = """
images:
  burOrchestrator:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "bur-orchestrator"
    tag: "1.0.0-95"
  otherImage:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "other-image"
    tag: "1.0.0-14"
"""
SAMPLE_ERIC_PRODUCT_INFO_4 = """
images:
  burOrchestrator:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "bur-orchestrator"
    tag: "1.0.0-99"
  otherImage:
    productName: "Identity Access Management"
    productNumber: "TBC"
    registry: "armdocker.rnd.ericsson.se"
    repoPath: "proj-orchestration-so"
    name: "other-image"
    tag: "1.0.0-5"
"""
TICKET_INFO_FILE = "outdated-ticket-file.txt"
EXISTING_TICKETS_JSON = """{
    "issues": [{
        "fields": {
            "status": {
                "name": "Open"
            },
            "summary": "This is the chart name: eric-cloud-native-base"
        }
    }, {
        "fields": {
            "status": {
                "name": "Closed"
            },
            "summary": "This is the chart name: eric-oss-common-base"
        }
    }]
}"""
LATEST_VERSIONS_JSON_KC = """{
    "tags": ["1.0.0-89", "1.0.0-90"]
}"""
LATEST_VERSIONS_JSON_OI = """{
    "tags": ["1.0.0-11", "1.0.0-8", "1.0.0-4", "1.0.0-14"]
}"""
LATEST_VERSIONS_JSON_BO = """{
    "tags": ["1.0.0-91", "1.0.0-90"]
}"""
HELMFILE_FILENAME = "helmfile/helmfile.yaml"
CB_GR_BUR_ORCHESTRATOR_PRODUCT_INFO = "eric-oss-common-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml"
CN_GR_BUR_ORCHESTRATOR_PRODUCT_INFO = "eric-cloud-native-base/charts/eric-gr-bur-orchestrator/eric-product-info.yaml"
COMMON_BASE_PRODUCT_INFO = "eric-oss-common-base/eric-product-info.yaml"
CLOUD_NATIVE_PRODUCT_INFO = "eric-cloud-native-base/eric-product-info.yaml"
LOG_SHIPPER_PRODUCT_INFO = "eric-oss-common-base/charts/log-shipper/eric-product-info.yaml"
USERNAME = "username"
PASSWORD = "password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No chart-full-path
    ("--create-tickets True --username joe --password pass",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No create-tickets
    ("--path-to-helmfile path --username joe --password pass",
     {'output': "Error: Missing option \"--create-tickets\""}),
    # No username
    ("--create-tickets True --path-to-helmfile path --password pass",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--create-tickets True --path-to-helmfile path --username joe",
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
def test_create_outdated_images_tickets_bad_args(test_cli_args, expected):
    """Test argument handling in confluence_exector.get_shared_images"""
    runner = CliRunner()
    result = runner.invoke(create_outdated_images_tickets, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_successful_run(monkeypatch, caplog):
    """Test for a successful run for creating outdated images tickets."""
    os.makedirs(os.path.dirname(HELMFILE_FILENAME))
    with open(HELMFILE_FILENAME, "w", encoding="utf-8") as helmfile:
        helmfile.writelines("name: eric-oss-common-base\n")
        helmfile.writelines("version: 1.1.1\n")
        helmfile.writelines("name: eric-cloud-native-base\n")
        helmfile.writelines("version: 1.1.1")
    if not os.path.exists("eric-cloud-native-base"):
        os.mkdir("eric-cloud-native-base")
    os.makedirs(os.path.dirname(CB_GR_BUR_ORCHESTRATOR_PRODUCT_INFO),
                exist_ok=True)
    os.makedirs(os.path.dirname(LOG_SHIPPER_PRODUCT_INFO),
                exist_ok=True)
    os.makedirs(os.path.dirname(CN_GR_BUR_ORCHESTRATOR_PRODUCT_INFO),
                exist_ok=True)

    with open(CB_GR_BUR_ORCHESTRATOR_PRODUCT_INFO, "a", encoding="utf-8")\
            as common_base_subchart_eric_product_info_gr,\
         open(LOG_SHIPPER_PRODUCT_INFO, "a", encoding="utf-8")\
            as common_base_subchart_eric_product_info_log,\
         open(CN_GR_BUR_ORCHESTRATOR_PRODUCT_INFO, "a", encoding="utf-8")\
            as cloud_native_subchart_eric_product_info,\
         open(COMMON_BASE_PRODUCT_INFO, "a", encoding="utf-8") as common_base_eric_product_info,\
         open(CLOUD_NATIVE_PRODUCT_INFO, "a",
              encoding="utf-8") as cloud_native_eric_product_info:
        common_base_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO)
        common_base_subchart_eric_product_info_gr.writelines(SAMPLE_ERIC_PRODUCT_INFO)
        common_base_subchart_eric_product_info_gr.writelines(SAMPLE_ERIC_PRODUCT_INFO_3)
        common_base_subchart_eric_product_info_log.writelines(SAMPLE_ERIC_PRODUCT_INFO_4)
        cloud_native_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO_2)
        cloud_native_subchart_eric_product_info.writelines(SAMPLE_ERIC_PRODUCT_INFO_4)

    # pylint: disable=unused-argument
    def fetch(path_to_helmfile):
        return True

    # pylint: disable=unused-argument, too-many-arguments
    def create_ticket(**kwargs):
        return True

    # pylint: disable=unused-argument, too-many-arguments
    def get_request(url, *args, **kwargs):
        if "keycloak-client" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_KC)
        elif "other-image" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_OI)
        elif "bur-orchestrator" in url:
            response = MockResponse(content=LATEST_VERSIONS_JSON_BO)
        else:
            response = MockResponse(content=EXISTING_TICKETS_JSON)
        return response

    def extract_tar_file(tar_file, directory):
        return True

    monkeypatch.setattr(cihelm, "cihelm_fetch", fetch)
    monkeypatch.setattr(jira, "create_jira", create_ticket)
    monkeypatch.setattr(requests, "get", get_request)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)

    runner = CliRunner()
    result = runner.invoke(create_outdated_images_tickets, args=[
        "--path-to-helmfile", HELMFILE_FILENAME,
        "--create-tickets", "True",
        "--skip-list", "None",
        "--username", USERNAME,
        "--password", PASSWORD])
    assert os.path.exists(TICKET_INFO_FILE)
    with open(TICKET_INFO_FILE, "r", encoding="utf-8") as outdated_image_file:
        ticket_info = outdated_image_file.readlines()
    assert "Chart: eric-oss-common-base, Image: armdocker.rnd.ericsson.se/proj-orchestration-so/keycloak-client, " \
           "Latest version: 1.0.0-90, Current version: 1.0.0-88\n" in ticket_info
    assert "Chart: eric-cloud-native-base/eric-gr-bur-orchestrator, " \
           "Image: armdocker.rnd.ericsson.se/proj-orchestration-so/other-image, " \
           "Latest version: 1.0.0-14, Current version: 1.0.0-5\n" in ticket_info
    assert "Removing eric-cloud-native-base as a ticket for this chart is active" in caplog.text
    assert "Creating tickets for the following charts: eric-oss-common-base" in caplog.text
    assert result.exit_code == 0
    os.remove(TICKET_INFO_FILE)
    os.remove(HELMFILE_FILENAME)
    os.remove(CB_GR_BUR_ORCHESTRATOR_PRODUCT_INFO)
    os.remove(CN_GR_BUR_ORCHESTRATOR_PRODUCT_INFO)
    os.remove(COMMON_BASE_PRODUCT_INFO)
    os.remove(CLOUD_NATIVE_PRODUCT_INFO)
    os.remove(LOG_SHIPPER_PRODUCT_INFO)
    del os.environ['FUNCTIONAL_USER_USERNAME']
    del os.environ['FUNCTIONAL_USER_PASSWORD']
