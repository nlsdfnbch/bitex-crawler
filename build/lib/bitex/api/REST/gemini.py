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

# Import Homebrew
from bitex.api.REST.api import APIClient


log = logging.getLogger(__name__)


class GeminiREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://api.gemini.com', timeout=5):
        super(GeminiREST, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        payload = params
        payload['nonce'] = nonce
        payload['request'] = endpoint_path

        js = json.dumps(payload)
        data = base64.standard_b64encode(js.encode('utf8'))
        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        headers = {'X-GEMINI-APIKEY': self.key,
                   'X-GEMINI-PAYLOAD': data,
                   'X-GEMINI-SIGNATURE': signature}
        return uri, {'headers': headers}

