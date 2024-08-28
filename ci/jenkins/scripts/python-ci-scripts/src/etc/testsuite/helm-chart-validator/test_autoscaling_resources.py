"""This module contains test cases to verify that HPA resources are not being used by charts."""

import pytest
from helm_template import HelmTemplate
from utils import mark_test_parameters, get_marks_from_skips
from skip_template import SkipTemplate

helm_template_object = HelmTemplate("/test-files/test_chart.tgz", "/test-files/site_values_template.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()


pod_autoscalers = helm_template_object.get_names_of_service_mesh_resources_of_given_kind("HorizontalPodAutoscaler")
skips = skip_template_object.get_skips_from_name('test_autoscaling_resources')
run_test = skip_template_object.get_run_tests_from_name('test_autoscaling_resources')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(pod_autoscalers, marks)

    # pylint: disable=unused-argument
    @pytest.mark.parametrize(('template_name', 'kind', 'pod_autoscaler'), test_parameters)
    def test_no_hpa_resources(template_name, kind, pod_autoscaler):
        """Test that there are no HPA resources within the helm template."""
        assert kind != "HorizontalPodAutoscaler"
