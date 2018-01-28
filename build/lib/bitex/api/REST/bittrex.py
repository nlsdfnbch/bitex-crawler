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


class BittrexREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1.1',
                 url='https://bittrex.com/api', timeout=5):
        super(BittrexREST, self).__init__(url, api_version=api_version, key=key,
                                          secret=secret, timeout=timeout)

    def sign(self, url, endpoint, endpoint_path, method_verb, *args, **kwargs):

        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        nonce = self.nonce()

        req_string = endpoint_path + '?apikey=' + self.key + "&nonce=" + nonce + '&'
        req_string += urllib.parse.urlencode(params)
        headers = {"apisign": hmac.new(self.secret.encode('utf-8'),
                                       (self.uri + req_string).encode('utf-8'),
                                       hashlib.sha512).hexdigest()}

        return self.uri + req_string, {'headers': headers, 'params': {}}

