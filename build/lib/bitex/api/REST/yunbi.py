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


class YunbiREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v2',
                 url='https://yunbi.com/api', timeout=5):
        super(YunbiREST, self).__init__(url, api_version=api_version, key=key,
                                         secret=secret, timeout=timeout)

    def sign(self, uri, endpoint, endpoint_path, method_verb, *args, **kwargs):
        nonce = self.nonce()
        try:
            params = kwargs['params']
        except KeyError:
            params = {}
        params['tonce'] = nonce
        params['access_key'] = self.key
        post_params = urllib.parse.urlencode(params)
        msg = '%s|%s|%s' % (method_verb, endpoint_path, post_params)

        sig = hmac.new(self.secret, msg, hashlib.sha256).hexdigest()
        uri += post_params + '&signature=' + sig

        return uri, {}

