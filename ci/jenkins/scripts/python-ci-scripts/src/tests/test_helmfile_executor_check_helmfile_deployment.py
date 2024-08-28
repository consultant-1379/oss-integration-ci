"""Test for helmfile executor check_helmfile_deployment_status."""
import os
import subprocess
import oyaml as yaml
import pytest
from click.testing import CliRunner

from lib import check_helmfile_deployment_status
from lib import errors
from lib import utils
from bin.helmfile_executor import check_helmfile_deployment


DEPLOYED_APPS = """
- app_version: 87.8.0
  chart: eric-cloud-native-base-87.8.0
  name: eric-cloud-native-base
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:30:19.961518031 +0000 UTC
- app_version: ""
  chart: eric-cncs-oss-config-0.0.0-44
  name: eric-cncs-oss-config
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:37:39.154638868 +0000 UTC
- app_version: ""
  chart: eric-cncs-oss-pre-config-0.0.0-1
  name: eric-cncs-oss-pre-config
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:30:13.931808852 +0000 UTC
- app_version: ""
  chart: eric-eo-config-0.0.0-1
  name: eric-eo-config
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:37:39.18477023 +0000 UTC
- app_version: ""
  chart: eric-eo-evnfm-2.24.0-149
  name: eric-eo-evnfm
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.424314587 +0000 UTC
- app_version: "1.0"
  chart: eric-eo-evnfm-vm-2.46.0-19
  name: eric-eo-evnfm-vm
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.292837625 +0000 UTC
- app_version: ""
  chart: eric-eo-so-3.12.0-95
  name: eric-eo-so
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.635499426 +0000 UTC
- app_version: ""
  chart: eric-oss-common-base-0.1.0-1134
  name: eric-oss-common-base
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:37:39.282578994 +0000 UTC
- app_version: ""
  chart: eric-oss-config-handling-0.0.0-154
  name: eric-oss-config-handling
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.445562532 +0000 UTC
- app_version: ""
  chart: eric-oss-dmm-0.0.0-345
  name: eric-oss-dmm
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.520741204 +0000 UTC
- app_version: ""
  chart: eric-oss-ericsson-adaptation-0.1.0-914
  name: eric-oss-ericsson-adaptation
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.469868993 +0000 UTC
- app_version: ""
  chart: eric-oss-function-orchestration-common-0.1.1-18
  name: eric-oss-function-orchestration-common
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.332745012 +0000 UTC
- app_version: ""
  chart: eric-oss-pf-2.16.0-10
  name: eric-oss-pf
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.328818046 +0000 UTC
- app_version: ""
  chart: eric-oss-uds-5.10.0-17
  name: eric-oss-uds
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.353682236 +0000 UTC
- app_version: ""
  chart: eric-topology-handling-0.0.2-132
  name: eric-topology-handling
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:47:34.390352563 +0000 UTC
- app_version: ""
  chart: secret-eric-data-object-storage-mn-1.0.0
  name: secret-eric-data-object-storage-mn
  namespace: eric-app-ns
  revision: "1"
  status: deployed
  updated: 2022-11-30 15:30:13.948867104 +0000 UTC
"""

