"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import hashlib
import hmac
import urllib
import urllib.parse

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class PoloniexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://poloniex.com', timeout=5):
        super(PoloniexREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        params['nonce'] = self.nonce()
        payload = params

        msg = urllib.parse.urlencode(payload).encode('utf-8')
        sig = hmac.new(self.secret.encode('utf-8'), msg, hashlib.sha512).hexdigest()
        headers = {'Key': self.key, 'Sign': sig}
        return uri, {'headers': headers, 'data': params}

