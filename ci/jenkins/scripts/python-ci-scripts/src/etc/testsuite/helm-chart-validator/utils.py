"""This module is a general utils files to share reusable functions with the tests scripts."""

import pytest
import re
from memoization import cached

from datetime import date


@cached
def find_key_in_dictionary(input_key, dictionary):
    """Get key from a given dictionary."""
    if hasattr(dictionary, 'items'):
        for k, v in dictionary.items():
            if k == input_key:
                yield v
            if isinstance(v, dict):
                for result in find_key_in_dictionary(input_key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find_key_in_dictionary(input_key, d):
                        yield result


@cached
def flatten_list(input_list):
    """Given the inputted of mixed values, get back a complete list."""
    output_list = []
    for i in input_list:
        if isinstance(i, list):
            for j in flatten_list(i):
                output_list.append(j)
        else:
            output_list.append(i)
    return output_list


@cached
def mark_test_parameters(parameter_list, marks):
    """Mark parameterized tests."""
    marked_test_parameters = []
    for test_parameter in parameter_list:
        template_name, template_kind, *key_or_path = test_parameter
        lookup_marks_result = __lookup_test_mark_list(marks, template_name, template_kind)
        if lookup_marks_result is None:
            marked_test_parameters.append(test_parameter)
        else:
            marked_test_parameter = pytest.param(template_name,
                                                 template_kind,
                                                 *key_or_path,
                                                 marks=lookup_marks_result)
            marked_test_parameters.append(marked_test_parameter)
    return marked_test_parameters


@cached
def __lookup_test_mark_list(marks, template_name, template_kind):
    for template_name_regex_list, template_kind_match_list, test_mark in marks:
        for template_name_regex in template_name_regex_list:
            if re.search(template_name_regex, template_name) is not None:
                for template_kind_match in template_kind_match_list:
                    if template_kind_match == template_kind:
                        return test_mark
    return None


def get_marks_from_skips(skips):
    """Get all the skips."""
    skips_in_tuple = []
    if skips:
        for skip in skips:
            type = skip[3]
            if "dates" in type:
                tuple_pytest = ()
                tuple_pytest = tuple_pytest + (pytest.mark.xfail(date.today() < date(2020, 8, 18), reason=skip[2]),)
                skip = skip[:2] + tuple_pytest
                skips_in_tuple.append(skip)

            if "xfail" in type:
                tuple_pytest = ()
                tuple_pytest = tuple_pytest + (pytest.mark.xfail(strict=True, reason=skip[2]),)
                skip = skip[:2] + tuple_pytest
                skips_in_tuple.append(skip)

            if "skip" in type:
                tuple_pytest = ()
                tuple_pytest = tuple_pytest + (pytest.mark.skip(reason=skip[2]),)
                skip = skip[:2] + tuple_pytest
                skips_in_tuple.append(skip)
    return skips_in_tuple
