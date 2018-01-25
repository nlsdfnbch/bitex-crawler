"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64

# Import Homebrew
from bitex.api.REST.api import APIClient

log = logging.getLogger(__name__)


class BitfinexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.bitfinex.com', timeout=5):
        super(BitfinexREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            req = kwargs['params']
        except KeyError:
            req = {}
        if self.version == 'v1':
            req['request'] = endpoint_path
            req['nonce'] = self.nonce()
            try:
                symbol = kwargs['symbol']
                req['symbol'] = symbol
            except Exception as e:
                print()
            js = json.dumps(req)
            data = base64.standard_b64encode(js.encode('utf8'))
        else:
            data = '/api/' + endpoint_path + self.nonce() + json.dumps(req)
        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        headers = {"X-BFX-APIKEY": self.key,
                   "X-BFX-SIGNATURE": signature,
                   "X-BFX-PAYLOAD": data}
        if self.version == 'v2':
            headers['content-type'] = 'application/json'

        return url, {'headers': headers}
