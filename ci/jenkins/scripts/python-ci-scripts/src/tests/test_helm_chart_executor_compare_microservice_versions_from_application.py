"""Test for helm chart executor compare_microservice_versions_from_application."""
import os
from unittest import mock
import pytest
from click.testing import CliRunner
from requests.exceptions import HTTPError

from bin.helm_chart_executor import compare_microservice_versions_from_application
from lib import helmfile
from lib import utils
from lib import get_all_microservices_from_helmfile
from lib import cihelm

USERNAME = "gerrit-username"
PASSWORD = "gerrit-password"
FUNCTIONAL_USER_USERNAME = "username"
FUNCTIONAL_USER_PASSWORD = "user-password"
CHART_NAME = "eric-oss-common-base"
PATH_TO_HELMFILE = "eric-eiae-helmfile/helmfile.yaml"
STATE_VALUES_FILE = "eric-eiae-helmfile/build-environment/tags_true.yaml"
MOCK_RELEASES_DICT_ADP = {"eric-adp-gui-aggregator-service": {
    "name": "eric-adp-gui-aggregator-service",
    "version": "2.6.0+30",
    "url": "https://arm.seli.gic.ericsson.se/artifactory/proj-eea-released-helm"
}}
MOCK_RELEASES_DICT_NON_ADP = {"eric-eo-credential-manager": {
    "name": "eric-eo-credential-manager",
    "version": "2.0.0-26",
    "url": "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm"
}}
MOCK_RELEASES_DICT_VALID = {"eric-adp-gui-aggregator-service": {
    "name": "eric-adp-gui-aggregator-service",
    "version": "2.6.0+30",
    "url": "https://arm.seli.gic.ericsson.se/artifactory/proj-eea-released-helm"
}}
MOCK_RELEASES_DICT_BAD_URLS = {
    "eric-evnfm-rbac-no-url": {
        "version": "0.68.0+1",
        "eric-evnfm-rbac-invalid-url": {
            "name": "eric-evnfm-rbac-invalid-url",
            "version": "0.68.0+1",
            "url": "file://someFile"
        }
    }
}
COMPONENT_NAME_REPO_VALID_EXPECTED_LINES_CSV = """Component,Current Version,Latest Version,Repo
eric-adp-gui-aggregator-service,2.6.0+30,2.6.0+31,https://arm.seli.gic.ericsson.se/artifactory/proj-eea-released-helm
"""
COMPONENT_MISMATCH_VALID_EXPECTED_LINES = """Version mismatch: eric-adp-gui-aggregator-service
Current version: 2.6.0+30
Latest version: 2.6.0+31\n
"""
COMPONENT_NAME_REPO_VERSION_CSV = "component_name_repo_version.csv"
COMPONENT_VERSION_MISMATCH = "component_version_mismatch.txt"
ARTIFACT_PROPERTIES = "artifact.properties"


def patch_common_functions(monkeypatch):
    """Function used to patch commonly used functions in unit tests."""
    # pylint: disable=unused-argument
    def build_netrc_file_with_repo_credentials_from_helmfile(state_values_file, path_to_helmfile, workspace):
        return True

    # pylint: disable=unused-argument
    def fetch(deps, netrc, mask, cwd, clean_up):
        return True

    # pylint: disable=unused-argument
    def extract_tar_file(tarfile, directory):
        return True

    monkeypatch.setattr(helmfile, "build_netrc_file_with_repo_credentials_from_helmfile",
                        build_netrc_file_with_repo_credentials_from_helmfile)
    monkeypatch.setattr(cihelm, "fetch",
                        fetch)
    monkeypatch.setattr(utils, "extract_tar_file", extract_tar_file)


