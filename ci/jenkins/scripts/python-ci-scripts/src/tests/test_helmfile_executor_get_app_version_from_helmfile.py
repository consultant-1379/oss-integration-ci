"""Test for helmfile executor get_app_version_from_helmfile."""
import os
import subprocess
import pytest
from click.testing import CliRunner
from bin.helmfile_executor import get_app_version_from_helmfile
from lib import helmfile
from lib import utils

HELM = "/usr/bin/helm"
HELMFILE = "/usr/bin/helmfile"
PATH_TO_HELMFILE = "helmfile.yaml"
STATE_VALUES_FILE = "site-values.yaml"
MOCK_STDOUT_NEWER_HELMFILE = "NAME NAMESPACE ENABLED INSTALLED LABELS CHART VERSION\n" +\
                             "test_app1 test_ns true true test_label test_chart test_version1\n" +\
                             "test_app2 test_ns true false test_label test_chart test_version2\n" +\
                             "test_app3 eric-crd-ns true true test_label test_chart test_version3\n" +\
                             "test_app4 test_ns true true test_label"
MOCK_STDOUT_OLDER_HELMFILE = "NAME NAMESPACE ENABLED INSTALLED VERSION\n" +\
                             "test_app1 test_ns true true test_version1\n" +\
                             "test_app2 test_ns true false test_version2\n" +\
                             "test_app3 eric-crd-ns true true test_version3\n" +\
                             "test_app4 test_ns true true"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No state-values-file
    ("--path-to-helmfile path --tags-set-to-true-only true",
     {'output': "Error: Missing option \"--state-values-file\""}),
    # No path-to-helmfile
    ("--state-values-file path --tags-set-to-true-only true",
     {'output': "Error: Missing option \"--path-to-helmfile\""}),
    # No tags-set-to-true-only
    ("--path-to-helmfile path --state-values-file path",
     {'output': "Error: Missing option \"--tags-set-to-true-only\""}),
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
    """Test argument handling for helmfile_executor.get_app_version_from_helmfile."""
    runner = CliRunner()
    result = runner.invoke(get_app_version_from_helmfile, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=invalid-name
def test_invalid_helmfile(monkeypatch, fp, caplog):
    """Testing an invalid helmfile being provided."""
    tags_set_to_true_only = "true"

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_NEWER_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_app_version_from_helmfile, args=[
        "--state-values-file", STATE_VALUES_FILE,
        "--path-to-helmfile", PATH_TO_HELMFILE,
        "--tags-set-to-true-only", tags_set_to_true_only])

    assert f"No such file or directory: '{PATH_TO_HELMFILE}'" in caplog.text
    assert result.exit_code == 1


# pylint: disable=invalid-name
def test_newer_helmfile_version_tags_true(monkeypatch, fp, caplog):
    """Testing a newer helmfile version with the tags set to true."""
    tags_set_to_true_only = "true"

    # pylint: disable=unspecified-encoding
    with open("helmfile.yaml", "w+") as helmfile_file:
        helmfile_file.write("labels: true")

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_NEWER_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_app_version_from_helmfile, args=[
                           "--state-values-file", STATE_VALUES_FILE,
                           "--path-to-helmfile", PATH_TO_HELMFILE,
                           "--tags-set-to-true-only", tags_set_to_true_only])

    assert os.path.isfile("artifact.properties") is True
    with open("artifact.properties") as output:
        file_content = output.readlines()
    assert ["test_app1=test_version1\n"] == file_content
    os.remove("helmfile.yaml")
    os.remove("artifact.properties")
    assert "Get app version comleted successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_older_helmfile_version_tags_true(monkeypatch, fp, caplog):
    """Testing an older helmfile version with the tags set to true."""
    tags_set_to_true_only = "true"

    # pylint: disable=unspecified-encoding
    with open("helmfile.yaml", "w+") as helmfile_file:
        helmfile_file.write("dummy: value")

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_OLDER_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_app_version_from_helmfile, args=[
                           "--state-values-file", STATE_VALUES_FILE,
                           "--path-to-helmfile", PATH_TO_HELMFILE,
                           "--tags-set-to-true-only", tags_set_to_true_only])

    assert os.path.isfile("artifact.properties") is True
    with open("artifact.properties") as output:
        file_content = output.readlines()
    assert ["test_app1=test_version1\n"] == file_content
    os.remove("helmfile.yaml")
    os.remove("artifact.properties")
    assert "Get app version comleted successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_newer_helmfile_version_tags_false(monkeypatch, fp, caplog):
    """Testing a newer helmfile version with the tags set to false."""
    tags_set_to_true_only = "false"

    # pylint: disable=unspecified-encoding
    with open("helmfile.yaml", "w+") as helmfile_file:
        helmfile_file.write("labels: true")

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_NEWER_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_app_version_from_helmfile, args=[
                           "--state-values-file", STATE_VALUES_FILE,
                           "--path-to-helmfile", PATH_TO_HELMFILE,
                           "--tags-set-to-true-only", tags_set_to_true_only])

    assert os.path.isfile("artifact.properties") is True
    with open("artifact.properties") as output:
        file_content = output.readlines()
    assert ["test_app1=test_version1\n", "test_app2=test_version2\n", "test_app3=test_version3\n"] == file_content
    os.remove("helmfile.yaml")
    os.remove("artifact.properties")
    assert "Get app version comleted successfully" in caplog.text
    assert result.exit_code == 0


# pylint: disable=invalid-name
def test_older_helmfile_version_tags_false(monkeypatch, fp, caplog):
    """Testing an older helmfile version with the tags set to false."""
    tags_set_to_true_only = "false"

    # pylint: disable=unspecified-encoding
    with open("helmfile.yaml", "w+") as helmfile_file:
        helmfile_file.write("dummy: value")

    # pylint: disable=unused-argument
    def helmfile_cmd(helmfile_path, site_values_file_path, config_file_path, *helmfile_args):
        command_and_args_list = [HELMFILE, '--helm-binary', HELM,
                                 '--file', helmfile_path,
                                 '--state-values-file', site_values_file_path]
        command_and_args_list.extend(helmfile_args)
        fp.register(command_and_args_list, stdout=MOCK_STDOUT_OLDER_HELMFILE)
        return utils.run_cli_command(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    monkeypatch.setattr(helmfile, "run_helmfile_command", helmfile_cmd)

    runner = CliRunner()
    result = runner.invoke(get_app_version_from_helmfile, args=[
                           "--state-values-file", STATE_VALUES_FILE,
                           "--path-to-helmfile", PATH_TO_HELMFILE,
                           "--tags-set-to-true-only", tags_set_to_true_only])

    assert os.path.isfile("artifact.properties") is True
    with open("artifact.properties") as output:
        file_content = output.readlines()
    assert ["test_app1=test_version1\n", "test_app2=test_version2\n", "test_app3=test_version3\n"] == file_content
    os.remove("helmfile.yaml")
    os.remove("artifact.properties")
    assert "Get app version comleted successfully" in caplog.text
    assert result.exit_code == 0
