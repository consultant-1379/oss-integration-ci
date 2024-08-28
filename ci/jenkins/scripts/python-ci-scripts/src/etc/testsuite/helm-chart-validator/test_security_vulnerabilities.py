"""This module contains test cases to verify that the templates follow the Security Guidelines in EO."""

import pytest
from utils import mark_test_parameters, get_marks_from_skips
from helm_template import HelmTemplate
from skip_template import SkipTemplate

helm_template_object = HelmTemplate("/test-files/test_chart.tgz", "/test-files/site_values_template.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()

service_types = helm_template_object.get_values_with_a_specific_path("spec.type")
skips = skip_template_object.get_skips_from_name('test_node_port_is_not_used_in_service_exposure')
run_test = skip_template_object.get_run_tests_from_name('test_node_port_is_not_used_in_service_exposure')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(service_types, marks)

    @pytest.mark.parametrize(('template', 'kind', 'service_type'), test_parameters)
    def test_node_port_is_not_used_in_service_exposure(template, kind, service_type):
        """Test that NodePort is not used in the template.type of all necessary resources."""
        assert 'NodePort' not in service_type
