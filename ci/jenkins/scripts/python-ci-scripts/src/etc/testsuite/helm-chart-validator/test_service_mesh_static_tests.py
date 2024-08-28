"""This module contains test cases to verify that the templates follow the Service Mesh Design Rules."""

import pytest
from helm_template import HelmTemplate
from utils import mark_test_parameters, get_marks_from_skips
from skip_template import SkipTemplate

helm_template_object = HelmTemplate("/test-files/test_chart.tgz", "/test-files/site_values_template.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()


skips = skip_template_object.get_skips_from_name(
    'test_service_mesh_virtual_service_export_to')
run_test = skip_template_object.get_run_tests_from_name(
    'test_service_mesh_virtual_service_export_to')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(
        helm_template_object.get_names_of_service_mesh_resources_of_given_kind('VirtualService'), marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'spec'), test_parameters)
    def test_service_mesh_virtual_service_export_to(template_name, kind, spec):
        """The field spec.exportTo shall be hardcoded to a single entry, which is set to "."""
        found = False
        if helm_template_object.does_service_mesh_object_have_export_to(spec=spec):
            found = True
        assert found is True


skips = skip_template_object.get_skips_from_name(
    'test_service_mesh_destination_rule_export_to')
run_test = skip_template_object.get_run_tests_from_name(
    'test_service_mesh_destination_rule_export_to')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(
        helm_template_object.get_names_of_service_mesh_resources_of_given_kind('DestinationRule'), marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'spec'), test_parameters)
    def test_service_mesh_destination_rule_export_to(template_name, kind, spec):
        """The field spec.exportTo shall be hardcoded to a single entry, which is set to "."."""
        found = False
        if helm_template_object.does_service_mesh_object_have_export_to(spec=spec):
            found = True
        assert found is True


skips = skip_template_object.get_skips_from_name(
    'test_service_mesh_service_entry_export_to')
run_test = skip_template_object.get_run_tests_from_name(
    'test_service_mesh_service_entry_export_to')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(
        helm_template_object.get_names_of_service_mesh_resources_of_given_kind('ServiceEntry'), marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'spec'), test_parameters)
    def test_service_mesh_service_entry_export_to(template_name, kind, spec):
        """The field spec.exportTo shall be hardcoded to a single entry, which is set to "."."""
        found = False
        if helm_template_object.does_service_mesh_object_have_export_to(spec=spec):
            found = True
        assert found is True


skips = skip_template_object.get_skips_from_name(
    'test_service_mesh_ingress_gateway_hosts')
run_test = skip_template_object.get_run_tests_from_name(
    'test_service_mesh_ingress_gateway_hosts')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(
        helm_template_object.get_names_of_service_mesh_gateway_resources_as_ingress(), marks)

    @pytest.mark.parametrize(('template_name', 'kind', 'spec'), test_parameters)
    def test_service_mesh_ingress_gateway_hosts(template_name, kind, spec):
        """The field spec.servers.hosts in case all hosts to be exposed are not known it can be set to "./*"."""
        found = False
        if helm_template_object.does_service_mesh_object_have_hosts_with_specific_namespace(spec=spec):
            found = True
        assert found is True
