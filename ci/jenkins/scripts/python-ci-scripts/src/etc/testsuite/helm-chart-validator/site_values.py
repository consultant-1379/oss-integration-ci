"""This module handles site values file interaction."""

from memoization import cached
import yaml


# pylint: disable=too-few-public-methods
class SiteValues:
    """This is the class to handle reading of values from the site_values_<template>.yaml."""

    @cached
    def __init__(self, values_file_path):
        """Use as a constructor."""
        self.values_file_path = values_file_path
        with open(values_file_path, encoding="utf-8") as values_file:
            self.site_values = yaml.load(values_file, Loader=yaml.CSafeLoader)