ALL_RELEASES = """
[{
    "name": "eric-tm-ingress-controller-cr-crd",
    "namespace": "eric-crd-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-tm-ingress-controller-cr-crd/eric-tm-ingress-controller-cr-crd",
    "version": "11.0.0+29"
}, {
    "name": "eric-mesh-controller-crd",
    "namespace": "eric-crd-ns",
    "enabled": false,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-mesh-controller-crd/eric-mesh-controller-crd",
    "version": "9.0.0+28"
}, {
    "name": "eric-sec-sip-tls-crd",
    "namespace": "eric-crd-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-sec-sip-tls-crd/eric-sec-sip-tls-crd",
    "version": "5.0.0+29"
}, {
    "name": "eric-data-wide-column-database-cd-crd",
    "namespace": "eric-crd-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-data-wide-column-database-cd-crd/eric-data-wide-column-database-cd-crd",
    "version": "1.13.0+3"
}, {
    "name": "eric-oss-kf-sz-op-crd",
    "namespace": "eric-crd-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-oss-kf-sz-op-crd/eric-oss-kf-sz-op-crd",
    "version": "1.0.0-0"
}, {
    "name": "eric-sec-certm-crd",
    "namespace": "eric-crd-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-sec-certm-crd/eric-sec-certm-crd",
    "version": "4.0.0+69"
}, {
    "name": "eric-data-key-value-database-rd-crd",
    "namespace": "eric-crd-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-data-key-value-database-rd-crd/eric-data-key-value-database-rd-crd",
    "version": "1.1.0+1"
}, {
    "name": "secret-eric-data-object-storage-mn",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "",
    "chart": "/tmp/chartify420760964/eric-app-ns/secret-eric-data-object-storage-mn",
    "version": ""
}, {
    "name": "eric-eo-config",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "",
    "chart": "charts/eric-eo-config",
    "version": ""
}, {
    "name": "eric-cncs-oss-pre-config",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "",
    "chart": "charts/eric-cncs-oss-pre-config",
    "version": ""
}, {
    "name": "eric-cloud-native-base",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cloud-native-base",
    "chart": "eric-cloud-native-base/eric-cloud-native-base",
    "version": "74.0.0"
}, {
    "name": "eric-cncs-oss-config",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-cncs-oss-config",
    "chart": "eric-cncs-oss-config/eric-cncs-oss-config",
    "version": "0.0.0-38"
}, {
    "name": "eric-mesh-controller",
    "namespace": "eric-app-ns",
    "enabled": false,
    "installed": true,
    "labels": "csar:eric-mesh-controller",
    "chart": "eric-mesh-controller/eric-mesh-controller",
    "version": "9.0.0+28"
}, {
    "name": "eric-oss-common-base",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-oss-common-base",
    "chart": "eric-oss-common-base/eric-oss-common-base",
    "version": "0.1.0-902"
}, {
    "name": "eric-eo-so",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-eo-so",
    "chart": "eric-eo-so/eric-eo-so",
    "version": "3.10.0-6"
}, {
    "name": "eric-oss-pf",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-oss-pf",
    "chart": "eric-oss-pf/eric-oss-pf",
    "version": "2.14.0-8"
}, {
    "name": "eric-oss-uds",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-oss-uds",
    "chart": "eric-oss-uds/eric-oss-uds",
    "version": "5.8.0-6"
}, {
    "name": "eric-eo-evnfm",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-eo-evnfm",
    "chart": "eric-eo-evnfm/eric-eo-evnfm",
    "version": "2.23.0-925"
}, {
    "name": "eric-eo-evnfm-vm",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-eo-evnfm-vm",
    "chart": "eric-eo-evnfm-vm/eric-eo-evnfm-vm",
    "version": "2.43.0-9"
}, {
    "name": "eric-oss-ericsson-adaptation",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-oss-ericsson-adaptation",
    "chart": "eric-oss-ericsson-adaptation/eric-oss-ericsson-adaptation",
    "version": "0.1.0-798"
}, {
    "name": "eric-oss-dmm",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-oss-dmm",
    "chart": "eric-oss-dmm/eric-oss-dmm",
    "version": "0.0.0-223"
}, {
    "name": "eric-topology-handling",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-topology-handling",
    "chart": "eric-topology-handling/eric-topology-handling",
    "version": "0.0.2-98"
}, {
    "name": "eric-oss-config-handling",
    "namespace": "eric-app-ns",
    "enabled": true,
    "installed": true,
    "labels": "csar:eric-oss-config-handling",
    "chart": "eric-oss-config-handling/eric-oss-config-handling",
    "version": "0.0.0-121"
}, {
    "name": "eric-eo-cm",
    "namespace": "eric-app-ns",
    "enabled": false,
    "installed": false,
    "labels": "csar:eric-eo-cm",
    "chart": "eric-eo-cm/eric-eo-cm",
    "version": "1.15.0-92"
}, {
    "name": "eric-eo-act-cna",
    "namespace": "eric-app-ns",
    "enabled": false,
    "installed": false,
    "labels": "csar:eric-eo-act-cna",
    "chart": "eric-eo-act-cna/eric-eo-act-cna",
    "version": "1.15.0-11"
}, {
    "name": "ericsson-core-assurance",
    "namespace": "eric-app-ns",
    "enabled": false,
    "installed": false,
    "labels": "csar:ericsson-core-assurance",
    "chart": "ericsson-core-assurance/ericsson-core-assurance",
    "version": "0.0.0-5"
}]
"""


