"""Test for helmfile executor check_helmfile_versions_against_given_versions."""
import os

import pytest
from click.testing import CliRunner
from bin.helmfile_executor import check_helmfile_versions_against_given_versions
from lib import helmfile

HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
PATH_TO_HELMFILE = "helmfile.yaml"
STATE_VALUES_FILE = "site-values.yaml"
CHART_NAMES = ""
CHART_VERSIONS = ""
MOCK_RESPONSE = [{"name": "eric-oss-dmm", "version": "0.560.0"},
                 {"name": "eric-oss-adc", "version": "0.125.0"},
                 {"name": "eric-cloud-native-base", "version": "0.111.0"},
                 {"name": "eric-oss-common-base", "version": "0.555.0"}]


@pytest.mark.parametrize("test_cli_args, expected", [
    # No helmfile path
    ("--state-values-file file " +
     "--chart-name name " +
     "--chart-version version",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No state values file
    ("--path-to-helmfile path " +
     "--chart-name name " +
     "--chart-version version",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No chart name
    ("--path-to-helmfile path " +
     "--state-values-file file " +
     "--chart-version version",
     {'output': "Error: Missing option \"--chart-name\""}),
    # No chart version
    ("--path-to-helmfile path " +
     "--state-values-file file " +
     "--chart-name name",
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
def test_check_helmfile_version_bad_args(test_cli_args, expected):
    """Test argument handling for helmfile_executor.check_helmfile_versions_against_given_versions."""
    runner = CliRunner()
    result = runner.invoke(check_helmfile_versions_against_given_versions, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_no_differences_in_chart_versions(caplog, monkeypatch):
    """Test where no differences were found."""
    # pylint: disable=unused-argument
    def mock_helmfile_list(state_values_file, path_to_helmfile):
        return MOCK_RESPONSE

    monkeypatch.setattr(helmfile, "helmfile_list", mock_helmfile_list)

    runner = CliRunner()
    result = runner.invoke(check_helmfile_versions_against_given_versions, args=[
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", "eric-oss-dmm,eric-oss-adc,eric-cloud-native-base,eric-oss-common-base",
        "--chart-version", "0.560.0,0.125.0,0.111.0,0.555.0"])

    assert "WARNING: Each of the chart versions in the CHART_VERSION " \
           "parameter are already in the helmfile" in caplog.text
    assert os.path.exists("./helmfile-version-check.properties")
    with open("./helmfile-version-check.properties", "r", encoding="utf-8") as properties_file:
        content = properties_file.readlines()
        assert "NO_CHART_VERSION_CHANGES=True\n" in content
    os.remove("./helmfile-version-check.properties")
    assert result.exit_code == 0


def test_differences_in_chart_versions(caplog, monkeypatch):
    """Test where differences were found."""
    # pylint: disable=unused-argument
    def mock_helmfile_list(state_values_file, path_to_helmfile):
        return MOCK_RESPONSE

    monkeypatch.setattr(helmfile, "helmfile_list", mock_helmfile_list)

    runner = CliRunner()
    result = runner.invoke(check_helmfile_versions_against_given_versions, args=[
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--state-values-file", STATE_VALUES_FILE,
        "--chart-name", "eric-oss-dmm,eric-oss-adc,eric-cloud-native-base,eric-oss-common-base",
        "--chart-version", "0.560.0,0.125.0,0.112.0,0.555.0"])

    assert "The following chart versions are being changed in " \
           "the helmfile: [('eric-cloud-native-base', '0.112.0')]" in caplog.text
    assert os.path.exists("./helmfile-version-check.properties")
    with open("./helmfile-version-check.properties", "r", encoding="utf-8") as properties_file:
        content = properties_file.readlines()
        assert "NO_CHART_VERSION_CHANGES=False\n" in content
    os.remove("./helmfile-version-check.properties")
    assert result.exit_code == 0
