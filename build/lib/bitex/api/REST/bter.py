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


class BterREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='http://data.bter.com/api', timeout=5):
        api_version = '1' if not api_version else api_version
        super(BterREST, self).__init__(url, api_version=api_version,
                                           key=key, secret=secret,
                                           timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        nonce = self.nonce()
        kwargs['nonce'] = nonce

        msg = urllib.parse.urlencode(params)

        signature = hmac.new(self.secret.encode(encoding='utf-8'),
                             msg.encode(encoding='utf-8'), hashlib.sha512).hexdigest()
        headers = {'Key': signature, 'Sign': signature}
        return uri + msg, {'headers': headers}

