"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import hashlib
import hmac

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class RockTradingREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.therocktrading.com', timeout=5):
        super(RockTradingREST, self).__init__(url, api_version=api_version,
                                              key=key, secret=secret,
                                              timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        payload = params
        payload['nonce'] = int(nonce)
        payload['request'] = endpoint_path

        msg = nonce + uri
        sig = hmac.new(self.secret.encode(), msg.encode(), hashlib.sha384).hexdigest()
        headers = {'X-TRT-APIKEY': self.key,
                   'X-TRT-Nonce': nonce,
                   'X-TRT-SIGNATURE': sig, 'Content-Type': 'application/json'}
        return uri, {'headers': headers}

