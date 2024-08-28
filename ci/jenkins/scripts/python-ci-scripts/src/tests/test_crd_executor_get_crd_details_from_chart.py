"""Test for crd executor get_crd_details_from_chart."""
import os
import glob
import shutil
import time
import pytest
from click.testing import CliRunner
import mock

from lib import cihelm
from lib import utils
from lib import containers
from bin.crd_executor import get_crd_details_from_chart


@pytest.mark.parametrize("test_cli_args, expected", [
    # No path-to-helmfile
    ("--chart-name eric-eo-helmfile --chart-version 1.0.0 --chart-repo https://repo --username joe --password bloggs",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No chart_name
    ("--path-to-helmfile /tmp/chart --chart-version 1.0.0 --chart-repo https://repo --username joe --password bloggs",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No chart version
    ("--path-to-helmfile /tmp/chart --chart-name oss-chart --chart-repo https://repo --username joe --password bloggs",
     {'output': "Error: Missing option \"--chart-version\""}),
    # No chart_repo
    ("--path-to-helmfile /tmp/chart --chart-name oss-chart --chart-version 1.0.0 --username joe --password bloggs",
     {'output': "Error: Missing option \"--chart-repo\""}),
    # No docker image set
    ("--path-to-helmfile /tmp/chart --chart-name eric-eo-helmfile --chart-version 1.0.0 --chart-repo https://repo"
     " --username joe --password bloggs",
     {'output': "Error: Missing option \"--image\""}),
    # No username set
    ("--path-to-helmfile /tmp/chart --chart-name eric-eo-helmfile --chart-version 1.0.0 --chart-repo https://repo"
     " --image adp-crd-handler --password bloggs",
     {'output': "Error: Missing option \"--username\""}),
    # No password set
    ("--path-to-helmfile /tmp/chart --chart-name eric-eo-helmfile --chart-version 1.0.0 --chart-repo https://repo"
     " --image adp-crd-handler --username joe",
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
def test_get_crd_details_from_chart_bad_args(test_cli_args, expected):
    """Test argument handling for crd_executor.get_crd_details_from_chart."""
    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


@mock.patch('glob.glob', mock.Mock())
# pylint: disable=too-many-locals
def test_get_crd_details_from_chart_success(monkeypatch, resource_path_root, tmp_path):
    """Test get successful get crd."""
    chart_name = "eric-cloud-native-base"
    chart_version = "79.9.0"
    chart_repo = "https://local/artifactory"
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:0.1.1-0"
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"
    utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name}-{chart_version}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name}-{chart_version}.tgz"))

    # pylint: disable=unused-argument
    def download_chart(deps, netrc, mask, cwd):
        return True
    monkeypatch.setattr(cihelm, "fetch", download_chart)

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(adp_crd_handler_image, cmd_args, env_list):
        return True
    monkeypatch.setattr(containers, "run_docker_command", execute_container)
    # Mock the CRDs returned from the package
    existing_apps = ['/dummy/CRD/eric-sec-access-mgmt-crd-1.1.0+1.tgz',
                     '/dummy/CRD/eric-sec-certm-crd-4.0.0+69.tgz',
                     '/dummy/CRD/eric-sec-sip-tls-crd-5.0.0+29.tgz',
                     '/dummy/CRD/eric-data-key-value-database-rd-crd-1.1.0+1.tgz',
                     '/dummy/CRD/eric-tm-ingress-controller-cr-crd-11.1.0+131.tgz'
                     ]
    glob.glob.return_value = (app for app in existing_apps)

    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--chart-name", chart_name, "--chart-version", chart_version,
                           "--chart-repo", chart_repo, "--image", image])
    os.environ.pop("GERRIT_USERNAME")
    os.environ.pop("GERRIT_PASSWORD")
    assert os.path.exists(os.path.join(os.getcwd(), "crd_details_artifact.properties")) is True
    with open(os.path.join(os.getcwd(), "crd_details_artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert ("CHART_NAME=eric-cloud-native-base, eric-sec-certm-crd,"
            " eric-sec-sip-tls-crd,"
            " eric-data-key-value-database-rd-crd, eric-tm-ingress-controller-cr-crd") in text
    assert "CHART_VERSION=79.9.0, 4.0.0+69, 5.0.0+29, 1.1.0+1, 11.1.0+131" in text
    assert ("CHART_REPO=https://local/artifactory, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm") in text
    assert result.exit_code == 0


@mock.patch('glob.glob', mock.Mock())
# pylint: disable=too-many-locals
def test_get_crd_details_from_multiple_chart_success(monkeypatch, resource_path_root, tmp_path):
    """Test input multiple chart to get crd successfully."""
    chart_name = "eric-cloud-native-base, eric-eo-act-cna"
    chart_version = "79.9.0, 1.14.0-42"
    chart_repo = "https://local/artifactory, https://local/artifactory"
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:0.1.1-0"
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"
    utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
    shutil.copyfile(os.path.join(resource_path_root, "eric-cloud-native-base-79.9.0.tgz.test"),
                    os.path.join(os.getcwd(), "eric-cloud-native-base-79.9.0.tgz"))
    shutil.copyfile(os.path.join(resource_path_root, "eric-eo-act-cna-1.14.0-42.tgz.test"),
                    os.path.join(os.getcwd(), "eric-eo-act-cna-1.14.0-42.tgz"))

    # pylint: disable=unused-argument
    def download_chart(deps, netrc, mask, cwd):
        return True
    monkeypatch.setattr(cihelm, "fetch", download_chart)

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(adp_crd_handler_image, cmd_args, env_list):
        return True
    monkeypatch.setattr(containers, "run_docker_command", execute_container)
    # Mock the CRDs returned from the package
    existing_apps = ['/dummy/CRD/eric-sec-access-mgmt-crd-1.1.0+1.tgz',
                     '/dummy/CRD/eric-sec-certm-crd-4.0.0+69.tgz',
                     '/dummy/CRD/eric-sec-sip-tls-crd-5.0.0+29.tgz',
                     '/dummy/CRD/eric-data-key-value-database-rd-crd-1.1.0+1.tgz',
                     '/dummy/CRD/eric-tm-ingress-controller-cr-crd-11.1.0+131.tgz'
                     ]
    glob.glob.return_value = (app for app in existing_apps)

    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--chart-name", chart_name, "--chart-version", chart_version,
                           "--chart-repo", chart_repo, "--image", image])
    os.environ.pop("GERRIT_USERNAME")
    os.environ.pop("GERRIT_PASSWORD")
    assert os.path.exists(os.path.join(os.getcwd(), "crd_details_artifact.properties")) is True
    with open(os.path.join(os.getcwd(), "crd_details_artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert ("CHART_NAME=eric-cloud-native-base, eric-sec-certm-crd,"
            " eric-sec-sip-tls-crd,"
            " eric-data-key-value-database-rd-crd, eric-tm-ingress-controller-cr-crd, eric-eo-act-cna") in text
    assert "CHART_VERSION=79.9.0, 4.0.0+69, 5.0.0+29, 1.1.0+1, 11.1.0+131, 1.14.0-42" in text
    assert ("CHART_REPO=https://local/artifactory, https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://arm.rnd.ki.sw.ericsson.se/artifactory/proj-adp-gs-all-helm, "
            "https://local/artifactory") in text
    assert result.exit_code == 0


@mock.patch('glob.glob', mock.Mock())
# pylint: disable=too-many-locals
def test_get_crd_details_from_chart_no_crd(monkeypatch, resource_path_root, tmp_path):
    """Test get crd details from chart with no crds."""
    chart_name = "eric-eo-act-cna"
    chart_version = "1.14.0-42"
    chart_repo = "https://local/artifactory"
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:0.1.1-0"
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"
    utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name}-{chart_version}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name}-{chart_version}.tgz"))

    # pylint: disable=unused-argument
    def download_chart(deps, netrc, mask, cwd):
        return True
    monkeypatch.setattr(cihelm, "fetch", download_chart)

    # pylint: disable=unused-argument
    def execute_container(adp_crd_handler_image, cmd_args, env_list):
        return True
    monkeypatch.setattr(containers, "run_docker_command", execute_container)
    # Mock the CRDs returned from the package
    existing_apps = ['/dummy/CRD/eric-data-key-value-database-rd-crd-1.1.0+1.tgz',
                     '/dummy/CRD/eric-data-wide-column-database-cd-crd-1.13.0+3.tgz',
                     '/dummy/CRD/eric-sec-access-mgmt-crd-1.0.0-3.tgz',
                     '/dummy/CRD/eric-sec-certm-crd-4.0.0+69.tgz',
                     '/dummy/CRD/eric-sec-sip-tls-crd-5.0.0+29.tgz',
                     '/dummy/CRD/eric-tm-ingress-controller-cr-crd-11.0.0+29.tgz']
    glob.glob.return_value = (app for app in existing_apps)

    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--chart-name", chart_name, "--chart-version", chart_version,
                           "--chart-repo", chart_repo, "--image", image])
    os.environ.pop("GERRIT_USERNAME")
    os.environ.pop("GERRIT_PASSWORD")
    assert os.path.exists(os.path.join(os.getcwd(), "crd_details_artifact.properties")) is True
    with open(os.path.join(os.getcwd(), "crd_details_artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    os.remove("crd_details_artifact.properties")
    assert f"CHART_NAME={chart_name}" in text
    assert f"CHART_VERSION={chart_version}" in text
    assert f"CHART_REPO={chart_repo}" in text
    assert result.exit_code == 0


def test_get_crd_details_from_chart_no_helmfile(tmp_path, caplog):
    """Test get crd details from chart helmfile not found."""
    chart_name = "eric-eo-act-cna"
    chart_version = "1.14.0-42"
    chart_repo = "https://local/artifactory"
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:0.1.1-0"
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"
    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--chart-name", chart_name, "--chart-version", chart_version,
                           "--chart-repo", chart_repo, "--image", image])
    os.environ.pop("GERRIT_USERNAME")
    os.environ.pop("GERRIT_PASSWORD")
    assert result.exit_code == 1
    assert "Check for CRD details failed with the following error" in caplog.text
    assert "helmfile.yaml is not found" in caplog.text


