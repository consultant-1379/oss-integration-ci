"""This module contains the Check Template which will pass in a file to specifically test for template."""
import logging
import json

LOG = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class CheckTemplate:
    """This class contains methods for retrieving information from the rendered chart."""

    def __init__(self, check_content_json):
        """Use as a constructor."""
        self.check_specific_content_json = check_content_json

    def get_check_content(self, name):
        """Get the list of content to check for the helmfile."""
        tuple_list = []
        with open(self.check_specific_content_json, encoding="utf-8") as json_file:
            json_object = json.load(json_file)
            content_arrays = json_object[name]['check']
            for content in content_arrays:
                mark_tuple = ()
                for mark in content:
                    LOG.info("mark %s", mark)
                    mark = ''.join(mark)
                    mark_tuple = mark_tuple + (mark,)
                tuple_list.append(mark_tuple)
        LOG.info("tuple_list %s", tuple_list)
        return tuple_list
