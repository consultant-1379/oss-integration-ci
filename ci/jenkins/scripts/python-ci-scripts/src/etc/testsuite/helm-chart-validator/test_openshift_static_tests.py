"""This module contains test cases to verify that the templates follow the guidelines for Openshift Environments."""

import pytest
from helm_template import HelmTemplate
from utils import mark_test_parameters, get_marks_from_skips
from skip_template import SkipTemplate

helm_template_object = HelmTemplate("/test-files/test_chart.tgz", "/test-files/site_values_template.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()

skips = skip_template_object.get_skips_from_name(
    'test_to_ensure_all_containers_with_security_context_has_run_as_non_root_set')
run_test = skip_template_object.get_run_tests_from_name(
    'test_to_ensure_all_containers_with_security_context_has_run_as_non_root_set')


if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(helm_template_object.get_pods_and_containers(), marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'pod_spec', 'container_spec'), test_parameters)
    def test_to_ensure_all_containers_with_security_context_has_run_as_non_root_set(template_name, kind,
                                                                                    pod_spec, container_spec):
        """
        Test that there is a runAsNonRoot set with appropriate permission associated with each security context set
        """
        resulting_security_context = \
            helm_template_object.get_resulting_container_security_context(
                pod_spec=pod_spec, container_spec=container_spec)
        assert isinstance(resulting_security_context.get('runAsNonRoot', None), bool)


skips = skip_template_object.get_skips_from_name(
    'test_ensure_network_policy_has_a_port_for_egress_open_connection')
run_test = skip_template_object.get_run_tests_from_name(
    'test_ensure_network_policy_has_a_port_for_egress_open_connection')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(
        helm_template_object.get_names_of_objects_of_kind_network_policy_with_test_params('NetworkPolicy'), marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'network_policy_spec'), test_parameters)
    def test_ensure_network_policy_has_a_port_for_egress_open_connection(
            template_name, kind, network_policy_spec):
        """Test that each Network Policy contains a pod selector tag and an egress connection."""
        found = False
        if helm_template_object.does_network_policy_have_an_egress_open_connection(
                network_policy=network_policy_spec
        ):
            found = True

        assert found is True
