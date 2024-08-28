"""Module for the generation of the netrc file."""
import os

MACHINE_ROW = 'machine %s login %s password %s\n'


class Netrc:
    """Netrc class."""

    def __init__(self,
                 path=None,
                 file_name=".netrc"):
        """Initialize Netrc object."""
        if path is None:
            path = os.environ.get("HOME", ".")
        self.file = os.path.join(path, file_name)

    def add_login(self, machine, login, password):
        """
        Add credential to netrc file.

        Inputs:
            machine: gerrit URL example gerrit-gamma.gic.ericsson.se
            login: username to log into the URL above
            password: password to log into the URL above
        """
        changemod = not os.path.exists(self.file)
        with open(self.file, 'a', encoding="utf-8") as file_cred:
            file_cred.write(MACHINE_ROW % (machine, login, password))
        if changemod:
            os.chmod(self.file, 0o600)

    def remove(self):
        """Remove the netrc object."""
        if os.path.exists(self.file):
            os.remove(self.file)
