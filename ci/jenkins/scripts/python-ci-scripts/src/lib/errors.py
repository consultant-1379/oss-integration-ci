"""This module defines custom exceptions."""


class Error(Exception):
    """The base class for exceptions in python-ci."""


class MissingCSARError(Error):
    """Exception raised when a CSAR can't be found."""


class InvalidArgumentValueError(Error):
    """Exception raised when an argument value is invalid."""


class HelmfileReleaseError(Error):
    """Exception raised when an error is found related to a Helmfile release."""


class MissingHelmfileTag(Error):
    """Exception raised when a specified tag is missing from a Helmfile."""


class HelmCommandError(Error):
    """Exception raised when a helm command fails."""


class NamespaceExistsError(Error):
    """Exception raised when a namespace is found."""


class NamespaceCreationError(Error):
    """Exception raised when a namespace creation fails."""


class NamespaceDeletionError(Error):
    """Exception raised when a namespace deletion fails."""


class InvalidPropertyError(Error):
    """Exception raised when an invalid property entry is found."""


class KubectlCommandError(Error):
    """Exception raised when a kubectl command fails."""


class ServiceAccountCreationError(Error):
    """Exception raised when a service account creation fails."""


class CreateSecretError(Error):
    """Exception raised when a secret fails to create."""


class DeleteSecretError(Error):
    """Exception raised when a secret fails to create."""


class RemovalOfHelmReleasesError(Error):
    """Exception raised when removing helm releases from a namespace fails."""


class ClusterRoleCreationError(Error):
    """Exception raised when a cluster role creation fails."""


class CreateClusterRolebindingError(Error):
    """Exception raised when creating a cluster rolebinding fails."""


class CRDComponentDeletionError(Error):
    """Exception raised when deleting CRD components from CRD namespace fails."""


class ClusterroleDeletionError(Error):
    """Exception raised when a cluster role deletion fails."""


class ClusterrolebindingDeletionError(Error):
    """Exception raised when a cluster rolebinding deletion fails."""


class AnnotationSearchError(Error):
    """Exception raised when a search for CRD components/Cluster Roles fails."""


class MissingHelmfileValueError(Error):
    """Exception raised when a helmfile is missing a necessary value."""


class MissingOptionalityValueError(Error):
    """Exception raised when a helmfile is missing an optionality value."""


class CRNonConformanceError(Error):
    """Exception raised when a CR does not conform to a CRD schema."""


class GerritError(Error):
    """Exception raised when a Gerrit Error is thrown."""


class GerritSubmitError(Error):
    """Exception raised when a Gerrit Submit Error is thrown."""


class DMVersionFetchError(Error):
    """Exception raised when trying to set the Deployment Manager version from the helmfile."""


class HelmRepoIndexFailedError(Error):
    """Exception raised when a helm repo index command fails."""


class PreCodeReviewFailedError(Error):
    """Exception raised when a helm repo index command fails."""


class PersistentVolumeWaitError(Error):
    """Exception raised when Persistent Volumes remain on the namespace."""
