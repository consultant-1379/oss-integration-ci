"""Test for helmfile executor compare_application_versions_from_helmfile."""
import os
from unittest import mock
import pytest
from click.testing import CliRunner
from requests.exceptions import HTTPError
from bin.helmfile_executor import compare_application_versions_from_helmfile
from lib import helmfile
from lib import utils

USERNAME = "username"
PASSWORD = "password"
PATH_TO_HELMFILE = "eric-eiae-helmfile/helmfile.yaml"
STATE_VALUES_FILE = "eric-eiae-helmfile/build-environment/tags_true.yaml"
MOCK_RELEASES_DICT_NON_ADP = {"eric-aiml-model-lcm-crd": {
    "name": "eric-aiml-model-lcm-crd",
    "version": "0.1.0-71",
    "chart": "gaia-mlops-drop/eric-aiml-model-lcm-crd",
    "labels": {"csar": "eric-oss-ml-execution-env"},
    "installed": "true",
    "condition": "eric-aiml-model-lcm-crd.enabled",
    "namespace": "eric-crd-ns",
    "values": ["./values-templates/eric-aiml-model-lcm-crd-site-values.yaml.gotmpl"],
    "url": "https://arm.seli.gic.ericsson.se/artifactory/something"}}
MOCK_RELEASES_DICT_VALID = {"eric-tm-ingress-controller-cr-crd": {
    "name": "eric-tm-ingress-controller-cr-crd",
    "version": "11.1.0+131",
    "chart": "adp-gs-all/eric-tm-ingress-controller-cr-crd",
    "labels": {"csar": "eric-cloud-native-base"},
    "installed": "null",
    "condition": "eric-tm-ingress-controller-cr-crd.enabled",
    "namespace": "eric-crd-ns",
    "values": ["./values-templates/eric-tm-ingress-controller-cr-crd-site-values.yaml.gotmpl"],
    "url": "https://arm.sero.gic.ericsson.se/artifactory/something"}
}
MOCK_RELEASES_DICT_BAD_URLS = {"eric-tm-ingress-controller-cr-crd-no-url": {
    "name": "eric-tm-ingress-controller-cr-crd-no-url",
    "version": "11.1.0+131",
    "chart": "adp-gs-all/eric-tm-ingress-controller-cr-crd",
    "labels": {"csar": "eric-cloud-native-base"},
    "installed": "null",
    "condition": "eric-tm-ingress-controller-cr-crd.enabled",
    "namespace": "eric-crd-ns",
    "values": ["./values-templates/eric-tm-ingress-controller-cr-crd-site-values.yaml.gotmpl"]
}, "eric-tm-ingress-controller-cr-crd-invalid-url": {
    "name": "eric-tm-ingress-controller-cr-crd-invalid-url",
    "version": "11.1.0+131",
    "chart": "adp-gs-all/eric-tm-ingress-controller-cr-crd",
    "labels": {"csar": "eric-cloud-native-base"},
    "installed": "null",
    "condition": "eric-tm-ingress-controller-cr-crd.enabled",
    "namespace": "eric-crd-ns",
    "values": ["./values-templates/eric-tm-ingress-controller-cr-crd-site-values.yaml.gotmpl"],
    "url": "file://something"
}}
COMPONENT_NAME_REPO_VALID_EXPECTED_LINES_CSV = """Component,Current Version,Latest Version,Repo
eric-tm-ingress-controller-cr-crd,11.1.0+131,11.1.0+132,https://arm.sero.gic.ericsson.se/artifactory/something
"""
COMPONENT_MISMATCH_VALID_EXPECTED_LINES = """Version mismatch: eric-tm-ingress-controller-cr-crd
Current version: 11.1.0+131
Latest version: 11.1.0+132\n
"""
COMPONENT_NAME_REPO_VERSION_CSV = "component_name_repo_version.csv"
COMPONENT_VERSION_MISMATCH = "component_version_mismatch.txt"
ARTIFACT_PROPERTIES = "artifact.properties"
COMPILED_CONTENT_HELMFILE = "compiledContent_helmfile.yaml"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No path-to-helmfile
    ("--state-values-file ${PWD}/eric-eiae-helmfile/build-environment/tags_true.yaml ",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No state-values-file
    ("--path-to-helmfile $PWD/eric-eiae-helmfile/helmfile.yaml ",
     {'output': "Error: Missing option \"--state-values-file\""}),
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
def test_compare_application_versions_from_helmfile_bad_args(test_cli_args, expected):
    """Test argument handling for helmfile_executor.compare_application_versions_from_helmfile."""
    runner = CliRunner()
    result = runner.invoke(compare_application_versions_from_helmfile, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_compare_application_versions_from_helmfile_fail(monkeypatch, caplog):
    """Test the flow of comparing the application versions in a helmfile when an exception is raised."""

    runner = CliRunner()

    def compare_application_versions_in_helmfile(state_values_file, path_to_helmfile):
        raise Exception("Exception affecting compare_application_versions_in_helmfile")

    monkeypatch.setattr(helmfile, "compare_application_versions_in_helmfile",
                        compare_application_versions_in_helmfile)

    result = runner.invoke(compare_application_versions_from_helmfile, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE
    ])

    assert 'Compare Application Versions from Helmfile failed with the following error' in caplog.text
    assert 'Exception affecting compare_application_versions_in_helmfile' in caplog.text

    assert result.exit_code == 1


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_compare_application_versions_from_helmfile_full(monkeypatch, caplog):
    """Test the full expected flow of comparing the application versions in a helmfile."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def execute_helmfile_with_build_command(state_values_file, path_to_helmfile):
        return True

    # pylint: disable=unused-argument
    def split_content_from_helmfile_build_file():
        with open(COMPILED_CONTENT_HELMFILE, "w", encoding="utf-8") as compiled_content:
            compiled_content.write("Test file")

    # pylint: disable=unused-argument
    def gather_release_and_repo_info(filename, releases_dict, csar_dict, get_all_images):
        return MOCK_RELEASES_DICT_VALID

    # pylint: disable=unused-argument
    def get_latest_artifact_version_from_repo(artifact_repo_url, artifact_name, adp_component):
        with open(ARTIFACT_PROPERTIES, "w", encoding="utf-8") as artifact_properties:
            artifact_properties.write("INT_CHART_VERSION:11.1.0+132")

    monkeypatch.setattr(helmfile, "execute_helmfile_with_build_command", execute_helmfile_with_build_command)
    monkeypatch.setattr(helmfile, "split_content_from_helmfile_build_file", split_content_from_helmfile_build_file)
    monkeypatch.setattr(helmfile, "gather_release_and_repo_info", gather_release_and_repo_info)
    monkeypatch.setattr(utils, "get_latest_artifact_version_from_repo", get_latest_artifact_version_from_repo)

    result = runner.invoke(compare_application_versions_from_helmfile, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE
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
    os.remove(COMPILED_CONTENT_HELMFILE)

    assert csv_lines == COMPONENT_NAME_REPO_VALID_EXPECTED_LINES_CSV

    assert mismatch_lines == COMPONENT_MISMATCH_VALID_EXPECTED_LINES

    assert "INT_CHART_VERSION:11.1.0+132" == latest_version

    assert "App Latest Version: 11.1.0+132" in caplog.text
    assert "App Name: eric-tm-ingress-controller-cr-crd" in caplog.text
    assert "App URL: https://arm.sero.gic.ericsson.se/artifactory/something" in caplog.text
    assert "App Version: 11.1.0+131" in caplog.text

    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_compare_application_versions_from_helmfile_non_adp(monkeypatch, caplog):
    """Test comparing the application versions in a helmfile when component is not an adp component."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def execute_helmfile_with_build_command(state_values_file, path_to_helmfile):
        return True

    # pylint: disable=unused-argument
    def split_content_from_helmfile_build_file():
        with open(COMPILED_CONTENT_HELMFILE, "w", encoding="utf-8") as compiled_content:
            compiled_content.write("Test file")

    # pylint: disable=unused-argument
    def gather_release_and_repo_info(filename, releases_dict, csar_dict, get_all_images):
        return MOCK_RELEASES_DICT_NON_ADP

    # pylint: disable=unused-argument
    def get_latest_artifact_version_from_repo(artifact_repo_url, artifact_name):
        with open(ARTIFACT_PROPERTIES, "w", encoding="utf-8") as artifact_properties:
            artifact_properties.write("INT_CHART_VERSION:0.1.0-72")

    monkeypatch.setattr(helmfile, "execute_helmfile_with_build_command", execute_helmfile_with_build_command)
    monkeypatch.setattr(helmfile, "split_content_from_helmfile_build_file", split_content_from_helmfile_build_file)
    monkeypatch.setattr(helmfile, "gather_release_and_repo_info", gather_release_and_repo_info)
    monkeypatch.setattr(utils, "get_latest_artifact_version_from_repo", get_latest_artifact_version_from_repo)

    result = runner.invoke(compare_application_versions_from_helmfile, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE
    ])

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)
    os.remove(ARTIFACT_PROPERTIES)
    os.remove(COMPILED_CONTENT_HELMFILE)

    assert "App Latest Version: 0.1.0-72" in caplog.text
    assert "App Name: eric-aiml-model-lcm-crd" in caplog.text
    assert "App URL: https://arm.seli.gic.ericsson.se/artifactory/something" in caplog.text
    assert "App Version: 0.1.0-71" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_compare_application_versions_from_helmfile_incorrect_url(monkeypatch, caplog):
    """Test comparing the application versions in a helmfile when a 404 error is raised."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def execute_helmfile_with_build_command(state_values_file, path_to_helmfile):
        return True

    # pylint: disable=unused-argument
    def split_content_from_helmfile_build_file():
        with open(COMPILED_CONTENT_HELMFILE, "w", encoding="utf-8") as compiled_content:
            compiled_content.write("Test file")

    # pylint: disable=unused-argument
    def gather_release_and_repo_info(filename, releases_dict, csar_dict, get_all_images):
        return MOCK_RELEASES_DICT_VALID

    # pylint: disable=unused-argument
    def get_latest_artifact_version_from_repo(artifact_repo_url, artifact_name, adp_component):
        raise HTTPError("404 Error")

    monkeypatch.setattr(helmfile, "execute_helmfile_with_build_command", execute_helmfile_with_build_command)
    monkeypatch.setattr(helmfile, "split_content_from_helmfile_build_file", split_content_from_helmfile_build_file)
    monkeypatch.setattr(helmfile, "gather_release_and_repo_info", gather_release_and_repo_info)
    monkeypatch.setattr(utils, "get_latest_artifact_version_from_repo", get_latest_artifact_version_from_repo)

    result = runner.invoke(compare_application_versions_from_helmfile, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE
    ])

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)
    os.remove(COMPILED_CONTENT_HELMFILE)

    assert "App Latest Version: Not Found" in caplog.text
    assert "404 Error" in caplog.text
    assert result.exit_code == 0


@mock.patch.dict(os.environ, {"FUNCTIONAL_USER_USERNAME": USERNAME, "FUNCTIONAL_USER_PASSWORD": PASSWORD})
def test_compare_application_versions_from_helmfile_bad_urls(monkeypatch, caplog):
    """Test comparing the application versions in a helmfile with bad urls."""

    runner = CliRunner()

    # pylint: disable=unused-argument
    def execute_helmfile_with_build_command(state_values_file, path_to_helmfile):
        return True

    # pylint: disable=unused-argument
    def split_content_from_helmfile_build_file():
        with open(COMPILED_CONTENT_HELMFILE, "w", encoding="utf-8") as compiled_content:
            compiled_content.write("Test file")

    # pylint: disable=unused-argument
    def gather_release_and_repo_info(filename, releases_dict, csar_dict, get_all_images):
        return MOCK_RELEASES_DICT_BAD_URLS

    monkeypatch.setattr(helmfile, "execute_helmfile_with_build_command", execute_helmfile_with_build_command)
    monkeypatch.setattr(helmfile, "split_content_from_helmfile_build_file", split_content_from_helmfile_build_file)
    monkeypatch.setattr(helmfile, "gather_release_and_repo_info", gather_release_and_repo_info)

    result = runner.invoke(compare_application_versions_from_helmfile, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE
    ])

    os.remove(COMPONENT_NAME_REPO_VERSION_CSV)
    os.remove(COMPONENT_VERSION_MISMATCH)
    os.remove(COMPILED_CONTENT_HELMFILE)

    assert "No URL for: eric-tm-ingress-controller-cr-crd-invalid-url" in caplog.text
    assert "URL not in component list for Appname: eric-tm-ingress-controller-cr-crd-no-url" in caplog.text
    assert "Version Mismatch - Current version: 11.1.0+131 New Version: Not Found" in caplog.text
    assert "App Name: eric-tm-ingress-controller-cr-crd-invalid-url" in caplog.text
    assert "App URL: Not Found" in caplog.text
    assert "App Version: 11.1.0+131" in caplog.text

    assert result.exit_code == 0