@pytest.mark.parametrize("test_cli_args, expected", [
    # No chart-name
    ("--state-values-file ${PWD}/eric-eiae-helmfile/build-environment/tags_true.yaml " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--chart-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local " +
     "--chart-version 0.2.0-73 "
     "--gerrit-username joe"
     "-gerrit-password bloggs"
     "--username username"
     "--user-password password",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No path-to-helmfile
    ("--chart-name eric-oss-common-base " +
     "--state-values-file ${PWD}/eric-eiae-helmfile/build-environment/tags_true.yaml " +
     "--chart-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local " +
     "--chart-version 0.2.0-73"
     "--gerrit-username joe"
     "--gerrit-password bloggs"
     "--username username"
     "--user-password password",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No state-values-file
    ("--chart-name eric-oss-common-base " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--chart-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local " +
     "--chart-version 0.2.0-73"
     "--gerrit-username joe"
     "--gerrit-password bloggs"
     "--username username"
     "--user-password password",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No chart-repo
    ("--state-values-file ${PWD}/eric-eiae-helmfile/build-environment/tags_true.yaml " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--chart-name eric-oss-common-base " +
     "--chart-version 0.2.0-73"
     "--gerrit-username joe"
     "--gerrit-password bloggs"
     "--username username"
     "--user-password password",
     {'output': "Error: Missing option \"--chart-repo\""}),
    # No chart-version
    ("--state-values-file ${PWD}/eric-eiae-helmfile/build-environment/tags_true.yaml " +
     "--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml " +
     "--chart-name eric-oss-common-base " +
     "--chart-repo https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local "
     "--gerrit-username joe"
     "--gerrit-password bloggs"
     "--username username"
     "--user-password password",
     {'output': "Error: Missing option \"--chart-version\""}),
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
def test_compare_microservice_versions_from_application_bad_args(test_cli_args, expected):
    """Test argument handling for helm_chart_executor.compare_microservice_versions_from_application."""
    runner = CliRunner()
    result = runner.invoke(compare_microservice_versions_from_application, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD,
                              "GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_compare_microservice_versions_in_application_incorrect_url(monkeypatch, caplog):
    """Test comparing the microservices versions in an application when a 404 error is raised."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def parse_and_write_chart_dependencies_to_file(chart_root_dir, services, output_file):
        return MOCK_RELEASES_DICT_ADP

    # pylint: disable=unused-argument
    def get_latest_artifact_version_from_repo(url, appname, adp_component):
        raise HTTPError("404 Error")

    # Patch commonly used methods
    patch_common_functions(monkeypatch)

    monkeypatch.setattr(get_all_microservices_from_helmfile, "parse_and_write_chart_dependencies_to_file",
                        parse_and_write_chart_dependencies_to_file)
    monkeypatch.setattr(utils, "get_latest_artifact_version_from_repo",
                        get_latest_artifact_version_from_repo)

    result = runner.invoke(compare_microservice_versions_from_application, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--chart-name", CHART_NAME,
        "--chart-version", "0.1.0-1283",
        "--chart-repo", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD,
        "--username", FUNCTIONAL_USER_USERNAME,
        "--user-password", FUNCTIONAL_USER_PASSWORD,
    ])

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)

    assert "App Latest Version: Not Found" in caplog.text
    assert "404 Error" in caplog.text
    assert result.exit_code == 0

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
    del os.environ['FUNCTIONAL_USER_USERNAME']
    del os.environ['FUNCTIONAL_USER_PASSWORD']


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD,
                              "GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_compare_included_version_against_latest_version_non_adp(monkeypatch, caplog):
    """Test comparing the microservices versions in an application when component is not an adp component."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def parse_and_write_chart_dependencies_to_file(chart_root_dir, services, output_file):
        return MOCK_RELEASES_DICT_NON_ADP

    # pylint: disable=unused-argument
    def get_latest_artifact_version_from_repo(artifact_repo_url, artifact_name):
        with open(ARTIFACT_PROPERTIES, "w", encoding="utf-8") as file:
            file.write("INT_CHART_VERSION:2.0.0-27")

    # Patch commonly used methods
    patch_common_functions(monkeypatch)

    monkeypatch.setattr(get_all_microservices_from_helmfile, "parse_and_write_chart_dependencies_to_file",
                        parse_and_write_chart_dependencies_to_file)
    monkeypatch.setattr(utils, "get_latest_artifact_version_from_repo",
                        get_latest_artifact_version_from_repo)

    result = runner.invoke(compare_microservice_versions_from_application, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--chart-name", CHART_NAME,
        "--chart-version", "0.1.0-1283",
        "--chart-repo", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD,
        "--username", FUNCTIONAL_USER_USERNAME,
        "--user-password", FUNCTIONAL_USER_PASSWORD,
    ])

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)

    os.remove(ARTIFACT_PROPERTIES)
    assert "App Latest Version: 2.0.0-27" in caplog.text
    assert "App Name: eric-eo-credential-manager" in caplog.text
    assert "App URL: https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm" in caplog.text
    assert "App Version: 2.0.0-26" in caplog.text
    assert result.exit_code == 0

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
    del os.environ['FUNCTIONAL_USER_USERNAME']
    del os.environ['FUNCTIONAL_USER_PASSWORD']


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD,
                              "GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_compare_included_version_against_latest_version_full(monkeypatch, caplog):
    """Test the full expected flow of comparing the microservices versions in an application."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def parse_and_write_chart_dependencies_to_file(chart_root_dir, services, output_file):
        return MOCK_RELEASES_DICT_VALID

    # pylint: disable=unused-argument
    def get_latest_artifact_version_from_repo(artifact_repo_url, artifact_name, adp_component):
        with open(ARTIFACT_PROPERTIES, "w", encoding="utf-8") as file:
            file.write("INT_CHART_VERSION:2.6.0+31")

    # Patch commonly used methods
    patch_common_functions(monkeypatch)

    monkeypatch.setattr(get_all_microservices_from_helmfile, "parse_and_write_chart_dependencies_to_file",
                        parse_and_write_chart_dependencies_to_file)
    monkeypatch.setattr(utils, "get_latest_artifact_version_from_repo",
                        get_latest_artifact_version_from_repo)

    result = runner.invoke(compare_microservice_versions_from_application, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--chart-name", CHART_NAME,
        "--chart-version", "0.1.0-1283",
        "--chart-repo", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD,
        "--username", FUNCTIONAL_USER_USERNAME,
        "--user-password", FUNCTIONAL_USER_PASSWORD,
    ])

    with open(COMPONENT_NAME_REPO_VERSION_CSV, "r", encoding="utf-8") as file:
        csv_lines = file.read()
    with open(COMPONENT_VERSION_MISMATCH, "r", encoding="utf-8") as file:
        mismatch_lines = file.read()
    with open(ARTIFACT_PROPERTIES, "r", encoding="utf-8") as file:
        latest_version = file.read()

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)
    os.remove(ARTIFACT_PROPERTIES)

    # assert app_details_lines == COMPONENT_NAME_REPO_VALID_EXPECTED_LINES

    assert csv_lines == COMPONENT_NAME_REPO_VALID_EXPECTED_LINES_CSV

    assert mismatch_lines == COMPONENT_MISMATCH_VALID_EXPECTED_LINES

    assert "INT_CHART_VERSION:2.6.0+31" == latest_version

    assert "App Latest Version: 2.6.0+31" in caplog.text
    assert "App Name: eric-adp-gui-aggregator-service" in caplog.text
    assert "App URL: https://arm.seli.gic.ericsson.se/artifactory/proj-eea-released-helm" in caplog.text
    assert "App Version: 2.6.0+30" in caplog.text

    assert result.exit_code == 0

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
    del os.environ['FUNCTIONAL_USER_USERNAME']
    del os.environ['FUNCTIONAL_USER_PASSWORD']


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD,
                              "GERRIT_USERNAME": USERNAME, "GERRIT_PASSWORD": PASSWORD})
def test_compare_included_version_against_latest_version_bad_urls(monkeypatch, caplog):
    """Test comparing the microservices versions in an application with bad urls."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def parse_and_write_chart_dependencies_to_file(chart_root_dir, services, output_file):
        return MOCK_RELEASES_DICT_BAD_URLS

    # Patch commonly used methods
    patch_common_functions(monkeypatch)

    monkeypatch.setattr(get_all_microservices_from_helmfile, "parse_and_write_chart_dependencies_to_file",
                        parse_and_write_chart_dependencies_to_file)

    result = runner.invoke(compare_microservice_versions_from_application, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--chart-name", CHART_NAME,
        "--chart-version", "0.1.0-1283",
        "--chart-repo", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
        "--gerrit-username", USERNAME,
        "--gerrit-password", PASSWORD,
        "--username", FUNCTIONAL_USER_USERNAME,
        "--user-password", FUNCTIONAL_USER_PASSWORD,
    ])

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)

    assert "No URL for: eric-evnfm-rbac-invalid-url" in caplog.text
    assert "URL not in component list for Appname: eric-evnfm-rbac-no-url" in caplog.text
    assert "Version Mismatch - Current version: 0.68.0+1 New Version: Not Found" in caplog.text
    assert "App Name: eric-evnfm-rbac-invalid-url" in caplog.text
    assert "App URL: Not Found" in caplog.text
    assert "App Version: 0.68.0+1" in caplog.text

    assert result.exit_code == 0

    del os.environ['GERRIT_USERNAME']
    del os.environ['GERRIT_PASSWORD']
    del os.environ['FUNCTIONAL_USER_USERNAME']
    del os.environ['FUNCTIONAL_USER_PASSWORD']
