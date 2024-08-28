"""This module defines custom exceptions."""


class Error(Exception):
    """The base class for exceptions in python-ci."""


class SpinCLIError(Error):
    """Exception raised for an error calling Spin CLI."""


class MissingEnvVarError(Error):
    """Exception raised when a required environment variable is not set."""


class LRCLIError(Error):
    """Exception raised for an error calling LR CLI."""