@pytest.fixture(name="helmfile_path")
def get_helmfile_path(resource_path_root):
    """Fixture to generate path to the helmfile"""
    def _get_helmfile_path():
        tarfile = os.path.join(resource_path_root, "eric-eo-helmfile.tgz.test")
        utils.extract_tar_file(tar_file=tarfile, directory=os.getcwd())
        return os.path.join(os.getcwd(), "eric-eo-helmfile", "helmfile.yaml")
    return _get_helmfile_path


@pytest.fixture(name="kubeconfig_path")
def get_kubeconfig_path(tmp_path):
    """Fixture to create fake kubeconfig file"""
    def _get_kubeconfig_path():
        kubeconfig = tmp_path / "kubeconfig"
        kubeconfig.parent.mkdir(exist_ok=True)
        kubeconfig.touch()
        return str(kubeconfig)
    return _get_kubeconfig_path


@pytest.fixture(name="subprocess_completed")
def mock_subprocess_completed(monkeypatch):
    """Fixture to mock subprocess completed for binary running"""
    # pylint: disable=unused-argument
    def _mock_run(command, **subprocess_run_options):
        content = ""
        if command[0] == "/usr/bin/helm":
            content = DEPLOYED_APPS
        elif command[0] == "/usr/bin/helmfile":
            content = ALL_RELEASES
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout=content.encode('utf-8'),
                                           returncode=0)
    monkeypatch.setattr(subprocess, "run", _mock_run)


