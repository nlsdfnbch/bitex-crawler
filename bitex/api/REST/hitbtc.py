"""Bitstamp REST API backend.

Documentation available here:
    https://api.hitbtc.com/
"""
# Import Built-ins
import logging

# Import Homebrew
from bitex.api.REST import RESTAPI

# Init Logging Facilities
log = logging.getLogger(__name__)


class HitBTCREST(RESTAPI):
    """HitBTC REST API class."""

    def __init__(self, key=None, secret=None, version=None, addr=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        version = '2' if not version else version
        addr = 'https://api.hitbtc.com/api' if not addr else addr
        super(HitBTCREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                         timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(HitBTCREST, self).sign_request_kwargs(endpoint,
                                                                 **kwargs)

        # prepare Payload arguments
        req_kwargs['auth'] = self.key, self.secret

        return req_kwargs
