"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import json
import hashlib
import hmac
import base64
import urllib
import urllib.parse

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class CryptopiaREST(APIClient):
    def __init__(self, key=None, secret=None, api_version=None,
                 url='https://www.cryptopia.co.nz/api', timeout=5):
        super(CryptopiaREST, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}

        post_data = json.dumps(params)

        # generate signature
        md5 = hashlib.md5()
        md5.update(post_data.encode('utf-8'))
        request_content_b64_string = base64.b64encode(md5.digest()).decode('utf-8')
        signature = (self.key + 'POST' +
                     urllib.parse.quote_plus(uri).lower() +
                     nonce + request_content_b64_string)

        hmac_sig = base64.b64encode(hmac.new(base64.b64decode(self.secret),
                                             signature.encode('utf-8'),
                                             hashlib.sha256).digest())
        header_data = 'amx ' + self.key + ':' + hmac_sig.decode('utf-8') + ':' + nonce

        # Update req_kwargs keys
        headers = {'Authorization': header_data,
                                 'Content-Type': 'application/json; charset=utf-8'}

        return uri, {'headers': headers, 'data': post_data}

