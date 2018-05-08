"""Quoine REST API backend.

Documentation available here:
    https://www.bitstamp.net/api/
"""
# Import Built-ins
import logging
import urllib
import urllib.parse

# Import Third-Party
import jwt
# Import Homebrew
from bitex.api.REST import RESTAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class QuoineREST(RESTAPI):
    """Quoine REST API class."""

    def __init__(self, key=None, secret=None, version=None, config=None,
                 addr=None, timeout=5):
        """Initialize the class instance."""
        addr = 'https://api.quoine.com/' if not addr else addr
        version = '2' if not version else version
        super(QuoineREST, self).__init__(addr=addr, version=version,
                                         key=key, secret=secret, config=config,
                                         timeout=timeout)

    def generate_uri(self, endpoint):
        """Generate a Unique Resource Identifier (URI).

        The Quoine Api requires the API version to be designated in each
        requests's header as {'X-Quoine-API-Version': 2}, instead of adding it
        to the URL. Hence, we need to adapt generate_uri.
        """
        return endpoint

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(QuoineREST, self).sign_request_kwargs(endpoint,
                                                                 **kwargs)

        # Prepare Payload arguments
        params = kwargs.get('params', {})

        path = '/' + endpoint

        if req_kwargs.get('method', 'POST') == 'POST':
            req_kwargs['json'] = params
            del req_kwargs['params']
        elif req_kwargs.get('method') == 'GET' and params:
            path += '?' + urllib.parse.urlencode(params)

        msg = {'path': path, 'nonce': self.nonce(), 'token_id': self.key}

        # generate signature
        signature = jwt.encode(msg, self.secret, algorithm='HS256')

        req_kwargs['headers'] = {'X-Quoine-API-Version': self.version,
                                 'X-Quoine-Auth': signature,
                                 'Content-Type': 'application/json'}

        return req_kwargs
