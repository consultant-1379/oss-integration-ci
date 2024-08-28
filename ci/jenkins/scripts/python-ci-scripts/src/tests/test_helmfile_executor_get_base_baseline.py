"""Test for helmfile executor get_base_baseline."""
import os
import subprocess
import pytest
from click.testing import CliRunner
from bin.helmfile_executor import get_base_baseline
from lib import utils
from lib import helmfile

HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
MOCK_STDOUT_HELMFILE = "\nNAME NAMESPACE ENABLED INSTALLED LABELS CHART VERSION\n" +\
                       "eric-cnbase-oss-config ns true true eric-oss-drop/eric-cnbase-oss-config 1.7.0\n" +\
                       "eric-cloud-native-base ns true true adp-umbrella-released/eric-cloud-native-base 122.2.0\n" +\
                       "eric-cncs-oss-config ns true true eric-oss-drop/eric-cncs-oss-config 0.21.0\n" +\
                       "eric-oss-common-base ns true true eric-oss-drop/eric-oss-common-base 0.185.0"

MOCK_STDOUT_HELMFILE_WITH_LABEL = "\nNAME NAMESPACE ENABLED INSTALLED LABELS CHART VERSION\n" +\
                       "eric-cnbase-oss-config ns true true project:eric-eiae-helmfile" \
                       " eric-oss-drop/eric-cnbase-oss-config 1.7.0\n" +\
                       "eric-cloud-native-base ns true true adp-umbrella-released/eric-cloud-native-base 122.2.0\n" +\
                       "eric-cncs-oss-config ns true true eric-oss-drop/eric-cncs-oss-config 0.21.0\n" +\
                       "eric-oss-common-base ns true true eric-oss-drop/eric-oss-common-base 0.185.0"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No path-to-helmfile
    ('--execution-type set_baseline',
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No execution-type
    ('--path-to-helmfile /dummy/dummy',
     {'output': "Error: Missing option \"--execution-type\""}),
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
def test_get_app_version_from_helmfile_bad_args(test_cli_args, expected):
    """Test argument handling for helmfile_executor.get_base_baseline."""
    runner = CliRunner()
    result = runner.invoke(get_base_baseline, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_helmfile_incorrect_path(resource_path_root, caplog):
    """
    Testing that the correct output is printed if the incorrect path to the helmfile is specified.
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'doesnotexist')

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--execution-type", "get_baseline"])
    assert "No such file or directory:" in caplog.text
    assert result.exit_code == 1
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")


def test_helmfile_no_repositories_yaml(resource_path_root, caplog):
    """
    Testing that the correct output is printed if the incorrect path to the repositories.yaml is specified.
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'no_repositories')

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--execution-type", "get_baseline"])
    assert "Error: Unable to open repositories.yaml, within" in caplog.text
    assert result.exit_code == 1
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")


# pylint: disable=invalid-name
def test_helmfile_no_input_file(monkeypatch, resource_path_root, fp, caplog):
    """
    Testing that the helmfile is parsed without any added input files and the correct details are
    displayed in the output.
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'helmfile')

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--execution-type", "get_baseline"])
    with open(os.path.join(os.getcwd(), "artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert "eric-cnbase-oss-config_version=1.7.0" in text
    assert "BASE_PLATFORM_BASELINE_CHART_NAME=eric-cnbase-oss-config, eric-cloud-native-base, " \
           "eric-cncs-oss-config, eric-oss-common-base" in text
    assert "BASE_PLATFORM_BASELINE_CHART_VERSION=1.7.0, 122.2.0, 0.21.0, 0.185.0" in text

    assert "BASE_PLATFORM_BASELINE_CHART_REPO=" \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local" in text
    assert "Completed successfully" in caplog.text
    assert result.exit_code == 0
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")


def test_helmfile_with_set_project(monkeypatch, resource_path_root, fp, caplog):
    """
    Testing that the helmfile is parsed giving in a project, if there is project label on any of the releases
    And this project is listed then the info should be gathered
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'helmfile')

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_HELMFILE_WITH_LABEL)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--project-file-name", "eric-eiae-helmfile",
        "--execution-type", "get_baseline"])
    with open(os.path.join(os.getcwd(), "artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert "eric-cnbase-oss-config_version=1.7.0" in text
    assert "BASE_PLATFORM_BASELINE_CHART_NAME=eric-cnbase-oss-config, eric-cloud-native-base, " \
           "eric-cncs-oss-config, eric-oss-common-base" in text
    assert "BASE_PLATFORM_BASELINE_CHART_VERSION=1.7.0, 122.2.0, 0.21.0, 0.185.0" in text

    assert "BASE_PLATFORM_BASELINE_CHART_REPO=" \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local" in text
    assert "Completed successfully" in caplog.text
    assert result.exit_code == 0
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")


def test_helmfile_with_not_listed_set_project(monkeypatch, resource_path_root, fp, caplog):
    """
    Testing that the helmfile is parsed giving in a project, if there is project label on any of the releases
    And this project is not listed then the info should not be gathered
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'helmfile')

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_HELMFILE_WITH_LABEL)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--project-file-name", "eric-eo-helmfile",
        "--execution-type", "get_baseline"])
    with open(os.path.join(os.getcwd(), "artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert "eric-cnbase-oss-config_version=1.7.0" not in text
    assert "BASE_PLATFORM_BASELINE_CHART_NAME=eric-cloud-native-base, " \
           "eric-cncs-oss-config, eric-oss-common-base" in text
    assert "BASE_PLATFORM_BASELINE_CHART_VERSION=122.2.0, 0.21.0, 0.185.0" in text

    assert "BASE_PLATFORM_BASELINE_CHART_REPO=" \
           "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local" in text
    assert "Completed successfully" in caplog.text
    assert result.exit_code == 0
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")


def test_helmfile_with_an_input_file_single_details(monkeypatch, resource_path_root, fp, caplog):
    """
    Testing that the correct output is printed if one entry is added to the input file.
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'helmfile')
    input_file = os.path.join(resource_path_root, 'base-baseline', 'inca_input.properties')

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--input-file", input_file,
        "--execution-type", "set_baseline"])
    with open(os.path.join(os.getcwd(), "artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert "eric-cnbase-oss-config_version=9.1.0-1-test" in text
    assert "BASE_PLATFORM_BASELINE_CHART_NAME=eric-cnbase-oss-config, eric-cloud-native-base, " \
           "eric-cncs-oss-config, eric-oss-common-base" in text
    assert "BASE_PLATFORM_BASELINE_CHART_VERSION=9.1.0-1-test, 122.2.0, 0.21.0, 0.185.0" in text
    assert "BASE_PLATFORM_BASELINE_CHART_REPO=" \
           "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/test, " \
           "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local" in text
    assert "Completed successfully" in caplog.text
    assert result.exit_code == 0
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")


def test_helmfile_with_an_input_file_multiple_details(monkeypatch, resource_path_root, fp, caplog):
    """
    Testing that the correct output is printed if multiple entries are added to the input file.
    """

    helmfile_path = os.path.join(resource_path_root, 'base-baseline', 'helmfile')
    input_file = os.path.join(resource_path_root, 'base-baseline', 'inca_multiple_input.properties')

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_base_baseline, args=[
        "--path-to-helmfile", helmfile_path,
        "--input-file", input_file,
        "--execution-type", "set_baseline"])
    with open(os.path.join(os.getcwd(), "artifact.properties"), 'r', encoding='utf-8') as properties_file:
        text = properties_file.read()
    assert "eric-cnbase-oss-config_version=9.1.0-1-testmulti" in text
    assert "BASE_PLATFORM_BASELINE_CHART_NAME=eric-cnbase-oss-config, eric-cloud-native-base, " \
           "eric-cncs-oss-config, eric-oss-common-base" in text
    assert "BASE_PLATFORM_BASELINE_CHART_VERSION=9.1.0-1-testmulti, 1.1.1-testmulti, 0.21.0, 0.185.0" in text
    assert "BASE_PLATFORM_BASELINE_CHART_REPO=" \
           "https://arm.sero.gic.ericsson.se/artifactory/proj-adp-umbrella-released-helm/testmulti, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local/testmulti, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local, " \
           "https://arm.seli.gic.ericsson.se/artifactory/proj-eric-oss-drop-helm-local" in text
    assert "Completed successfully" in caplog.text
    assert result.exit_code == 0
    if os.path.isfile("artifact.properties"):
        os.remove("artifact.properties")