def test_get_crd_details_from_chart_no_chart(resource_path_root, tmp_path, caplog, monkeypatch):
    """Test get crd details from chart no chart in repo."""
    chart_name = "eric-eo-act-cna"
    chart_version = "1.14.0-42"
    chart_repo = "https://local/artifactory"
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:0.1.1-0"
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"
    utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name}-{chart_version}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name}-{chart_version}.tgz"))

    # pylint: disable=unused-argument
    def download_chart(deps, netrc, mask, cwd):
        raise Exception("Cannot connect to host local:443 ssl")
    monkeypatch.setattr(cihelm, "fetch", download_chart)

    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--chart-name", chart_name, "--chart-version", chart_version,
                           "--chart-repo", chart_repo, "--image", image])
    os.environ.pop("GERRIT_USERNAME")
    os.environ.pop("GERRIT_PASSWORD")
    assert result.exit_code == 1
    assert "Cannot connect to host local:443" in caplog.text


@mock.patch('glob.glob', mock.Mock())
# pylint: disable=too-many-locals
def test_get_crd_details_from_chart_docker_error(caplog, monkeypatch, resource_path_root, tmp_path):
    """Test get successful get crd."""
    chart_name = "eric-cloud-native-base"
    chart_version = "79.9.0"
    chart_repo = "https://local/artifactory"
    image = "armdocker.rnd.ericsson.se/proj-adp-cicd-drop/adp-crd-handler:0.1.1-0"
    tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
    helmfile_path = os.path.join(tmp_path, "eric-eo-helmfile", "helmfile.yaml")
    os.environ["GERRIT_USERNAME"] = "dummy"
    os.environ["GERRIT_PASSWORD"] = "dummyPassword"
    utils.extract_tar_file(tar_file=tarfile, directory=tmp_path)
    shutil.copyfile(os.path.join(resource_path_root, f"{chart_name}-{chart_version}.tgz.test"),
                    os.path.join(os.getcwd(), f"{chart_name}-{chart_version}.tgz"))

    # pylint: disable=unused-argument
    def download_chart(deps, netrc, mask, cwd):
        return True
    monkeypatch.setattr(cihelm, "fetch", download_chart)

    # Mock the execution of the docker image to retrieve the CRDs from the package.
    # pylint: disable=unused-argument
    def execute_container(adp_crd_handler_image, cmd_args, env_list):
        raise Exception("Docker error")
    monkeypatch.setattr(containers, "run_docker_command", execute_container)

    # Removing the time.sleep(30) to reduce testing time
    # pylint: disable=unused-argument
    def reduce_sleep_time(sleep_time):
        return True
    monkeypatch.setattr(time, "sleep", reduce_sleep_time)

    runner = CliRunner()
    result = runner.invoke(get_crd_details_from_chart, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--chart-name", chart_name, "--chart-version", chart_version,
                           "--chart-repo", chart_repo, "--image", image])
    os.environ.pop("GERRIT_USERNAME")
    os.environ.pop("GERRIT_PASSWORD")
    assert os.path.exists(os.path.join(os.getcwd(), "crd_details_artifact.properties")) is False
    assert "An exception occurred in collecting the CRD files: Docker error" in caplog.text
    assert result.exit_code == 1
    os.remove("eric-cloud-native-base/Chart.yaml")
