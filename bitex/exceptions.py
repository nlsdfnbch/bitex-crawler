"""Contains all custom Warnings and Exceptions used in BitEx."""
# Import Built-Ins
import logging

# Import Third-Party

# Import Homebrew

# Init Logging Facilities
log = logging.getLogger(__name__)


class IncompleteCredentialsWarning(UserWarning):
    """Raised when a required parameter for authentication is not given."""

    pass


class IncompleteCredentialConfigurationWarning(UserWarning):
    """Raised when a required parameter for authentication isn't found in a config file."""

    pass


class IncompleteCredentialsError(Exception):
    """Raised when attempting to call private_query() of an API.

    For example when missing essential values to create a message signature (key, secret
    or additional other values, dependent on the exchange).
    """

    pass


class IncompleteAPIConfigurationWarning(UserWarning):
    """Raised if either the version or address key word is not found in a given config file."""

    pass


class EmptySupportedPairListWarning(UserWarning):
    """Raised when _supported_pairs is Empty or None while querying an API."""

    pass


class UnsupportedPairError(ValueError):
    """Raised if a given pair isn't supported by an Interface / API."""

    pass


class UnsupportedEndpointError(AttributeError):
    """Raised if a call to an API method, not part of the current API version, is made."""

    pass
