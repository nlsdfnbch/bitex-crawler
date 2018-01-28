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


class BitstampREST(APIClient):
    def __init__(self, user_id='', key=None, secret=None, api_version=None,
                 url='https://www.bitstamp.net/api', timeout=5):
        self.id = user_id
        super(BitstampREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def load_key(self, path):
        """Load key and secret from file."""
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.id = f.readline().strip()

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        message = nonce + self.id + self.key

        signature = hmac.new(self.secret.encode(), message.encode(),
                             hashlib.sha256)
        signature = signature.hexdigest().upper()

        try:
            req = kwargs['params']
        except KeyError:
            req = {}
        req['key'] = self.key
        req['nonce'] = nonce
        req['signature'] = signature
        return url, {'data': req}

