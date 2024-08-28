"""This module contains test cases to verify replica count."""

import logging
import pytest
from helmfile_template import HelmfileTemplate
from utils import mark_test_parameters, get_marks_from_skips
from skip_template import SkipTemplate
from site_values import SiteValues
from check_template import CheckTemplate

LOG = logging.getLogger(__name__)

helmfile_template_object = HelmfileTemplate("/test-files/helmfile", "/test-files/site_values.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()
site_values = SiteValues("/test-files/site_values.yaml")


check_specific_content_object = CheckTemplate("/test-files/check_specific_content.json")
input_minimum_replica_count_params = check_specific_content_object.get_check_content(
    'test_validate_minimum_replica_count'
)
LOG.info("input_minimum_replica_count_params %s", input_minimum_replica_count_params)

input_minimum_replica_count_params = site_values.update_minimum_replica_count(input_minimum_replica_count_params)
spec_replicas = helmfile_template_object.get_values_with_a_specific_path("spec.replicas")
skips = skip_template_object.get_skips_from_name('test_validate_minimum_replica_count')
run_test = skip_template_object.get_run_tests_from_name('test_validate_minimum_replica_count')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(spec_replicas, marks)

    @pytest.mark.parametrize(('input_template_name', 'input_kind', 'input_minimum_replica_count'),
                             input_minimum_replica_count_params)
    def test_validate_minimum_replica_count(input_template_name, input_kind, input_minimum_replica_count):
        """Validate the minimum replicaCount for the given service from input parameters.

            Args:
                input_template_name (str): The template name to validate.
                input_kind (str): The kind of the template to validate.
                input_minimum_replica_count (int): The minimum replica count to validate.

            Raises:
                AssertionError: If the replicaCount/replicas field is missing or does not meet the specified conditions.

            Example:
                spec_result = helmfile_template_object.get_replica_count(spec_replicas, "template1")
                spec_result = [("template1", "kind1", 3)]
                     spec_result[0][0] = "template1"
                     spec_result[0][1] = "kind1"
                     spec_result[0][2] = 3
                test_validate_minimum_replica_count("template1", "kind1", 3)
                # Assert if replicaCount/replicas is of type int.
                # Assert if replicaCount/replicas >= given input_minimum_replica_count
        """
        replica_count_result = helmfile_template_object.get_replica_count(spec_replicas, input_template_name)
        replicas_result = helmfile_template_object.get_replicas(spec_replicas, input_template_name)
        input_minimum_replica_count = int(input_minimum_replica_count)

        if len(replica_count_result) > 0:
            if replica_count_result[0][0] == input_template_name and \
               replica_count_result[0][1] == input_kind and \
               isinstance(replica_count_result[0][2], int) and \
               replica_count_result[0][2] >= input_minimum_replica_count:
                assert True
        elif len(replicas_result) > 0:
            if replicas_result[0][0] == input_template_name and \
               replicas_result[0][1] == input_kind and \
               isinstance(replicas_result[0][2], int) and \
               replicas_result[0][2] >= input_minimum_replica_count:
                assert True
        else:
            assert False
