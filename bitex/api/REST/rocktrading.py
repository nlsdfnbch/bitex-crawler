"""The Rock Trading Ltd. REST API backend.

Documentation available here:
    https://api.therocktrading.com/doc/
"""
# Import Built-ins
import logging
import hashlib
import hmac
from urllib.parse import urlencode

# Import Third-Party

# Import Homebrew# Import Homebrew
from bitex.api.REST import RESTAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class RockTradingREST(RESTAPI):
    """The Rock Trading Ltd REST API class."""

    def __init__(self, key=None, secret=None, version=None, config=None, addr=None, timeout=5,
                 **kwargs):
        """Initialize the class instance."""
        version = 'v1' if not version else version
        addr = 'https://api.therocktrading.com' if not addr else addr
        super(RockTradingREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                              timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(RockTradingREST, self).sign_request_kwargs(endpoint,
                                                                      **kwargs)
        # Prepare Payload arguments
        nonce = self.nonce()
        params = kwargs.get('params', {})
        payload = params

        # generate signature
        encoded_params = urlencode(params)
        encoded_url = req_kwargs['url'] + '?' + encoded_params
        msg = nonce + encoded_url
        sig = hmac.new(self.secret.encode(), msg.encode(),
                       hashlib.sha512).hexdigest()

        # Update req_kwargs keys
        req_kwargs['headers'] = {'X-TRT-KEY': self.key, 'X-TRT-NONCE': int(nonce),
                                 'X-TRT-SIGN': sig,
                                 'Content-Type': 'application/json'}
        req_kwargs['json'] = payload
        req_kwargs['url'] = encoded_url
        return req_kwargs
