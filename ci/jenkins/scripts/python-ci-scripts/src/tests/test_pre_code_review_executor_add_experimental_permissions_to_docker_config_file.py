"""Test for Pre Code Review Executor for Create Image Information Json File"""
import os
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import add_experimental_permissions_for_docker_config_file

SAMPLE_CONFIG_FILE = """
{
    "auths": {
        "armdocker.rnd.ericsson.se": {
            "auth": "ZW9hZG0xMDA6QzZvZzcmJlQyKnVhRjR0Zw=="
        },
        "serodocker.sero.gic.ericsson.se": {
            "auth": "ZW9hZG0xMDA6QzZvZzcmJlQyKnVhRjR0Zw=="
        }
    },
    "HttpHeaders": {
        "User-Agent": "Docker-Client/19.03.12 (linux)"
    }
}
"""
OUTPUT_FILE = ".docker/config.json"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No --docker-file-full-path
    ("",
     {'output': "Error: Missing option \"--docker-file-full-path\""}),
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
def test_add_experimental_permissions_for_docker_config_file_images_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.check_eric_product_info_images"""
    runner = CliRunner()
    result = runner.invoke(add_experimental_permissions_for_docker_config_file, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_add_experimental_permissions_for_docker_config_file_success(monkeypatch, caplog):
    """Test add_experimental_permissions_for_docker_config_file on chart for success"""
    if not os.path.exists(".docker"):
        os.mkdir(".docker")

    with open(OUTPUT_FILE, "a", encoding="utf-8") as docker_config_file:
        docker_config_file.writelines(SAMPLE_CONFIG_FILE)

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(0, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(add_experimental_permissions_for_docker_config_file, args=[
        "--docker-file-full-path", OUTPUT_FILE])
    assert result.exit_code == 0
    assert os.path.exists(OUTPUT_FILE)
    assert "Addition of Experimental Permissions for Docker Config File has completed successfully" in caplog.text
    os.remove(OUTPUT_FILE)


# pylint: disable=too-many-locals
def test_add_experimental_permissions_for_docker_config_file_failure(monkeypatch, caplog):
    """Test add_experimental_permissions_for_docker_config_file on chart for failure"""
    docker_file_full_path = "./eric-oss-app-mgr"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "Error Output")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(add_experimental_permissions_for_docker_config_file, args=[
        "--docker-file-full-path", docker_file_full_path])
    assert result.exit_code == 1
    assert "Please refer to the following log" in caplog.text
