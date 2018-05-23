"""API Base Classes for BitEx."""
# Import Built-Ins
import logging
import warnings
import configparser
import time
import os

# Import Homebrew
from bitex.exceptions import IncompleteCredentialsWarning
from bitex.exceptions import IncompleteCredentialsError
from bitex.exceptions import IncompleteAPIConfigurationWarning
from bitex.exceptions import IncompleteCredentialConfigurationWarning

# Init Logging Facilities
log = logging.getLogger(__name__)


class BaseAPI:
    """
    BaseAPI provides lowest-common-denominator methods used in all API types.

    It provides a nonce() method, basic configuration loading and credential
    validity checking method check_auth_requirements(), which should be
    extended in subclasses to cover any additional parameters that are necessary.
    """

    def __init__(self, *, addr, key, secret, version, config):
        """
        Initialize a BaseAPI instance.

        :param addr: str, API url
        :param key: str, API key
        :param secret: str, API secret
        :param version: str, version of API to request
        :param config: str, path to config file
        """
        # validate inputs
        if key == '' or secret == '':
            raise ValueError("Invalid key or secret - cannot be empty string! "
                             "Pass None instead!")

        self.addr = addr
        self.key = key if key else None
        self.secret = secret if secret else None
        self.version = version if version else None

        try:
            self.check_auth_requirements()
        except IncompleteCredentialsError:
            if config is None:
                warnings.warn("Incomplete Credentials were given - "
                              "authentication may not work!",
                              IncompleteCredentialsWarning)

        self.config_file = config
        if self.config_file:
            self.load_config(self.config_file)

    def check_auth_requirements(self):
        """
        Check that neither self.key nor self.secret are None.

        If so, this method raises an IncompleteCredentialsError. Otherwise returns None.

        Extend this in child classes if you need to check for further
        required values.

        :raise: IncompleteCredentialsError
        :return: None
        """
        if any(attr is None for attr in (self.key, self.secret)):
            raise IncompleteCredentialsError
        else:
            return

    def load_config(self, fname):
        """
        Load configuration from an ini file.

        Return it, in case this func needs to be extended.

        :param fname: path to file
        :return: configparser.ConfigParser() Obj
        """
        if not os.path.exists(fname):
            raise FileNotFoundError

        conf = configparser.ConfigParser(allow_no_value=True)
        conf.read(fname)
        try:
            self.key = conf['AUTH']['key']
        except KeyError:
            if self.key is None:
                warnings.warn("Key parameter not present in config - "
                              "authentication may not work!",
                              IncompleteCredentialConfigurationWarning)
        try:
            self.secret = conf['AUTH']['secret']
        except KeyError:
            if self.secret is None:
                warnings.warn("Secret parameter not present in config - "
                              "authentication may not work!",
                              IncompleteCredentialConfigurationWarning)
        try:
            self.addr = conf['API']['address']
        except KeyError:
            if self.addr is None:
                warnings.warn("API address not present in config - "
                              "requests may not work!",
                              IncompleteAPIConfigurationWarning)
        try:
            self.version = conf['API']['version']
        except KeyError:
            if self.version is None:
                warnings.warn("API version was not present in config - "
                              "requests may not work!",
                              IncompleteAPIConfigurationWarning)
        return conf

    @staticmethod
    def nonce():
        """
        Create a Nonce value for signature generation.

        :return: Nonce as string
        """
        return str(int(round(1000 * time.time())))
