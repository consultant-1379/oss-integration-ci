"""
This module contains test cases to verify the minimum docker image version that is used
"""

import pytest
from semver import VersionInfo
from helm_template import HelmTemplate
from skip_template import SkipTemplate
from utils import mark_test_parameters, get_marks_from_skips


@pytest.fixture(scope="module")
def image_versions():
    return [("keycloak-client", "1.0.0-17")]


helm_template_object = HelmTemplate("/test-files/test_chart.tgz", "/test-files/site_values_template.yaml")
skip_template_object = SkipTemplate("/test-files/skip_list.json", "/test-files/common_skip_list.json")
master_skip_list = skip_template_object.get_master_skips_file()

images = helm_template_object.get_all_references_with_given_key("image")
skips = skip_template_object.get_skips_from_name('test_minimum_image_version')
run_test = skip_template_object.get_run_tests_from_name('test_minimum_image_version')

if run_test:
    marks = get_marks_from_skips(skips)
    test_parameters = mark_test_parameters(images, marks)

    @pytest.mark.parametrize(('template', 'kind', 'image'), test_parameters)
    def test_minimum_image_version(template, kind, image, image_versions):
        """Test that docker images used in the Chart don't fall below a minimum image version (Only Keycloak-client)"""
        for image_version in image_versions:
            if image_version[0] in image:
                assert VersionInfo.compare(VersionInfo.parse(image.split(":")[1]),
                                           VersionInfo.parse(image_version[1])) != -1
