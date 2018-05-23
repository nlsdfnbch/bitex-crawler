"""Kraken REST API backend.

Documentation available here:
    https://www.kraken.com/en-us/help/api
"""
# Import Built-ins
import logging
import hashlib
import hmac
import base64
import urllib
import urllib.parse

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class KrakenREST(RESTAPI):
    """Kraken REST API class."""

    def __init__(self, key=None, secret=None, version=None, addr=None, timeout=5, config=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = 'https://api.kraken.com' if not addr else addr
        version = '0' if not version else version
        super(KrakenREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                         config=config, timeout=timeout, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(KrakenREST, self).sign_request_kwargs(endpoint,
                                                                 **kwargs)
        # Prepare Payload
        payload = kwargs.get('params', {})
        payload['nonce'] = self.nonce()

        # Generate Signature
        postdata = urllib.parse.urlencode(payload)
        encoded = (payload['nonce'] + postdata).encode('utf-8')
        message = self.generate_uri(endpoint).encode('utf-8') + hashlib.sha256(encoded).digest()
        sig_hmac = hmac.new(base64.b64decode(self.secret), message, hashlib.sha512)
        signature = base64.b64encode(sig_hmac.digest())

        # Update request kwargs
        req_kwargs['headers'] = {'API-Key': self.key,
                                 'API-Sign': signature.decode('utf-8')}
        req_kwargs['data'] = payload

        return req_kwargs
