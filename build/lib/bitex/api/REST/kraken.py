"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import hashlib
import hmac
import base64
import urllib
import urllib.parse

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class KrakenREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='0',
                 url='https://api.kraken.com', timeout=5):
        super(KrakenREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret, timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            req = kwargs['params']
        except KeyError:
            req = {}

        req['nonce'] = self.nonce()
        postdata = urllib.parse.urlencode(req)

        # Unicode-objects must be encoded before hashing
        encoded = (str(req['nonce']) + postdata).encode('utf-8')
        message = (endpoint_path.encode('utf-8') +
                   hashlib.sha256(encoded).digest())

        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        sigdigest = base64.b64encode(signature.digest())

        headers = {
            'API-Key': self.key,
            'API-Sign': sigdigest.decode('utf-8')
        }

        return url, {'data': req, 'headers': headers}

