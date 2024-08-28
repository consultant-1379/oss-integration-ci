"""This module contains test cases to verify that only the default storage class is referenced."""
# flake8: noqa: E501
import pytest
from helmfile_template import HelmfileTemplate
from utils import mark_test_parameters, get_marks_from_skips
from skip_template import SkipTemplate

helmfile_template_object = HelmfileTemplate("/test-files/helmfile", "/test-files/site_values.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()

storage_class_names = helmfile_template_object.get_all_references_with_given_key("storageClassName")
skips = skip_template_object.get_skips_from_name('test_storage_class_names_use_default_storage_class')
run_test = skip_template_object.get_run_tests_from_name('test_storage_class_names_use_default_storage_class')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(storage_class_names, marks)

    # pylint: disable=unused-argument
    @pytest.mark.parametrize(('template', 'kind', 'storage_class_name'), test_parameters)
    def test_storage_class_names_use_default_storage_class(template, kind, storage_class_name):
        """Test that the default storage class is used."""
        if kind != 'CustomResourceDefinition':
            assert storage_class_name is None
