"""Bitfinex REST API backend.

Documentation available at:
    https://docs.bitfinex.com/docs
    Important:
        If an IP address exceeds a certain number of requests per minute (between 10 and 90) to a
        specific REST API endpoint e.g., /ticker, the requesting IP address will be blocked for
        10-60 seconds on that endpoint and the JSON response {"error": "ERR_RATE_LIMIT"} will be
        returned.

"""
# pylint: disable=too-many-arguments
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64

# Import Third-Party

# Import Homebrew
from bitex.api.REST import RESTAPI

log = logging.getLogger(__name__)


class BitfinexREST(RESTAPI):
    """Bitfinex REST API class."""

    def __init__(self, addr=None, key=None, secret=None, version=None, config=None, timeout=None,
                 **kwargs):
        """Initialize the class instance."""
        addr = 'https://api.bitfinex.com' if not addr else addr
        version = 'v1' if not version else version
        super(BitfinexREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                           timeout=timeout, config=config, **kwargs)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(BitfinexREST, self).sign_request_kwargs(endpoint,
                                                                   **kwargs)

        # Parameters go into headers, so pop params key and generate signature
        params = req_kwargs.pop('params')
        uri = self.generate_uri(endpoint)
        nonce = self.nonce()

        if self.version == 'v1':

            params['request'] = uri
            params['nonce'] = nonce

            # convert to json, encode and hash
            payload = json.dumps(params)
            data = base64.standard_b64encode(payload.encode('utf8'))

            hmac_sig = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
            signature = hmac_sig.hexdigest()

            # Update headers and return
            req_kwargs['headers'] = {"X-BFX-APIKEY": self.key,
                                     "X-BFX-SIGNATURE": signature,
                                     "X-BFX-PAYLOAD": data,
                                     "Content-Type": "application/json",
                                     "Accept": "application/json"}

        elif self.version == 'v2':

            # convert to json, encode and hash
            payload = json.dumps(params)
            signature = "/api" + uri + nonce + payload
            data = signature.encode('utf8')

            hmac_sig = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
            signature = hmac_sig.hexdigest()

            # Update headers and return
            req_kwargs['headers'] = {"bfx-apikey": self.key,
                                     "bfx-signature": signature,
                                     "bfx-nonce": nonce,
                                     "content-type": "application/json"}

        return req_kwargs
