"""Module for mocking request.response."""
import json
import requests


# pylint: disable=too-few-public-methods
class MockResponse:
    """Class to mock the requests.response object."""

    # pylint: disable=too-many-arguments
    def __init__(self, content=None, status_code=200, timeout=False, redirects=False,
                 headers=None):
        """Create MockResponse with parameters."""
        self.content = content
        self.status_code = status_code
        self.timeout = timeout
        self.redirects = redirects
        self.headers = {} if headers is None else headers

    def raise_for_status(self):
        """Mock response throws exception based on parameters."""
        if self.status_code != 200:
            self.content = "HTTPError generated"
            raise requests.exceptions.HTTPError(f"Status: HTTPError - Error Code {self.status_code}")
        if self.timeout:
            self.content = "Timeout error generated"
            raise requests.exceptions.Timeout("Request Timed Out")
        if self.redirects:
            self.content = "TooManyRedirects error generated"
            raise requests.exceptions.TooManyRedirects("Too Many Redirects")

    def json(self):
        """Mock method to convert the content to JSON."""
        return json.loads(self.content)

    # pylint: disable=unused-argument
    def iter_content(self, chunk_size):
        """Mock method to convert the content to an iterative."""
        return self.content.split()