@pytest.mark.parametrize("test_cli_args, expected", [
    # No helmfile_path
    ("--kubeconfig-file /kubeconfig --namespace name --deployment-tags true\
      --optional-tags true --optional-key-value-list list --check-tags true --check-full-version true",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No kubeconfig
    ("--path-to-helmfile /helmfile --namespace name --deployment-tags true\
      --optional-tags true --optional-key-value-list list --check-tags true --check-full-version true",
     {'output': "Error: Missing option \"--kubeconfig-file\""}),
    # No namespace
    ("--path-to-helmfile /helmfile --kubeconfig-file /kubeconfig --deployment-tags true\
      --optional-tags true --optional-key-value-list list --check-tags true --check-full-version true",
     {'output': "Error: Missing option \"--namespace\""}),
    # No deployment tags
    ("--path-to-helmfile /helmfile --kubeconfig-file /kubeconfig --namespace name\
      --optional-tags true --optional-key-value-list list --check-tags true --check-full-version true",
     {'output': "Error: Missing option \"--deployment-tags\""}),
    # No optional tags
    ("--path-to-helmfile /helmfile --kubeconfig-file /kubeconfig --namespace name\
      --deployment-tags true --optional-key-value-list list --check-tags true --check-full-version true",
     {'output': "Error: Missing option \"--optional-tags\""}),
    # No optional key/value list
    ("--path-to-helmfile /helmfile --kubeconfig-file /kubeconfig --namespace name\
      --deployment-tags true --optional-tags true --check-tags true --check-full-version true",
     {'output': "Error: Missing option \"--optional-key-value-list\""}),
    # No check tags
    ("--path-to-helmfile /helmfile --kubeconfig-file /kubeconfig --namespace name\
      --deployment-tags true --optional-tags true --optional-key-value-list list --check-full-version true",
     {'output': "Error: Missing option \"--check-tags\""}),
    # No check version
    ("--path-to-helmfile /helmfile --kubeconfig-file /kubeconfig --namespace name\
      --deployment-tags true --optional-tags true --optional-key-value-list list --check-tags true",
     {'output': "Error: Missing option \"--check-full-version\""}),
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
def test_check_helmfile_deployment_status_bad_args(test_cli_args, expected):
    """Test argument handling."""
    runner = CliRunner()
    result = runner.invoke(check_helmfile_deployment, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=unused-argument
def test_run_check_check_helmfile_deployment(helmfile_path, kubeconfig_path, subprocess_completed):
    """test successfull run."""
    helmfile_path = helmfile_path()
    kubeconfig_path = kubeconfig_path()
    namespace = "eric-app-ns"
    deployment_tags = "eoSo eoPf eoUds eoEvnfm eoVmvnfm"
    optional_tags = ""
    optional_key_value_list = "None"
    check_tags = ""
    runner = CliRunner()
    result = runner.invoke(check_helmfile_deployment, args=[
                           "--path-to-helmfile", helmfile_path,
                           "--kubeconfig-file", kubeconfig_path,
                           "--namespace", namespace,
                           "--deployment-tags", deployment_tags,
                           "--optional-tags", optional_tags,
                           "--optional-key-value-list", optional_key_value_list,
                           "--check-tags", check_tags,
                           "--check-full-version", "false"])
    assert result.exit_code == 0


def test_tag_update(helmfile_path):
    """Test for tag updated in site-values file"""
    path_to_helmfile = helmfile_path()
    # Test single tag update
    tags = "eoCm"
    optional_tags = ""
    site_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")
    updated = utils.update_new_site_values_with_tags(site_values_file, tags, optional_tags)
    assert updated['tags']['eoCm'] is True

    # Test multiple tag updates
    tags = "eoEvnfm eoPf eoUds"
    optional_tags = ""
    updated = utils.update_new_site_values_with_tags(site_values_file, tags, optional_tags)
    assert updated['tags']['eoEvnfm'] is True
    assert updated['tags']['eoPf'] is True
    assert updated['tags']['eoUds'] is True
    assert updated['tags']['eoCm'] is False

    # Test update non-existent tag
    tags = "eoNotThere"
    optional_tags = ""
    updated = utils.update_new_site_values_with_tags(site_values_file, tags, optional_tags)
    assert "eoNotThere" not in updated['tags']

    # Test bad pattern in tags (two spaces) should still work
    tags = "eoEvnfm  eoPf"
    optional_tags = ""
    updated = utils.update_new_site_values_with_tags(site_values_file, tags, optional_tags)
    assert updated['tags']['eoEvnfm'] is True
    assert updated['tags']['eoPf'] is True


def test_update_sitevalues_namespace_defaults(helmfile_path):
    """Test update of namespace defaults in site-values"""
    path_to_helmfile = helmfile_path()
    site_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")
    with open(site_values_file, 'r', encoding='utf-8') as site_values:
        values = yaml.safe_load(site_values)

    updated = check_helmfile_deployment_status.update_site_values_yaml_with_namespace_defaults(values)
    assert 'helmfile' in updated
    assert updated['helmfile']['app']['namespace'] == "eric-app-ns"
    assert updated['helmfile']['crd']['namespace'] == "eric-crd-ns"
    test_site_val = {
        "helmfile": {
            "app": {
                "namespace": "not-app-namespace"
            },
            "crd": {
                "namespace": "not-crd-namespace"
            }
        }
    }
    updated = check_helmfile_deployment_status.update_site_values_yaml_with_namespace_defaults(test_site_val)
    assert updated['helmfile']['app']['namespace'] == "eric-app-ns"
    assert updated['helmfile']['crd']['namespace'] == "eric-crd-ns"


def test_update_site_values_key_value_list(helmfile_path):
    """Test update of site values using key/value list."""
    # Test single key/value update
    path_to_helmfile = helmfile_path()
    key_value_list = "eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true"
    site_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")
    with open(site_values_file, 'r', encoding='utf-8') as site_values:
        values = yaml.safe_load(site_values)
    updated = utils.update_yaml_dict_with_key_value_list(values, key_value_list)

    assert updated['eric-cloud-native-base']['eric-sec-access-mgmt']['accountManager']['enabled'] is True

    # Test multiple key/value updates
    key_value_list = ('eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true,'
                      'eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false,'
                      'global.hosts.gm=host.hart102.ericsson.se')
    site_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")
    with open(site_values_file, 'r', encoding='utf-8') as site_values:
        values = yaml.safe_load(site_values)
    updated = utils.update_yaml_dict_with_key_value_list(values, key_value_list)

    assert updated['eric-cloud-native-base']['eric-sec-access-mgmt']['accountManager']['enabled'] is True
    assert updated['eric-oss-common-base']['eric-oss-ddc']['autoUpload']['enabled'] is False
    assert updated['global']['hosts']['gm'] == 'host.hart102.ericsson.se'

    # Test bad pattern in list (no = to set value)
    key_value_list = "eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled.true"
    site_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")
    with open(site_values_file, 'r', encoding='utf-8') as site_values:
        values = yaml.safe_load(site_values)
    updated = utils.update_yaml_dict_with_key_value_list(values, key_value_list)

    assert (updated['eric-cloud-native-base']['eric-sec-access-mgmt']['accountManager']['enabled']['true']
            == "eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled.true")

    # Test bad pattern in list (invalid separator)
    key_value_list = ('eric-cloud-native-base.eric-sec-access-mgmt.accountManager.enabled=true '
                      'eric-oss-common-base.eric-oss-ddc.autoUpload.enabled=false')
    site_values_file = os.path.join(os.path.dirname(path_to_helmfile), "templates", "site-values-template.yaml")
    with open(site_values_file, 'r', encoding='utf-8') as site_values:
        values = yaml.safe_load(site_values)
    updated = utils.update_yaml_dict_with_key_value_list(values, key_value_list)

    assert updated['eric-cloud-native-base']['eric-sec-access-mgmt']['accountManager']['enabled'] is False


def test_fail_retrieving_deployed_releases(monkeypatch, caplog, kubeconfig_path):
    """Test for error handling with release retrieval failure"""
    kubeconfig = kubeconfig_path()

    # pylint: disable=unused-argument
    def _mock_failed_run(command, **subprocess_run_options):
        command = []
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout=''.encode('utf-8'),
                                           returncode=1)
    monkeypatch.setattr(subprocess, "run", _mock_failed_run)

    all_deployed_releases = []
    with pytest.raises(errors.HelmCommandError) as exc_info:
        check_helmfile_deployment_status.set_helm_deployed_releases_yaml(all_deployed_releases, kubeconfig, "bob")
    assert "Unable to list deployed releases" in caplog.text
    assert str(exc_info.value) == "Unable to list deployed releases"


def test_check_deployed_releases(caplog):
    """Test check number of deployed releases"""
    deployed_releases_yaml = []
    has_deployed_releases = check_helmfile_deployment_status.check_deployed_releases(deployed_releases_yaml, "bob")
    assert "*** No releases found in namespace bob - New deployment is required" in caplog.text
    assert has_deployed_releases is False

    deployed_releases_yaml.extend(yaml.safe_load(ALL_RELEASES))
    has_deployed_releases = check_helmfile_deployment_status.check_deployed_releases(deployed_releases_yaml, "bob")
    assert "*** Releases found in namespace bob" in caplog.text
    assert has_deployed_releases is True


def test_fail_retrieving_all_releases(monkeypatch, caplog, kubeconfig_path):
    """Test to validate error handling with failure to retrieve all releases"""
    kubeconfig = kubeconfig_path()

    # pylint: disable=unused-argument
    def _mock_failed_run(command, **subprocess_run_options):
        command = []
        return subprocess.CompletedProcess(args=command,
                                           stderr=''.encode('utf-8'),
                                           stdout=''.encode('utf-8'),
                                           returncode=1)
    monkeypatch.setattr(subprocess, "run", _mock_failed_run)

    all_releases = []
    deployed_releases = []
    with pytest.raises(errors.HelmCommandError) as exc_info:
        check_helmfile_deployment_status.set_and_log_helm_all_releases_yaml(all_releases, deployed_releases,
                                                                            kubeconfig, "bob")
    assert "Unable to list all releases:" in caplog.text
    assert str(exc_info.value) == "Unable to list all releases"


def test_check_successful_releases(caplog):
    """Test to validate testing of successful releases"""
    artifacts_properties = "/ci-scripts/output-files/artifact.properties"
    num_deployed = 5
    num_released = 5
    deployed_releases = yaml.safe_load(DEPLOYED_APPS)
    if os.path.exists(artifacts_properties):
        os.remove(artifacts_properties)
    ret_val = check_helmfile_deployment_status.check_successful_releases(num_deployed, num_released, deployed_releases)
    # same number so no artifact properties written
    assert ret_val is True
    assert os.path.exists(artifacts_properties) is False
    assert "*** Number of successful releases matches number of total releases" in caplog.text

    # test incorrect number of releases
    if os.path.exists(artifacts_properties):
        os.remove(artifacts_properties)
    num_released = 7
    ret_val = check_helmfile_deployment_status.check_successful_releases(num_deployed, num_released, deployed_releases)
    assert "*** Number of successful releases does not match number of total releases" in caplog.text
    assert ret_val is False
    assert os.path.exists(artifacts_properties) is True


def test_write_artifacts_properties():
    """Test the creation of the artifacts properites file"""
    artifacts_properties = "/ci-scripts/output-files/artifact.properties"
    content = ""
    if os.path.exists(artifacts_properties):
        os.remove(artifacts_properties)
    deployed_releases = yaml.safe_load(DEPLOYED_APPS)
    # skip deletion true
    check_helmfile_deployment_status \
        .write_skip_deletion_and_deployed_versions_to_artifact_properties(True, deployed_releases)
    assert os.path.exists(artifacts_properties) is True
    with open(artifacts_properties, 'r', encoding='utf-8') as props:
        content = props.read()
    assert "SKIP_DELETION=true" in content
    assert "eric-eo-evnfm-2.24.0-149" in content
    assert "eric-eo-so-3.12.0-95" in content
    assert "eric-oss-pf-2.16.0-10" in content
    assert "eric-oss-uds-5.10.0-17" in content

    if os.path.exists(artifacts_properties):
        os.remove(artifacts_properties)
    check_helmfile_deployment_status \
        .write_skip_deletion_and_deployed_versions_to_artifact_properties(False, deployed_releases)
    with open(artifacts_properties, 'r', encoding='utf-8') as props:
        content = props.read()
    assert "SKIP_DELETION=false" in content
    assert "eric-eo-evnfm-2.24.0-149" in content
    assert "eric-eo-so-3.12.0-95" in content
    assert "eric-oss-pf-2.16.0-10" in content
    assert "eric-oss-uds-5.10.0-17" in content


def test_get_charts_with_tag_from_helmfile(helmfile_path):
    """Validate getting tags from helmfile."""
    path_to_helmfile = helmfile_path()
    filter_tags = ["eoCm"]
    charts_with_tag = check_helmfile_deployment_status.get_charts_with_tag_dict_from_helmfile(path_to_helmfile,
                                                                                              filter_tags)
    assert len(charts_with_tag) == 1
    assert "eoCm" in charts_with_tag
    # Use tags that don't exist in the helmfile
    filter_tags = ["eoNot", "eoThere"]
    charts_with_tag = check_helmfile_deployment_status.get_charts_with_tag_dict_from_helmfile(path_to_helmfile,
                                                                                              filter_tags)
    assert len(charts_with_tag) == 0
    # Multiple tags some there some not
    filter_tags = ["eoSo", "eoPf", "eoUds", "eoEvnfm", "eoNot", "eoThere"]
    charts_with_tag = check_helmfile_deployment_status.get_charts_with_tag_dict_from_helmfile(path_to_helmfile,
                                                                                              filter_tags)
    assert len(charts_with_tag) == 4
    assert "eoSo" in charts_with_tag
    assert "eoPf" in charts_with_tag
    assert "eoUds" in charts_with_tag
    assert "eoEvnfm" in charts_with_tag

    # No filter
    charts_with_tag = check_helmfile_deployment_status.get_charts_with_tag_dict_from_helmfile(path_to_helmfile)
    assert len(charts_with_tag) == 7


def test_analyze_chart_tags(helmfile_path, caplog):
    """Test analyzing chart tags."""
    path_to_helmfile = helmfile_path()
    # test tag not found
    tags = "eoNotThere"
    deployed = ["chart: ericsson-core-assurance-0.0.0-5",
                "chart: eric-eo-evnfm-2.24.0-149",
                "chart: eric-eo-so-3.12.0-95",
                "chart: eric-oss-pf-2.16.0-10",
                "chart: eric-oss-dmm-0.0.0-345"]
    with pytest.raises(errors.MissingHelmfileTag) as exc_info:
        check_helmfile_deployment_status.analyze_chart_tags(path_to_helmfile, deployed, tags)
    assert str(exc_info.value) == "Unable to find tag eoNotThere in helmfile chart enables"

    tags = "eoUds"
    ret_val = check_helmfile_deployment_status.analyze_chart_tags(path_to_helmfile, deployed, tags)
    assert "EOUDS_DEPLOY=true but eric-oss-uds is not deployed on system" in caplog.text
    assert ret_val is False

    deployed = ["chart: ericsson-core-assurance-0.0.0-5",
                "chart: eric-eo-evnfm-2.24.0-149",
                "chart: eric-eo-so-3.12.0-95",
                "chart: eric-oss-pf-2.16.0-10",
                "chart: eric-oss-dmm-0.0.0-345",
                "chart: eric-oss-ericsson-adaptation-0.1.0-914",
                "chart: eric-topology-handling-0.0.2-132",
                "chart: eric-oss-uds-5.10.0-17",
                "chart: eric-oss-config-handling-0.0.0-154"]
    tags = "eoSo eoPf"
    ret_val = check_helmfile_deployment_status.analyze_chart_tags(path_to_helmfile, deployed, tags)
    assert ret_val is True


def test_compare_apps(caplog):
    """Test compare apps function."""
    deployed_apps = ["ericsson-core-assurance-0.0.0-5",
                     "eric-eo-evnfm-2.24.0-149"]
    helmfile_apps = ["ericsson-core-assurance-0.0.0-5",
                     "eric-eo-evnfm-2.24.0-149"]
    ret_val = check_helmfile_deployment_status.compare_apps(deployed_apps, helmfile_apps)
    assert ret_val is True
    assert "Deployed applications:" in caplog.text

    ret_val = check_helmfile_deployment_status.compare_apps(deployed_apps, helmfile_apps, True)
    assert ret_val is True
    assert "Deployed specific (check-tags) applications:" in caplog.text

    helmfile_apps = ["ericsson-core-assurance-0.0.0-5",
                     "eric-eo-evnfm-2.24.0-666"]
    ret_val = check_helmfile_deployment_status.compare_apps(deployed_apps, helmfile_apps)
    assert ret_val is False


def test_chart_entry_in_chart_list():
    """Test function chart_entry_in_chart_list."""
    chart_list = "eric-eo-evnfm"
    chart_entry = "chart: eric-eo-evnfm-2.24.0-149"
    with pytest.raises(Exception) as exc_info:
        check_helmfile_deployment_status.chart_entry_exists_in_chart_list(chart_entry, chart_list)
    assert str(exc_info.value) == "Invalid chart_list parameter found"

    chart_list = ["ericsson-core-assurance",
                  "eric-eo-evnfm"]
    ret_val = check_helmfile_deployment_status.chart_entry_exists_in_chart_list(chart_entry, chart_list)
    assert ret_val is True

    chart_list = ["ericsson-core-assurance",
                  "eric-topology-handling"]
    ret_val = check_helmfile_deployment_status.chart_entry_exists_in_chart_list(chart_entry, chart_list)
    assert ret_val is False
