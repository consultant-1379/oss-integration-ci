"""This module contains the Skip Template which will pass in a file to skip specific sections."""

import json


class Singleton(type):
    """Ensures a single instance of the helm skip template object is created."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Use to verify the class creation."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SkipTemplate(metaclass=Singleton):
    """This class contains methods for retrieving information from the rendered chart."""

    def __init__(self, skip_list_path_json, common_skip_list_path_json):
        """Use as a constructor."""
        self.skip_list_path_json = skip_list_path_json
        self.common_skip_list_path_json = common_skip_list_path_json
        self.master_list_path_json = "./master_skip_list.json"

    def get_master_skips_file(self):
        """Get all the test to skip as one master list."""
        with open(self.common_skip_list_path_json) as common_skip_list, open(self.skip_list_path_json) as skip_list:
            common_skip_list_json_object = json.load(common_skip_list)
            skip_list_json_object = json.load(skip_list)

        for common_skip_object in common_skip_list_json_object:
            for skip_object in skip_list_json_object:
                master_skips = []
                if skip_object == common_skip_object:
                    for skip in common_skip_list_json_object[common_skip_object]["skips"]:
                        if skip not in master_skips:
                            master_skips.append(skip)

                    for skip in skip_list_json_object[skip_object]["skips"]:
                        if skip not in master_skips:
                            master_skips.append(skip)

                    skip_list_json_object[skip_object]["skips"] = master_skips

        with open(self.master_list_path_json, 'w') as output_file:
            json.dump(skip_list_json_object, output_file, indent=4)

    def get_skips_from_name(self, name):
        """Get the list of test to skip."""
        tuple_list = []
        with open(self.master_list_path_json) as json_file:
            json_object = json.load(json_file)

            skips_arrays = json_object[name]['skips']

            for skip in skips_arrays:
                mark_tuple = ()
                for mark in skip:
                    mark_tuple = mark_tuple + (mark,)
                tuple_list.append(mark_tuple)

        return tuple_list

    def get_run_tests_from_name(self, name):
        """Get the list of tests to execute."""
        with open(self.master_list_path_json) as json_file:
            json_object = json.load(json_file)

            return json_object[name]['runTests']
