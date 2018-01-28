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


class CCEXRest(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://c-cex.com/t', timeout=5):
        super(CCEXRest, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        params['apikey'] = self.key
        params['nonce'] = nonce
        post_params = params
        post_params.update({'nonce': nonce, 'method': endpoint})
        post_params = urllib.parse.urlencode(post_params)

        url = uri + post_params

        sig = hmac.new(url, self.secret, hashlib.sha512)
        headers = {'apisign': sig}

        return url, {'headers': headers}

