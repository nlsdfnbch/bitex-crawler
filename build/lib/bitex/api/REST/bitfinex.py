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
        global headers
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
                try:
                    symbol = kwargs['currency']
                    req['currency'] = symbol
                except Exception as e:
                    print()
            js = json.dumps(req)
            data = base64.standard_b64encode(js.encode('utf8'))
            signature = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384).hexdigest()
            headers = {"X-BFX-APIKEY": self.key,
                       "X-BFX-SIGNATURE": signature,
                       "X-BFX-PAYLOAD": data}
        elif self.version == 'v2':
            data = '/api/' + endpoint_path + self.nonce() + json.dumps(req)
            data = base64.standard_b64encode(data.encode('utf8'))
            signature = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384).hexdigest()
            headers = {'bfx-nonce': self.nonce(),
                       'bfx-apikey': self.key,
                       'bfx-signature': signature,
                       'btx-payload': data,
                       'content-type': 'application/json'}
        return url, {'headers': headers}
