"""This module contains test cases to verify that the templates follow the guidelines for Customer Environments."""

import pytest
from helm_template import HelmTemplate
from site_values import SiteValues
from skip_template import SkipTemplate
from utils import mark_test_parameters, get_marks_from_skips


@pytest.fixture(scope="module")
def site_values_object():
    return SiteValues("/test-files/site_values_template.yaml")


helm_template_object = HelmTemplate("/test-files/test_chart.tgz", "/test-files/site_values_template.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()


containers = helm_template_object.get_values_with_a_specific_path("spec.template.spec.containers")
skips = skip_template_object.get_skips_from_name('test_zypper_commands_are_not_used')
run_test = skip_template_object.get_run_tests_from_name('test_zypper_commands_are_not_used')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(containers, marks)

    @pytest.mark.parametrize(('template', 'kind', 'container'), test_parameters)
    def test_zypper_commands_are_not_used(template, kind, container):
        """Test that zypper is not used in the template.spec.containers of all necessary resources."""
        assert 'zypper' not in str(container)
