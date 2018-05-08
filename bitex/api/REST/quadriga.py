"""QuadrigaCX REST API backend.

Documentation available here:
    https://www.quadrigacx.com/api_info
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

# Init Logging Facilities
log = logging.getLogger(__name__)


class QuadrigaCXREST(RESTAPI):
    """QuadrigaCX REST API class."""

    def __init__(self, key=None, secret=None, client_id=None, version=None,
                 addr=None, timeout=5, config=None):
        """Initialize the class instance."""
        version = 'v2' if not version else version
        addr = 'https://api.quadrigacx.com' if not addr else addr

        if client_id == '':
            raise ValueError("Invalid client id - cannot be empty string! "
                             "Pass None instead!")
        self.client_id = client_id
        super(QuadrigaCXREST, self).__init__(addr=addr, version=version,
                                             key=key, secret=secret,
                                             timeout=timeout, config=config)

    def check_auth_requirements(self):
        """Check if authentication requirements are met."""
        try:
            super(QuadrigaCXREST, self).check_auth_requirements()
        except IncompleteCredentialsError:
            raise

        if self.client_id is None:
            raise IncompleteCredentialsError
        else:
            return

    def load_config(self, fname):
        """Load configuration from a file."""
        conf = super(QuadrigaCXREST, self).load_config(fname)
        try:
            self.client_id = conf['AUTH']['client_id']
        except KeyError:
            warnings.warn("'client_id' not found in config!",
                          IncompleteCredentialConfigurationWarning)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(QuadrigaCXREST, self).sign_request_kwargs(endpoint,
                                                                     **kwargs)

        # Prepare Payload arguments
        params = kwargs.get('params', {})
        nonce = self.nonce()
        msg = nonce + self.client_id + self.key

        # generate signature
        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'),
                             hashlib.sha256).hexdigest()
        params.update({'key': self.key, 'signature': signature, 'nonce': nonce})
        # update req_kwargs keys
        req_kwargs['json'] = params
        return req_kwargs
