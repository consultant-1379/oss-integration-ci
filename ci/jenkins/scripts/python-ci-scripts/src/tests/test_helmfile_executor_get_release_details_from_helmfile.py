"""Test for helmfile executor get_release_details_from_helmfile."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from click.testing import CliRunner

from bin.helmfile_executor import get_release_details_from_helmfile
from lib import utils
from lib import helmfile
from lib import cihelm

HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
ALL_NAMES = ["eric-mesh-controller", "eric-cloud-native-base", "eric-cncs-oss-config", "eric-oss-common-base",
             "eric-oss-oran-support", "eric-eo-so", "eric-oss-pf", "eric-oss-uds", "eric-oss-adc", "eric-oss-dmm",
             "eric-topology-handling", "eric-oss-ericsson-adaptation", "eric-oss-app-mgr", "eric-oss-config-handling",
             "eric-oss-pm-stats-calc-handling"]
ALL_VERSIONS = ["10.0.0+34", "79.9.0", "0.0.0-48", "0.1.0-1236", "0.0.0-75", "3.13.0-37", "2.17.0-15", "5.11.0-24",
                "0.0.2-827", "0.0.0-223", "0.0.2-143", "0.1.0-979", "1.1.0-428", "0.0.0-173", "0.0.0-220"]
ALL_URLS = ["https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm",
            "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/,"
            "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/",
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/",
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local",
            "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"]
ENABLED_NAMES = ["eric-cloud-native-base", "eric-oss-dmm"]
ENABLED_VERSIONS = ["79.9.0", "0.0.0-223"]
ENABLED_URLs = ["https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/,"
                "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-so-gs-all-helm/",
                "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local"]
CWD = os.getcwd()


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state-values-file
    ("--path-to-helmfile path --get-all-images true --fetch-charts true " +
     "--helmfile-url path",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No path-to-helmfile
    ("--state-values-file file --get-all-images true --fetch-charts true " +
     "--helmfile-url path",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No --get-all-images
    ("--state-values-file file --path-to-helmfile path --fetch-charts true " +
     "--helmfile-url path",
     {'output': "Error: Missing option \"--get-all-images\""}),
    # No --fetch-charts
    ("--state-values-file file --path-to-helmfile path --get-all-images true " +
     "--helmfile-url path",
     {'output': "Error: Missing option \"--fetch-charts\""}),
    # No helmfile-url
    ("--state-values-file file --path-to-helmfile path --get-all-images true " +
     "--fetch-charts true",
     {'output': "Error: Missing option \"--helmfile-url\""}),
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
def test_get_release_details_from_helmfile_args(test_cli_args, expected):
    """Test argument handling in helmfile_executor.get_release_details_from_helmfile"""
    runner = CliRunner()
    result = runner.invoke(get_release_details_from_helmfile, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_failed_helmfile_build(caplog):
    """Test for failed helmfile build."""
    runner = CliRunner()
    result = runner.invoke(get_release_details_from_helmfile, args=[
        "--state-values-file", "file",
        "--path-to-helmfile", "path",
        "--get-all-images", "true",
        "--fetch-charts", "false",
        "--helmfile-url", "path"
    ])

    assert "specified state file path is not found" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name, too-many-locals
def test_successful_run_get_all_charts_true_fetch_charts_false(resource_path_root, caplog, monkeypatch, fp):
    """Test for a successful run with get_all_charts set to true and fetch_charts set to false"""
    shutil.copyfile(os.path.join(resource_path_root, "helmfile_build_output_full.txt"),
                    os.path.join(os.getcwd(), "helmfile_build_output_full.txt"))
    with open("helmfile_build_output_full.txt", "r", encoding="utf-8") as helmfile_build_output:
        mock_response = helmfile_build_output.read()

    path_to_helmfile = os.path.join(resource_path_root, 'base-baseline', 'helmfile', 'helmfile.yaml')

    # pylint: disable=unused-argument
    def run_helmfile_build_command(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):

        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=mock_response)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", run_helmfile_build_command)

    runner = CliRunner()
    result = runner.invoke(get_release_details_from_helmfile, args=[
        "--state-values-file", "file",
        "--path-to-helmfile", path_to_helmfile,
        "--get-all-images", "true",
        "--fetch-charts", "false",
        "--helmfile-url", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"
    ])

    assert os.path.exists("csar_build.properties") is True
    assert os.path.exists("helmfile_json_content.json") is True
    assert os.path.exists("csar_to_be_built.properties") is True
    assert os.path.exists("releases_and_associated_csar.json") is True
    assert os.path.exists("individual_App_SiteValues.txt") is False
    assert os.path.exists("individual_App_Optionality.txt") is False
    assert os.path.exists("combined_optionality.yaml") is False
    assert os.path.exists("am_package_manager.properties") is False
    with open("csar_build.properties", "r", encoding="utf-8") as csar_build_properties_file,\
         open("helmfile_json_content.json", "r", encoding="utf-8") as helmfile_json_content_file,\
         open("csar_to_be_built.properties", "r", encoding="utf-8") as csar_to_be_built_file,\
         open("releases_and_associated_csar.json", "r", encoding="utf-8") as releases_and_associated_csar_file:
        csar_build_properties_content = csar_build_properties_file.read()
        helmfile_json_content = helmfile_json_content_file.read()
        csar_to_be_built_content = csar_to_be_built_file.read()
        releases_and_associated_csar_content = releases_and_associated_csar_file.read()
    assert_metadata_included(csar_build_properties_content, csar_to_be_built_content)
    for name, version, url in zip(ALL_NAMES, ALL_VERSIONS, ALL_URLS):
        assert f"{name}_name={name}" in csar_build_properties_content
        assert f"{name}_version={version}" in csar_build_properties_content
        assert f"{name}_url={url}" in csar_build_properties_content
        assert f"\"name\": \"{name}\"" in helmfile_json_content
        assert f"\"version\": \"{version}\"" in helmfile_json_content
        if name == "eric-cloud-native-base":
            assert f"\"url\": \"{url.split(',')[0]}\"" in helmfile_json_content
        else:
            assert f"\"url\": \"{url}\"" in helmfile_json_content
        assert f"{name}:{version}" in csar_to_be_built_content
        assert f"\n    \"{name}\": \"{name}\"" in releases_and_associated_csar_content
    os.remove("csar_build.properties")
    os.remove("helmfile_json_content.json")
    os.remove("csar_to_be_built.properties")
    os.remove("releases_and_associated_csar.json")
    assert "CSAR's to be built" in caplog.text
    for name, version in zip(ALL_NAMES, ALL_VERSIONS):
        assert f"{name}:{version}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name, too-many-locals
def test_successful_run_get_all_charts_false_fetch_charts_false(resource_path_root, caplog, monkeypatch, fp):
    """Test for a successful run with get_all_charts set to false and fetch_charts set to false"""
    shutil.copyfile(os.path.join(resource_path_root, "helmfile_build_output_full.txt"),
                    os.path.join(os.getcwd(), "helmfile_build_output_full.txt"))
    with open("helmfile_build_output_full.txt", "r", encoding="utf-8") as helmfile_build_output:
        mock_response = helmfile_build_output.read()

    # pylint: disable=unused-argument
    def run_helmfile_build_command(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):

        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=mock_response)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", run_helmfile_build_command)

    path_to_helmfile = os.path.join(resource_path_root, 'helmfile.yaml')

    runner = CliRunner()
    result = runner.invoke(get_release_details_from_helmfile, args=[
        "--state-values-file", "file",
        "--path-to-helmfile", path_to_helmfile,
        "--get-all-images", "false",
        "--fetch-charts", "false",
        "--helmfile-url", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"
    ])

    assert os.path.exists("csar_build.properties") is True
    assert os.path.exists("helmfile_json_content.json") is True
    assert os.path.exists("csar_to_be_built.properties") is True
    assert os.path.exists("releases_and_associated_csar.json") is True
    assert os.path.exists("individual_App_SiteValues.txt") is False
    assert os.path.exists("individual_App_Optionality.txt") is False
    assert os.path.exists("combined_optionality.yaml") is False
    assert os.path.exists("am_package_manager.properties") is False
    with open("csar_build.properties", "r", encoding="utf-8") as csar_build_properties_file,\
         open("helmfile_json_content.json", "r", encoding="utf-8") as helmfile_json_content_file,\
         open("csar_to_be_built.properties", "r", encoding="utf-8") as csar_to_be_built_file,\
         open("releases_and_associated_csar.json", "r", encoding="utf-8") as releases_and_associated_csar_file:
        csar_build_properties_content = csar_build_properties_file.read()
        helmfile_json_content = helmfile_json_content_file.read()
        csar_to_be_built_content = csar_to_be_built_file.read()
        releases_and_associated_csar_content = releases_and_associated_csar_file.read()
    assert_metadata_not_included(csar_build_properties_content, csar_to_be_built_content)
    for name, version, url in zip(ALL_NAMES, ALL_VERSIONS, ALL_URLS):
        if name in ENABLED_NAMES:
            assert f"{name}_name={name}" in csar_build_properties_content
            assert f"{name}_version={version}" in csar_build_properties_content
            assert f"{name}_url={url}" in csar_build_properties_content
            assert f"{name}:{version}" in csar_to_be_built_content
            assert f"\n    \"{name}\": \"{name}\"" in releases_and_associated_csar_content
        else:
            assert f"{name}_name={name}" not in csar_build_properties_content
            assert f"{name}_version={version}" not in csar_build_properties_content
            assert f"{name}_url={url}" not in csar_build_properties_content
            assert f"{name}:{version}" not in csar_to_be_built_content
            assert f"\n    \"{name}\": \"{name}\"" not in releases_and_associated_csar_content
        assert f"\"name\": \"{name}\"" in helmfile_json_content
        assert f"\"version\": \"{version}\"" in helmfile_json_content
        assert f"\"url\": \"{url.split(',')[0]}\"" in helmfile_json_content
    os.remove("csar_build.properties")
    os.remove("helmfile_json_content.json")
    os.remove("csar_to_be_built.properties")
    os.remove("releases_and_associated_csar.json")
    assert "CSAR's to be built" in caplog.text
    for name, version in zip(ENABLED_NAMES, ENABLED_VERSIONS):
        assert f"{name}:{version}" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name, too-many-locals, too-many-statements
def test_successful_run_fetch_charts_true(resource_path_root, monkeypatch, fp):
    """Test for a successful run with get_all_charts set to false and fetch_charts set to true"""
    shutil.copyfile(os.path.join(resource_path_root, "helmfile_build_output_full.txt"),
                    os.path.join(os.getcwd(), "helmfile_build_output_full.txt"))
    with open("helmfile_build_output_full.txt", "r", encoding="utf-8") as helmfile_build_output:
        mock_response = helmfile_build_output.read()
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile-reduced.tgz.test")
    utils.extract_tar_file(tar_file=tarfile, directory=".")
    Path(os.path.join(".", "eric-eo-helmfile", "csar")).touch()
    helmfile_path = os.path.join(".", "eric-eo-helmfile", "helmfile.yaml")
    for name, version in zip(ENABLED_NAMES, ENABLED_VERSIONS):
        shutil.copyfile(os.path.join(resource_path_root, f"{name}-{version}.tgz.test"),
                        os.path.join(os.getcwd(), f"{name}-{version}.tgz"))
    shutil.copyfile(os.path.join(resource_path_root, "eric-tm-ingress-controller-cr-crd-11.0.0+29.tgz.test"),
                    os.path.join(os.getcwd(), "eric-tm-ingress-controller-cr-crd-11.0.0+29.tgz"))

    # pylint: disable=unused-argument
    def run_helmfile_build_command(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=mock_response)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # pylint: disable=unused-argument
    def mock_helmfile_command(state_values_file, path_to_helmfile):
        return True

    # pylint: disable=unused-argument
    def mock_fetch_name_version_repo_details_from_helmfile(state_values_file,
                                                           path_to_helmfile,
                                                           only_enabled_releases=False):
        return True

    # pylint: disable=unused-argument
    def mock_build_netrc_file(state_values_file,
                              path_to_helmfile,
                              workspace=CWD):
        return True

    # pylint: disable=unused-argument
    def mock_cihelm_fetch(deps, netrc, mask, workspace, clean_up=False):
        return True

    def mock_download_dependencies(**kwargs):
        return True

    monkeypatch.setattr(helmfile, "run_helmfile_command", run_helmfile_build_command)
    monkeypatch.setattr(helmfile, "build", mock_helmfile_command)
    monkeypatch.setattr(helmfile, "fetch_name_version_repo_details_from_helmfile",
                        mock_fetch_name_version_repo_details_from_helmfile)
    monkeypatch.setattr(helmfile, "build_netrc_file_with_repo_credentials_from_helmfile",
                        mock_build_netrc_file)
    monkeypatch.setattr(cihelm, "fetch", mock_cihelm_fetch)
    monkeypatch.setattr(helmfile, "download_dependencies", mock_download_dependencies)

    runner = CliRunner()
    result = runner.invoke(get_release_details_from_helmfile, args=[
        "--state-values-file", "file",
        "--path-to-helmfile", helmfile_path,
        "--get-all-images", "false",
        "--fetch-charts", "true",
        "--helmfile-url", "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm"
    ])

    assert os.path.exists("csar_build.properties") is True
    assert os.path.exists("helmfile_json_content.json") is True
    assert os.path.exists("csar_to_be_built.properties") is True
    assert os.path.exists("releases_and_associated_csar.json") is True
    assert os.path.exists("individual_App_SiteValues.txt") is True
    assert os.path.exists("individual_App_Optionality.txt") is True
    assert os.path.exists("combined_optionality.yaml") is True
    assert os.path.exists("am_package_manager.properties") is True
    with open("csar_build.properties", "r", encoding="utf-8") as csar_build_properties_file,\
         open("helmfile_json_content.json", "r", encoding="utf-8") as helmfile_json_content_file,\
         open("csar_to_be_built.properties", "r", encoding="utf-8") as csar_to_be_built_file,\
         open("releases_and_associated_csar.json", "r", encoding="utf-8") as releases_and_associated_csar_file,\
         open("am_package_manager.properties", "r", encoding="utf-8") as am_package_manager_properties_file:
        csar_build_properties_content = csar_build_properties_file.read()
        helmfile_json_content = helmfile_json_content_file.read()
        csar_to_be_built_content = csar_to_be_built_file.read()
        releases_and_associated_csar_content = releases_and_associated_csar_file.read()
        am_package_manager_properties_content = am_package_manager_properties_file.read()
    assert_metadata_included(csar_build_properties_content, csar_to_be_built_content)
    for name, version, url in zip(ALL_NAMES, ALL_VERSIONS, ALL_URLS):
        if name in ENABLED_NAMES:
            assert f"{name}_name={name}" in csar_build_properties_content
            assert f"{name}_version={version}" in csar_build_properties_content
            assert f"{name}_url={url}" in csar_build_properties_content
            assert f"{name}:{version}" in csar_to_be_built_content
            assert f"\n    \"{name}\": \"{name}\"" in releases_and_associated_csar_content
            assert f"{name}-{version}.tgz" in am_package_manager_properties_content
        else:
            assert f"{name}_name={name}" not in csar_build_properties_content
            assert f"{name}_version={version}" not in csar_build_properties_content
            assert f"{name}_url={url}" not in csar_build_properties_content
            assert f"{name}:{version}" not in csar_to_be_built_content
            assert f"\n    \"{name}\": \"{name}\"" not in releases_and_associated_csar_content
            assert f"{name}-{version}.tgz" not in am_package_manager_properties_content
        assert f"\"name\": \"{name}\"" in helmfile_json_content
        assert f"\"version\": \"{version}\"" in helmfile_json_content
        assert f"\"url\": \"{url.split(',')[0]}\"" in helmfile_json_content
    assert "eric-tm-ingress-controller-cr-crd-11.0.0+29.tgz" in am_package_manager_properties_content
    assert "eric-eo-helmfile-2.6.0-90.tgz" in am_package_manager_properties_content
    os.remove("csar_build.properties")
    os.remove("helmfile_json_content.json")
    os.remove("csar_to_be_built.properties")
    os.remove("releases_and_associated_csar.json")
    os.remove("individual_App_SiteValues.txt")
    os.remove("individual_App_Optionality.txt")
    os.remove("combined_optionality.yaml")
    os.remove("am_package_manager.properties")
    assert result.exit_code == 0


def assert_metadata_included(csar_build_properties_content, csar_to_be_built_content):
    """Test metadata are added to csar_build_properties and csar_to_be_built"""
    assert "eric-eo-helmfile_name=eric-eo-helmfile" in csar_build_properties_content
    assert "eric-eo-helmfile_version=2.6.0-90" in csar_build_properties_content
    assert "eric-eo-helmfile_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm" \
           in csar_build_properties_content
    assert "eric-eo-helmfile:2.6.0-90" in csar_to_be_built_content


def assert_metadata_not_included(csar_build_properties_content, csar_to_be_built_content):
    """Test metadata are NOT added to csar_build_properties and csar_to_be_built"""
    assert "eric-eo-helmfile_name=eric-eo-helmfile" not in csar_build_properties_content
    assert "eric-eo-helmfile_version=2.6.0-90" not in csar_build_properties_content
    assert "eric-eo-helmfile_url=https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm" \
           not in csar_build_properties_content
    assert "eric-eo-helmfile:2.6.0-90" not in csar_to_be_built_content
