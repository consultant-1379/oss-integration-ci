"""Test for crd_executor.py check_crs_from_templates_dir."""
import os
import shutil
import pytest
from click.testing import CliRunner

from lib import containers
from bin.crd_executor import check_crs_from_templates_dir

KUBECONFORM_IMAGE = "armdocker.rnd.ericsson.se/proj-eric-oss-drop/eric-oss-ci-kubeconform:latest"
TEMPLATE_PATH = os.path.join(os.getcwd(), "templates")


@pytest.mark.parametrize("test_cli_args, expected", [
    # No dir
    ("--image testimage",
     {'output': "Error: Missing option \"--dir\""}),
    # No image
    ("--dir /templates",
     {'output': "Error: Missing option \"--image\""}),
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
def test_check_crs_from_templates_dir_bad_args(test_cli_args, expected):
    """Test argument handling in crd_exector.check_crs_from_templates_dir."""
    runner = CliRunner()
    result = runner.invoke(check_crs_from_templates_dir, test_cli_args)
    assert expected['output'] in result.output
    assert result.exit_code == 2


def test_cr_validation_success(monkeypatch, resource_path_root, caplog):
    """Test successful CR validation with no non-conformances reported."""
    os.makedirs(TEMPLATE_PATH)
    shutil.copyfile(os.path.join(resource_path_root, "1.22.0.yaml.matching_crs"),
                    os.path.join(TEMPLATE_PATH, "1.22.0.yaml"))

    # pylint: disable=unused-argument
    def mock_run_kubeconform(kubeconform_image, cmd):
        if "/kubeconform/openapi2jsonschema.py" in cmd:
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-matching_crs",
                                         "siptls-internalcertificate-v1.json"),
                            os.path.join(TEMPLATE_PATH, "1.22.0",
                                         "siptls-internalcertificate-v1.json"))
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-matching_crs",
                                         "siptls-internalcertificate-v1alpha1.json"),
                            os.path.join(TEMPLATE_PATH, "1.22.0",
                                         "siptls-internalcertificate-v1alpha1.json"))
        return "".encode('utf-8')
    monkeypatch.setattr(containers, "run_kubeconform", mock_run_kubeconform)

    runner = CliRunner()
    result = runner.invoke(check_crs_from_templates_dir, args=[
                           "--dir", TEMPLATE_PATH,
                           "--image", KUBECONFORM_IMAGE])
    shutil.rmtree(TEMPLATE_PATH)
    assert "CR conformance checks completed with no errors found" in caplog.text
    assert result.exit_code == 0


def test_template_validation_no_crs_success(monkeypatch, resource_path_root, caplog):
    """Test successful CR validation when no CRs are included in templates."""
    os.makedirs(TEMPLATE_PATH)
    shutil.copyfile(os.path.join(resource_path_root, "1.22.0.yaml.no_crs"),
                    os.path.join(TEMPLATE_PATH, "1.22.0.yaml"))

    # pylint: disable=unused-argument
    def mock_run_kubeconform(kubeconform_image, cmd):
        if "/kubeconform/openapi2jsonschema.py" in cmd:
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-no_crs",
                                         "config-adapter-v1alpha2.json"),
                            os.path.join(TEMPLATE_PATH, "1.22.0",
                                         "config-adapter-v1alpha2.json"))
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-no_crs",
                                         "config-attributemanifest-v1alpha2.json"),
                            os.path.join(TEMPLATE_PATH, "1.22.0",
                                         "config-attributemanifest-v1alpha2.json"))
        return "".encode('utf-8')
    monkeypatch.setattr(containers, "run_kubeconform", mock_run_kubeconform)

    runner = CliRunner()
    result = runner.invoke(check_crs_from_templates_dir, args=[
                           "--dir", TEMPLATE_PATH,
                           "--image", KUBECONFORM_IMAGE])
    shutil.rmtree(TEMPLATE_PATH)
    assert "CR conformance checks completed with no errors found" in caplog.text
    assert result.exit_code == 0


def test_cr_nonconformance_failed(monkeypatch, resource_path_root, caplog):
    """Test CR validation with non-conformances reported."""
    os.makedirs(TEMPLATE_PATH)
    shutil.copyfile(os.path.join(resource_path_root, "1.22.0.yaml.cr_error"),
                    os.path.join(TEMPLATE_PATH, "1.22.0.yaml"))

    # pylint: disable=unused-argument
    def mock_run_kubeconform(kubeconform_image, cmd):
        if "/kubeconform/openapi2jsonschema.py" in cmd:
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-cr_error",
                                         "config-adapter-v1alpha2.json"),
                            os.path.join(TEMPLATE_PATH,
                                         "1.22.0",
                                         "config-adapter-v1alpha2.json"))
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-cr_error",
                                         "kafka-kafka-v1beta2.json"),
                            os.path.join(TEMPLATE_PATH,
                                         "1.22.0",
                                         "kafka-kafka-v1beta2.json"))
            shutil.copyfile(os.path.join(resource_path_root, "1.22.0-cr_error",
                                         "wcdbcd-cassandracluster-v1alpha1.json"),
                            os.path.join(TEMPLATE_PATH,
                                         "1.22.0",
                                         "wcdbcd-cassandracluster-v1alpha1.json"))
            return "JSON schema written".encode('utf-8')
        if "wcdbcd-cassandracluster-v1alpha1.yaml" in cmd:
            return f"{TEMPLATE_PATH}/1.22.0/wcdbcd-cassandracluster-v1alpha1.yaml" \
                   " - CassandraCluster eric-data-wide-column-database-cd is invalid:" \
                   " For field spec.dataCenters.0.backupAndRestore.brsc.env: Invalid type." \
                   " Expected: array, given: null".encode('utf-8')
        return f"{TEMPLATE_PATH}/1.22.0/kafka-kafka-v1beta2.yaml" \
               " - Kafka eric-oss-dmm-kf-op-sz is invalid: For field" \
               " spec.entityOperator.template.pod: Invalid type. " \
               "Expected: object, given: null".encode('utf-8')
    monkeypatch.setattr(containers, "run_kubeconform", mock_run_kubeconform)

    runner = CliRunner()
    result = runner.invoke(check_crs_from_templates_dir, args=[
                           "--dir", TEMPLATE_PATH,
                           "--image", KUBECONFORM_IMAGE])
    shutil.rmtree(TEMPLATE_PATH)
    assert "Number of CRs that do not conform for version 1.22.0: 2" in caplog.text
    assert result.exit_code == 1
