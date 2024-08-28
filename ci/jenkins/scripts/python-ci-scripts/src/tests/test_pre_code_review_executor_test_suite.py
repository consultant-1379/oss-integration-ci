"""Test for script executor check_for_existing_csar"""
import os
import pytest
from click.testing import CliRunner

from lib import cmd_common
from bin.pre_code_review_executor import static_tests

CHART = "/ci-scripts/tests/testresources/eric-cloud-native-base-79.9.0.tgz.test"
TEST_VALUES_FILE = "/ci-scripts/tests/testresources/test_values.yaml"
SPECIFIC_SKIP = "/ci-scripts/tests/testresources/specific_skip_list.json"
COMMON_SKIP = "/ci-scripts/tests/testresources/common_skip_list.json"
SAMPLE_HTML_OUTPUT = """
</script>
    <h1>report.html</h1>
    <p>Report generated on 14-Mar-2024 at 12:48:56 by <a href="https://pypi.python.org/pypi/pytest-html">pytest-html</a>
    <h2>Summary</h2>
    <p>65 tests ran in 0.68 seconds. </p>
    <h2>Results</h2>
    <table id="results-table">
      <thead id="results-table-head">
        <tr>
          <th class="sortable result initial-sort" col="result">Result</th>
          <th class="sortable" col="name">Test</th>
          <th class="sortable" col="duration">Duration</th>
          <th class="sortable links" col="links">Links</th></tr>
        <tr hidden="true" id="not-found-message">
          <th colspan="4">No results found. Try to check the filters</th></tr></thead>
      <tbody class="skipped results-table-row">
        <tr>
          <td class="col-result">Skipped</td>
          <td class="col-name">helm-chart-validator[template_name0-kind0-pod_autoscaler0]</td>
          <td class="col-duration">0.00</td>
          <td class="col-links"></td></tr>
        <tr>
          <td class="extra" colspan="4">
            <div class="log">(Skipped: got empty parameter set)></div></td></tr></tbody>
"""


@pytest.mark.parametrize("test_cli_args, expected", [
    # No common-skip-files
    ("--state-values-file \"site-value.yaml\" --chart-full-path \"path\" --specific-skip-file \"path\"",
     {'output': "Error: Missing option \"--common-skip-file\""}),
    # No specific-skip-files
    ("--state-values-file \"site-value.yaml\" --chart-full-path \"path\" --common-skip-file \"path\"",
     {'output': "Error: Missing option \"--specific-skip-file\""}),
    # No chart-full-path
    ("--state-values-file \"site-value.yaml\" --common-skip-file \"path\" --specific-skip-file \"path\"",
     {'output': "Error: Missing option \"--chart-full-path\""}),
    # No state-values-file
    ("--chart-full-path \"path\" --common-skip-file \"path\" --specific-skip-file \"path\"",
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
     {'output': 'Error: no such option: --unknown'})
])
def test_static_tests_bad_args(test_cli_args, expected):
    """Test argument handling for pre_code_review_executor.static_tests."""
    runner = CliRunner()
    result = runner.invoke(static_tests, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


# pylint: disable=too-many-locals
def test_static_tests_success(monkeypatch, caplog):
    """Test get successful get crd."""
    state_values_file = "/ci-scripts/tests/testresources/test_values.yaml"
    chart_full_path = "/ci-scripts/tests/testresources/eric-cloud-native-base-79.9.0.tgz.test"
    specific_skip_file = "/ci-scripts/tests/testresources/specific_skip_list.json"
    common_skip_file = "/ci-scripts/tests/testresources/common_skip_list.json"
    test_folder = "/test-files"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        with open("report.html", "w", encoding="utf-8") as report_file:
            report_file.write(SAMPLE_HTML_OUTPUT)
        return cmd_common.Response(0, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(static_tests, args=[
        "--state-values-file", state_values_file,
        "--chart-full-path", chart_full_path,
        "--specific-skip-file", specific_skip_file,
        "--common-skip-file", common_skip_file])
    assert result.exit_code == 0
    assert os.path.exists(os.path.join(test_folder, "skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "common_skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "test_chart.tgz")) is True
    assert os.path.exists(os.path.join(test_folder, "site_values_template.yaml")) is True
    assert "Editing report.html to clarify test cases where the resources under test were not found..." in caplog.text
    assert "Execution completed successfully" in caplog.text
    os.remove("report.html")


# pylint: disable=too-many-locals
def test_static_tests_error(monkeypatch, caplog):
    """Test get successful get crd."""
    state_values_file = "/ci-scripts/tests/testresources/test_values.yaml"
    chart_full_path = "/ci-scripts/tests/testresources/eric-cloud-native-base-79.9.0.tgz.test"
    specific_skip_file = "/ci-scripts/tests/testresources/specific_skip_list.json"
    common_skip_file = "/ci-scripts/tests/testresources/common_skip_list.json"
    test_folder = "/test-files"

    # pylint: disable=unused-argument
    def execute_command(cmd, mask, verbose=True):
        return cmd_common.Response(1, "Test Output", "")
    monkeypatch.setattr(cmd_common, "execute_command", execute_command)

    runner = CliRunner()
    result = runner.invoke(static_tests, args=[
        "--state-values-file", state_values_file,
        "--chart-full-path", chart_full_path,
        "--specific-skip-file", specific_skip_file,
        "--common-skip-file", common_skip_file])
    assert result.exit_code == 1
    assert os.path.exists(os.path.join(test_folder, "skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "common_skip_list.json")) is True
    assert os.path.exists(os.path.join(test_folder, "test_chart.tgz")) is True
    assert os.path.exists(os.path.join(test_folder, "site_values_template.yaml")) is True
    assert "See failure(s) above" in caplog.text
