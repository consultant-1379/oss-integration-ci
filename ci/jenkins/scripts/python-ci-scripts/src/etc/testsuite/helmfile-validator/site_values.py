"""This module handles site values file interaction."""

from memoization import cached
import yaml


class SiteValues:
    """This is the class to handle reading of values from the site_values_<template>.yaml."""

    @cached
    def __init__(self, values_file_path):
        """Use as a constructor."""
        self.values_file_path = values_file_path
        with open(values_file_path, encoding="utf-8") as values_file:
            self.site_values = yaml.load(values_file, Loader=yaml.CSafeLoader)

    def update_minimum_replica_count(self, minimum_replica_count_params):
        """Update minimum replica count template names."""
        tls = ('eric-data-search-engine-ingest-tls', 'Deployment', 2)
        if self.check_tls_status():
            return [tls if e[0] == 'eric-data-search-engine-ingest' else e for e in minimum_replica_count_params]
        return minimum_replica_count_params

    def check_tls_status(self):
        """Check if TLS has been enabled in the site values file."""
        for key in self.site_values['global'].items():
            if 'security' in key:
                for i_key in self.site_values['global']['security'].items():
                    if 'tls' in i_key:
                        return self.site_values['global']['security']['tls']['enabled']
        return False
