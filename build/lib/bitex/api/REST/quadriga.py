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


class QuadrigaCXREST(APIClient):
    def __init__(self, key=None, secret=None, client_id='', api_version='v2',
                 url='https://api.quoine.com/', timeout=5):
        self.client_id = client_id
        super(QuadrigaCXREST, self).__init__(url, api_version=api_version,
                                             key=key, secret=secret,
                                             timeout=timeout)

    def load_key(self, path):
        """
        Load key and secret from file.
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.client_id = f.readline().strip()

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        msg = nonce + self.client_id + self.key

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha256)
        headers = {'key': self.key, 'signature': signature,
                   'nonce': nonce}
        return self.uri, {'headers': headers, 'data': params}

