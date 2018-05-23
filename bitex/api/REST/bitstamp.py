"""Bitstamp REST API backend.

Documentation available here:
    https://www.bitstamp.net/api/
"""
# Import Built-ins
import logging
import hashlib
import hmac
import warnings

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI
from bitex.exceptions import IncompleteCredentialsError
from bitex.exceptions import IncompleteCredentialConfigurationWarning

log = logging.getLogger(__name__)


class BitstampREST(RESTAPI):
    """Bitstamp REST API class."""

    def __init__(self, addr=None, key=None, secret=None, version=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = addr or 'https://www.bitstamp.net/api'
        user_id = kwargs['user_id']
        if user_id == '':
            raise ValueError("Invalid user id - cannot be empty string! "
                             "Pass None instead!")
        version = version or 'v2'
        self.user_id = user_id
        super(BitstampREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                           timeout=timeout, config=config, **kwargs)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(BitstampREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

        if self.user_id is None:
            raise IncompleteCredentialsError

    def load_config(self, fname):
        """Load configuration from a file."""
        conf = super(BitstampREST, self).load_config(fname)
        try:
            self.user_id = conf['AUTH']['user_id']
        except KeyError:
            if self.user_id is None:
                warnings.warn("'user_id' not found in config!",
                              IncompleteCredentialConfigurationWarning)
        return conf

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the reuqest."""
        req_kwargs = super(BitstampREST, self).sign_request_kwargs(endpoint,
                                                                   **kwargs)

        # Generate Signature
        nonce = self.nonce()
        message = nonce + self.user_id + self.key
        signature = hmac.new(self.secret.encode('utf-8'),
                             message.encode('utf-8'), hashlib.sha256)
        signature = signature.hexdigest().upper()

        # Parameters go into the data kwarg, so move it there from 'params'
        params = req_kwargs.pop('params')
        params['key'] = self.key
        params['nonce'] = nonce
        params['signature'] = signature
        req_kwargs['data'] = params or req_kwargs['data']
        if endpoint.startswith('api'):
            req_kwargs['url'] = self.addr + '/' + endpoint

        return req_kwargs
