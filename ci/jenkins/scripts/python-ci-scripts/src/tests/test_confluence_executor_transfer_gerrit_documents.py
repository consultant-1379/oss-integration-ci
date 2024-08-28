"""Test for confluence_executor.transfer_gerrit_documents"""
import os

import pytest
import requests
from click.testing import CliRunner
from mock_response import MockResponse

from bin.confluence_executor import transfer_gerrit_documents

JSON_CONTENT = '{"results": [{"title": "document_1.md", "id": "12345"}], "version": {"number": 1}}'
USERNAME = "username"
PASSWORD = "password"


@pytest.mark.parametrize("test_cli_args, expected", [
    # No space-key
    ("--url abc.com --parent-id 123 --documents-path ./docs --username joe --password pass",
     {'output': "Error: Missing option \"--space-key\""}),
    # No url
    ("--space-key ABC --parent-id 123 --documents-path ./docs --username joe --password pass",
     {'output': "Error: Missing option \"--url\""}),
    # No parent-id
    ("--space-key ABC --url abc.com --documents-path ./docs --username joe --password pass",
     {'output': "Error: Missing option \"--parent-id\""}),
    # No documents-path
    ("--space-key ABC --url abc.com --parent-id 123 --username joe --password pass",
     {'output': "Error: Missing option \"--documents-path\""}),
    # No username
    ("--space-key ABC --url abc.com --parent-id 123 --documents-path ./docs --password pass",
     {'output': "Error: Missing option \"--username\""}),
    # No password
    ("--space-key ABC --url abc.com --parent-id 123 --documents-path ./docs --username joe",
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
def test_uds_backend_job_wait_bad_args(test_cli_args, expected):
    """Test arg handling for confluence_executor.uds_backend_job_wait."""
    runner = CliRunner()
    result = runner.invoke(transfer_gerrit_documents, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_successful_run(caplog, monkeypatch):
    """Test for a successful run."""
    os.makedirs(os.path.dirname("./docs/document_1.md"), exist_ok=True)
    os.makedirs(os.path.dirname("./docs/document_2.md"), exist_ok=True)

    with open("./docs/document_1.md", "w", encoding="utf-8") as file_one, \
         open("./docs/document_2.md", "w", encoding="utf-8") as file_two:
        file_one.write("Text")
        file_two.write("Text")

    # pylint: disable=unused-argument
    def get_response(**kwargs):
        response = MockResponse(content=JSON_CONTENT)
        return response

    # pylint: disable=unused-argument
    def put_or_post(url, data, headers, auth, timeout):
        response = MockResponse(content=JSON_CONTENT)
        return response
    monkeypatch.setattr(requests, "get", get_response)
    monkeypatch.setattr(requests, "post", put_or_post)
    monkeypatch.setattr(requests, "put", put_or_post)

    runner = CliRunner()
    result = runner.invoke(transfer_gerrit_documents, args=[
        "--space-key", "DGBase",
        "--url", "https://abc.com",
        "--parent-id", "12345",
        "--documents-path", "./docs",
        "--username", USERNAME,
        "--password", PASSWORD])
    assert "Page updated successfully for document 1" in caplog.text
    assert "Page created successfully for document 2" in caplog.text
    assert result.exit_code == 0
    del os.environ['FUNCTIONAL_USER_USERNAME']
    del os.environ['FUNCTIONAL_USER_PASSWORD']
