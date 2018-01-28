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


class VaultoroREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://api.vaultoro.com', timeout=5):
        api_version = '' if not api_version else api_version
        super(VaultoroREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        kwargs['nonce'] = nonce
        kwargs['apikey'] = self.key
        msg = uri + urllib.parse.urlencode(params)

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-Signature': signature}
        return msg, {'headers': headers}

