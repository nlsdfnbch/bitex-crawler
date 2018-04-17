"""CoinOne REST API backend.

Documentation available at:
    https://coinone.co.kr/developer/
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


class CoinoneREST(RESTAPI):
    """Coinone REST API class."""

    def __init__(self, addr=None, key=None, secret=None, version=None, config=None, timeout=None,
                 user_id=None, proxies=None):
        """Initialize the class instance."""
        addr = 'https://api.coinone.co.kr' if not addr else addr
        super(CoinoneREST, self).__init__(addr=addr, version=version, key=key, secret=secret,
                                          timeout=timeout, config=config, proxies=proxies)

    def sign_request_kwargs(self, endpoint, **kwargs):
        """Sign the request."""
        req_kwargs = super(CoinoneREST, self).sign_request_kwargs(endpoint, **kwargs)

        # Parameters go into headers & data, so pop params key and generate signature
        payload = req_kwargs.pop('params')
        payload['nonce'] = self.nonce()
        dumped_json = json.dumps(payload)
        encoded_payload = base64.b64encode(bytes(dumped_json, encoding='utf8'))

        sign = hmac.new(bytes(self.secret.upper(), encoding='utf8'), encoded_payload,
                        hashlib.sha512)
        signature = sign.hexdigest()
        headers = {
            'Content-Type': 'application/json',
            'X-COINONE-PAYLOAD': encoded_payload,
            'X-COINONE-SIGNATURE': signature,
        }
        req_kwargs['data'] = encoded_payload
        req_kwargs['headers'] = headers

        return req_kwargs
