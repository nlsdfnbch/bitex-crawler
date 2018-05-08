"""GDAX REST API backend.

Documentation available here:
    https://docs.gdax.com/
"""
# Import Built-ins
import logging
import hashlib
import hmac
import base64
import time
import warnings

# Import Third-Party
from requests.auth import AuthBase

# Import Homebrew
from bitex.api.REST import RESTAPI
from bitex.exceptions import IncompleteCredentialsError
from bitex.exceptions import IncompleteCredentialConfigurationWarning

log = logging.getLogger(__name__)


class GDAXAuth(AuthBase):
    """GDAX Auth object."""

    def __init__(self, api_key, secret_key, passphrase):
        """Initialize the class instance."""
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        """Generate authentication headers."""
        timestamp = str(time.time())
        body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        body = body or ''
        message = (timestamp + request.method + request.path_url + body)
        hmac_key = base64.b64decode(self.secret_key.encode('utf8'))
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({'CB-ACCESS-SIGN': signature_b64,
                                'CB-ACCESS-TIMESTAMP': timestamp,
                                'CB-ACCESS-KEY': self.api_key,
                                'CB-ACCESS-PASSPHRASE': self.passphrase,
                                'Content-Type': 'application/json'})
        return request


class GDAXREST(RESTAPI):
    """GDAX REST API class."""

    def __init__(self, passphrase=None, key=None, secret=None, version=None,
                 addr=None, config=None, timeout=5):
        """Initialize the class instance."""
        if passphrase == '':
            raise ValueError("Invalid user id - cannot be empty string! "
                             "Pass None instead!")
        self.passphrase = passphrase
        addr = 'https://api.gdax.com' if not addr else addr

        super(GDAXREST, self).__init__(addr=addr, version=version, key=key,
                                       secret=secret, timeout=timeout,
                                       config=config)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(GDAXREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

        if self.passphrase is None:
            raise IncompleteCredentialsError
        return

    def load_config(self, fname):
        """Load configuration from a file."""
        conf = super(GDAXREST, self).load_config(fname)
        try:
            self.passphrase = conf['AUTH']['passphrase']
        except KeyError:
            warnings.warn("'passphrase' not found in config!",
                          IncompleteCredentialConfigurationWarning)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(GDAXREST, self).sign_request_kwargs(endpoint,
                                                               **kwargs)
        req_kwargs['auth'] = GDAXAuth(self.key, self.secret, self.passphrase)

        try:
            req_kwargs['json'] = kwargs['params']
        except KeyError:
            pass

        return req_kwargs
