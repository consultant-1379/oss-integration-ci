"""This module contains test cases to verify that the templates follow the guidelines for Openshift Environments."""
# flake8: noqa: E501
import pytest
from helmfile_template import HelmfileTemplate
from utils import mark_test_parameters, get_marks_from_skips
from skip_template import SkipTemplate

helmfile_template_object = HelmfileTemplate("/test-files/helmfile", "/test-files/site_values.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()

pods_and_containers = helmfile_template_object.get_pods_and_containers()
skips = skip_template_object.get_skips_from_name('test_to_ensure_all_containers_with_securitycontext_has_runAsNonRoot_set')
run_test = skip_template_object.get_run_tests_from_name('test_to_ensure_all_containers_with_securitycontext_has_runAsNonRoot_set')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(pods_and_containers, marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'pod_spec', 'container_spec'), test_parameters)
    def test_to_ensure_all_containers_with_securitycontext_has_runAsNonRoot_set(template_name, kind, pod_spec, container_spec):
        """Test that there is a runAsNonRoot set with appropriate permission associated with each security context set"""
        resulting_security_context = helmfile_template_object.get_resulting_container_security_context(pod_spec=pod_spec, container_spec=container_spec)
        assert type(resulting_security_context.get('runAsNonRoot', None)) is bool


pods_and_containers = helmfile_template_object.get_pods_and_containers()
skips = skip_template_object.get_skips_from_name('test_to_ensure_cvnfm_containters_with_securitycontext_dont_have_runAsUser_set')
run_test = skip_template_object.get_run_tests_from_name('test_to_ensure_cvnfm_containters_with_securitycontext_dont_have_runAsUser_set')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(pods_and_containers, marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'pod_spec', 'container_spec'), test_parameters)
    def test_to_ensure_cvnfm_containters_with_securitycontext_dont_have_runAsUser_set(template_name, kind, pod_spec, container_spec):
        """Test that there is no runUser parameter set associated to each security context"""
        resulting_security_context = helmfile_template_object.get_resulting_container_security_context(pod_spec=pod_spec, container_spec=container_spec)
        assert resulting_security_context.get('runAsUser', None) is None
