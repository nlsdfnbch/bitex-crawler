"""Vaultoro REST API backend.

Documentation available here:
    https://api.vaultoro.com/
"""
# Import Built-ins
import logging
import hashlib
import hmac
import urllib
import urllib.parse

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class VaultoroREST(RESTAPI):
    """Vaultoro REST API class."""

    def __init__(self, key=None, secret=None, version=None, addr=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = 'https://api.vaultoro.com' if not addr else addr
        super(VaultoroREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                           timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(VaultoroREST, self).sign_request_kwargs(endpoint,
                                                                   **kwargs)

        # prepare Payload arguments
        params = kwargs.get('params', {})
        nonce = self.nonce()
        url = (self.addr + '/1/' + endpoint + '?' + 'apikey=' + self.key + '&nonce=' +
               nonce + '&' + urllib.parse.urlencode(params))

        # generate signature
        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             url.encode(encoding='utf-8'),
                             hashlib.sha256).hexdigest()

        # update req_kwargs keys
        req_kwargs['headers'] = {'X-Signature': signature}
        req_kwargs['url'] = url
        return req_kwargs
