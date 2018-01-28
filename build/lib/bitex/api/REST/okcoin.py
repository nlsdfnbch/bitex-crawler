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


class OKCoinREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://www.okcoin.com/api', timeout=5):
        super(OKCoinREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret,
                                         timeout=timeout)

    def sign(self,url, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()

        # sig = nonce + url + req
        data = (nonce + url).encode()

        h = hmac.new(self.secret.encode('utf8'), data, hashlib.sha256)
        signature = h.hexdigest()
        headers = {"ACCESS-KEY":       self.key,
                   "ACCESS-NONCE":     nonce,
                   "ACCESS-SIGNATURE": signature}

        return url, {'headers': headers}

