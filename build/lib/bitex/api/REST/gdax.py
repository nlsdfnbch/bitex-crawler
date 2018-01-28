"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import hashlib
import hmac
import base64
import time

# Import Third-Party
from requests.auth import AuthBase

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class GdaxAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key.encode('utf-8')
        self.secret_key = secret_key.encode('utf-8')
        self.passphrase = passphrase.encode('utf-8')

    def __call__(self, request):
        timestamp = str(time.time())
        message = (timestamp + request.method + request.path_url +
                   (request.body.decode('utf-8') or ''))
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest())

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


class GDAXRest(APIClient):
    def __init__(self, passphrase='', key=None, secret=None, api_version=None,
                 url='https://api.gdax.com', timeout=5):
        self.passphrase = passphrase
        super(GDAXRest, self).__init__(url, api_version=api_version, key=key,
                                       secret=secret, timeout=timeout)

    def load_key(self, path):
        """
        Load key and secret from file.
        """
        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
            self.passphrase = f.readline().strip()

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        auth = GdaxAuth(self.key, self.secret, self.passphrase)
        try:
            js = kwargs['params']
        except KeyError:
            js = {}

        return url, {'json': js, 'auth': auth}

